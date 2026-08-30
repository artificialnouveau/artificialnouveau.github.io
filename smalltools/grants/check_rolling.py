#!/usr/bin/env python3
"""Recheck rolling / undated grants, which nothing else in the pipeline revisits.

prune_grants.py only drops entries whose DEADLINE is over a year past, and
recheck_grants.py only looks at entries whose deadline fell 180-270 days ago.
Both are deadline-driven, so an entry with ``deadline: null`` is never looked at
again after it is added: a filled job or a discontinued fund sits on the desk
forever. This script closes that gap.

For every rolling entry it fetches the stored URL and sorts it into three piles:

  DEAD   the page 404s, or its text says the call is closed / the role is filled.
         These are safe to remove, and --apply does exactly that.
  CHECK  something a human has to look at: a bot-block (403), a connection
         failure, a 5xx, or an entry whose only explicit dates have all passed.
         Never auto-removed - Cloudflare 403s are routine on FilmFreeway and
         similar hosts, and a past date is often a launch date, not a closure.
  OK     reachable, with no closure wording.

Deliberately stdlib-only (urllib, not requests) so it runs anywhere generate_feed.py
does, with no install step.

Run locally:
    python3 smalltools/grants/check_rolling.py                # report only
    python3 smalltools/grants/check_rolling.py --json r.json  # machine-readable
    python3 smalltools/grants/check_rolling.py --apply        # remove DEAD, asks first
    python3 smalltools/grants/check_rolling.py --apply --auto # no prompt (CI)

After --apply, run generate_feed.py and commit, exactly as for prune_grants.py.
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
GRANTS_FILE = HERE / "grants.json"
REPORT_FILE = Path("/tmp/rolling_report.md")

TIMEOUT_S = 25
WORKERS = 8
MAX_BYTES = 400_000  # plenty for a closure banner, keeps big pages cheap
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# Phrases that mean "this specific call or role is over". Kept narrow on
# purpose: a generic word like "closed" matches navigation ("Closed Calls"),
# cookie banners and unrelated archive links on half the sites out there.
CLOSED_PATTERNS = [
    r"no longer accepting applications",
    r"no longer open",
    r"(?:this )?(?:position|role|vacancy|posting|job)\s+(?:has been|is|was)\s+(?:filled|closed)",
    r"closed vacancy",
    r"applications? (?:are|is|have) (?:now )?closed",
    r"this (?:call|round|programme|program|opportunity) (?:is|has) (?:now )?closed",
    r"we are not accepting applications",
    r"the (?:call|fund|programme|program) (?:is|has been) discontinued",
    r"job board you were viewing is no longer active",
]
CLOSED_RE = re.compile("|".join(CLOSED_PATTERNS), re.I)

MONTHS = {
    m.lower(): i
    for i, m in enumerate(
        [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ],
        1,
    )
}
DATE_DMY = re.compile(
    r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d\d)",
    re.I,
)
DATE_MDY = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d\d)",
    re.I,
)


def strip_html(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html).strip()


def fetch(url: str) -> tuple[int | None, str, str]:
    """Return (status, text, error). status is None when the fetch never landed."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=ctx) as r:
            return r.status, strip_html(r.read(MAX_BYTES).decode("utf-8", "ignore")), ""
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = strip_html(e.read(MAX_BYTES).decode("utf-8", "ignore"))
        except Exception:
            pass
        return e.code, body, ""
    except Exception as e:  # URLError, socket timeout, bad TLS, redirect loop
        return None, "", f"{type(e).__name__}: {e}"[:160]


def fetch_with_retry(url: str) -> tuple[int | None, str, str]:
    """One retry over the www/apex variant.

    Learned the hard way: rcdij.org answered nothing on https://www. but 200 on
    the apex host after redirects, and flagging that as dead would have been wrong.
    """
    status, text, err = fetch(url)
    if status is not None:
        return status, text, err
    if "://www." in url:
        alt = url.replace("://www.", "://", 1)
    else:
        alt = re.sub(r"://", "://www.", url, count=1)
    return fetch(alt)


def past_dates_only(grant: dict, today: date) -> str:
    """Flag entries whose every explicit date has passed.

    A weak signal on its own (the date is often a launch or an award-announcement
    date, not a closure), so it only ever lands an entry in CHECK.
    """
    blob = " ".join(str(grant.get(k, "")) for k in ("description", "amount", "duration", "location"))
    found = []
    for m in DATE_DMY.finditer(blob):
        found.append(date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1))))
    for m in DATE_MDY.finditer(blob):
        found.append(date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2))))
    if not found or any(d >= today for d in found):
        return ""
    return f"every date in the entry has passed (latest {max(found).isoformat()})"


def snippet(text: str, match: re.Match) -> str:
    start = max(0, match.start() - 120)
    return "..." + text[start:match.end() + 120].strip() + "..."


def classify(grant: dict, today: date) -> dict:
    url = grant.get("url") or ""
    row = {
        "id": grant["id"],
        "title": grant.get("title", ""),
        "url": url,
        "addedDate": grant.get("addedDate"),
        "status": None,
        "verdict": "ok",
        "reason": "",
        "evidence": "",
    }
    if not url:
        row.update(verdict="check", reason="entry has no url")
        return row

    status, text, err = fetch_with_retry(url)
    row["status"] = status

    if status in (404, 410):
        row.update(verdict="dead", reason=f"HTTP {status}")
        return row
    if status is None:
        row.update(verdict="check", reason=f"unreachable ({err or 'no response'})")
        return row
    if status != 200:
        # 403 is nearly always Cloudflare refusing a script, not a closed call.
        row.update(verdict="check", reason=f"HTTP {status}")
        return row

    m = CLOSED_RE.search(text)
    if m:
        row.update(verdict="dead", reason=f"page says: {m.group(0)}", evidence=snippet(text, m))
        return row

    stale = past_dates_only(grant, today)
    if stale:
        row.update(verdict="check", reason=stale)
    return row


def cut_entry(src: str, gid: str) -> str | None:
    """Delete one grant object from the raw JSON text.

    Raw-text surgery rather than json.dump so the other thousand-odd entries stay
    byte-identical and the diff shows only the removal. Two shapes to handle: a
    normal entry ends "},", the LAST entry in the array ends "}" with no comma,
    so that one is cut together with the comma in front of it.
    """
    body = r"\n    \{\n      \"id\": \"%s\",.*?\n    \}" % re.escape(gid)
    m = re.search(body + ",", src, flags=re.S)
    if m:
        return src[:m.start()] + src[m.end():]
    m = re.search("," + body + r"(?=\n  \])", src, flags=re.S)
    if m:
        return src[:m.start()] + src[m.end():]
    return None


def render_report(rows: list[dict]) -> str:
    dead = [r for r in rows if r["verdict"] == "dead"]
    check = [r for r in rows if r["verdict"] == "check"]
    ok = [r for r in rows if r["verdict"] == "ok"]
    out = [
        f"# Rolling grant check ({date.today().isoformat()})",
        "",
        f"Checked {len(rows)} rolling/undated entries: "
        f"{len(dead)} dead, {len(check)} to check by hand, {len(ok)} fine.",
        "",
    ]
    if dead:
        out += ["## Dead (safe to remove)", ""]
        for r in dead:
            out.append(f"- **{r['title']}** (`{r['id']}`) - {r['reason']}")
            out.append(f"  - {r['url']}")
            if r["evidence"]:
                out.append(f"  - > {r['evidence']}")
        out.append("")
    if check:
        out += ["## Needs a human", ""]
        for r in check:
            out.append(f"- **{r['title']}** (`{r['id']}`) - {r['reason']}")
            out.append(f"  - {r['url']}")
        out.append("")
    return "\n".join(out)


def set_output(name: str, value: str) -> None:
    out_path = os.environ.get("GITHUB_OUTPUT")
    if not out_path:
        return
    with open(out_path, "a") as f:
        f.write(f"{name}={value}\n")


def main() -> int:
    argv = sys.argv[1:]
    apply_changes = "--apply" in argv
    auto = "--auto" in argv
    json_out = None
    if "--json" in argv:
        i = argv.index("--json")
        json_out = argv[i + 1] if i + 1 < len(argv) else "rolling_report.json"

    src = GRANTS_FILE.read_text(encoding="utf-8")
    data = json.loads(src)
    grants = data.get("grants", []) or []
    rolling = [g for g in grants if not g.get("deadline")]
    today = date.today()

    print(f"Checking {len(rolling)} rolling/undated entries of {len(grants)} total...\n")
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        rows = list(ex.map(lambda g: classify(g, today), rolling))

    rows.sort(key=lambda r: ({"dead": 0, "check": 1, "ok": 2}[r["verdict"]], r["id"]))
    for r in rows:
        if r["verdict"] == "ok":
            continue
        label = "DEAD " if r["verdict"] == "dead" else "CHECK"
        print(f"{label}  {r['id']}")
        print(f"        {r['reason']}")
        print(f"        {r['url']}")
        if r["evidence"]:
            print(f"        > {r['evidence'][:240]}")

    dead = [r for r in rows if r["verdict"] == "dead"]
    check = [r for r in rows if r["verdict"] == "check"]
    print(f"\n{len(dead)} dead, {len(check)} to check by hand, "
          f"{len(rows) - len(dead) - len(check)} fine.")

    REPORT_FILE.write_text(render_report(rows), encoding="utf-8")
    print(f"Report written to {REPORT_FILE}")
    if json_out:
        Path(json_out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"JSON written to {json_out}")
    set_output("dead_count", str(len(dead)))
    set_output("check_count", str(len(check)))
    set_output("has_dead", "true" if dead else "false")

    if not apply_changes:
        if dead:
            print("\nDry run. Re-run with --apply to remove the DEAD entries.")
        return 0
    if not dead:
        print("\nNothing to remove.")
        return 0

    if not auto:
        confirm = input(f"\nRemove {len(dead)} dead entries? Type 'yes' to confirm: ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            return 1

    dead_ids = {r["id"] for r in dead}
    removed = 0
    for gid in dead_ids:
        cut = cut_entry(src, gid)
        if cut is None:
            print(f"WARNING: could not locate {gid} in the file; skipped.")
            continue
        src = cut
        removed += 1
    json.loads(src)  # refuse to write anything that is not valid JSON
    GRANTS_FILE.write_text(src, encoding="utf-8")

    remaining = json.loads(src).get("grants", [])
    print(f"\nWrote grants.json with {len(remaining)} grants ({removed} removed).")
    print("Now run: python3 smalltools/grants/generate_feed.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
