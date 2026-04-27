#!/usr/bin/env python3
"""Weekly grants bot for The Grant Desk.

Searches Bluesky's public API for posts under a curated hashtag list, follows
each post's external link to the actual grant page (resolving shorteners),
asks Claude Haiku 4.5 to extract a structured grant entry, and inserts
high-confidence candidates with future deadlines at the top of grants.json.

Outputs a PR body to /tmp/pr_body.md and emits has_candidates / count to
GITHUB_OUTPUT so the workflow can decide whether to open a draft PR.

Run locally:
    ANTHROPIC_API_KEY=sk-... python3 smalltools/grants/grants_bot.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from anthropic import Anthropic, APIError

HERE = Path(__file__).parent
GRANTS_FILE = HERE / "grants.json"
STATE_FILE = HERE / ".bot_state.json"
PR_BODY_FILE = Path("/tmp/pr_body.md")

BLUESKY_SEARCH = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"
USER_AGENT = "GrantsBot/1.0 (+https://www.artificialnouveau.com/smalltools/grants/)"

HASHTAGS = [
    "opencall",
    "artistsopportunities",
    "residency",
    "fellowship",
    "grants",
    "funding",
    "call4artists",
    "artgrant",
]

LOOKBACK_DAYS = 14
MAX_POSTS_PER_TAG = 50
MAX_PROCESSED_HISTORY = 1000
CONFIDENCE_THRESHOLD = 0.7
PAGE_FETCH_TIMEOUT_S = 20
PAGE_TEXT_MAX_CHARS = 12000
INTER_CALL_SLEEP_S = 0.5

MODEL = "claude-haiku-4-5"

EXTRACTION_PROMPT = """You are extracting grant entries for The Grant Desk. The desk is for PAID open calls (cash component required) for individuals, small teams, or nonprofits, with FUTURE deadlines.

You will receive: a Bluesky post, any embedded links, and a category hint.

REJECT (return {"reject": "<reason>"}) if:
- Deadline is past or you cannot determine a deadline
- The opportunity is solely in-kind (free studio, housing, mentorship without cash)
- It's a scholarship, internship, job, or paid call for a thesis/dissertation
- The post is general commentary, not a specific call
- Information is too vague to verify (no url, no org name)
- The applicant must pay a fee TO participate (paid program, not a grant)

OTHERWISE return JSON matching this schema strictly:
{
  "title": "string (the grant name, no extra commentary)",
  "organization": "string",
  "location": "string",
  "region": "EU"|"US"|"UK"|"NL"|"Canada"|"Remote"|"Worldwide",
  "category": "ai"|"tech"|"research"|"film"|"arts"|"cross",
  "amount": "string (include currency symbol)",
  "deadline": "YYYY-MM-DD",
  "url": "string (the canonical apply page, NOT the bsky.app post URL)",
  "description": "string (2-4 sentence summary in plain English)",
  "confidence": 0.0-1.0
}

Set confidence below 0.7 if any field is uncertain. Return ONLY the JSON object. No prose, no code fences, no commentary."""


# --- Bluesky -------------------------------------------------------------- #


def search_bluesky(query: str, limit: int = MAX_POSTS_PER_TAG) -> list:
    params = {"q": query, "limit": limit, "sort": "latest"}
    try:
        r = requests.get(
            BLUESKY_SEARCH,
            params=params,
            timeout=20,
            headers={"User-Agent": USER_AGENT},
        )
        r.raise_for_status()
        return r.json().get("posts", [])
    except (requests.RequestException, ValueError) as e:
        print(f"[search] {query!r} failed: {e}", file=sys.stderr)
        return []


def is_bsky_url(u: str) -> bool:
    return "bsky.app" in u or "bsky.social" in u


def extract_post_links(post: dict) -> list[str]:
    """Pull external URLs from embed, facets, and raw text — skipping bsky.app."""
    urls: list[str] = []
    record = post.get("record") or {}

    embed = record.get("embed") or {}
    if embed.get("$type") == "app.bsky.embed.external":
        ext = embed.get("external") or {}
        if ext.get("uri"):
            urls.append(ext["uri"])

    for facet in record.get("facets") or []:
        for feature in facet.get("features") or []:
            uri = feature.get("uri")
            if uri:
                urls.append(uri)

    text = record.get("text", "")
    for m in re.finditer(r"https?://\S+", text):
        urls.append(m.group(0).rstrip(").,;:!?\"'"))

    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u and u not in seen and not is_bsky_url(u):
            seen.add(u)
            out.append(u)
    return out


def post_uri_to_url(uri: str, handle: str) -> str:
    m = re.search(r"app\.bsky\.feed\.post/(.+)$", uri or "")
    if not m:
        return uri or ""
    return f"https://bsky.app/profile/{handle}/post/{m.group(1)}"


# --- Page fetch ----------------------------------------------------------- #


def resolve_redirects(url: str) -> str:
    try:
        r = requests.head(
            url,
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        if r.status_code < 400 and r.url:
            return r.url
    except requests.RequestException:
        pass
    return url


def fetch_page_text(url: str) -> str:
    try:
        r = requests.get(
            url,
            timeout=PAGE_FETCH_TIMEOUT_S,
            headers={"User-Agent": USER_AGENT},
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return f"[Could not fetch page: {e}]"
    text = r.text
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:PAGE_TEXT_MAX_CHARS]


# --- Claude --------------------------------------------------------------- #


def call_claude(
    client: Anthropic,
    post_text: str,
    link_url: str,
    page_text: str,
    category_hint: str,
) -> dict | None:
    user_content = (
        f"BLUESKY POST TEXT:\n{post_text}\n\n"
        f"LINKED URL: {link_url}\n\n"
        f"CATEGORY HINT: {category_hint}\n\n"
        f"LINKED PAGE CONTENT (truncated):\n{page_text}"
    )
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": EXTRACTION_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )
    except APIError as e:
        print(f"[claude] API error: {e}", file=sys.stderr)
        return None

    text = ""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text = block.text
            break
    if not text:
        return None

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


# --- Helpers -------------------------------------------------------------- #


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"processed_uris": []}


def save_state(state: dict) -> None:
    state["processed_uris"] = state["processed_uris"][-MAX_PROCESSED_HISTORY:]
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def slugify(s: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return slug[:60] or "untitled"


CATEGORY_TAGS = {
    "ai": ["fellowship", "AI", "research"],
    "tech": ["grant", "tech"],
    "research": ["grant", "research"],
    "film": ["grant", "film"],
    "arts": ["grant", "art"],
    "cross": ["grant", "cross-disciplinary"],
}


def category_to_tags(category: str) -> list[str]:
    return CATEGORY_TAGS.get(category, ["grant"])


CATEGORY_HINT_FOR_TAG = {
    "opencall": "arts",
    "artistsopportunities": "arts",
    "residency": "arts",
    "fellowship": "research",
    "grants": "cross",
    "funding": "cross",
    "call4artists": "arts",
    "artgrant": "arts",
}


def category_hint_for(query: str) -> str:
    return CATEGORY_HINT_FOR_TAG.get(query, "cross")


def parse_iso_date(s: str | None) -> date | None:
    try:
        return datetime.strptime(s or "", "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def set_output(name: str, value: str) -> None:
    out_path = os.environ.get("GITHUB_OUTPUT")
    if not out_path:
        return
    with open(out_path, "a") as f:
        f.write(f"{name}={value}\n")


# --- Main ----------------------------------------------------------------- #


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    state = load_state()
    processed_uris: set[str] = set(state.get("processed_uris", []))

    grants_data = json.loads(GRANTS_FILE.read_text())
    existing_ids: set[str] = {g["id"] for g in grants_data.get("grants", [])}
    existing_urls: set[str] = {
        (g.get("url") or "").rstrip("/") for g in grants_data.get("grants", [])
    }

    client = Anthropic(api_key=api_key)

    today = date.today()
    cutoff = today - timedelta(days=LOOKBACK_DAYS)
    candidates: list[dict] = []
    seen_post_uris: set[str] = set()
    seen_link_urls: set[str] = set()

    for tag in HASHTAGS:
        print(f"[search] #{tag}")
        posts = search_bluesky(f"#{tag}")
        for post in posts:
            uri = post.get("uri") or ""
            if not uri or uri in processed_uris or uri in seen_post_uris:
                continue
            seen_post_uris.add(uri)

            indexed = post.get("indexedAt") or ""
            try:
                post_date = datetime.fromisoformat(
                    indexed.replace("Z", "+00:00")
                ).date()
            except (TypeError, ValueError):
                continue
            if post_date < cutoff:
                continue

            urls = extract_post_links(post)
            if not urls:
                continue
            link_url = resolve_redirects(urls[0])
            normalised = link_url.rstrip("/")
            if normalised in existing_urls or link_url in seen_link_urls:
                processed_uris.add(uri)
                continue
            seen_link_urls.add(link_url)

            print(f"  → {link_url}")
            page_text = fetch_page_text(link_url)

            post_text = (post.get("record") or {}).get("text", "")
            handle = (post.get("author") or {}).get("handle", "")
            extracted = call_claude(
                client, post_text, link_url, page_text, category_hint_for(tag)
            )
            time.sleep(INTER_CALL_SLEEP_S)

            if not extracted or "reject" in extracted:
                processed_uris.add(uri)
                continue

            try:
                confidence = float(extracted.get("confidence", 0) or 0)
            except (TypeError, ValueError):
                confidence = 0.0
            if confidence < CONFIDENCE_THRESHOLD:
                processed_uris.add(uri)
                continue

            deadline_str = extracted.get("deadline")
            deadline_date = parse_iso_date(deadline_str)
            if not deadline_date or deadline_date < today:
                processed_uris.add(uri)
                continue

            grant_url = (extracted.get("url") or link_url).strip()
            if grant_url.rstrip("/") in existing_urls:
                processed_uris.add(uri)
                continue

            base_id = slugify(extracted.get("title") or "untitled")
            grant_id = base_id
            counter = 2
            while grant_id in existing_ids:
                grant_id = f"{base_id}-{counter}"
                counter += 1

            entry = {
                "id": grant_id,
                "title": extracted.get("title") or "Untitled",
                "organization": extracted.get("organization") or "",
                "location": extracted.get("location") or "",
                "region": extracted.get("region") or "Worldwide",
                "amount": extracted.get("amount") or "",
                "duration": "Per project",
                "startDate": None,
                "deadline": deadline_str,
                "addedDate": today.isoformat(),
                "description": extracted.get("description") or "",
                "url": grant_url,
                "tags": category_to_tags(extracted.get("category") or "cross"),
                "fee": False,
                "featured": False,
            }

            candidates.append(
                {
                    "post_uri": uri,
                    "post_url": post_uri_to_url(uri, handle),
                    "entry": entry,
                    "confidence": confidence,
                    "category_hint": category_hint_for(tag),
                }
            )
            existing_ids.add(grant_id)
            existing_urls.add(grant_url.rstrip("/"))
            processed_uris.add(uri)

    state["processed_uris"] = sorted(processed_uris)
    save_state(state)

    set_output("has_candidates", "true" if candidates else "false")
    set_output("count", str(len(candidates)))

    if not candidates:
        print("No new candidates this run.")
        return 0

    grants_data["grants"] = [c["entry"] for c in candidates] + grants_data.get(
        "grants", []
    )
    grants_data["lastUpdated"] = today.isoformat()
    GRANTS_FILE.write_text(
        json.dumps(grants_data, indent=2, ensure_ascii=False) + "\n"
    )

    body_lines = [
        f"# Grants bot - {today.isoformat()}",
        "",
        f"Found **{len(candidates)}** candidate grant(s) from Bluesky in the last {LOOKBACK_DAYS} days.",
        "",
        "Review the diff in `smalltools/grants/grants.json`. Delete any rows you don't want, then mark this PR ready to merge. The branch deletes itself on merge.",
        "",
        "---",
        "",
    ]
    for c in candidates:
        e = c["entry"]
        body_lines.extend(
            [
                f"### {e['title']}",
                f"- **Organisation:** {e['organization']}",
                f"- **Region / Location:** {e['region']} - {e['location']}",
                f"- **Amount:** {e['amount']}",
                f"- **Deadline:** {e['deadline']}",
                f"- **Confidence:** {c['confidence']:.2f} - Category hint: {c['category_hint']}",
                f"- **Description:** {e['description']}",
                f"- **Apply URL:** {e['url']}",
                f"- **Source post:** {c['post_url']}",
                "",
            ]
        )
    PR_BODY_FILE.write_text("\n".join(body_lines))

    print(f"Wrote {len(candidates)} candidate(s) to grants.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
