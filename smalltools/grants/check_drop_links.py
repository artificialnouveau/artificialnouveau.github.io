#!/usr/bin/env python3
"""Check the apply links of every grant in the next Sunday RSS drop.

Report only: nothing is edited or removed. Run on Saturdays by
.github/workflows/check-drop-links.yml, so a dead or closed page can be fixed
(or the grant taken out) before the drop goes out.

Which grants: the ones the next drop will carry, worked out the same way
generate_feed.py does (added-era, not opted out of feeds, not yet sent in the
main feed according to feed-drop-ledger.json, due by that drop, and still open
after its Sunday).

Each link lands in one of three piles (fetching and closure wording are shared
with check_rolling.py):

  BROKEN   404/410, or the page says the call is closed. Fix before Sunday.
  CHECK    the site refused a script (403, 429, ...) or did not answer. These
           almost always open fine in a browser; click them once.
  OK       loaded normally.

The run fails (so GitHub emails the repo owner) only when something is BROKEN.

Run locally:
    python3 smalltools/grants/check_drop_links.py
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import check_rolling as cr  # noqa: E402
import generate_feed as gf  # noqa: E402

# Drop grants are calls, not job ads: leave out check_rolling's job-listing
# phrases ("role is filled", "closed vacancy", "job board ... no longer
# active"), which grant pages trip over in unrelated text ("once that role is
# filled" on a funder's hiring blurb).
cr.CLOSED_RE = cr.re.compile("|".join(
    p for p in cr.CLOSED_PATTERNS
    if not any(w in p for w in ("position|role", "vacancy", "job board"))
), cr.re.I)


def next_drop_sunday(today):
    """The drop this check is for: the coming Sunday (today, if it is Sunday)."""
    return today + timedelta(days=(6 - today.weekday()) % 7)


def drop_grants(grants, ledger, sunday):
    """Grants the main feed will carry in the drop on ``sunday``."""
    monday = sunday - timedelta(days=6)
    entry = gf.ledger_entry(ledger.get(gf.feed_filename(None, weekly=True))) or {"sent": []}
    sent = set(entry["sent"])
    return [
        g for g in grants
        if g.get("feed") is not False and gf.in_added_era(g)
        and g.get("id") not in sent
        and gf.bucket_date(g) <= monday
        and gf.open_for_drop(g, sunday)
    ]


def main() -> int:
    data = json.loads((HERE / "grants.json").read_text(encoding="utf-8"))
    ledger_path = HERE / gf.DROP_LEDGER
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}
    today = datetime.now(timezone.utc).date()
    sunday = next_drop_sunday(today)
    grants = drop_grants(data.get("grants", []) or [], ledger, sunday)

    print(f"Checking {len(grants)} apply links for the {sunday:%d %b %Y} drop...\n")
    with ThreadPoolExecutor(max_workers=cr.WORKERS) as ex:
        rows = list(ex.map(lambda g: cr.classify(g, today), grants))

    broken = [r for r in rows if r["verdict"] == "dead"]
    # check_rolling's "every date has passed" hint is meant for rolling entries;
    # a dated call in the drop is open by construction, so only fetch problems count.
    check = [r for r in rows if r["verdict"] == "check" and r["status"] != 200]
    ok_count = len(rows) - len(broken) - len(check)

    lines = [f"# Apply links for the {sunday:%d %b %Y} drop", "",
             f"{len(rows)} links: {len(broken)} broken, {len(check)} to open by hand, "
             f"{ok_count} fine.", ""]
    if broken:
        lines += ["## Broken (fix or remove before Sunday)", ""]
        for r in broken:
            lines.append(f"- **{r['title']}** (`{r['id']}`): {r['reason']}")
            lines.append(f"  - {r['url']}")
            if r["evidence"]:
                lines.append(f"  - > {r['evidence'][:240]}")
        lines.append("")
    if check:
        lines += ["## Open by hand (the site refused a script; usually fine in a browser)", ""]
        for r in check:
            lines.append(f"- **{r['title']}** (`{r['id']}`): {r['reason']}")
            lines.append(f"  - {r['url']}")
        lines.append("")
    report = "\n".join(lines)
    print(report)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
