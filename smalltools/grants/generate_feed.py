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
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
PAGE_URL = "https://www.artificialnouveau.com/smalltools/grants/"
TITLE = "The Grant Desk"

# Attribution appended to outbound grant links so funders can see referral traffic came
# from The Grant Desk. Applied to clickable/actionable links only, not to GUIDs or
# JSON-LD structured-data URLs (those stay canonical).
def with_utm(url):
    """Return an http(s) URL tagged with our UTM attribution only. Any pre-existing utm_*
    params on the URL are stripped first so only ours shows. Existing non-utm query params
    and #fragments are preserved. Falsy/non-http values are returned unchanged."""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return url
    parts = urlsplit(url)
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith("utm_")]
    kept.extend([("utm_source", "artificialnouveaugrantdesk"), ("utm_medium", "referral")])
    query = urlencode(kept)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))

DESCRIPTION = (
    "Paid open calls, fellowships and residencies in AI, tech, research, and digital and mixed-media arts, "
    "sorted into the right pile. Updated as new calls land on the desk."
)
MAX_ITEMS = 50

REGIONS = ["EU", "US", "UK", "NL", "Asia", "Africa", "Canada", "Australia", "LatAm", "Remote", "Worldwide"]
TIMELINES = ["30d", "90d", "added-30d"]
CATEGORIES = ["ai", "tech", "research", "writers", "film", "arts", "game", "design", "curator", "audio", "cross"]
CATEGORY_LABELS = {
    "ai": "AI & Safety",
    "tech": "Tech & Infrastructure",
    "research": "Research & Journalism",
    "writers": "Writers",
    "film": "Film & Video",
    "arts": "Visual & Media Arts",
    "game": "Game Design",
    "design": "Design",
    "curator": "Curator",
    "audio": "Audio, Sound & Music",
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
    apply_link = with_utm(grant.get("url")) or PAGE_URL
    # pubDate and feed ordering use the RSS-release date (feedDate, falling back to
    # addedDate). This keeps a staggered grant - released today via a future feedDate
    # but added earlier - from sorting to the middle of the feed with an old pubDate,
    # which would stop RSS readers from surfacing it as new.
    release = parse_date(grant.get("feedDate") or grant.get("addedDate"))
    pub = rfc822(release) if release else rfc822(datetime.now(timezone.utc))

    deadline = parse_date(grant.get("deadline"))
    label = deadline_label(deadline, today)

    # Title stays clean - the grant title only. The amount and deadline
    # appear once in the bullet list below, not duplicated in the title.
    title_full = title

    fields = []
    org = grant.get("organization")
    if org:
        fields.append(f"<p><strong>Organisation:</strong> {escape(str(org))}</p>")
    location = grant.get("location")
    if location:
        fields.append(f"<p><strong>Location:</strong> {escape(str(location))}</p>")
    amount = grant.get("amount")
    if amount:
        fields.append(f"<p><strong>Award:</strong> {escape(str(amount))}</p>")
    duration = grant.get("duration")
    if duration:
        fields.append(f"<p><strong>Duration:</strong> {escape(str(duration))}</p>")
    fields.append(f"<p><strong>Deadline:</strong> {escape(label)}</p>")

    body = ["\n".join(fields)]

    desc = grant.get("description")
    if desc:
        body.append(f"<p>{escape(str(desc))}</p>")
    body.append(f'<p><a href="{escape(apply_link)}">Open call details</a></p>')
    body.append(
        f'<p>Want to see more grants? Visit '
        f'<a href="{escape(PAGE_URL)}">The Grant Desk</a> ({escape(PAGE_URL)}).</p>'
    )
    body_html = "\n".join(body)

    cats = []
    region = grant.get("region")
    if region:
        cats.append(f"    <category>{escape(str(region))}</category>\n")
    for tag in grant.get("tags", []) or []:
        cats.append(f"    <category>{escape(str(tag))}</category>\n")

    return (
        "  <item>\n"
        f"    <title>{escape(title_full)}</title>\n"
        f"    <link>{escape(apply_link)}</link>\n"
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
        key=lambda g: parse_date(g.get("feedDate") or g.get("addedDate")) or date.min,
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
        apply_url = with_utm(url)

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
            desc_parts.append(f"More: {apply_url}")
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
            event.append(f"URL:{apply_url}")
        if location:
            event.append(f"LOCATION:{ics_escape(location)}")
        event.append("END:VEVENT")
        lines.extend(event)

    lines.append("END:VCALENDAR")
    return "\r\n".join(fold_line(line) for line in lines) + "\r\n"


SITE_ROOT_URL = "https://www.artificialnouveau.com/"
GRANTS_BASE_PATH = "smalltools/grants/"

REGION_PHRASE = {
    "EU": "the EU",
    "US": "the US",
    "UK": "the UK",
    "NL": "the Netherlands",
    "Asia": "Asia",
    "Africa": "Africa",
    "Canada": "Canada",
    "Australia": "Australia",
    "LatAm": "Latin America",
    "Remote": "Remote (work-from-anywhere)",
    "Worldwide": "Worldwide",
}

REGION_TITLE_TAIL = {
    "EU": "in the EU",
    "US": "in the US",
    "UK": "in the UK",
    "NL": "in the Netherlands",
    "Asia": "in Asia",
    "Africa": "in Africa",
    "Canada": "in Canada",
    "Australia": "in Australia",
    "LatAm": "in Latin America",
    "Remote": "(Remote)",
    "Worldwide": "(Worldwide)",
}

CATEGORY_TITLE_PHRASE = {
    "ai": "AI and AI Safety",
    "tech": "Tech and Infrastructure",
    "research": "Research and Journalism",
    "writers": "Writing and Translation",
    "film": "Film and Video",
    "arts": "Visual and Media Arts",
    "game": "Game Design",
    "design": "Design",
    "curator": "Curatorial",
    "audio": "Audio, Sound and Music",
    "cross": "Cross-Disciplinary and Social Impact",
}


def static_slug(region=None, category=None):
    parts = []
    if category:
        parts.append(category)
    if region:
        parts.append(region.lower())
    return "-".join(parts) if parts else ""


def static_page_url(region=None, category=None):
    slug = static_slug(region=region, category=category)
    if not slug:
        return SITE_ROOT_URL + GRANTS_BASE_PATH
    return f"{SITE_ROOT_URL}{GRANTS_BASE_PATH}{slug}/"


def static_page_title(region=None, category=None):
    if category and region:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants {REGION_TITLE_TAIL[region]} | The Grant Desk"
    if category:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants, Fellowships and Residencies | The Grant Desk"
    if region:
        return f"Grants, Fellowships and Residencies {REGION_TITLE_TAIL[region]} | The Grant Desk"
    return "AI, Arts & Tech Grants, Fellowships and Residencies | The Grant Desk"


def static_page_h1(region=None, category=None):
    if category and region:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants {REGION_TITLE_TAIL[region]}"
    if category:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants, Fellowships and Residencies"
    if region:
        return f"Grants, Fellowships and Residencies {REGION_TITLE_TAIL[region]}"
    return "AI, Arts and Tech Grants, Fellowships and Residencies"


def static_page_intro(grant_count, region=None, category=None):
    cat_phrase = CATEGORY_TITLE_PHRASE[category].lower() if category else None
    region_phrase = REGION_PHRASE[region] if region else None
    if cat_phrase and region_phrase:
        scope = f"{cat_phrase} grants, fellowships and residencies open to applicants in {region_phrase}"
    elif cat_phrase:
        scope = f"paid {cat_phrase} grants, fellowships and residencies"
    elif region_phrase:
        scope = f"paid grants, fellowships and residencies open to applicants in {region_phrase}, across AI, arts, film, research, tech and cross-disciplinary practice"
    else:
        scope = "paid grants, fellowships and residencies in AI, arts, film, research, tech and cross-disciplinary practice"
    return (
        f"Currently <strong>{grant_count}</strong> active {scope}. "
        "Hand-curated and updated weekly. Almost every entry is funded; a few notable unpaid open calls and festival submissions are included as clearly flagged exceptions. "
        "Browse the list below, or use the interactive desk for filtering and shortlisting."
    )


def amount_value_currency(amount_str):
    if not amount_str:
        return None, None
    s = str(amount_str)
    currency = None
    if "€" in s or "EUR" in s.upper():
        currency = "EUR"
    elif "£" in s or "GBP" in s.upper():
        currency = "GBP"
    elif "$" in s or "USD" in s.upper():
        currency = "USD"
    elif "CAD" in s.upper():
        currency = "CAD"
    return s, currency


def grant_jsonld(grant):
    name = grant.get("title", "Untitled")
    url = grant.get("url") or PAGE_URL
    description = grant.get("description") or ""
    org = grant.get("organization") or ""
    location = grant.get("location") or ""
    amount_text, currency = amount_value_currency(grant.get("amount"))

    item = {
        "@type": "MonetaryGrant",
        "name": name,
        "description": description,
        "url": url,
    }
    if org:
        item["funder"] = {"@type": "Organization", "name": org}
    if amount_text:
        if currency:
            item["amount"] = {
                "@type": "MonetaryAmount",
                "currency": currency,
                "value": amount_text,
            }
        else:
            item["amount"] = amount_text
    additional = []
    deadline = parse_date(grant.get("deadline"))
    if deadline:
        additional.append({
            "@type": "PropertyValue",
            "name": "applicationDeadline",
            "value": deadline.isoformat(),
        })
    if location:
        additional.append({
            "@type": "PropertyValue",
            "name": "location",
            "value": location,
        })
    region = grant.get("region")
    if region:
        additional.append({
            "@type": "PropertyValue",
            "name": "region",
            "value": region,
        })
    if additional:
        item["additionalProperty"] = additional
    return item


def jsonld_dumps(payload):
    """json.dumps for inline <script> embedding: '</' would end the script
    block early if a description ever contained '</script>'."""
    return json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")


def itemlist_jsonld(grants, page_url, page_name):
    items = []
    for idx, g in enumerate(grants, start=1):
        items.append({
            "@type": "ListItem",
            "position": idx,
            "item": grant_jsonld(g),
        })
    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": page_name,
        "url": page_url,
        "numberOfItems": len(grants),
        "itemListElement": items,
    }
    return jsonld_dumps(payload)


def website_jsonld():
    payload = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "The Grant Desk",
        "url": SITE_ROOT_URL + GRANTS_BASE_PATH,
        "description": (
            "A curated database of paid grants, fellowships and residencies for "
            "artists, researchers and technologists in AI, arts, film, research, "
            "tech and cross-disciplinary practice."
        ),
        "publisher": {
            "@type": "Person",
            "name": "Ahnjili ZhuParris",
            "url": SITE_ROOT_URL,
        },
    }
    return jsonld_dumps(payload)


def filter_published(grants, today):
    """Drop grants whose RSS release date is in the future. This is the RSS throttle:
    set a staggered future ``feedDate`` on a batch of grants (e.g. 3 per day) and each
    tranche only enters the RSS FEEDS once its feedDate arrives.

    ``feedDate`` is the RSS-release date ONLY; it is independent of ``addedDate``, which
    is the true upload date that drives the website's "new since last visit" badge. This
    keeps the throttle from making grants look perpetually new on the site. A grant with
    no ``feedDate`` falls back to ``addedDate``; with neither, it is always published.

    The website, static SEO pages and calendars are NOT throttled - they show every grant
    immediately. A daily scheduled regenerate (see .github/workflows/publish-grants.yml)
    re-runs this so queued tranches reach the feeds on schedule even without a manual push."""
    out = []
    for g in grants:
        # Per-grant opt-out: ``"feed": false`` keeps an entry off ALL RSS feeds
        # while leaving it on the website, static SEO pages and calendars.
        if g.get("feed") is False:
            continue
        release = parse_date(g.get("feedDate") or g.get("addedDate"))
        if release and (release - today).days > 0:
            continue
        out.append(g)
    return out


def filter_active(grants, today):
    out = []
    for g in grants:
        d = parse_date(g.get("deadline"))
        if d and (d - today).days < 0:
            continue
        out.append(g)
    return out


def sort_by_deadline(grants):
    return sorted(
        grants,
        key=lambda g: parse_date(g.get("deadline")) or date.max,
    )


def html_escape(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_grant_list_html(grants, today):
    if not grants:
        return "<p><em>No grants currently match this slice. Check back soon.</em></p>"
    parts = ["<ol>"]
    for g in grants:
        title = html_escape(g.get("title", "Untitled"))
        url = html_escape(with_utm(g.get("url")) or PAGE_URL)
        org = html_escape(g.get("organization", ""))
        location = html_escape(g.get("location", ""))
        amount = html_escape(g.get("amount", ""))
        description = html_escape(g.get("description", ""))
        deadline = parse_date(g.get("deadline"))
        deadline_str = deadline_label(deadline, today)
        meta_bits = []
        if org:
            meta_bits.append(org)
        if location:
            meta_bits.append(location)
        meta_bits.append(f"Deadline: {html_escape(deadline_str)}")
        if amount:
            meta_bits.append(f"Award: {amount}")
        meta_line = " &middot; ".join(meta_bits)
        parts.append("<li>")
        parts.append(f'<h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>')
        parts.append(f'<p class="meta-line">{meta_line}</p>')
        if description:
            parts.append(f"<p>{description}</p>")
        parts.append("</li>")
    parts.append("</ol>")
    return "\n".join(parts)


def related_links_html(current_region, current_category):
    items = []
    if not current_category:
        for cat in CATEGORIES:
            label = CATEGORY_TITLE_PHRASE[cat]
            href = f"/{GRANTS_BASE_PATH}{static_slug(category=cat)}/"
            items.append(f'<li><a href="{href}">{html_escape(label)} grants</a></li>')
    if not current_region:
        for region in REGIONS:
            label = REGION_PHRASE[region]
            href = f"/{GRANTS_BASE_PATH}{static_slug(region=region)}/"
            items.append(f'<li><a href="{href}">Grants in {html_escape(label)}</a></li>')
    if current_category and not current_region:
        for region in REGIONS:
            label = REGION_PHRASE[region]
            href = f"/{GRANTS_BASE_PATH}{static_slug(region=region, category=current_category)}/"
            items.append(f'<li><a href="{href}">{html_escape(CATEGORY_TITLE_PHRASE[current_category])} in {html_escape(label)}</a></li>')
    if current_region and not current_category:
        for cat in CATEGORIES:
            label = CATEGORY_TITLE_PHRASE[cat]
            href = f"/{GRANTS_BASE_PATH}{static_slug(region=current_region, category=cat)}/"
            items.append(f'<li><a href="{href}">{html_escape(label)} in {html_escape(REGION_PHRASE[current_region])}</a></li>')
    if not items:
        return ""
    return "<ul class='related-links'>" + "".join(items) + "</ul>"


STATIC_PAGE_CSS = """
body { font-family: 'Space Grotesk', 'Inter', -apple-system, sans-serif; background: #F4ECDC; color: #1F1B16; margin: 0; line-height: 1.55; }
.wrap { max-width: 880px; margin: 0 auto; padding: 32px 24px 80px; }
.top-bar { font-family: 'DM Mono', monospace; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; padding-bottom: 18px; border-bottom: 2px solid #2A241D; margin-bottom: 28px; }
.top-bar a { color: #1F1B16; }
h1 { font-family: 'Space Grotesk', sans-serif; font-size: clamp(28px, 5vw, 44px); font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; margin: 12px 0 18px; }
h2 { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 700; margin: 32px 0 14px; }
.intro { font-size: 16px; color: #4A413A; max-width: 720px; margin-bottom: 24px; }
ol { list-style: none; padding: 0; }
ol li { background: #fff; border: 2px solid #2A241D; border-radius: 6px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 3px 3px 0 #2A241D; }
ol h3 { font-family: 'Space Grotesk', sans-serif; font-size: 17px; font-weight: 600; margin-bottom: 6px; }
ol h3 a { color: #1F1B16; text-decoration: none; border-bottom: 1px solid #1F1B16; }
ol .meta-line { font-family: 'DM Mono', monospace; font-size: 12px; color: #7A6F63; margin-bottom: 8px; }
ol p { font-size: 14px; color: #4A413A; }
.related-links { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.related-links li a { display: inline-block; background: #fff; border: 1.5px solid #2A241D; padding: 6px 12px; border-radius: 999px; font-size: 13px; color: #1F1B16; text-decoration: none; font-family: 'DM Mono', monospace; }
.related-links li a:hover { background: #FFE066; }
.back-link { display: inline-block; background: #FFE066; padding: 8px 14px; border: 2px solid #2A241D; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 13px; text-decoration: none; color: #1F1B16; box-shadow: 2px 2px 0 #2A241D; }
.back-link:hover { transform: translate(-1px, -1px); box-shadow: 3px 3px 0 #2A241D; }
footer { margin-top: 48px; padding-top: 24px; border-top: 1px solid #7A6F63; font-family: 'DM Mono', monospace; font-size: 11px; color: #7A6F63; text-transform: uppercase; letter-spacing: 0.05em; }
"""


def build_static_page(grants_for_slice, today, region=None, category=None):
    title = static_page_title(region=region, category=category)
    h1 = static_page_h1(region=region, category=category)
    page_url = static_page_url(region=region, category=category)
    active = filter_active(grants_for_slice, today)
    sorted_grants = sort_by_deadline(active)
    intro = static_page_intro(len(sorted_grants), region=region, category=category)
    grant_html = render_grant_list_html(sorted_grants, today)
    related = related_links_html(region, category)
    itemlist = itemlist_jsonld(sorted_grants, page_url, h1)
    description = (
        f"{len(sorted_grants)} active paid grants, fellowships and residencies. "
        "Curated weekly. RSS and calendar feeds available."
    )

    feed_url = SITE_ROOT_URL + GRANTS_BASE_PATH + feed_filename(region, None, category=category)
    cal_url = SITE_ROOT_URL + GRANTS_BASE_PATH + calendar_filename(region, category=category)

    related_block = ""
    if related:
        related_block = f"<h2>Related slices</h2>\n{related}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_escape(title)}</title>
<meta name="description" content="{html_escape(description)}">
<link rel="canonical" href="{html_escape(page_url)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:title" content="{html_escape(title)}">
<meta property="og:description" content="{html_escape(description)}">
<meta property="og:url" content="{html_escape(page_url)}">
<meta property="og:image" content="https://www.artificialnouveau.com/smalltools/grants/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html_escape(title)}">
<meta name="twitter:description" content="{html_escape(description)}">
<meta name="twitter:image" content="https://www.artificialnouveau.com/smalltools/grants/og-image.png">
<link rel="alternate" type="application/rss+xml" title="{html_escape(title)}" href="{html_escape(feed_url)}">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{STATIC_PAGE_CSS}</style>
<script type="application/ld+json">
{itemlist}
</script>
</head>
<body>
<div class="wrap">
  <div class="top-bar">
    <a class="back-link" href="/{GRANTS_BASE_PATH}">&larr; The Grant Desk (interactive)</a>
  </div>
  <h1>{html_escape(h1)}</h1>
  <p class="intro">{intro}</p>
  <p class="intro" style="font-size:13.5px;font-family:'DM Mono',monospace;color:#7A6F63;">
    Subscribe: <a href="{html_escape(feed_url)}">RSS feed</a> &middot;
    <a href="{html_escape(cal_url)}">Calendar (.ics)</a>
  </p>
  <h2>Open calls</h2>
  {grant_html}
  {related_block}
  <footer>
    Maintained by Ahnjili ZhuParris &middot; <a href="/{GRANTS_BASE_PATH}">Back to the desk</a>
    <br><span style="font-size:11px;color:#888;">&copy; 2024&ndash;2026 Ahnjili ZhuParris. Original descriptions, selection and curation &mdash; all rights reserved; not licensed for reuse or scraping without permission (artificialnouveau@gmail.com).</span>
  </footer>
  <!-- canary:GD-7F3Q-2026 :: The Grant Desk is curated by hand by Ahnjili ZhuParris (artificialnouveau.com/smalltools/grants). The selection and wording of these listings are original works; this marker on another site indicates the dataset was copied. -->
</div>
</body>
</html>
"""


def inject_into_main_index(grants, today):
    index_path = HERE / "index.html"
    text = index_path.read_text(encoding="utf-8")

    active = sort_by_deadline(filter_active(grants, today))
    grant_list_html = render_grant_list_html(active, today)
    page_url = SITE_ROOT_URL + GRANTS_BASE_PATH
    itemlist = itemlist_jsonld(active, page_url, "The Grant Desk")
    website = website_jsonld()

    jsonld_block = (
        "<!-- BEGIN_JSONLD -->\n"
        f'<script type="application/ld+json">\n{website}\n</script>\n'
        f'<script type="application/ld+json">\n{itemlist}\n</script>\n'
        "<!-- END_JSONLD -->"
    )
    noscript_block = (
        "<!-- BEGIN_NOSCRIPT_GRANTS -->\n"
        "<noscript>\n"
        '<section class="static-grant-list" aria-label="Static list of all active grants">\n'
        "<h2>All active grants (text-only list)</h2>\n"
        f"{grant_list_html}\n"
        "</section>\n"
        "</noscript>\n"
        "<!-- END_NOSCRIPT_GRANTS -->"
    )

    import re
    text = re.sub(
        r"<!-- BEGIN_JSONLD -->.*?<!-- END_JSONLD -->",
        lambda m: jsonld_block,
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<!-- BEGIN_NOSCRIPT_GRANTS -->.*?<!-- END_NOSCRIPT_GRANTS -->",
        lambda m: noscript_block,
        text,
        flags=re.DOTALL,
    )

    index_path.write_text(text, encoding="utf-8")


def discover_smalltools_pages(repo_root):
    smalltools = repo_root / "smalltools"
    found = []
    if not smalltools.exists():
        return found
    for child in sorted(smalltools.iterdir()):
        if child.is_dir() and (child / "index.html").exists():
            found.append(f"smalltools/{child.name}/")
    return found


def build_sitemap(static_paths, today, repo_root):
    lastmod = today.isoformat()
    urls = []
    urls.append(SITE_ROOT_URL)
    for path in discover_smalltools_pages(repo_root):
        urls.append(SITE_ROOT_URL + path)
    urls.append(SITE_ROOT_URL + GRANTS_BASE_PATH)
    for path in static_paths:
        urls.append(SITE_ROOT_URL + GRANTS_BASE_PATH + path + "/")

    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)

    body_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    body_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in deduped:
        body_parts.append(
            f"  <url><loc>{escape(u)}</loc><lastmod>{lastmod}</lastmod></url>"
        )
    body_parts.append("</urlset>\n")
    return "\n".join(body_parts)


def build_robots_txt():
    sitemap_url = SITE_ROOT_URL + "sitemap.xml"
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {sitemap_url}\n"
    )


def build_llms_txt():
    base = SITE_ROOT_URL + GRANTS_BASE_PATH
    return f"""# The Grant Desk

A curated database of paid grants, fellowships and residencies for artists, researchers and technologists working in AI and AI safety, digital and mixed-media arts, film and video, research and journalism, tech and infrastructure, and cross-disciplinary practice.

Maintained by Ahnjili ZhuParris. Updated weekly. Almost every entry is funded; a few notable unpaid open calls and festival submissions are included as clearly flagged exceptions.

## Primary

- [The Grant Desk (interactive)]({base}): Filterable list of all active grants, fellowships and residencies.
- [All grants RSS feed]({base}feed.xml): Full RSS feed of all entries, sorted by date added.
- [All grants calendar (.ics)]({base}calendar.ics): ICS calendar of all upcoming deadlines.

## By category

- [AI and AI safety]({base}ai/)
- [Tech and infrastructure]({base}tech/)
- [Research and journalism]({base}research/)
- [Writing and literature]({base}writers/)
- [Film and video]({base}film/)
- [Visual and media arts]({base}arts/)
- [Games and interactive]({base}game/)
- [Design]({base}design/)
- [Curatorial]({base}curator/)
- [Audio and sound art]({base}audio/)
- [Cross-disciplinary and social impact]({base}cross/)

## By region

- [EU]({base}eu/)
- [UK]({base}uk/)
- [US]({base}us/)
- [Netherlands]({base}nl/)
- [Asia]({base}asia/)
- [Africa]({base}africa/)
- [Canada]({base}canada/)
- [Australia]({base}australia/)
- [Latin America]({base}latam/)
- [Remote (work-from-anywhere)]({base}remote/)
- [Worldwide]({base}worldwide/)

## Data

- [grants.json]({base}grants.json): Source of truth, machine-readable. Each entry has: id, title, organization, location, region, amount, duration, deadline, addedDate, category, description, url, tags, fee, featured.
"""


def main():
    src = HERE / "grants.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    grants = data.get("grants", []) or []
    today = date.today()

    # RSS throttle: grants with a future addedDate are held out of the FEEDS
    # only. The website, static SEO pages and calendars below use the full
    # `grants` list and show every grant immediately - throttling applies to
    # RSS subscribers, not the page.
    feed_grants = filter_published(grants, today)
    queued = len(grants) - len(feed_grants)
    if queued:
        print(f"RSS throttle: {queued} grant(s) held out of feeds (future addedDate); shown on the site immediately.")

    region_options = [None] + REGIONS
    timeline_options = [None] + TIMELINES

    written = []
    # Region x Timeline matrix (existing)
    for region in region_options:
        for timeline in timeline_options:
            filtered = filter_grants(feed_grants, region, timeline, today)
            feed = build_feed(filtered, region, timeline, today)
            name = feed_filename(region, timeline)
            (HERE / name).write_text(feed, encoding="utf-8")
            written.append((name, len(filtered)))

    # Category x Region x Timeline cross-product
    for category in CATEGORIES:
        for region in region_options:
            for timeline in timeline_options:
                filtered = filter_grants(feed_grants, region, timeline, today, category=category)
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

    # --- Static SEO landing pages (per region, per category, and cross-product when dense) ---
    static_paths_written = []
    MIN_GRANTS_FOR_PAGE = 1  # always emit single-axis pages
    MIN_GRANTS_FOR_CROSS = 3  # avoid thin content

    # Single-axis: region only
    for region in REGIONS:
        slice_grants = [g for g in grants if g.get("region") == region]
        active_count = len(filter_active(slice_grants, today))
        if active_count < MIN_GRANTS_FOR_PAGE:
            continue
        slug = static_slug(region=region)
        out_dir = HERE / slug
        out_dir.mkdir(exist_ok=True)
        html = build_static_page(slice_grants, today, region=region)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        static_paths_written.append(slug)

    # Single-axis: category only
    for category in CATEGORIES:
        slice_grants = [g for g in grants if g.get("category") == category]
        active_count = len(filter_active(slice_grants, today))
        if active_count < MIN_GRANTS_FOR_PAGE:
            continue
        slug = static_slug(category=category)
        out_dir = HERE / slug
        out_dir.mkdir(exist_ok=True)
        html = build_static_page(slice_grants, today, category=category)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        static_paths_written.append(slug)

    # Cross-product: category x region (only when dense enough to avoid thin-content pages)
    for category in CATEGORIES:
        for region in REGIONS:
            slice_grants = [
                g for g in grants
                if g.get("category") == category and g.get("region") == region
            ]
            active_count = len(filter_active(slice_grants, today))
            if active_count < MIN_GRANTS_FOR_CROSS:
                continue
            slug = static_slug(region=region, category=category)
            out_dir = HERE / slug
            out_dir.mkdir(exist_ok=True)
            html = build_static_page(slice_grants, today, region=region, category=category)
            (out_dir / "index.html").write_text(html, encoding="utf-8")
            static_paths_written.append(slug)

    print(f"Wrote {len(static_paths_written)} static SEO pages: {', '.join(static_paths_written)}")

    # --- Inject JSON-LD + noscript fallback into main index.html ---
    inject_into_main_index(grants, today)
    print("Injected JSON-LD and noscript fallback into smalltools/grants/index.html")

    # --- Sitemap, robots.txt, llms.txt at site root ---
    repo_root = HERE.parent.parent
    sitemap_xml = build_sitemap(static_paths_written, today, repo_root)
    (repo_root / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (repo_root / "robots.txt").write_text(build_robots_txt(), encoding="utf-8")
    (repo_root / "llms.txt").write_text(build_llms_txt(), encoding="utf-8")
    print(f"Wrote sitemap.xml, robots.txt, llms.txt at repo root ({repo_root})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
