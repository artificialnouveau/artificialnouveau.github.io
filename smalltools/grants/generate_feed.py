#!/usr/bin/env python3
"""Generate per-region and per-timeline RSS feeds, plus calendar.ics,
from grants.json for The Grant Desk.

Outputs:
- feed.xml                  (all grants)
- feed-{region}.xml         (one per region: eu/us/uk/nl/remote/worldwide,
                             plus the merged remote-worldwide slice)
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
import re
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

# Hard cap on how many grants may enter the RSS feeds on any single day. Manual
# feedDate staggering, bot additions and auto-published tranches all funnel through
# this: overflow spills to the next day with a free slot (soonest deadlines first).
# Releases dated before FEED_CAP_START are grandfathered untouched: the cap must not
# rewrite feed history, and anchoring at a FIXED date (rather than the run day) keeps
# the schedule identical across daily regenerates so deferred grants cannot leak back
# in early. Do not move FEED_CAP_START backwards.
FEED_MAX_PER_DAY = 5
FEED_CAP_START = date(2026, 7, 14)

REGIONS = ["EU", "US", "UK", "NL", "Switzerland", "Asia", "Africa", "Canada", "Australia", "LatAm", "Remote", "Worldwide"]

# Regions the RSS subscribe picker does not offer, because they sit almost
# entirely inside EU (NL 91%, Switzerland 95%) and mostly gave subscribers the
# same grants twice. This is a SYNDICATION decision only: the website's region
# filter, the static SEO pages and the calendars all still carry them in full.
# Their bare feeds stay as compatibility aliases; permutations are not built.
FEED_REGIONS_EXCLUDED = {"NL", "Switzerland"}

# Remote and Worldwide overlapped by 29 percent (12 shared calls) and read as the
# same promise to a subscriber, so the pickers offer them as ONE box backed by one
# real combined slice, exactly like CATEGORY_GROUPS below. Syndication only: the
# website's region filter and the static SEO pages still carry each region on its
# own, and both members keep their bare feed and their own calendars as
# compatibility aliases for anyone who subscribed before the merge.
REGION_GROUPS = {
    "remote-worldwide": ["Remote", "Worldwide"],
}
REGION_LABELS = {"remote-worldwide": "Remote & Worldwide"}
_GROUPED_REGION_MEMBERS = {m for ms in REGION_GROUPS.values() for m in ms}
SYNDICATION_REGIONS = REGIONS + list(REGION_GROUPS)
PICKER_REGIONS = [
    r for r in SYNDICATION_REGIONS
    if r not in FEED_REGIONS_EXCLUDED and r not in _GROUPED_REGION_MEMBERS
]
LEGACY_BARE_REGIONS = [r for r in REGIONS if r not in PICKER_REGIONS]
TIMELINES = ["30d", "90d", "added-30d"]
CATEGORIES = ["ai", "tech", "research", "writers", "film", "arts", "game", "design", "curator", "audio", "cross"]

# Two of the subscribe-picker checkboxes bundle a pair of categories under one
# label. Without a real combined slice, one ticked box produced TWO feed URLs
# (one per member), which is not what "one option, one feed" should mean. These
# groups get their own feeds and calendars so each checkbox maps to exactly one
# file. They are syndication-only: static SEO pages stay on the canonical
# single categories so the group slugs never become indexable duplicate pages.
CATEGORY_GROUPS = {
    "media-arts": ["film", "arts", "audio"],
    "ai-tech-research": ["ai", "tech", "research"],
    # Design and Game Design are too small to stand alone (57 and 14) but pair
    # naturally, and together they clear the bar for their own stream.
    "design-games": ["design", "game"],
}
SYNDICATION_CATEGORIES = CATEGORIES + list(CATEGORY_GROUPS)

# Single categories the picker no longer offers because they were merged into a
# group (or excluded). Their BARE feed is still built as a compatibility alias so
# anyone who subscribed before the merge keeps receiving items, but none of their
# region/type permutations are: nothing can reach those, and they were half the
# feed directory. Populated after PICKER_CATEGORIES is derived, below.

# What the subscribe picker actually offers as tickboxes: the grouped slugs plus
# the singles no group absorbed. Overlap reporting must use THIS list, not
# SYNDICATION_CATEGORIES, or it reports group-vs-member containment that no user
# can ever tick (ai-tech always contains all of ai).
_GROUPED_MEMBERS = {m for ms in CATEGORY_GROUPS.values() for m in ms}
# Categories the picker deliberately does not offer despite being ungrouped.
# Being ungrouped is not the same as being offered; without this the derivation
# below hands every loose single a checkbox automatically.
#   curator      - 73% of curatorial calls already surface under another category.
#   design-games - 40% of it sits inside the media group; too thin to earn a row.
# Group slugs are filtered here too, not just loose singles.
PICKER_EXCLUDED = {"curator", "design-games"}
_ALL_SYNDICATED = CATEGORIES + list(CATEGORY_GROUPS)
PICKER_CATEGORIES = [
    c for c in _ALL_SYNDICATED
    if c not in _GROUPED_MEMBERS and c not in PICKER_EXCLUDED
]
LEGACY_BARE_CATEGORIES = [c for c in _ALL_SYNDICATED if c not in PICKER_CATEGORIES]
CATEGORY_LABELS = {
    "ai": "AI & Safety",
    "tech": "Tech & Infrastructure",
    "research": "Research & Journalism",
    "writers": "Writers",
    "film": "Film & Video",
    "arts": "Visual & Media Arts",
    "game": "Game Design",
    "design": "Design",
    "curator": "Curatorial",
    "audio": "Audio, Sound & Music",
    "cross": "Cross-disciplinary & Social Impact",
    "media-arts": "Media Arts, Film & Sound",
    "ai-tech-research": "AI, Tech & Research",
    "design-games": "Design & Games",
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
    # pubDate and feed ordering use the RSS-release date (the capped schedule from
    # apply_release_schedule, falling back to feedDate then addedDate). This keeps a
    # staggered grant - released today via a future feedDate but added earlier - from
    # sorting to the middle of the feed with an old pubDate, which would stop RSS
    # readers from surfacing it as new.
    release = feed_release(grant)
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
    # Untagged grants (the bot adds these) fall back to a single "other" tag so
    # no item ever ships without a category chip.
    for tag in grant.get("tags") or ["other"]:
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


def feed_filename(region, timeline, category=None, weekly=False, opp_type=None):
    """Fixed slot order: feed [cat-<category>] [region] [type] [timeline] [weekly].

    The order is a contract with the subscribe picker's JS, which assembles the
    same slots client-side. No type slug collides with a region or timeline slug,
    so the flat name stays unambiguous."""
    parts = ["feed"]
    if category:
        parts.append("cat")
        parts.append(category)
    if region:
        parts.append(region.lower())
    if opp_type:
        parts.append(opp_type)
    if timeline:
        parts.append(timeline)
    if weekly:
        parts.append("weekly")
    return "-".join(parts) + ".xml"


def feed_title_desc(region, timeline, category=None, weekly=False, opp_type=None):
    suffix = []
    if opp_type:
        suffix.append(OPPORTUNITY_TYPE_TITLE_PHRASE.get(opp_type, opp_type))
    if category:
        suffix.append(CATEGORY_LABELS.get(category, category))
    if region:
        suffix.append(REGION_LABELS.get(region, region))
    if timeline == "30d":
        suffix.append("next 30 days")
    elif timeline == "90d":
        suffix.append("next 90 days")
    elif timeline == "added-30d":
        suffix.append("added in last 30 days")
    if weekly:
        suffix.append("weekly digest")
    if suffix:
        title = f"{TITLE} - {', '.join(suffix)}"
        desc = f"{DESCRIPTION} Filtered to: {', '.join(suffix)}."
    else:
        title, desc = TITLE, DESCRIPTION
    if weekly:
        desc += (
            " Released weekly: the week's new grants arrive together on Sunday, "
            "one entry per grant plus a short roundup header, instead of "
            "trickling out daily."
        )
    return title, desc


def region_matches(grant, region):
    """True when a grant belongs to a region view. Switzerland is a tag-driven
    sub-region: Swiss grants keep ``region: "EU"`` (so they stay in the EU feeds,
    pages and filter) and additionally populate the Switzerland views via their
    ``switzerland`` tag.

    A grant may also carry an optional ``regions`` list to appear in several
    views at once. The singular ``region`` remains the canonical primary and is
    what the card chip and feed category show; ``regions`` only widens which
    views the grant is surfaced in.

    ``region`` may also be a REGION_GROUPS slug (``remote-worldwide``), which
    matches when the grant belongs to any member. Groups exist for syndication
    only; nothing in grants.json ever carries a group slug.

    A region label can be earned three different ways, and all three are valid:
      1. HOST      - where the funding organisation sits (Stimuleringsfonds: NL)
      2. ELIGIBILITY - where applicants may be based (Stimuleringsfonds: NL too,
         since it requires establishment in the Kingdom of the Netherlands and a
         KvK registration; verified against the scheme pages, July 2026)
      3. CONTAINMENT - the primary sits inside a wider view (NL is in the EU)

    Do NOT award ``Worldwide`` for international ACTIVITY. A call whose funded
    work happens abroad but whose applicants must be local (Creative Australia's
    International Engagement Fund, Canada Council's Arts Across Canada and
    Abroad) is not open worldwide, and tagging it so makes the Worldwide view
    return calls the applicant is ineligible for."""
    members = REGION_GROUPS.get(region)
    if members:
        return any(region_matches(grant, m) for m in members)
    if grant.get("region") == region:
        return True
    if region in (grant.get("regions") or []):
        return True
    return region == "Switzerland" and "switzerland" in (grant.get("tags") or [])


def category_matches(grant, category):
    """True when a grant belongs to a category view. Mirrors ``region_matches``:
    the singular ``category`` is canonical (it drives the feed ``<category>`` and
    the card chip) and an optional ``categories`` list only widens which views
    surface the grant, for calls that genuinely sit in two disciplines."""
    members = CATEGORY_GROUPS.get(category)
    if members:
        return any(category_matches(grant, m) for m in members)
    if grant.get("category") == category:
        return True
    return category in (grant.get("categories") or [])


def filter_grants(grants, region, timeline, today, category=None, opp_type=None):
    out = []
    for g in grants:
        if opp_type and not type_matches(g, opp_type):
            continue
        if category and not category_matches(g, category):
            continue
        if region and not region_matches(g, region):
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


def build_feed(grants, region, timeline, today, category=None, opp_type=None):
    title, desc = feed_title_desc(region, timeline, category, opp_type=opp_type)
    filename = feed_filename(region, timeline, category, opp_type=opp_type)
    feed_url = PAGE_URL + filename

    # Never publish an item that was already expired on its release date (a late
    # addition or mis-staggered feedDate can land on/after the deadline). Items
    # that expired AFTER their release stay: they are feed history, and pulling
    # them would churn readers' archives.
    def open_at_release(g):
        deadline = parse_date(g.get("deadline"))
        release = feed_release(g)
        return deadline is None or release is None or release <= deadline

    grants_sorted = sorted(
        (g for g in grants if open_at_release(g)),
        key=lambda g: feed_release(g) or date.min,
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


# How many past weeks a digest feed carries. 26 keeps roughly six months of
# history in a file that stays small, since each item is a whole week.
MAX_WEEKS = 26


def week_start(d):
    """Monday of the ISO week containing ``d``."""
    return d - timedelta(days=d.weekday())


# Singular/plural nouns for the weekly digest count phrase, keyed by the feed's
# opportunity type. The default covers the untyped feeds.
WEEKLY_NOUNS = {
    None: ("grant", "grants"),
    "grants": ("grant", "grants"),
    "residencies": ("residency", "residencies"),
    "fellowships": ("fellowship", "fellowships"),
    "prizes": ("prize", "prizes"),
    "open-calls": ("open call", "open calls"),
}


# Weeks ending on or after this date are released as a "Sunday drop": one item
# per grant, all published together when the week completes. Earlier weeks keep
# the single digest item so existing subscribers' guids stay stable and readers
# are not flooded with months of new-looking items at the switch.
WEEKLY_DROP_SINCE = date(2026, 9, 6)


def weekly_grant_parts(g, today):
    """(escaped title, escaped UTM href, escaped bare url, detail bits) for one
    grant's line in a weekly feed."""
    gtitle = escape(str(g.get("title", "Untitled")))
    gurl = escape(with_utm(g.get("url")) or PAGE_URL)
    plain_url = escape(g.get("url") or PAGE_URL)
    bits = []
    org = g.get("organization")
    if org:
        bits.append(escape(str(org)))
    bits.append(f"deadline {escape(deadline_label(parse_date(g.get('deadline')), today))}")
    amount = g.get("amount")
    if amount:
        bits.append(escape(str(amount)))
    return gtitle, gurl, plain_url, bits


def weekly_count_phrase(count, category, opp_type):
    """'2 new AI, Tech & Research grants' style phrase naming the feed's slice."""
    singular, plural = WEEKLY_NOUNS.get(opp_type, ("grant", "grants"))
    noun = singular if count == 1 else plural
    return f"{CATEGORY_LABELS.get(category, category)} {noun}" if category else noun


def build_weekly_drop_items(monday, grants_in_week, today, slug, category=None, opp_type=None):
    """One week as a Sunday drop: a short header item plus one item per grant.

    Plain-text renderers such as Slack's RSS app truncate every item at a fixed
    length, so a single digest item only ever shows its first entry or two
    there. Splitting the week into per-grant items keeps the weekly cadence
    (nothing is emitted until the week has ended) while every grant arrives
    complete: title, link, organization, deadline and full amount.
    """
    sunday = monday + timedelta(days=6)
    if sunday > today:
        # The week is still running; hold it back so subscribers get one
        # Sunday batch instead of a daily trickle.
        return ""
    label = monday.strftime("%d %b %Y")
    open_at_stamp = [
        g for g in grants_in_week
        if (lambda d: d is None or d >= sunday)(parse_date(g.get("deadline")))
    ]
    if not open_at_stamp:
        return ""
    count = len(open_at_stamp)
    what = weekly_count_phrase(count, category, opp_type)
    pub = rfc822(sunday)

    # The title carries the whole message (count and week); the description
    # stays empty so renderers show the header as a single line. The item's
    # own <link> still points at the Grant Desk.
    # Same guid scheme as the digest era so a reader that saw a week as a
    # digest never sees its header twice.
    items = [
        "  <item>\n"
        f"    <title>{escape(f'{count} new {what} - week of {label}')}</title>\n"
        f"    <link>{escape(PAGE_URL)}</link>\n"
        f'    <guid isPermaLink="false">{escape(f"{PAGE_URL}{slug}#week-{monday.isoformat()}")}</guid>\n'
        f"    <pubDate>{pub}</pubDate>\n"
        "    <description><![CDATA[]]></description>\n"
        "  </item>\n"
    ]
    for g in sorted(open_at_stamp, key=lambda x: (parse_date(x.get("deadline")) or date.max)):
        # No visible URL line here: unlike the digest era, the grant's link is
        # the item's own <link>, which every renderer (Slack included) puts on
        # the title.
        gtitle, gurl, plain_url, bits = weekly_grant_parts(g, today)
        guid = f"{PAGE_URL}{slug}#week-{monday.isoformat()}-{g.get('id') or g.get('url') or gtitle}"
        body = f"<p>{' &middot; '.join(bits)}</p>"
        items.append(
            "  <item>\n"
            f"    <title>{gtitle}</title>\n"
            f"    <link>{gurl}</link>\n"
            f'    <guid isPermaLink="false">{escape(guid)}</guid>\n'
            f"    <pubDate>{pub}</pubDate>\n"
            f"    <description><![CDATA[{body}]]></description>\n"
            "  </item>\n"
        )
    return "".join(items)


def build_weekly_item(monday, grants_in_week, today, slug, category=None, opp_type=None):
    """One digest <item> covering a single week's releases.

    The per-grant feeds emit one item per grant; at the 5/day release cap that is
    ~35 items a week. This collapses the same content into a single item so a
    subscriber gets one entry (and, via an RSS-to-email bridge, one email) a week
    regardless of how often their reader polls.
    """
    sunday = monday + timedelta(days=6)
    if sunday >= WEEKLY_DROP_SINCE:
        return build_weekly_drop_items(
            monday, grants_in_week, today, slug, category=category, opp_type=opp_type
        )
    label = monday.strftime("%d %b %Y")

    # pubDate must not sit in the future or readers may hide the item: for the
    # current, still-running week stamp it today rather than at Sunday.
    stamp = sunday if sunday <= today else today

    # Skip grants already closed when this digest publishes. Filter against the
    # item's own stamp, not today: past weeks regenerate daily, and a today-based
    # filter would slowly empty archived items as their deadlines pass.
    open_at_stamp = [
        g for g in grants_in_week
        if (lambda d: d is None or d >= stamp)(parse_date(g.get("deadline")))
    ]
    if not open_at_stamp:
        return ""
    count = len(open_at_stamp)
    # Name the slice in the count phrase ("2 new AI, Tech & Research grants")
    # so a digest forwarded out of context still says what it covers.
    what = weekly_count_phrase(count, category, opp_type)
    title = f"{count} new {what} - week of {label}"

    rows = []
    for g in sorted(open_at_stamp, key=lambda x: (parse_date(x.get("deadline")) or date.max)):
        # The bare-URL line under the title serves plain-text renderers that
        # strip anchor tags; the href keeps the UTM tag.
        gtitle, gurl, plain_url, bits = weekly_grant_parts(g, today)
        rows.append(
            f'<li><a href="{gurl}"><strong>{gtitle}</strong></a><br>'
            f'<a href="{gurl}">{plain_url}</a><br>'
            f'{" &middot; ".join(bits)}</li>'
        )

    # The title already says "N new X - week of ...": start straight with the
    # listing so truncating renderers (Slack) spend their budget on grants.
    body = (
        f"<ul>\n" + "\n".join(rows) + "\n</ul>\n"
        f'<p>Full listing with filters: <a href="{escape(PAGE_URL)}">The Grant Desk</a> '
        f"({escape(PAGE_URL)}).</p>"
    )

    # The guid MUST include the feed's own filename. Every weekly feed emits an
    # item per calendar week, so a guid keyed on the week alone would collide
    # across feeds: a reader subscribed to two weekly digests would treat two
    # DIFFERENT roundups as the same item and silently drop one of them.
    guid = f"{PAGE_URL}{slug}#week-{monday.isoformat()}"
    return (
        "  <item>\n"
        f"    <title>{escape(title)}</title>\n"
        f"    <link>{escape(PAGE_URL)}</link>\n"
        f'    <guid isPermaLink="false">{escape(guid)}</guid>\n'
        f"    <pubDate>{rfc822(stamp)}</pubDate>\n"
        f"    <description><![CDATA[{body}]]></description>\n"
        "  </item>\n"
    )


def build_weekly_feed(grants, region, timeline, today, category=None, opp_type=None):
    """Digest twin of build_feed: same grant slice, grouped into one item per week."""
    title, desc = feed_title_desc(region, timeline, category, weekly=True, opp_type=opp_type)
    filename = feed_filename(region, timeline, category=category, weekly=True, opp_type=opp_type)
    feed_url = PAGE_URL + filename

    buckets = {}
    for g in grants:
        release = feed_release(g)
        if not release:
            continue
        buckets.setdefault(week_start(release), []).append(g)

    weeks = sorted(buckets.keys(), reverse=True)[:MAX_WEEKS]
    items = "".join(
        build_weekly_item(w, buckets[w], today, filename, category=category, opp_type=opp_type)
        for w in weeks
    )
    build_date = rfc822(datetime.now(timezone.utc))

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">\n'
        "<channel>\n"
        f"  <title>{escape(title)}</title>\n"
        f"  <link>{escape(PAGE_URL)}</link>\n"
        f"  <description>{escape(desc)}</description>\n"
        "  <language>en</language>\n"
        "  <ttl>1440</ttl>\n"
        "  <sy:updatePeriod>weekly</sy:updatePeriod>\n"
        "  <sy:updateFrequency>1</sy:updateFrequency>\n"
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


def calendar_filename(region, category=None, opp_type=None):
    """Same slot order as feed_filename: calendar [cat-<category>] [region] [type]."""
    parts = ["calendar"]
    if category:
        parts.append("cat")
        parts.append(category)
    if region:
        parts.append(region.lower())
    if opp_type:
        parts.append(opp_type)
    if len(parts) == 1:
        return "calendar.ics"
    return "-".join(parts) + ".ics"


def build_calendar(grants, today, region=None, category=None, opp_type=None):
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix_parts = []
    if opp_type:
        suffix_parts.append(OPPORTUNITY_TYPE_TITLE_PHRASE.get(opp_type, opp_type))
    if category:
        suffix_parts.append(CATEGORY_LABELS.get(category, category))
    if region:
        suffix_parts.append(REGION_LABELS.get(region, region))
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
    if opp_type:
        grants = [g for g in grants if type_matches(g, opp_type)]
    if category:
        grants = [g for g in grants if category_matches(g, category)]
    if region:
        grants = [g for g in grants if region_matches(g, region)]
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
    "Switzerland": "Switzerland",
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
    "Switzerland": "in Switzerland",
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

# --- Opportunity-type axis ---------------------------------------------------
# A third landing-page axis alongside region and category. Discipline ("arts")
# and place ("eu") together still miss how people actually search: "artist
# residencies in europe" and "art fellowships" are much higher-volume queries
# than either axis expresses. Matching is precision-first - an explicit tag, or
# the word in the title. Nothing is inferred from descriptions, because a
# description that merely mentions a residency does not make the entry one.
OPPORTUNITY_TYPES = ["residencies", "fellowships", "prizes", "open-calls"]

# What the subscribe picker offers and what type-sliced feeds are built for.
# Deliberately NOT the same list as OPPORTUNITY_TYPES: "grants" is a feed/picker
# type only, and "open-calls" stays a static SEO page but is dropped from the
# picker, because as a type it mostly restated categories people already filter.
FEED_TYPES = ["grants", "residencies", "fellowships", "prizes"]

# A "grants" type earns its place: 38% of the desk (project subsidies, funds,
# commissions) matched none of the four original types and so was unreachable
# from the type filter entirely. This catches ~70% of that gap; what remains is
# mostly jobs and calls for papers, which genuinely are not any of these types.
OPPORTUNITY_TYPE_TAGS = {
    "grants": {"grant", "grants", "funding", "fund", "project-grant", "bursary",
               "subsidy", "production-grant", "travel-grant", "mobility",
               "commission", "microgrant", "micro-grant"},
    "residencies": {"residency", "residencies", "artist-in-residence"},
    "fellowships": {"fellowship", "fellowships"},
    "prizes": {"prize", "award", "competition"},
    "open-calls": {"open-call", "exhibition", "festival"},
}

OPPORTUNITY_TYPE_TITLE_KEYS = {
    "grants": ["grant", "fund", "bursary", "subsidy", "stipend", "support scheme", "scholarship"],
    "residencies": ["residency", "residencies", "artist in residence", "artist-in-residence"],
    "fellowships": ["fellowship"],
    "prizes": ["prize", "award"],
    "open-calls": ["open call", "submissions"],
}

OPPORTUNITY_TYPE_TITLE_PHRASE = {
    "grants": "Grants",
    "residencies": "Artist Residencies",
    "fellowships": "Fellowships",
    "prizes": "Prizes and Awards",
    "open-calls": "Open Calls",
}

OPPORTUNITY_TYPE_PHRASE = {
    "grants": "grants and funds",
    "residencies": "funded artist residencies",
    "fellowships": "fellowships",
    "prizes": "prizes and awards",
    "open-calls": "open calls",
}

# --- Country axis ------------------------------------------------------------
# Country pages catch the highest-volume long-tail query shape in this space
# ("artist residencies in germany"), which the coarse EU/Asia/Africa regions
# cannot serve. Matched on the `location` field ONLY - that field says where the
# opportunity happens, which is exactly what those searches mean - and gated on
# the parent region (or Worldwide) so that "Athens, Georgia" and "New Mexico"
# cannot land on the Greece and Mexico pages. Keys are matched on word
# boundaries. A country only gets a page once it clears MIN_GRANTS_FOR_COUNTRY
# active entries, so thin pages are never emitted.
COUNTRIES = {
    "germany": ("Germany", "EU", ["germany", "berlin", "munich", "hamburg", "cologne",
                                  "leipzig", "frankfurt", "karlsruhe", "stuttgart", "dresden"]),
    "france": ("France", "EU", ["france", "paris", "marseille", "lyon", "nantes", "bordeaux"]),
    "spain": ("Spain", "EU", ["spain", "madrid", "barcelona", "valencia", "bilbao"]),
    "belgium": ("Belgium", "EU", ["belgium", "brussels", "ghent", "antwerp", "liege"]),
    "italy": ("Italy", "EU", ["italy", "rome", "milan", "venice", "florence", "turin",
                              "bologna", "naples"]),
    "austria": ("Austria", "EU", ["austria", "vienna", "linz", "graz", "salzburg"]),
    "greece": ("Greece", "EU", ["greece", "athens", "thessaloniki"]),
    "norway": ("Norway", "EU", ["norway", "oslo", "bergen", "tromso"]),
    "denmark": ("Denmark", "EU", ["denmark", "copenhagen", "aarhus"]),
    "sweden": ("Sweden", "EU", ["sweden", "stockholm", "malmo", "gothenburg"]),
    "finland": ("Finland", "EU", ["finland", "helsinki", "turku", "tampere"]),
    "poland": ("Poland", "EU", ["poland", "warsaw", "krakow", "poznan", "wroclaw", "lodz"]),
    "portugal": ("Portugal", "EU", ["portugal", "lisbon", "porto"]),
    "ireland": ("Ireland", "EU", ["ireland", "dublin", "cork", "galway"]),
    "japan": ("Japan", "Asia", ["japan", "tokyo", "kyoto", "osaka", "fukuoka", "yokohama"]),
    "india": ("India", "Asia", ["india", "new delhi", "mumbai", "bengaluru", "bangalore",
                                "kolkata", "chennai"]),
    "china": ("China", "Asia", ["china", "beijing", "shanghai", "nanjing", "chengdu",
                                "guangzhou", "hong kong"]),
    "south-korea": ("South Korea", "Asia", ["south korea", "seoul", "gwangju", "busan"]),
    "kenya": ("Kenya", "Africa", ["kenya", "nairobi"]),
    "turkey": ("Turkey", "EU", ["turkey", "turkiye", "istanbul", "ankara"]),
}

_COUNTRY_PATTERNS = {
    slug: re.compile(r"\b(" + "|".join(re.escape(k) for k in keys) + r")\b")
    for slug, (_, _, keys) in COUNTRIES.items()
}


def type_matches(grant, opp_type):
    if not opp_type:
        return True
    tags = {str(t).lower() for t in (grant.get("tags") or [])}
    if tags & OPPORTUNITY_TYPE_TAGS[opp_type]:
        return True
    title = str(grant.get("title") or "").lower()
    return any(k in title for k in OPPORTUNITY_TYPE_TITLE_KEYS[opp_type])


def country_matches(grant, country):
    if not country:
        return True
    _, parent_region, _ = COUNTRIES[country]
    if not (region_matches(grant, parent_region) or region_matches(grant, "Worldwide")):
        return False
    return bool(_COUNTRY_PATTERNS[country].search(str(grant.get("location") or "").lower()))


def static_slug(region=None, category=None, opp_type=None, country=None):
    if country:
        return country
    parts = []
    if opp_type:
        parts.append(opp_type)
    if category:
        parts.append(category)
    if region:
        parts.append(region.lower())
    return "-".join(parts) if parts else ""


def static_page_url(region=None, category=None, opp_type=None, country=None):
    slug = static_slug(region=region, category=category, opp_type=opp_type, country=country)
    if not slug:
        return SITE_ROOT_URL + GRANTS_BASE_PATH
    return f"{SITE_ROOT_URL}{GRANTS_BASE_PATH}{slug}/"


def static_page_title(region=None, category=None, opp_type=None, country=None):
    if country:
        return f"Grants, Fellowships and Residencies in {COUNTRIES[country][0]} | The Grant Desk"
    if opp_type and region:
        return f"Funded {OPPORTUNITY_TYPE_TITLE_PHRASE[opp_type]} {REGION_TITLE_TAIL[region]} | The Grant Desk"
    if opp_type:
        return f"Funded {OPPORTUNITY_TYPE_TITLE_PHRASE[opp_type]}, Open for Applications | The Grant Desk"
    if category and region:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants {REGION_TITLE_TAIL[region]} | The Grant Desk"
    if category:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants, Fellowships and Residencies | The Grant Desk"
    if region:
        return f"Grants, Fellowships and Residencies {REGION_TITLE_TAIL[region]} | The Grant Desk"
    return "AI, Arts & Tech Grants, Fellowships and Residencies | The Grant Desk"


def static_page_h1(region=None, category=None, opp_type=None, country=None):
    if country:
        return f"Grants, Fellowships and Residencies in {COUNTRIES[country][0]}"
    if opp_type and region:
        return f"Funded {OPPORTUNITY_TYPE_TITLE_PHRASE[opp_type]} {REGION_TITLE_TAIL[region]}"
    if opp_type:
        return f"Funded {OPPORTUNITY_TYPE_TITLE_PHRASE[opp_type]}, Open for Applications"
    if category and region:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants {REGION_TITLE_TAIL[region]}"
    if category:
        return f"{CATEGORY_TITLE_PHRASE[category]} Grants, Fellowships and Residencies"
    if region:
        return f"Grants, Fellowships and Residencies {REGION_TITLE_TAIL[region]}"
    return "AI, Arts and Tech Grants, Fellowships and Residencies"


def static_page_intro(grant_count, region=None, category=None, opp_type=None, country=None):
    if country:
        label = COUNTRIES[country][0]
        return (
            f"Currently <strong>{grant_count}</strong> active paid grants, fellowships and residencies "
            f"taking place in {label}, across AI, arts, film, journalism, research, tech and "
            "cross-disciplinary practice. Many are open to applicants of any nationality; check each "
            "entry for residency and citizenship requirements. "
            "Hand-curated and updated weekly. "
            "Browse the list below, or use the interactive desk for filtering and shortlisting."
        )
    if opp_type:
        type_phrase = OPPORTUNITY_TYPE_PHRASE[opp_type]
        where = f" open to applicants in {REGION_PHRASE[region]}" if region else ""
        return (
            f"Currently <strong>{grant_count}</strong> active {type_phrase}{where}, across AI, arts, "
            "film, journalism, research, tech and cross-disciplinary practice. "
            "Hand-curated and updated weekly. Almost every entry is funded; a few notable unpaid open calls "
            "and festival submissions are included as clearly flagged exceptions. "
            "Browse the list below, or use the interactive desk for filtering and shortlisting."
        )
    cat_phrase = CATEGORY_TITLE_PHRASE[category].lower() if category else None
    region_phrase = REGION_PHRASE[region] if region else None
    if cat_phrase and region_phrase:
        scope = f"{cat_phrase} grants, fellowships and residencies open to applicants in {region_phrase}"
    elif cat_phrase:
        scope = f"paid {cat_phrase} grants, fellowships and residencies"
    elif region_phrase:
        scope = f"paid grants, fellowships and residencies open to applicants in {region_phrase}, across AI, arts, film, journalism, research, tech and cross-disciplinary practice"
    else:
        scope = "paid grants, fellowships and residencies in AI, arts, film, journalism, research, tech and cross-disciplinary practice"
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
            "artists, researchers and technologists in AI, arts, film, journalism, "
            "research, tech and cross-disciplinary practice."
        ),
        "publisher": {
            "@type": "Person",
            "name": "Ahnjili ZhuParris",
            "url": SITE_ROOT_URL,
        },
    }
    return jsonld_dumps(payload)


def feed_release(grant):
    """Effective RSS-release date for a grant: the capped schedule computed by
    apply_release_schedule when available, else feedDate, else addedDate."""
    return parse_date(grant.get("_feedRelease") or grant.get("feedDate") or grant.get("addedDate"))


def apply_release_schedule(grants, cap=FEED_MAX_PER_DAY):
    """Enforce a hard cap of ``cap`` feed releases per day, in memory only.

    Each grant's nominal release date is feedDate (falling back to addedDate). When a
    day holds more than ``cap`` nominal releases - manual staggering, bot additions and
    auto-published tranches can all collide on one day - the overflow spills forward to
    the next day with a free slot. The result is stored on the grant as ``_feedRelease``
    (ISO string), which feed_release() prefers; grants.json on disk is never modified.

    Releases nominally dated before FEED_CAP_START keep their date and consume no
    slots: they are feed history, and rescheduling them would cascade the whole backlog
    forward and pull long-published grants back out of the feeds. From FEED_CAP_START
    onward the schedule is a pure function of grants.json (no dependence on today's
    date), so the daily scheduled regenerate recomputes the identical schedule and
    queued grants drip out at most ``cap`` per day. Slot order within a day is
    soonest-deadline-first, then id, so time-critical calls are never the ones
    deferred. A grant is never pushed past its own deadline: rather than miss the feed
    entirely, it releases on its deadline day even if that day is full.

    Returns the number of grants deferred beyond their nominal date."""
    def nominal(g):
        return parse_date(g.get("feedDate") or g.get("addedDate"))

    eligible = [g for g in grants if g.get("feed") is not False and nominal(g)]
    eligible.sort(key=lambda g: (
        nominal(g),
        parse_date(g.get("deadline")) or date.max,
        str(g.get("id") or ""),
    ))

    counts = {}
    deferred = 0
    for g in eligible:
        day = nominal(g)
        if day < FEED_CAP_START:
            g["_feedRelease"] = day.isoformat()
            continue
        deadline = parse_date(g.get("deadline"))
        while counts.get(day, 0) >= cap and not (deadline and day >= deadline):
            day += timedelta(days=1)
        counts[day] = counts.get(day, 0) + 1
        if day != nominal(g):
            deferred += 1
        g["_feedRelease"] = day.isoformat()
    return deferred


def filter_published(grants, today):
    """Drop grants whose RSS release date is in the future. This is the RSS throttle:
    set a staggered future ``feedDate`` on a batch of grants and each tranche only
    enters the RSS FEEDS once its feedDate arrives. apply_release_schedule() additionally
    caps releases at FEED_MAX_PER_DAY per day, spilling overflow to later days.

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
        release = feed_release(g)
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


def related_links_html(current_region, current_category, current_type=None,
                       current_country=None, available=None):
    """Internal cross-links for a static landing page.

    Every href is filtered through `available` - the set of slugs actually being
    written this run - so the grid never links to a slice that fell below its
    density threshold and was skipped. Passing available=None disables the check
    (useful in isolation, not in a real run).
    """
    def link(slug, label):
        if available is not None and slug not in available:
            return None
        return f'<li><a href="/{GRANTS_BASE_PATH}{slug}/">{html_escape(label)}</a></li>'

    items = []

    # Country pages are a leaf: they link up to the parent region and sideways to
    # sibling countries, and skip the category grid entirely.
    if current_country:
        parent = COUNTRIES[current_country][1]
        items.append(link(static_slug(region=parent), f"All of {REGION_PHRASE[parent]}"))
        for slug in sorted(COUNTRIES):
            if slug != current_country:
                items.append(link(slug, f"Grants in {COUNTRIES[slug][0]}"))
        items = [i for i in items if i]
        return "<ul class='related-links'>" + "".join(items) + "</ul>" if items else ""

    # Opportunity-type pages link down into their per-region slices, or back up.
    if current_type:
        if current_region:
            items.append(link(static_slug(opp_type=current_type),
                              f"All {OPPORTUNITY_TYPE_PHRASE[current_type]}"))
        for region in REGIONS:
            if region == current_region:
                continue
            items.append(link(static_slug(region=region, opp_type=current_type),
                              f"{OPPORTUNITY_TYPE_TITLE_PHRASE[current_type]} in {REGION_PHRASE[region]}"))
        items = [i for i in items if i]
        return "<ul class='related-links'>" + "".join(items) + "</ul>" if items else ""

    # Region and category pages surface the opportunity-type axis first, then the
    # existing category/region grid.
    for opp_type in OPPORTUNITY_TYPES:
        label = OPPORTUNITY_TYPE_TITLE_PHRASE[opp_type]
        if current_region:
            items.append(link(static_slug(opp_type=opp_type, region=current_region),
                              f"{label} in {REGION_PHRASE[current_region]}"))
        else:
            items.append(link(static_slug(opp_type=opp_type), label))

    # On a bare region page, list the countries that sit inside it.
    if current_region and not current_category:
        for slug in sorted(COUNTRIES):
            if COUNTRIES[slug][1] == current_region:
                items.append(link(slug, f"Grants in {COUNTRIES[slug][0]}"))

    if not current_category:
        for cat in CATEGORIES:
            items.append(link(static_slug(category=cat), f"{CATEGORY_TITLE_PHRASE[cat]} grants"))
    if not current_region:
        for region in REGIONS:
            items.append(link(static_slug(region=region), f"Grants in {REGION_PHRASE[region]}"))
    if current_category and not current_region:
        for region in REGIONS:
            items.append(link(static_slug(region=region, category=current_category),
                              f"{CATEGORY_TITLE_PHRASE[current_category]} in {REGION_PHRASE[region]}"))
    if current_region and not current_category:
        for cat in CATEGORIES:
            items.append(link(static_slug(region=current_region, category=cat),
                              f"{CATEGORY_TITLE_PHRASE[cat]} in {REGION_PHRASE[current_region]}"))

    items = [i for i in items if i]
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


def build_static_page(grants_for_slice, today, region=None, category=None,
                      opp_type=None, country=None, available=None):
    title = static_page_title(region=region, category=category, opp_type=opp_type, country=country)
    h1 = static_page_h1(region=region, category=category, opp_type=opp_type, country=country)
    page_url = static_page_url(region=region, category=category, opp_type=opp_type, country=country)
    active = filter_active(grants_for_slice, today)
    sorted_grants = sort_by_deadline(active)
    intro = static_page_intro(len(sorted_grants), region=region, category=category,
                              opp_type=opp_type, country=country)
    grant_html = render_grant_list_html(sorted_grants, today)
    related = related_links_html(region, category, current_type=opp_type,
                                 current_country=country, available=available)
    itemlist = itemlist_jsonld(sorted_grants, page_url, h1)
    description = (
        f"{len(sorted_grants)} active paid grants, fellowships and residencies. "
        "Curated weekly. RSS and calendar feeds available."
    )

    # The opportunity-type and country axes have no feeds of their own, so they
    # point at the closest existing one: the parent region's, or the full feed.
    feed_region = region
    if country:
        feed_region = COUNTRIES[country][1]
    feed_category = None if (opp_type or country) else category
    # Only the picker's own slugs get permutations built. A category that was
    # merged into a group (arts, ai) or a region the picker no longer offers
    # (NL, Remote) keeps a BARE alias file and nothing else, so pairing the two
    # here would link a name that is never generated. Drop the narrower axis
    # instead and point at the slice that does exist.
    cal_category = feed_category if feed_category in PICKER_CATEGORIES else None
    if feed_category and (feed_category not in PICKER_CATEGORIES
                          or feed_region not in PICKER_REGIONS):
        feed_category = None
    # SEO pages advertise the weekly digest; per-grant feeds still exist but are
    # no longer offered anywhere on the site.
    feed_url = SITE_ROOT_URL + GRANTS_BASE_PATH + feed_filename(
        feed_region, None, category=feed_category, weekly=True
    )
    cal_url = SITE_ROOT_URL + GRANTS_BASE_PATH + calendar_filename(feed_region, category=cal_category)

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


# Overlap note ---------------------------------------------------------------
# A grant can legitimately sit in several regions (the optional `regions` array),
# several categories (the optional `categories` array), and match several types
# (type matching is tag- and title-driven). So ticking two boxes can surface the
# same grant twice. Rather than hand-maintain a list of "watch out for EU and
# NL", the note is COMPUTED from the live data each build, so it can never drift
# from what the feeds actually contain.
# ONE threshold for both the asterisks on the checkboxes and the explanatory
# note, so the two can never disagree. Running two different bars meant the note
# listed pairs that carried no star, which just read as a bug to anyone looking
# at the panel. A pair qualifies when it covers this much of the smaller side.
OVERLAP_SHARE = 0.25


def heavy_overlap_pairs(grants):
    """Pairs where the smaller filter is largely swallowed by the larger one.

    Returned per axis with the picker's own values (lowercased for regions, which
    the markup writes in lowercase) so the subscribe picker can mark the exact
    checkboxes involved without duplicating any of this logic client-side."""
    import itertools
    axes = [
        ("regions", PICKER_REGIONS, region_matches,
         {r: REGION_LABELS.get(r, r) for r in PICKER_REGIONS}, True),
        ("categories", PICKER_CATEGORIES, category_matches,
         {c: CATEGORY_LABELS.get(c, c) for c in PICKER_CATEGORIES}, False),
        ("types", FEED_TYPES, type_matches,
         {t: OPPORTUNITY_TYPE_TITLE_PHRASE.get(t, t) for t in FEED_TYPES}, False),
    ]
    out = []
    for axis, keys, matcher, labels, lower in axes:
        sets = {k: {g.get("id") for g in grants if matcher(g, k)} for k in keys}
        for a, b in itertools.combinations(keys, 2):
            shared = len(sets[a] & sets[b])
            if not shared:
                continue
            small, big = (a, b) if len(sets[a]) <= len(sets[b]) else (b, a)
            share = shared / len(sets[small])
            if share < OVERLAP_SHARE:
                continue
            out.append({
                "axis": axis,
                "a": small.lower() if lower else small,
                "b": big.lower() if lower else big,
                "aLabel": labels[small],
                "bLabel": labels[big],
                "shared": shared,
                "share": round(share, 3),
            })
    out.sort(key=lambda r: -r["share"])
    return out


def build_overlap_note(grants):
    """Explain the asterisks. Renders exactly the pairs heavy_overlap_pairs()
    marks, so the prose and the checkbox markers are the same list by
    construction. Emits nothing at all when no pair qualifies."""
    rows = heavy_overlap_pairs(grants)
    if not rows:
        return "<!-- BEGIN_OVERLAP_NOTE --><!-- END_OVERLAP_NOTE -->"

    axis_titles = {"regions": "Regions", "categories": "Categories", "types": "Types"}
    blocks = []
    for axis in ("regions", "categories", "types"):
        in_axis = [r for r in rows if r["axis"] == axis]
        if not in_axis:
            continue
        items = "".join(
            f"<li><strong>{escape(r['aLabel'])}</strong> and "
            f"<strong>{escape(r['bLabel'])}</strong> &mdash; {r['shared']} shared</li>"
            for r in in_axis
        )
        blocks.append(
            f'<p class="overlap-axis">{escape(axis_titles[axis])}</p><ul>{items}</ul>'
        )

    # The star data ships INLINE, in the same injected block as the prose. It used
    # to be fetched from feeds-manifest.json, which meant the HTML and the JSON
    # cached independently: a browser could hold fresh markup saying "some filters
    # are marked *" next to a stale manifest that produced no stars at all. Same
    # payload, same response, so they cannot disagree.
    payload = json.dumps(rows, separators=(",", ":"))
    return (
        "<!-- BEGIN_OVERLAP_NOTE -->\n"
        f'<script type="application/json" id="overlap-data">{payload}</script>\n'
        '<details class="overlap-note">\n'
        "<summary>Why some filters are marked *</summary>\n"
        "<p>A single grant can sit in more than one region, category or type, so two "
        "filters can hand you the same call twice. The pairs below overlap enough to "
        "be worth flagging, and every filter involved carries an asterisk above.</p>\n"
        + "\n".join(blocks)
        + "\n</details>\n"
        "<!-- END_OVERLAP_NOTE -->"
    )


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
    overlap_block = build_overlap_note(grants)
    text = re.sub(
        r"<!-- BEGIN_OVERLAP_NOTE -->.*?<!-- END_OVERLAP_NOTE -->",
        lambda m: overlap_block,
        text,
        flags=re.DOTALL,
    )

    index_path.write_text(text, encoding="utf-8")


# Root-level directories that are never their own indexable page: build output,
# asset stores, source trees, and the grants tree (enumerated separately below).
SITEMAP_SKIP_DIRS = {
    "_site",
    "_includes",
    "_layouts",
    "_posts",
    "assets",
    "demo",
    "smalltools",
    "workshops",
    "artnoudrones",
    "voice_mixer",
}

_HEAD_RE = re.compile(r"<head\b.*?</head>", re.S | re.I)
_ROBOTS_NOINDEX_RE = re.compile(r"<meta[^>]+name=[\"']robots[\"'][^>]*noindex", re.I)
_META_REFRESH_RE = re.compile(r"<meta[^>]+http-equiv=[\"']refresh[\"']", re.I)
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def is_indexable_page(path):
    """True if the file at `path` should appear in sitemap.xml.

    Excludes pages that opt out of indexing (a robots noindex meta tag, or Jekyll
    `indexing: false` frontmatter, which _includes/head.html renders as noindex)
    and redirect stubs (meta http-equiv=refresh), which have no content of their
    own and only exist to forward to their target.

    The noindex/refresh checks are scoped to <head> on purpose: some pages carry
    those strings inside inline JavaScript that writes markup for a different
    document, and a whole-file match would wrongly drop them.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    fm = _FRONTMATTER_RE.match(text)
    if fm and re.search(r"^\s*indexing:\s*false\s*$", fm.group(1), re.M | re.I):
        return False

    head_match = _HEAD_RE.search(text)
    head = head_match.group(0) if head_match else text[:4000]
    if _ROBOTS_NOINDEX_RE.search(head) or _META_REFRESH_RE.search(head):
        return False
    return True


def _index_file(directory):
    for name in ("index.html", "index.md"):
        candidate = directory / name
        if candidate.exists():
            return candidate
    return None


def discover_smalltools_pages(repo_root):
    smalltools = repo_root / "smalltools"
    found = []
    if not smalltools.exists():
        return found
    for child in sorted(smalltools.iterdir()):
        if not child.is_dir() or child.name == "grants":
            continue
        index = _index_file(child)
        if index and is_indexable_page(index):
            found.append(f"smalltools/{child.name}/")
    return found


def discover_site_pages(repo_root):
    """Top-level section pages (/gallery/, /press/, /talks/, ...).

    Discovered rather than hardcoded so a new section directory lands in the
    sitemap without anyone remembering to edit this list.
    """
    found = []
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name in SITEMAP_SKIP_DIRS:
            continue
        index = _index_file(child)
        if index and is_indexable_page(index):
            found.append(f"{child.name}/")
    return found


def discover_post_pages(repo_root):
    """Gallery entries built from _posts.

    _config.yml gives posts the permalink /gallery/:title/, where :title is the
    post filename with its leading date stripped.
    """
    posts_dir = repo_root / "_posts"
    found = []
    if not posts_dir.exists():
        return found
    for post in sorted(posts_dir.iterdir()):
        if post.suffix.lower() not in (".md", ".markdown", ".html"):
            continue
        match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", post.stem)
        if not match:
            continue
        if not is_indexable_page(post):
            continue
        found.append(f"gallery/{match.group(1)}/")
    return found


def build_sitemap(static_paths, today, repo_root):
    lastmod = today.isoformat()
    urls = []
    urls.append(SITE_ROOT_URL)
    for path in discover_site_pages(repo_root):
        urls.append(SITE_ROOT_URL + path)
    for path in discover_post_pages(repo_root):
        urls.append(SITE_ROOT_URL + path)
    urls.append(SITE_ROOT_URL + "smalltools/")
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


EMBED_COUNT = 30
EMBED_LICENSE = (
    "Factual fields (title, organization, deadline, region, category, apply URL) are free to reuse "
    "and embed with attribution and a link back to The Grant Desk. Original written descriptions are "
    "not included here and remain all rights reserved. Terms: "
    "https://www.artificialnouveau.com/smalltools/grants/data/"
)


def build_embed_json(grants, today):
    """Data source for embed.js, the drop-in widget other sites can install.

    Regenerated on every run for the same reason the feeds are: a widget sitting on
    somebody else's page is the one surface we cannot fix after the fact, so it must
    never serve a closed call. Only active entries, soonest deadline first, and only
    the factual fields the embed licence covers - descriptions stay out.
    """
    active = sort_by_deadline(filter_active(grants, today))[:EMBED_COUNT]
    payload = {
        "source": TITLE,
        "url": PAGE_URL,
        "generated": today.isoformat(),
        "license": EMBED_LICENSE,
        "attribution": f"Curated by {TITLE} ({PAGE_URL})",
        "count": len(active),
        "grants": [
            {
                "id": g.get("id"),
                "title": g.get("title"),
                "organization": g.get("organization"),
                "region": g.get("region"),
                "category": g.get("category"),
                "deadline": g.get("deadline"),
                "applyUrl": with_utm(g.get("url")) or PAGE_URL,
                "grantDeskUrl": PAGE_URL + "?utm_source=grantdeskembed&utm_medium=referral",
            }
            for g in active
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def build_llms_txt():
    base = SITE_ROOT_URL + GRANTS_BASE_PATH
    return f"""# The Grant Desk

A curated database of paid grants, fellowships and residencies for artists, researchers and technologists working in AI and AI safety, digital and mixed-media arts, film and video, research and journalism, tech and infrastructure, and cross-disciplinary practice.

Maintained by Ahnjili ZhuParris. Updated weekly. Almost every entry is funded; a few notable unpaid open calls and festival submissions are included as clearly flagged exceptions.

## Primary

- [The Grant Desk (interactive)]({base}): Filterable list of all active grants, fellowships and residencies.
- [All grants RSS feed]({base}feed-weekly.xml): Weekly digest RSS feed of all entries, one item per week.
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

## By opportunity type

- [Artist residencies]({base}residencies/)
- [Fellowships]({base}fellowships/)
- [Prizes and awards]({base}prizes/)
- [Open calls]({base}open-calls/)

## By country

Country pages are emitted only where enough active entries exist, so this list changes over time. Check the sitemap for the current set.

- [Germany]({base}germany/) - [France]({base}france/) - [Spain]({base}spain/) - [Belgium]({base}belgium/) - [Italy]({base}italy/) - [Austria]({base}austria/) - [Greece]({base}greece/) - [Norway]({base}norway/) - [Denmark]({base}denmark/) - [Japan]({base}japan/) - [India]({base}india/) - [China]({base}china/)

## Data

- [embed.json]({base}embed.json): The 30 soonest-closing active entries, factual fields only, powering the embeddable widget at {base}embed.js.
- [grants.json]({base}grants.json): Source of truth, machine-readable. Each entry has: id, title, organization, location, region, amount, duration, deadline, addedDate, category, description, url, tags, fee, featured.
"""


def main():
    src = HERE / "grants.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    grants = data.get("grants", []) or []
    today = date.today()

    # RSS throttle: grants with a future release date are held out of the FEEDS
    # only. The website, static SEO pages and calendars below use the full
    # `grants` list and show every grant immediately - throttling applies to
    # RSS subscribers, not the page.
    deferred = apply_release_schedule(grants)
    if deferred:
        print(f"Feed cap: {deferred} grant(s) deferred past their nominal date to keep releases at <= {FEED_MAX_PER_DAY}/day.")
    feed_grants = filter_published(grants, today)
    queued = len(grants) - len(feed_grants)
    if queued:
        print(f"RSS throttle: {queued} grant(s) held out of feeds (future release date); shown on the site immediately.")

    region_options = [None] + PICKER_REGIONS
    timeline_options = [None] + TIMELINES

    written = []
    weekly_written = []
    typed_manifest = []

    def emit(region, timeline, category=None, opp_type=None):
        """Write the per-grant feed and its weekly-digest twin for one slice.

        Type-bearing slices are PRUNED: a combination with no matching grants is
        not written at all, because the full type cross-product is mostly empty
        (5,824 permutations, roughly a third of them populated). The names that
        do get written are recorded in feeds-manifest.json so the subscribe
        picker can avoid offering a combination that would 404. Untyped slices
        are always written, empty or not, so the picker's default paths and any
        existing subscriptions can never break.
        """
        filtered = filter_grants(feed_grants, region, timeline, today,
                                 category=category, opp_type=opp_type)
        if opp_type and not filtered:
            return
        name = feed_filename(region, timeline, category=category, opp_type=opp_type)
        (HERE / name).write_text(
            build_feed(filtered, region, timeline, today, category=category, opp_type=opp_type),
            encoding="utf-8",
        )
        written.append((name, len(filtered)))

        wname = feed_filename(region, timeline, category=category, weekly=True, opp_type=opp_type)
        (HERE / wname).write_text(
            build_weekly_feed(filtered, region, timeline, today, category=category, opp_type=opp_type),
            encoding="utf-8",
        )
        weekly_written.append(wname)
        if opp_type:
            typed_manifest.append(name)

    type_options = [None] + FEED_TYPES

    # Category x Region x Type cross-product, over the categories the PICKER can
    # actually offer. TIMELINE IS DELIBERATELY NOT PART OF THIS CROSS: it
    # multiplied every slice by four for the least benefit, and "closing in the
    # next 30 days" is a question the website answers better than a feed reader
    # can. Timeline survives below as a standalone filter.
    for opp_type in type_options:
        for category in [None] + PICKER_CATEGORIES:
            for region in region_options:
                emit(region, None, category=category, opp_type=opp_type)

    # Compatibility aliases: bare feeds for the pre-merge single categories and
    # for regions the picker no longer offers, with no permutations.
    for category in LEGACY_BARE_CATEGORIES:
        emit(None, None, category=category)
    for region in LEGACY_BARE_REGIONS:
        emit(region, None)

    # Standalone timeline feeds, uncrossed.
    for timeline in TIMELINES:
        emit(None, timeline)

    # Manifest of the pruned, type-bearing feeds. The picker fetches this to grey
    # out combinations that produced no grants. Weekly twins are omitted: a
    # weekly file exists exactly when its per-grant sibling does.
    # Orphan sweep. Narrowing the axes (or pruning an empty type slice) leaves
    # files on disk that nothing generates any more; without this they linger
    # forever, get served as stale feeds and bloat the repo.
    current = {n for n, _ in written} | set(weekly_written)
    orphans = sorted(
        f.name for f in HERE.glob("feed*.xml") if f.name not in current
    )
    for name in orphans:
        (HERE / name).unlink()
    if orphans:
        print(f"Removed {len(orphans)} stale feed file(s) no longer generated.")

    cals_written = []
    typed_cal_manifest = []

    def emit_cal(region, category=None, opp_type=None):
        """Mirrors emit() for feeds: type-bearing calendars are pruned when empty
        and recorded in the manifest so the calendar picker never offers a dead
        link. Untyped calendars are always written."""
        sliced = [g for g in grants if type_matches(g, opp_type)] if opp_type else grants
        if category:
            sliced = [g for g in sliced if category_matches(g, category)]
        if region:
            sliced = [g for g in sliced if region_matches(g, region)]
        # An .ics only carries dated, not-long-expired calls, so judge emptiness
        # on that same basis rather than on the raw slice.
        if opp_type and not any(
            parse_date(g.get("deadline")) and (today - parse_date(g["deadline"])).days <= 60
            for g in sliced
        ):
            return
        name = calendar_filename(region, category=category, opp_type=opp_type)
        (HERE / name).write_text(
            build_calendar(grants, today, region=region, category=category, opp_type=opp_type),
            encoding="utf-8",
        )
        cals_written.append(name)
        if opp_type:
            typed_cal_manifest.append(name)

    # Calendars span every REGION, not PICKER_REGIONS. Dropping NL and
    # Switzerland was a SYNDICATION decision: the calendar picker still offers
    # NL, so narrowing this loop would 404 every NL-plus-category calendar.
    for opp_type in [None] + FEED_TYPES:
        for category in [None] + PICKER_CATEGORIES:
            for region in [None] + REGIONS + list(REGION_GROUPS):
                emit_cal(region, category=category, opp_type=opp_type)

    # Compatibility aliases: bare calendars for categories the picker dropped.
    for category in LEGACY_BARE_CATEGORIES:
        emit_cal(None, category=category)

    # Written here, after BOTH the feed and calendar loops, so the manifest can
    # record the pruned type slices for each. The pickers read it to avoid
    # offering a combination that produced no file.
    (HERE / "feeds-manifest.json").write_text(
        json.dumps({
            "typedFeeds": sorted(typed_manifest),
            "typedCalendars": sorted(typed_cal_manifest),
            "heavyOverlaps": heavy_overlap_pairs(grants),
        }, separators=(",", ":")),
        encoding="utf-8",
    )

    stale_cals = sorted(
        f.name for f in HERE.glob("calendar*.ics") if f.name not in set(cals_written)
    )
    for nm in stale_cals:
        (HERE / nm).unlink()
    if stale_cals:
        print(f"Removed {len(stale_cals)} stale calendar file(s) no longer generated.")

    print(f"Wrote {len(written)} RSS feeds:")
    for name, count in written:
        print(f"  {name}: {count} items")
    print(f"Wrote {len(weekly_written)} weekly-digest RSS feeds (one item per week).")
    print(f"Wrote feeds-manifest.json listing {len(typed_manifest)} type-filtered feeds "
          f"(empty type combinations pruned).")
    print(f"Wrote {len(cals_written)} calendars: {', '.join(cals_written)}")

    # --- Static SEO landing pages ---
    # Four axes: region, category, opportunity type (residencies/fellowships/
    # prizes/open calls) and country. Built in two passes: pass one decides which
    # slices clear their density threshold, pass two renders them. The two passes
    # exist so build_static_page can be handed the full set of slugs and filter
    # its cross-links against it - otherwise the related-links grid would point at
    # slices that were skipped for thinness, and every one of those is a 404.
    MIN_GRANTS_FOR_PAGE = 1  # always emit single-axis pages
    MIN_GRANTS_FOR_CROSS = 3  # avoid thin content
    MIN_GRANTS_FOR_COUNTRY = 5  # countries need more before a page earns its place

    planned = []  # (slug, kwargs, slice_grants)

    def plan(slug, slice_grants, minimum, **kwargs):
        if len(filter_active(slice_grants, today)) < minimum:
            return
        planned.append((slug, kwargs, slice_grants))

    for region in REGIONS:
        plan(static_slug(region=region),
             [g for g in grants if region_matches(g, region)],
             MIN_GRANTS_FOR_PAGE, region=region)

    for category in CATEGORIES:
        plan(static_slug(category=category),
             [g for g in grants if category_matches(g, category)],
             MIN_GRANTS_FOR_PAGE, category=category)

    for category in CATEGORIES:
        for region in REGIONS:
            plan(static_slug(region=region, category=category),
                 [g for g in grants if category_matches(g, category) and region_matches(g, region)],
                 MIN_GRANTS_FOR_CROSS, region=region, category=category)

    for opp_type in OPPORTUNITY_TYPES:
        plan(static_slug(opp_type=opp_type),
             [g for g in grants if type_matches(g, opp_type)],
             MIN_GRANTS_FOR_PAGE, opp_type=opp_type)
        for region in REGIONS:
            plan(static_slug(opp_type=opp_type, region=region),
                 [g for g in grants if type_matches(g, opp_type) and region_matches(g, region)],
                 MIN_GRANTS_FOR_CROSS, opp_type=opp_type, region=region)

    for country in COUNTRIES:
        plan(static_slug(country=country),
             [g for g in grants if country_matches(g, country)],
             MIN_GRANTS_FOR_COUNTRY, country=country)

    available_slugs = {slug for slug, _, _ in planned}
    static_paths_written = []
    for slug, kwargs, slice_grants in planned:
        out_dir = HERE / slug
        out_dir.mkdir(exist_ok=True)
        html = build_static_page(slice_grants, today, available=available_slugs, **kwargs)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        static_paths_written.append(slug)

    print(f"Wrote {len(static_paths_written)} static SEO pages: {', '.join(static_paths_written)}")

    # --- embed.json (data source for the embed.js widget) ---
    embed_path = HERE / "embed.json"
    embed_path.write_text(build_embed_json(grants, today), encoding="utf-8")
    print(f"Wrote embed.json ({embed_path})")

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
