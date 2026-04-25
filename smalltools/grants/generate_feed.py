#!/usr/bin/env python3
"""Generate feed.xml (RSS 2.0) and calendar.ics from grants.json
for The Grant Desk.

Run manually:
    python3 smalltools/grants/generate_feed.py

Also wired into .github/workflows/jekyll.yml so both files are
regenerated on every Pages deploy. No external dependencies,
only stdlib.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
PAGE_URL = "https://artificialnouveau.github.io/smalltools/grants/"
FEED_URL = PAGE_URL + "feed.xml"
CAL_URL = PAGE_URL + "calendar.ics"
TITLE = "The Grant Desk"
DESCRIPTION = (
    "Paid open calls, fellowships and residencies in tech, art and research, "
    "sorted into the right pile. Updated as new calls land on the desk."
)
MAX_ITEMS = 50


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def rfc822(d: date | datetime) -> str:
    if isinstance(d, datetime):
        dt = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    else:
        dt = datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def deadline_label(deadline: date | None, today: date) -> str:
    if not deadline:
        return "Rolling / undated"
    days = (deadline - today).days
    formatted = deadline.strftime("%d %b %Y")
    if days < 0:
        return f"Closed {formatted}"
    if days == 0:
        return f"Due today ({formatted})"
    if days == 1:
        return f"1 day left, {formatted}"
    return f"{formatted} ({days} days left)"


def build_item(grant: dict, today: date) -> str:
    title = grant.get("title", "Untitled")
    link = grant.get("url") or PAGE_URL
    guid = grant.get("id") or link
    added = parse_date(grant.get("addedDate"))
    pub = rfc822(added) if added else rfc822(datetime.now(timezone.utc))

    deadline = parse_date(grant.get("deadline"))
    label = deadline_label(deadline, today)
    title_full = f"{title} - deadline {label}"

    body = []
    org = grant.get("organization")
    if org:
        body.append(f"<p><strong>{escape(str(org))}</strong></p>")
    location = grant.get("location")
    if location:
        body.append(f"<p>Location: {escape(str(location))}</p>")
    amount = grant.get("amount")
    if amount:
        body.append(f"<p>Award: {escape(str(amount))}</p>")
    duration = grant.get("duration")
    if duration:
        body.append(f"<p>Duration: {escape(str(duration))}</p>")
    body.append(f"<p>Deadline: {escape(label)}</p>")
    desc = grant.get("description")
    if desc:
        body.append(f"<p>{escape(str(desc))}</p>")
    body.append(f'<p><a href="{escape(link)}">Open call details</a></p>')
    body_html = "".join(body)

    cats = []
    region = grant.get("region")
    if region:
        cats.append(f"    <category>{escape(str(region))}</category>\n")
    for tag in grant.get("tags", []) or []:
        cats.append(f"    <category>{escape(str(tag))}</category>\n")

    return (
        "  <item>\n"
        f"    <title>{escape(title_full)}</title>\n"
        f"    <link>{escape(link)}</link>\n"
        f'    <guid isPermaLink="false">{escape(str(guid))}</guid>\n'
        f"    <pubDate>{pub}</pubDate>\n"
        + "".join(cats)
        + f"    <description><![CDATA[{body_html}]]></description>\n"
        "  </item>\n"
    )


def sort_key(grant: dict):
    added = parse_date(grant.get("addedDate"))
    return added or date.min


def ics_escape(value: str) -> str:
    if not value:
        return ""
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def fold_line(line: str) -> str:
    """Fold lines longer than 75 octets per RFC 5545."""
    if len(line.encode("utf-8")) <= 75:
        return line
    out = []
    current = ""
    for ch in line:
        candidate = current + ch
        if len(candidate.encode("utf-8")) > 75:
            out.append(current)
            current = " " + ch
        else:
            current = candidate
    out.append(current)
    return "\r\n".join(out)


def build_calendar(grants: list[dict]) -> str:
    today = date.today()
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//The Grant Desk//Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"NAME:{ics_escape(TITLE)}",
        f"X-WR-CALNAME:{ics_escape(TITLE + ' deadlines')}",
        f"X-WR-CALDESC:{ics_escape(DESCRIPTION)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]

    for grant in grants:
        deadline = parse_date(grant.get("deadline"))
        if not deadline:
            continue
        # Keep recently expired (last 60 days) so subscribers see them
        # briefly disappear from the calendar rather than vanishing instantly.
        if (today - deadline).days > 60:
            continue

        end = deadline + timedelta(days=1)
        title = grant.get("title", "Untitled")
        url = grant.get("url") or ""
        guid = grant.get("id") or url or title
        uid = f"{guid}@artificialnouveau.github.io"

        org = grant.get("organization", "")
        location = grant.get("location", "")
        amount = grant.get("amount", "")
        duration = grant.get("duration", "")

        desc_parts = []
        if grant.get("description"):
            desc_parts.append(grant["description"])
        meta_bits = []
        if org:
            meta_bits.append(f"Organisation: {org}")
        if location:
            meta_bits.append(f"Location: {location}")
        if amount:
            meta_bits.append(f"Award: {amount}")
        if duration:
            meta_bits.append(f"Duration: {duration}")
        if meta_bits:
            desc_parts.append("\n".join(meta_bits))
        if url:
            desc_parts.append(f"More: {url}")
        desc = "\n\n".join(desc_parts)

        event = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{deadline.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
            f"SUMMARY:{ics_escape('Deadline: ' + title)}",
            f"DESCRIPTION:{ics_escape(desc)}",
        ]
        if url:
            event.append(f"URL:{url}")
        if location:
            event.append(f"LOCATION:{ics_escape(location)}")
        event.append("END:VEVENT")
        lines.extend(event)

    lines.append("END:VCALENDAR")
    return "\r\n".join(fold_line(line) for line in lines) + "\r\n"


def main() -> int:
    src = HERE / "grants.json"
    feed_dst = HERE / "feed.xml"
    cal_dst = HERE / "calendar.ics"
    data = json.loads(src.read_text(encoding="utf-8"))
    grants = data.get("grants", []) or []

    today = date.today()
    grants_sorted = sorted(grants, key=sort_key, reverse=True)[:MAX_ITEMS]

    build_date = rfc822(datetime.now(timezone.utc))
    items = "".join(build_item(g, today) for g in grants_sorted)

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "<channel>\n"
        f"  <title>{escape(TITLE)}</title>\n"
        f"  <link>{escape(PAGE_URL)}</link>\n"
        f"  <description>{escape(DESCRIPTION)}</description>\n"
        "  <language>en</language>\n"
        "  <ttl>360</ttl>\n"
        f"  <lastBuildDate>{build_date}</lastBuildDate>\n"
        f'  <atom:link href="{escape(FEED_URL)}" rel="self" type="application/rss+xml"/>\n'
        + items
        + "</channel>\n"
        "</rss>\n"
    )
    feed_dst.write_text(feed, encoding="utf-8")
    print(f"Wrote {feed_dst.relative_to(HERE.parent.parent)} ({len(grants_sorted)} RSS items)")

    cal_dst.write_text(build_calendar(grants), encoding="utf-8")
    cal_event_count = sum(
        1 for g in grants
        if (d := parse_date(g.get("deadline"))) and (today - d).days <= 60
    )
    print(f"Wrote {cal_dst.relative_to(HERE.parent.parent)} ({cal_event_count} calendar events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
