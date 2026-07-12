#!/usr/bin/env python3
"""Recheck past grants for a new cycle, 6-9 months after their deadline.

Scans grants.json for entries whose deadline fell 180-270 days ago, fetches
each entry's stored URL (plus the site root if the page looks stale), and asks
Claude Haiku whether a new edition with a future deadline is announced. High
confidence hits are inserted into grants.json as candidates, exactly like
grants_bot.py does, so the scheduled workflow can open a draft PR for review.

Entries are skipped when the same organization already has an active entry, or
when they were already rechecked recently (state in .recheck_state.json:
'no_new' retries after RETRY_DAYS; 'proposed' is never rechecked).

Outputs a PR body to /tmp/recheck_pr_body.md and emits has_candidates / count
to GITHUB_OUTPUT.

Run locally:
    ANTHROPIC_API_KEY=sk-... python3 smalltools/grants/recheck_grants.py
    DRY_RUN=1 ANTHROPIC_API_KEY=... python3 ... (report only, no file writes)
"""
from __future__ import annotations

import json
import os
import re
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

from anthropic import Anthropic

from grants_bot import call_claude_json, fetch_page_text, parse_iso_date, set_output

HERE = Path(__file__).parent
GRANTS_FILE = HERE / "grants.json"
INDEX_FILE = HERE / "index.html"
STATE_FILE = HERE / ".recheck_state.json"
PR_BODY_FILE = Path("/tmp/recheck_pr_body.md")

WINDOW_MIN_DAYS = 180
WINDOW_MAX_DAYS = 270
RETRY_DAYS = 60
MAX_CHECKS_PER_RUN = 12
MAX_WATCHLIST_CHECKS_PER_RUN = 10
MIN_CONFIDENCE = 0.7

WATCHLIST_LI_RE = re.compile(
    r'(<li data-watchlist-until="([\d-]+)">\s*'
    r'<a href="([^"]+)"[^>]*><strong>([^<]+)</strong></a>\s*'
    r'\.\s*(.*?)</li>)',
    re.DOTALL,
)

RECHECK_PROMPT = """You check whether a grant/open call has announced a NEW cycle.

You are given a PREVIOUS grant entry (title, organization, deadline that has
passed) and the CURRENT content of its web page (and possibly the site root).
Decide whether a new edition/cycle/round of the SAME opportunity is announced
with an application deadline strictly AFTER {today}.

Return new_cycle=false when:
- The page still describes the old cycle, or only says "check back later"
- The new cycle's deadline is unclear, already passed, or not yet announced
- The program is discontinued
- The new cycle requires program/participation/tuition fees without also
  providing funding (a stipend or award on top)

OTHERWISE return JSON strictly matching:
{{
  "new_cycle": true,
  "title": "string (updated name, include the new year/edition)",
  "deadline": "YYYY-MM-DD",
  "url": "string (page describing the new cycle; keep the old URL if it is the same page)",
  "amount": "string (updated amount with currency, or the old amount if unchanged)",
  "description": "string (2-4 sentence summary of the new cycle in plain English)",
  "confidence": 0.0-1.0
}}
Respond with the JSON object only, no commentary."""

WATCHLIST_PROMPT = """You check whether a watched grant/open call has OPENED.

You are given a "watch for next round" note about a funder whose call was
expected to reopen (with its expected timing), and the CURRENT content of its
web page. Decide whether the new cycle is NOW OPEN for applications with a
deadline strictly AFTER {today}.

Return open=false when the call has not opened yet, the deadline is unclear or
passed, the program is discontinued, or the new cycle requires
program/participation/tuition fees without also providing funding.

OTHERWISE return JSON strictly matching:
{{
  "open": true,
  "title": "string (name including the new year/edition)",
  "organization": "string",
  "location": "string (city/country and any residency restriction)",
  "region": "EU"|"US"|"UK"|"NL"|"Asia"|"Africa"|"Canada"|"Australia"|"LatAm"|"Remote"|"Worldwide",
  "category": "ai"|"tech"|"research"|"writers"|"film"|"arts"|"game"|"design"|"curator"|"audio"|"cross",
  "amount": "string (with currency)",
  "deadline": "YYYY-MM-DD",
  "url": "string (the page describing the open call)",
  "fee": true|false (true only if applying costs money),
  "description": "string (2-4 sentence summary in plain English)",
  "confidence": 0.0-1.0
}}
Respond with the JSON object only, no commentary."""


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def org_key(org: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", org.lower())[:40]


def pick_candidates(grants: list, state: dict, today: date) -> list:
    active_orgs = set()
    for g in grants:
        dl = parse_iso_date(g.get("deadline"))
        if dl is None or dl >= today:
            active_orgs.add(org_key(g.get("organization", "")))

    out = []
    for g in grants:
        dl = parse_iso_date(g.get("deadline"))
        if dl is None:
            continue
        days_past = (today - dl).days
        if not (WINDOW_MIN_DAYS <= days_past <= WINDOW_MAX_DAYS):
            continue
        if org_key(g.get("organization", "")) in active_orgs:
            continue
        st = state.get(g["id"], {})
        if st.get("result") == "proposed":
            continue
        checked = parse_iso_date(st.get("checked"))
        if checked and (today - checked).days < RETRY_DAYS:
            continue
        out.append(g)
    out.sort(key=lambda g: g.get("deadline") or "")
    return out[:MAX_CHECKS_PER_RUN]


def safe_confidence(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def next_year_id(old_id: str, deadline: str) -> str:
    year = deadline[:4]
    # strip trailing year or year-range segments: -2026, -2026-27, -2026-2027
    stripped = re.sub(r"(-\d{4})(-\d{2}|-\d{4})?$", "", old_id)
    return f"{stripped}-{year}"


def build_entry(old: dict, ex: dict, today: date) -> dict:
    entry = {k: old.get(k) for k in (
        "organization", "location", "region", "category", "applicant", "tags", "fee")}
    entry.update({
        "id": next_year_id(old["id"], ex["deadline"]),
        "title": str(ex.get("title") or old["title"]).strip()[:160],
        "amount": str(ex.get("amount") or old.get("amount", "")).strip(),
        "duration": old.get("duration", ""),
        "startDate": None,
        "deadline": ex["deadline"],
        "addedDate": today.isoformat(),
        "category": old.get("category", "arts"),
        "description": (
            str(ex.get("description", "")).strip()
            + f" NOTE: auto-proposed by the recheck bot from the previous cycle ({old['id']}); verify details on the page before publishing."
        ),
        "url": str(ex.get("url") or old["url"]).strip(),
        "featured": False,
    })
    return entry


def parse_watchlist(html: str) -> list[dict]:
    """Parse the Watch for next round drawer items out of index.html."""
    m = re.search(r'<ul class="watchlist-list" id="watchlist-list">.*?</ul>', html, re.DOTALL)
    if not m:
        return []
    items = []
    for full, until, url, title, note in WATCHLIST_LI_RE.findall(m.group(0)):
        items.append({
            "li": full,
            "until": until,
            "url": url,
            "title": title.strip(),
            "note": re.sub(r"\s+", " ", note).strip(),
        })
    return items


def pick_watchlist_candidates(items: list[dict], state: dict, today: date) -> list[dict]:
    out = []
    for it in items:
        until = parse_iso_date(it["until"])
        if until and until < today:
            continue  # expired; the drawer auto-hides these, manual cleanup
        key = f"watchlist:{it['url']}"
        st = state.get(key, {})
        if st.get("result") == "proposed":
            continue
        checked = parse_iso_date(st.get("checked"))
        if checked and (today - checked).days < RETRY_DAYS:
            continue
        out.append(it)
    out.sort(key=lambda it: it["until"])
    return out[:MAX_WATCHLIST_CHECKS_PER_RUN]


def build_watchlist_entry(it: dict, ex: dict, today: date) -> dict:
    slug = re.sub(r"[^a-z0-9]+", "-", str(ex.get("title", it["title"])).lower()).strip("-")[:60]
    cat = ex.get("category") if ex.get("category") in (
        "ai", "tech", "research", "writers", "film", "arts", "game",
        "design", "curator", "audio", "cross") else "arts"
    return {
        "id": slug,
        "title": str(ex.get("title") or it["title"]).strip()[:160],
        "organization": str(ex.get("organization", "")).strip() or it["title"],
        "location": str(ex.get("location", "")).strip(),
        "region": ex.get("region") if ex.get("region") in (
            "EU", "US", "UK", "NL", "Asia", "Africa", "Canada",
            "Australia", "LatAm", "Remote", "Worldwide") else "Worldwide",
        "amount": str(ex.get("amount", "")).strip(),
        "duration": "",
        "startDate": None,
        "deadline": ex["deadline"],
        "addedDate": today.isoformat(),
        "category": cat,
        "applicant": "individuals",
        "description": (
            str(ex.get("description", "")).strip()
            + " NOTE: auto-proposed by the recheck bot from the Watch for next round drawer; verify details on the page before publishing."
        ),
        "url": str(ex.get("url") or it["url"]).strip(),
        "tags": [cat, "recheck-bot"],
        "fee": bool(ex.get("fee", False)),
        "featured": False,
    }


def main() -> int:
    dry_run = bool(os.environ.get("DRY_RUN"))
    today = date.today()
    data = json.loads(GRANTS_FILE.read_text())
    grants = data["grants"]
    state = load_state()
    existing_ids = {g["id"] for g in grants}

    index_html = INDEX_FILE.read_text()
    watch_items = parse_watchlist(index_html)
    watch_candidates = pick_watchlist_candidates(watch_items, state, today)

    candidates = pick_candidates(grants, state, today)
    print(f"[recheck] {len(candidates)} past entr(ies) in the {WINDOW_MIN_DAYS}-{WINDOW_MAX_DAYS} day window; "
          f"{len(watch_candidates)} of {len(watch_items)} watchlist item(s) to check")
    if not candidates and not watch_candidates:
        set_output("has_candidates", "false")
        set_output("count", "0")
        return 0

    client = Anthropic()
    proposals = []
    watch_proposals = []

    for it in watch_candidates:
        page = fetch_page_text(it["url"])
        user_content = (
            f"WATCHLIST NOTE:\ntitle: {it['title']}\nurl: {it['url']}\n"
            f"note: {it['note']}\n\n"
            f"CURRENT PAGE CONTENT (truncated):\n{page}"
        )
        ex = call_claude_json(client, WATCHLIST_PROMPT.format(today=today.isoformat()), user_content)
        key = f"watchlist:{it['url']}"
        if ex is None:
            # API/parse failure: record nothing so the item retries next run
            # instead of being deferred RETRY_DAYS.
            print(f"[recheck] watchlist {it['title']}: skipped (no model reply)")
            continue
        result = "no_new"
        if ex.get("open"):
            dl = parse_iso_date(ex.get("deadline"))
            conf = safe_confidence(ex.get("confidence"))
            if dl and dl > today and conf >= MIN_CONFIDENCE:
                entry = build_watchlist_entry(it, ex, today)
                if entry["id"] not in existing_ids:
                    watch_proposals.append((it, entry))
                    existing_ids.add(entry["id"])
                    result = "proposed"
        state[key] = {"checked": today.isoformat(), "result": result}
        print(f"[recheck] watchlist {it['title']}: {result}")
    for g in candidates:
        page = fetch_page_text(g["url"])
        root = ""
        if page.startswith("[Could not fetch page") or len(page) < 500:
            parsed = urlparse(g["url"])
            root_url = f"{parsed.scheme}://{parsed.netloc}/"
            if root_url != g["url"]:
                root = fetch_page_text(root_url)
        user_content = (
            f"PREVIOUS ENTRY:\n"
            f"title: {g['title']}\norganization: {g['organization']}\n"
            f"old deadline (passed): {g['deadline']}\nurl: {g['url']}\n"
            f"amount: {g.get('amount', '')}\n\n"
            f"CURRENT PAGE CONTENT (truncated):\n{page}\n\n"
            + (f"SITE ROOT CONTENT (truncated):\n{root}" if root else "")
        )
        ex = call_claude_json(client, RECHECK_PROMPT.format(today=today.isoformat()), user_content)
        if ex is None:
            print(f"[recheck] {g['id']}: skipped (no model reply)")
            continue
        result = "no_new"
        if ex.get("new_cycle"):
            dl = parse_iso_date(ex.get("deadline"))
            conf = safe_confidence(ex.get("confidence"))
            if dl and dl > today and conf >= MIN_CONFIDENCE:
                entry = build_entry(g, ex, today)
                if entry["id"] not in existing_ids:
                    proposals.append((g, entry))
                    existing_ids.add(entry["id"])
                    result = "proposed"
        state[g["id"]] = {"checked": today.isoformat(), "result": result}
        print(f"[recheck] {g['id']}: {result}")

    total = len(proposals) + len(watch_proposals)

    if dry_run:
        print(f"[recheck] DRY_RUN: {total} proposal(s), not writing files")
        set_output("has_candidates", "false")
        set_output("count", "0")
        return 0

    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")

    if not total:
        set_output("has_candidates", "false")
        set_output("count", "0")
        return 0

    for _, entry in proposals + watch_proposals:
        grants.insert(0, entry)
    data["lastUpdated"] = today.isoformat()
    GRANTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    # Promoted watchlist items leave the drawer; the removal rides the same PR.
    if watch_proposals:
        for it, _ in watch_proposals:
            index_html = index_html.replace(it["li"], "")
        INDEX_FILE.write_text(index_html)

    lines = [
        "The recheck bot found likely NEW OR REOPENED CYCLES. Verify each page",
        "before merging; entries carry an auto-proposed note in their description",
        "that should be removed on review.",
        "",
    ]
    if proposals:
        lines.append("New cycles of past grants (6-9 months after their deadline):")
        for old, entry in proposals:
            lines.append(f"- **{entry['title']}** - deadline {entry['deadline']} - {entry['url']}")
            lines.append(f"  - previous cycle: `{old['id']}` (deadline {old['deadline']})")
        lines.append("")
    if watch_proposals:
        lines.append("Opened calls promoted from the Watch for next round drawer (li removed):")
        for it, entry in watch_proposals:
            lines.append(f"- **{entry['title']}** - deadline {entry['deadline']} - {entry['url']}")
    PR_BODY_FILE.write_text("\n".join(lines) + "\n")
    print("PR BODY:\n" + "\n".join(lines))

    set_output("has_candidates", "true")
    set_output("count", str(total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
