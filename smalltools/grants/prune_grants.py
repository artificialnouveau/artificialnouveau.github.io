#!/usr/bin/env python3
"""Prune grants whose deadline is more than 365 days in the past.

Usage:
    python3 smalltools/grants/prune_grants.py            # dry-run, just lists
    python3 smalltools/grants/prune_grants.py --apply    # actually deletes

Always lists what would be removed first. The --apply flag still asks for
y/N confirmation before writing. Rolling/undated grants are never pruned
since they have no deadline. Run this once a year (or whenever the file
feels heavy) to reclaim space.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).parent
CUTOFF_DAYS = 365


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def main():
    apply = "--apply" in sys.argv
    src = HERE / "grants.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    grants = data.get("grants", []) or []
    today = date.today()

    keep = []
    drop = []
    for g in grants:
        d = parse_date(g.get("deadline"))
        if not d:
            keep.append(g)
            continue
        days_past = (today - d).days
        if days_past > CUTOFF_DAYS:
            drop.append((g, days_past))
        else:
            keep.append(g)

    if not drop:
        print(f"Nothing to prune. {len(keep)} grants in the file, none are older than {CUTOFF_DAYS} days past their deadline.")
        return 0

    print(f"Found {len(drop)} grants closed more than {CUTOFF_DAYS} days ago:\n")
    for g, days in drop:
        print(f"  - [{days} days past] {g.get('title', g.get('id'))}")
        print(f"      deadline: {g.get('deadline')} | url: {g.get('url')}")
    print(f"\nWould keep: {len(keep)} grants. Would drop: {len(drop)}.")

    if not apply:
        print("\nDry run. Re-run with --apply to actually remove these.")
        return 0

    confirm = input("\nProceed with deletion? Type 'yes' to confirm: ").strip().lower()
    if confirm != "yes":
        print("Aborted.")
        return 1

    data["grants"] = keep
    src.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {src.name} with {len(keep)} grants. {len(drop)} dropped.")
    print("Now run: python3 smalltools/grants/generate_feed.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
