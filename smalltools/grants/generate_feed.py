#!/usr/bin/env python3
"""Generate per-region and per-timeline RSS feeds, plus calendar.ics,
from grants.json for The Grant Desk.

Outputs:
- feed.xml                  (all grants)
- feed-{region}.xml         (one per region: eu/us/uk/nl/remote/worldwide)
- feed-30d.xml              (deadlines in next 30 days)
- feed-90d.xml              (deadlines in next 90 days)
- feed-{region}-{30d|90d}.xml  (cross product)
- calendar.ics              (all grants with a deadline)

Run manually:
    python3 smalltools/grants/generate_feed.py

Wired into .github/workflows/jekyll.yml so feeds regenerate on every
Pages deploy. No external dependencies, only stdlib.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
PAGE_URL = "https://www.artificialnouveau.com/smalltools/grants/"
TITLE = "The Grant Desk"
DESCRIPTION = (
    "Paid open calls, fellowships and residencies in AI, tech, research, and digital and mixed-media arts, "
    "sorted into the right pile. Updated as new calls land on the desk."
)
MAX_ITEMS = 50

REGIONS = ["EU", "US", "UK", "NL", "Remote", "Worldwide"]
TIMELINES = ["30d", "90d", "added-30d"]
CATEGORIES = ["ai", "tech", "research", "film", "arts", "cross"]
CATEGORY_LABELS = {
    "ai": "AI & Safety",
    "tech": "Tech & Infrastructure",
    "research": "Research & Journalism",
    "film": "Film & Video",
    "arts": "Visual & Media Arts",
    "cross": "Cross-disciplinary & Social Impact",
}


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def rfc822(d):
    if isinstance(d, datetime):
        dt = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    else:
        dt = datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def deadline_label(deadline, today):
    if not deadline:
        return "Rolling / undated"
    formatted = deadline.strftime("%d %b %Y")
    if (deadline - today).days < 0:
        return f"Closed {formatted}"
    return formatted


def build_item(grant, today):
    title = grant.get("title", "Untitled")
    link = grant.get("url") or PAGE_URL
    guid = grant.get("id") or link
    added = parse_date(grant.get("addedDate"))
    pub = rfc822(added) if added else rfc822(datetime.now(timezone.utc))

    deadline = parse_date(grant.get("deadline"))
    label = deadline_label(deadline, today)
    amount = grant.get("amount")
    parts = [title]
    if amount:
        parts.append(str(amount))
    if deadline and (deadline - today).days >= 0:
        parts.append(f"deadline {label}")
    else:
        parts.append(label)
    title_full = " - ".join(parts)

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
    body.append(
        f'<p>Want to see more grants? Visit '
        f'<a href="{escape(PAGE_URL)}">The Grant Desk</a> ({escape(PAGE_URL)}).</p>'
    )
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


def feed_filename(region, timeline, category=None):
    parts = ["feed"]
    if category:
        parts.append("cat")
        parts.append(category)
    if region:
        parts.append(region.lower())
    if timeline:
        parts.append(timeline)
    return "-".join(parts) + ".xml"


def feed_title_desc(region, timeline, category=None):
    suffix = []
    if category:
        suffix.append(CATEGORY_LABELS.get(category, category))
    if region:
        suffix.append(region)
    if timeline == "30d":
        suffix.append("next 30 days")
    elif timeline == "90d":
        suffix.append("next 90 days")
    elif timeline == "added-30d":
        suffix.append("added in last 30 days")
    if suffix:
        return (
            f"{TITLE} - {', '.join(suffix)}",
            f"{DESCRIPTION} Filtered to: {', '.join(suffix)}.",
        )
    return TITLE, DESCRIPTION


def filter_grants(grants, region, timeline, today, category=None):
    out = []
    for g in grants:
        if category and g.get("category") != category:
            continue
        if region and g.get("region") != region:
            continue
        if timeline and timeline.startswith("added-"):
            window_days = int(timeline.split("-")[1].rstrip("d"))
            added = parse_date(g.get("addedDate"))
            if not added:
                continue
            age_days = (today - added).days
            if age_days < 0 or age_days > window_days:
                continue
        elif timeline:
            d = parse_date(g.get("deadline"))
            if not d:
                continue
            days = (d - today).days
            if days < 0:
                continue
            if timeline == "30d" and days > 30:
                continue
            if timeline == "90d" and days > 90:
                continue
        out.append(g)
    return out


def build_feed(grants, region, timeline, today, category=None):
    title, desc = feed_title_desc(region, timeline, category)
    filename = feed_filename(region, timeline, category)
    feed_url = PAGE_URL + filename

    grants_sorted = sorted(
        grants,
        key=lambda g: parse_date(g.get("addedDate")) or date.min,
        reverse=True,
    )[:MAX_ITEMS]

    build_date = rfc822(datetime.now(timezone.utc))
    items = "".join(build_item(g, today) for g in grants_sorted)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "<channel>\n"
        f"  <title>{escape(title)}</title>\n"
        f"  <link>{escape(PAGE_URL)}</link>\n"
        f"  <description>{escape(desc)}</description>\n"
        "  <language>en</language>\n"
        "  <ttl>360</ttl>\n"
        f"  <lastBuildDate>{build_date}</lastBuildDate>\n"
        f'  <atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml"/>\n'
        + items
        + "</channel>\n"
        "</rss>\n"
    )


def ics_escape(value):
    if not value:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def fold_line(line):
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


def calendar_filename(region, category=None):
    parts = ["calendar"]
    if category:
        parts.append("cat")
        parts.append(category)
    if region:
        parts.append(region.lower())
    if len(parts) == 1:
        return "calendar.ics"
    return "-".join(parts) + ".ics"


def build_calendar(grants, today, region=None, category=None):
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix_parts = []
    if category:
        suffix_parts.append(CATEGORY_LABELS.get(category, category))
    if region:
        suffix_parts.append(region)
    name_suffix = f" - {', '.join(suffix_parts)}" if suffix_parts else ""
    desc_suffix = f" Filtered to: {', '.join(suffix_parts)}." if suffix_parts else ""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//The Grant Desk//Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"NAME:{ics_escape(TITLE + name_suffix)}",
        f"X-WR-CALNAME:{ics_escape(TITLE + name_suffix + ' deadlines')}",
        f"X-WR-CALDESC:{ics_escape(DESCRIPTION + desc_suffix)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    if category:
        grants = [g for g in grants if g.get("category") == category]
    if region:
        grants = [g for g in grants if g.get("region") == region]
    for grant in grants:
        deadline = parse_date(grant.get("deadline"))
        if not deadline:
            continue
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


def main():
    src = HERE / "grants.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    grants = data.get("grants", []) or []
    today = date.today()

    region_options = [None] + REGIONS
    timeline_options = [None] + TIMELINES

    written = []
    # Region x Timeline matrix (existing)
    for region in region_options:
        for timeline in timeline_options:
            filtered = filter_grants(grants, region, timeline, today)
            feed = build_feed(filtered, region, timeline, today)
            name = feed_filename(region, timeline)
            (HERE / name).write_text(feed, encoding="utf-8")
            written.append((name, len(filtered)))

    # Category x Region x Timeline cross-product
    for category in CATEGORIES:
        for region in region_options:
            for timeline in timeline_options:
                filtered = filter_grants(grants, region, timeline, today, category=category)
                feed = build_feed(filtered, region, timeline, today, category=category)
                name = feed_filename(region, timeline, category=category)
                (HERE / name).write_text(feed, encoding="utf-8")
                written.append((name, len(filtered)))

    cals_written = []
    for region in [None] + REGIONS:
        ics_text = build_calendar(grants, today, region=region)
        name = calendar_filename(region)
        (HERE / name).write_text(ics_text, encoding="utf-8")
        cals_written.append(name)
    for category in CATEGORIES:
        for region in [None] + REGIONS:
            ics_text = build_calendar(grants, today, region=region, category=category)
            name = calendar_filename(region, category=category)
            (HERE / name).write_text(ics_text, encoding="utf-8")
            cals_written.append(name)

    print(f"Wrote {len(written)} RSS feeds:")
    for name, count in written:
        print(f"  {name}: {count} items")
    print(f"Wrote {len(cals_written)} calendars: {', '.join(cals_written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
