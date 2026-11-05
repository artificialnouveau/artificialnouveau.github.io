# The Grant Desk — maintainer's README

This folder contains the data and code for [The Grant Desk](https://www.artificialnouveau.com/smalltools/grants/), a curated database of paid open calls, fellowships, residencies and grants.

Everything is plain HTML, JSON and Python. No build tool, no framework. You can update the site by hand in a text editor.

## What's in here

| File | What it does |
|---|---|
| `grants.json` | The source of truth. Every grant is one object in the `grants` array. Edit this file to add, change or remove a grant. |
| `add.html` | Browser-only form that builds a valid grant entry (with duplicate check) to paste into `grants.json`. Keep its options in sync with the schema below. |
| `index.html` | The single-page app. Loads `grants.json` and renders the cards. Also holds the FAQ, the Watch for next round drawer, and the filter UI. |
| `generate_feed.py` | Reads `grants.json` and writes the RSS feeds, ICS calendars, static SEO pages, JSON-LD inside `index.html`, `embed.json`, `feeds-manifest.json`, and the root `sitemap.xml`, `robots.txt` and `llms.txt`. Run it after any change to `grants.json` or to the static-page region/category lists. |
| `prune_grants.py` | Optional cleanup helper. Drops entries whose deadline is over a year past. Never touches rolling entries. |
| `check_rolling.py` | Rechecks the rolling/undated entries, which nothing else revisits. Fetches each stored URL and reports dead pages and closed calls. Run by hand; no workflow calls it. |
| `grants_bot.py` | Weekly bot (`.github/workflows/grants-bot.yml`, Sundays). Reads Bluesky hashtags and RSS sources, asks Claude to extract candidates, and opens a draft PR; only its state file `.bot_state.json` is pushed straight to master. The state keeps the newest 1000 processed Bluesky posts and RSS entries, oldest first. A post or entry is only marked processed once Claude has answered, so an API error or a dead key means it is retried the next Sunday instead of being skipped for good. Proposed deadlines are stored as zero-padded `YYYY-MM-DD`. |
| `recheck_grants.py` | Weekly bot (`recheck-grants.yml`). Rechecks closed entries and Watch for next round items for a new cycle and opens a draft PR with proposals. State in `.recheck_state.json`. Proposed deadlines are stored as zero-padded `YYYY-MM-DD`. |
| `generate_og_image.py` | Manual tool: regenerates `og-image.png` with Pillow. |
| `embed.js`, `embed.json` | Embeddable widget for other sites and its data file (generated). |
| `feed-*.xml`, `calendar-*.ics` | Generated. Do not edit by hand. |
| `<region>/index.html`, `<category>/index.html`, `<category>-<region>/index.html`, `<type>[-<region>]/index.html`, `<country>/index.html` | Generated SEO landing pages. Do not edit by hand. |

Scheduled workflows: `publish-grants.yml` (daily, regenerates and commits; its Sunday run records and releases that week's RSS drop), `prune-grants.yml` (monthly, runs `prune_grants.py`), plus the two bots above. All four share one concurrency group so they never push to master at the same time. One GitHub quirk: a group holds one running and one pending run, and a newly queued run cancels the older pending one, so a manual dispatch queued while the bot is still running can cancel a waiting daily publish. Nothing is lost: the next day's publish records any drop that was missed (with its own, later stamp). The deploy (`jekyll.yml`) runs after every successful publish or prune run.

## Workflow at a glance

```
edit grants.json    →    python3 generate_feed.py    →    git commit + push
```

Pushing to `master` triggers GitHub Pages, which is where the site is hosted. There is no separate deploy step.

---

## How to add a new grant

1. Open `grants.json` in your editor.
2. Update the top-level `lastUpdated` field to today's date (ISO format, `YYYY-MM-DD`).
3. Add a new object inside the `grants` array. The simplest way is to copy an existing entry that looks similar and edit the fields. Put new entries near the top of the array — that's the convention.
4. Make sure the JSON is valid. Run `python3 -c "import json; json.load(open('grants.json'))"`. If it errors, you have a stray comma or quote somewhere.
5. Run the feed generator: `python3 generate_feed.py`. This rewrites all the feeds, calendars, static SEO pages and the JSON-LD inside `index.html`.
6. Commit and push. See "Committing and pushing" below.

### Adding a grant from the browser (no local tools, no Claude)

You can add a grant entirely from a browser; nothing needs to run on your
machine, because the daily `publish-grants.yml` workflow runs
`generate_feed.py` on GitHub's servers and commits the regenerated feeds,
calendars and SEO pages for you.

1. Open the form at
   [artificialnouveau.com/smalltools/grants/add.html](https://www.artificialnouveau.com/smalltools/grants/add.html).
   It knows the schema, checks for duplicates against the live `grants.json`,
   leaves `feedDate` null (it no longer affects the weekly feeds), and generates a correctly
   formatted JSON entry. It is noindexed and purely client-side.
2. Copy the generated entry.
3. Open `grants.json` in the browser editor at
   [github.dev](https://github.dev/artificialnouveau/artificialnouveau.github.io/blob/master/smalltools/grants/grants.json)
   (the file is too large for the regular github.com editor; github.dev is
   GitHub's VS Code web editor and handles it; log in with the repo account).
4. Go to the end of the file. Before the final `]`, add a comma after the
   last entry's `}` and paste the new entry. Update `lastUpdated` at the top.
5. Commit from the Source Control sidebar (message `Grant Desk: add ...`).
6. The entry is live on the site as soon as GitHub Pages deploys (about a
   minute). That deploy also regenerates the calendars and static pages.
   The grant reaches the RSS feeds in the next Sunday drop, which the daily
   publish run (06:00 UTC) records; to run it now, open
   [the Publish workflow](https://github.com/artificialnouveau/artificialnouveau.github.io/actions/workflows/publish-grants.yml)
   and press "Run workflow".

The same flow works for edits: change the entry in github.dev, commit, done.
If a push/commit fails because the bot updated the file in the meantime,
reload github.dev and redo the paste on the fresh version; never merge by
hand.

### The grant schema

A complete grant entry looks like this:

```json
{
  "id": "unique-kebab-case-slug",
  "title": "Funder: Programme Name (year or round)",
  "organization": "Funder name as it appears on their site",
  "location": "Where the work happens; any eligibility caveats",
  "region": "EU",
  "amount": "Funding details. Be specific about currency, cap, what's covered.",
  "duration": "How long the project / residency runs",
  "startDate": "2026-09-01",
  "deadline": "2026-08-15",
  "deadlineTime": "17:00",
  "deadlineTz": "Europe/Paris",
  "addedDate": "2026-05-17",
  "feedDate": null,
  "category": "arts",
  "applicant": "individuals",
  "description": "Long-form description: what the call is, eligibility, support, application process. This is the only field that supports multi-sentence prose.",
  "url": "https://...",
  "tags": ["region-tag", "topic-tag", "type-tag"],
  "fee": false,
  "featured": false,
  "eligibility": "open",
  "attendance": "onsite",
  "career": "any",
  "ageCap": null
}
```

### Field rules

- **`id`** — Lowercase kebab-case slug, unique. Pick something descriptive (`gasworks-residency-greece-2026`).
- **`title`** — How the card renders. Convention is `Funder: Programme Name (year/round)`.
- **`location`** — Where the work happens, plus any geographic eligibility restriction. Free text.
- **`region`** — Must be exactly one of: `EU`, `US`, `UK`, `NL`, `Asia`, `Africa`, `Canada`, `Australia`, `LatAm`, `Remote`, `Worldwide`. Drives the Region filter and the static-page generation. If you need a new region, see "Adding a new region" below. Special case: Switzerland is a tag-driven sub-region. Give Swiss calls `region: "EU"` plus a `switzerland` tag; they then appear under BOTH the EU and Switzerland filters, feeds, calendars and SEO pages (see `region_matches` in `generate_feed.py` and `grantRegions` in `index.html`). Never set `region: "Switzerland"` directly. NL-primary grants also count as Europe (`EU`) in every view, feeds included, since 2 November 2026; there is no need to add `EU` to their `regions`. China-HK-Taiwan works the same way under Asia: give such calls `region: "Asia"` plus a `china`, `hong-kong` or `taiwan` tag, and never set `region: "China-HK-Taiwan"` directly (a call hosted elsewhere, like an NL-funded Hong Kong residency, keeps its own region and still surfaces via the tag).
- **`amount`** — Free text. Include currency, range, what's covered. If there's no artist fee/honorarium and only travel is covered, flag that explicitly (e.g., "NO artist fee, stipend or honorarium. Travel and accommodation covered.").
- **`startDate`** — ISO `YYYY-MM-DD` or `null`.
- **`deadline`** — ISO `YYYY-MM-DD` for fixed deadlines. `null` for rolling/continuous calls (the card lands in "Rolling or Continuous Calls"). Categorisation into Hot / Soon / Long / Rolling / Filed Away is automatic from this field.
- **`deadlineTime`** / **`deadlineTz`** — Optional, both or neither. The stated closing time (24-hour `HH:MM`) and its IANA time zone (`Europe/Paris` for CET, `Europe/London` for GMT/UK time, `America/New_York` for ET, `Etc/GMT+12` for Anywhere on Earth). "Midnight" on a date is stored as `23:59` on the last day applications are accepted (a stated "12 Nov 00:00" becomes `2026-11-11` at `23:59`); the generator warns on `00:00`. The time must be strict `HH:MM` (00:00 to 23:59) and must not fall in an hour skipped or repeated by a daylight-saving change; otherwise the generator warns and the event is all-day. Labels use the zone's letter abbreviation for European, American and Australian zones (CET, EST, AEDT) and "<City> time" elsewhere ("Hong Kong time"), identically in the calendars and the site's exports. When set, calendars (and the site's shortlist export and "Add to Google Calendar" link) show a timed event ending at that moment in each subscriber's zone, titled e.g. "Deadline 17:00 CET: ..."; otherwise an all-day event. The weekly drops use it too: a grant closing by the drop Sunday in UTC is not sent. Backfilled for 58 upcoming grants on 4 Nov 2026.
- **`addedDate`** — ISO `YYYY-MM-DD`, the true day you added the entry. Drives the website's "NEW since last visit" badge and RSS ordering. Use today's date; do NOT future-date or back-date it: since 8 Nov 2026 it also picks the weekly RSS drop.
- **`feedDate`**: Leave `null`. Since 4 Nov 2026 it does nothing for new grants. **How the weekly RSS drops work:** each Sunday drop (from 06:00 UTC, released by the first recording run after that, normally the daily publish; the deploy never releases one) carries every grant whose `addedDate` falls in the Sunday-to-Saturday week before it, uncapped, minus any closing by the drop Sunday. The first added-era drop (8 Nov 2026) covers additions from Sunday 1 Nov. Sunday additions (the grants bot runs Sundays 09:00 UTC) wait for the next drop. Released drops are recorded in `feed-drop-ledger.json` (per feed: the grant ids of each released week, plus a never-pruned list of every id ever sent) and replayed from it. Only the daily publish run, the monthly prune run (or a local run) record drops, and both workflows run with `GRANT_DESK_STRICT=1`; the deploy build runs with `GRANT_DESK_READONLY=1`, records nothing, and holds back any drop the committed ledger has not recorded (including every drop of a feed being seeded). Grants-bot and recheck PRs do not regenerate anything: they carry only their `grants.json` edits, and the deploy and daily publish regenerate after the merge. Items within a drop are ordered by deadline, then id, so a recorded drop renders identically on every later run. A drop recorded late (say Monday, after a failed Sunday run) leaves out any grant that had closed by the moment of recording. Each drop's pubDate is the moment the publish run recorded it (stored in the ledger as `stamps`), not a fixed 06:00, so a late cron run never back-dates a drop. Every item in one drop shares that pubDate (for example `Sun, 08 Nov 2026 06:17:00 +0000`), and it is never the grant's deadline; drops before 8 Nov 2026 keep their original stamp of midnight UTC on their Sunday. The channel's `lastBuildDate` is only the time the file was last regenerated. It still precedes the moment the drop goes live by the length of the deploy (a few minutes, or longer if a deploy fails and the next one is later); readers that de-duplicate by guid, as most do, are unaffected. A feed the ledger has never seen is seeded from `addedDate`. Thanks to the ledger, editing a grant's deadline, region, categories or tags, or merging a PR with an older `addedDate`, sends that grant in the next unreleased drop rather than into one that already went out. Never regenerate the ledger from scratch. A local run first fetches origin; if origin has ledger commits your checkout lacks, it runs read-only (records nothing) and tells you to pull, so a stale checkout can never re-send a week. Ids of grants deleted from grants.json are trimmed from the ledger. Corrections to a grant (title, amount, deadline) do show up in its already-published items, since items are rebuilt from grants.json. Feeds exist only for the slices the subscribe picker offers. A type-filtered feed is created once it has something to send (once the ledger knows a slice that has emptied, its entry is a tombstone that still records each released drop as empty, so a grant edited into it later goes into the next drop, not a past one; a slice the ledger has never seen has no entry and is seeded from `addedDate` when it first gets a grant, which is harmless because nobody can be subscribed to a file that does not exist yet), and from then on keeps being written even when it goes quiet (like the calendars), so subscribers never hit a 404; the picker only offers typed feeds that have items. Feed types (Grants, Residencies, Fellowships, Prizes) use `FEED_TYPE_RULES` in `generate_feed.py`, which must match the website's `TYPE_RULES` (all whole-word rules), and the NL-in-Europe rule in `region_matches()` must match `grantRegions()` in `index.html` (NL as primary region or in `regions[]`); the generator warns when either drifts, and strict runs (`GRANT_DESK_STRICT=1`) fail. A calendar with no events carries a bare UTC `VTIMEZONE`, since RFC 5545 requires at least one component. Calendar events are marked free (`TRANSP:TRANSPARENT`), so deadlines never block a subscriber's busy time. History: until 8 Nov 2026 a 5/day drip (`feedDate` staggering plus `FEED_MAX_PER_DAY`) fed a 10-15 item Sunday cap, soonest deadlines first, so grants queued until their deadline forced them out; drops from that era are frozen in the ledger, and the grants still queued at the switch were deliberately never sent.
- **`category`** — Must be exactly one of: `ai`, `tech`, `research`, `writers`, `film`, `arts`, `game`, `design`, `curator`, `audio`, `cross`. (`media-arts`, `ai-tech-research` and `design-games` are feed groupings, not categories.) If you need a new category, see "Adding a new category" below.
- **`categories`**: *Optional* array of extra category slugs from the same list, never repeating `category`. Widens which category chips and feeds surface the entry.
- **`regions`**: *Optional* array of extra regions, never repeating `region`. Puts one grant in several region views; `region` stays the canonical primary.
- **`applicant`** — Must be exactly one of: `individuals`, `organizations`, `both`. Drives the "Who can apply" filter. When the user filters to Individuals, cards tagged `individuals` AND `both` show; same logic for Organizations. So default ambiguous cases to `individuals` (this site is individual-focused) or `both` if a grant is genuinely open to either.
- **`description`** — Long prose. Include eligibility, what's funded, application process, deadline restated, contact email if relevant.
- **`url`** — Funder's primary application page if possible. Avoid aggregator URLs (TransArtists, On The Move) unless the funder doesn't have a public page.
- **`tags`** — Free-text tags for search. Lowercase, hyphen-separated. The card's coloured tab label is NOT taken from tags anymore; it always shows the opportunity type (RESIDENCY, FELLOWSHIP, PRIZE, GRANT, FESTIVAL, JOB, or OPEN CALL), detected by `detectTypes()` in `index.html` from the tags and title. Include a `residency`/`fellowship`/`prize`/`grant` tag where applicable so the type detection and the Type filter classify the entry correctly.
- **`fee`** — Boolean. `false` means no application fee charged to the applicant. `true` means there IS an application fee (skip these unless you have a strong reason — the desk's mission excludes pay-to-play submissions).
- **`featured`** — Boolean. Currently unused for visual emphasis; safe to leave `false`.
- **`suggestedBy`** — *Optional.* String like `@handle` or `Jane Doe`. Renders a small "Suggested by ..." credit line on the card. Only set this if the submitter explicitly opted in via the Suggest a grant form.
- **`eligibility`** — Must be exactly one of: `open`, `residents`, `nationals`, `unknown`. Drives the Eligibility filter. `open` = anyone worldwide may apply; `residents` = restricted by where you live (country, region or city); `nationals` = citizenship/nationality requirement. When the call text does not state it clearly, use `unknown` (there is an Unknown chip).
- **`attendance`** — Must be exactly one of: `remote`, `hybrid`, `onsite`, `unknown`. Drives the Attendance filter. `remote` = can be done from where you live; `onsite` = requires being there (in-person residencies default here).
- **`career`** — Must be exactly one of: `any`, `emerging`, `established`, `unknown`. Drives the Career stage filter. `any` only when the call states all stages are welcome.
- **`ageCap`** — Integer maximum applicant age (e.g. `35` for an under-35 call) or `null`. A minimum age (18+) is NOT a cap. Cards with a cap also match the "Has age cap" chip in the Career stage filter.
- **Duration buckets** are NOT stored; the site derives them from the freetext `duration` field at render time (`detectDurationBuckets` in `index.html`). Write durations with explicit numbers and units ("6 months", "4-week residency", "2 to 6 months") so they bucket correctly; "Per project" and similar file under Unknown / project-based.

### Selection criteria

What qualifies for the desk, and what gets rejected, regardless of how prestigious the host is:

- **Relevance bar.** Only opportunities that are genuinely tech or art related. Paid civic/ops fellowships (the FUSE Corps type) do not qualify.
- **No self-funded or pay-to-attend programs.** If the artist pays program, tuition or participation fees, it is out, unless the program is also funded (a stipend or award on top of the fee).
- **Cash required.** Do not add opportunities without actual cash attached (a stipend, fee, grant or prize). Free housing, expenses-only support, festival passes, exhibition-only showcases and cashless full scholarships do not qualify. The old grandfather clause for free-housing-only entries was retired on 29 September 2026, when the remaining cashless entries were culled.
- **Festival exception to the cash rule.** Festival open calls may be added without a cash amount, but only when they have a firm deadline (no rolling or undated festival calls). Say so in the `amount` field ("NO PUBLISHED CASH, listed under the desk's festival exception").
- **Festival and prize submission fees are acceptable** but must be flagged with `"fee": true` and stated in the `amount` field.
- **No generic photography award contests** (pay-per-image photo prizes), even if they have an aerial category. Drone/aerial-centric calls are the exception.
- **Audio category** is tech-x-music and experimental/sound-art only, not pure/popular/classical music showcases.
- **Dedupe before adding.** Grep `grants.json` by organization and title first; the bots propose entries via PRs, so duplicates are common. When researching new opportunities, skip organizations already tracked.
- **Watch-list entries** (calls not yet open) do NOT go in `grants.json`; they belong in the "Watch for next round" drawer in `index.html` (see the drawer section below). Grants.json is for calls that are open now (fixed deadline or genuinely rolling).

### Conventions worth following

- Spell out currency: `USD 5,000`, `EUR 3,500`, `GBP 20,000`, `CAD 12,000`, `CHF 4,000` rather than just `$` (US visitors will assume USD; everyone else won't).
- Avoid em dashes. Use commas, semicolons, periods or parentheses instead.
- Use plain ASCII for special characters where reasonable (`Boell` not `Böll`, `Marie Sklodowska-Curie` is fine as-is in JSON — UTF-8 is supported and used).
- Avoid emojis in entries.

---

## How to edit or remove a grant

1. Find the entry in `grants.json` by its `id` (use your editor's find).
2. Edit the relevant field, OR delete the whole `{ ... },` block.
3. Update `lastUpdated` at the top of the file.
4. Run `python3 generate_feed.py`.
5. Commit and push.

Closed calls auto-file into the "Filed Away (for 1 year)" drawer when their `deadline` is in the past. You generally don't need to remove them by hand — `prune_grants.py` exists for periodic cleanup if you want it.

---

## How to update the "Watch for next round" drawer

The Watchlist is a small block in `index.html` directly (not in `grants.json`) so that watchlist entries don't inflate the active-grants count.

1. Open `index.html` and search for `id="section-watchlist"`. The drawer is right after the Filed Away section, inside `<main>`.
2. Each entry is one `<li data-watchlist-until="YYYY-MM-DD">` tag. The `data-watchlist-until` date is when the entry auto-removes itself (set it to slightly after the funder's expected next-round deadline).
3. Copy an existing `<li>`, paste it, and edit the URL, name and description.
4. Save. No regen needed — the watchlist is pure HTML.
5. Commit and push.

When all watchlist entries expire, the section auto-hides. The "Open drawer" button lets visitors toggle it.

---

## Checking the rolling entries

Rolling entries (`deadline: null`) are the one blind spot in the pipeline: `prune_grants.py` only drops entries whose deadline is over a year past, and `recheck_grants.py` only revisits entries whose deadline fell 180 to 270 days ago. Both are deadline-driven, so an undated entry is never looked at again after it is added, and a filled job or a discontinued fund can sit on the desk indefinitely.

```bash
cd smalltools/grants
python3 check_rolling.py                # report only, changes nothing
python3 check_rolling.py --json r.json  # same, plus machine-readable output
python3 check_rolling.py --apply        # remove the DEAD ones, asks to confirm
python3 check_rolling.py --apply --auto # no prompt, for CI
```

It fetches every rolling entry's `url` and sorts the results into three piles:

- **DEAD** — the page 404s, or its text matches a closure phrase ("this position has been filled", "applications are now closed"). Only these are removable with `--apply`.
- **CHECK** — needs a human: a 403 (routine on FilmFreeway and other Cloudflare hosts, and not evidence of anything), a connection or TLS failure, a 5xx, or an entry whose every explicit date has already passed. Never auto-removed, because a past date is usually a launch or results date rather than a closure.
- **OK** — reachable, no closure wording.

A markdown report lands at `/tmp/rolling_report.md`, and `dead_count`, `check_count` and `has_dead` are written to `GITHUB_OUTPUT` so a scheduled workflow can open a PR the way `recheck_grants.py` does. Stdlib only, no dependencies. After `--apply`, run `generate_feed.py` and commit, exactly as for `prune_grants.py`.

The closure phrases are deliberately narrow. A bare "closed" matches navigation menus ("Closed calls"), cookie banners and archive links on a large fraction of funder sites, so widening the list trades false negatives for false positives, and a false positive here deletes a live opportunity. Prefer adding a specific phrase you have actually seen over a general one.

---

## Running the feed generator

```bash
cd smalltools/grants
python3 generate_feed.py
```

This regenerates:

- One weekly RSS feed per category x region x type combination the subscribe picker offers (`feed-*-weekly.xml`), plus `feed-drop-ledger.json`.
- One ICS calendar per combination the calendar picker offers (`calendar-*.ics`), the same slices as the RSS feeds. Static pages link the nearest one, the same way they pick their feed.
- One static SEO page per region, per category, per region+category combination, per type (alone and by region) and per country (`<region>/index.html`, `<category>/index.html`, `<type>-<region>/index.html`, `<country>/index.html`, etc.). Each page's RSS link points at the nearest feed the picker offers: a dropped region maps to its container (NL and Switzerland to Europe, China-HK-Taiwan to Asia, Africa/Canada/LatAm/Australia to all regions) and a merged category to its group, so the Arts in Europe page links the Media Arts, Film & Sound in Europe feed. In each grant's JSON-LD, the amount's currency is the first ISO code (EUR, AUD, CHF, ...) or symbol (EUR sign, GBP sign, a bare `$` or `US$`) named in `amount`; `A$`, `NT$` or `HK$` never count as US dollars, and an amount with no recognisable currency is emitted as plain text.
- `feeds-manifest.json` (which typed feeds and calendars exist, for the pickers) and `embed.json`.
- The JSON-LD `<script type="application/ld+json">` block and the overlap note (the asterisks in the RSS picker, counted over grants added in the last 26 weeks) injected into `index.html`.
- The repo-root `sitemap.xml`, `robots.txt` and `llms.txt`.

The generator is pure Python stdlib. No dependencies to install.

You can run it as often as you like. On an unchanged `grants.json` a rerun on the same day only rewrites run timestamps (`lastBuildDate`, `DTSTAMP`, `lastmod`). Across days the output also moves on its own: a Sunday run records that week's drop in the ledger, calendars drop deadlines more than 14 days past, static pages move closed calls out of their listings, and the overlap note's 26-week window slides.

---

## Committing and pushing

The repo is hosted on GitHub Pages. Pushing to `master` is the deploy.

```bash
git add grants.json index.html
git add *.xml *.ics                 # the regenerated feeds and calendars
git add *.json                      # feed-drop-ledger.json, feeds-manifest.json, embed.json
git add */index.html                # the regenerated static SEO pages
git add ../../sitemap.xml ../../robots.txt ../../llms.txt   # repo-root files
git commit -m "Grant Desk: short summary of the change"
git push
```

Or stage everything tracked in one go:

```bash
git add -A . && git add ../../sitemap.xml ../../robots.txt ../../llms.txt
# inspect with `git status` before committing
git commit -m "..."
git push
```

Conventions for commit messages on this folder:
- Start with `Grant Desk: ` so it's easy to scan in `git log`.
- Mention what changed (added grants, retagged, filter UI tweak, FAQ, etc.).
- Don't add `Co-Authored-By` lines.

---

## Adding a new region

If you need a new region (say, "Africa"), update **both** the JavaScript filter wiring AND the Python generator:

1. In `index.html`:
   - Add the key to the `REGION_LABELS` object: `Africa: 'Africa'`.
   - Add to the `SEED_REGIONS` array.
   - Add to the `regionOrder` array.
2. In `generate_feed.py`:
   - Add to the `REGIONS` list (top of file).
   - Add to `REGION_PHRASE` (e.g., `"Africa": "Africa"`).
   - Add to `REGION_TITLE_TAIL` (e.g., `"Africa": "in Africa"`).
3. Tag any existing grants that should now use the new region (edit `grants.json` and change their `region` field).
4. Run `python3 generate_feed.py` to generate the new `africa/` SEO page and per-region feeds/calendars.
5. Commit and push.

### Regions the subscribe picker offers

`REGIONS` is the full set. What the RSS and calendar pickers offer is narrower, and lives in three constants at the top of `generate_feed.py`:

- `FEED_REGIONS_EXCLUDED` drops regions from RSS entirely: NL, Switzerland and China-HK-Taiwan (they sit almost entirely inside EU or Asia), and Africa, Canada, LatAm and Australia (under 2 new calls a week). Since 5 Nov 2026 they have no calendars either (see below).
- `REGION_GROUPS` merges regions that overlap heavily into a single option with a single real feed, the same way `CATEGORY_GROUPS` does for categories. `remote-worldwide` is the one group: Remote and Worldwide shared 29 percent of their calls and read as the same promise, so one tick now gives one URL covering both.
- `PICKER_REGIONS` is what falls out of those two, and is what the RSS picker in `index.html` must mirror. The calendar picker offers the same regions (`CAL_PICKER_REGIONS = PICKER_REGIONS`), so calendars and feeds cover exactly the same slices. A checkbox value there is used verbatim as the filename slug, so `remote-worldwide` in the HTML has to match the `REGION_GROUPS` key exactly.

Group members get no feeds or calendars of their own: since 4 Nov 2026 only picker feeds are built, and since 5 Nov 2026 only picker calendars. The website's region filter and the static SEO pages still carry every region separately: merging is a syndication decision only.

**Retired calendars (5 Nov 2026).** Matching the calendars to the feeds retired 118 calendar files: everything for NL, Africa, Canada, Australia and Latin America, the bare Remote, Worldwide, Switzerland and China-HK-Taiwan calendars, and the single-category calendars (AI, Arts, Film and so on). Until `CAL_RETIRE_UNTIL` (5 Dec 2026) the generator still serves each of them with no events and the name "The Grant Desk deadlines (retired)", so subscribers' copies empty out instead of freezing with old deadlines (Google and Apple keep the last synced events of a URL that starts returning 404). From that date the stale-calendar sweep deletes them, and any calendar that later drops out of generation is deleted straight away.

---

## Adding a new category

1. In `index.html`:
   - Add the key to `CATEGORY_LABELS` (the chip label as the user sees it).
   - Add to `CATEGORY_ORDER` (controls left-to-right order of category chips).
2. In `generate_feed.py`:
   - Add to `CATEGORIES`.
   - Add to `CATEGORY_LABELS`.
   - Add to `CATEGORY_TITLE_PHRASE` (used in static-page titles like "X Grants in the EU").
3. Tag any existing grants that should use the new category.
4. Run `python3 generate_feed.py`.
5. Commit and push.

---

## FAQ and lede

The visible FAQ and the JSON-LD copy live inside `index.html`:

- The accordion FAQ is wrapped in `<section class="faq">`.
- The matching JSON-LD `FAQPage` schema is in the `<script type="application/ld+json">` block right after the FAQ section. If you add or edit a question in the visible FAQ, **update both copies** to keep the page and the search-engine metadata in sync.

The lede paragraph (the intro text under the H1) is in `<p class="lede">` near the top of `<body>`.

---

## Submit-a-grant form

The page in `index.html` links out to a Tally form at `https://tally.so/r/BzLb4K` (top strip "Suggest a grant" link and the bottom Submit Card). The form's success message and any optional credit-handle field are configured in Tally's form builder, not in this repo.

When you receive a submission and decide to add it, paste any "credit handle" the submitter provided into the `suggestedBy` field of the new entry in `grants.json`. That renders a "Suggested by ..." line on the card.

---

## Troubleshooting

**`json.load` errors.** Stray comma, missing quote, or unescaped backslash. Pipe the error line number into your editor or run `python3 -m json.tool grants.json` for a clearer trace.

**A card doesn't appear after editing.** Usually one of:
- Browser cached the old `grants.json` — hard reload (Cmd+Shift+R).
- The `deadline` is in the past, so the card moved into "Filed Away".
- The `region` or `category` value has a typo — must match exactly.

**Filter chip is missing.** A new region or category needs the steps in "Adding a new region" / "Adding a new category" above, not just an entry in `grants.json`.

**JSON-LD doesn't show your latest change.** Run `python3 generate_feed.py` — the generator re-injects the JSON-LD block into `index.html`. The visible page reads `grants.json` directly at runtime, so it updates as soon as you reload, but the injected JSON-LD is only refreshed by the generator.

**A grant has no submission fee but the platform charges one (e.g., Submittable convenience fee).** Set `fee: false` if the funder itself does not charge — convenience fees from a third-party platform aren't the same as a pay-to-play submission. Flag the convenience fee in `description` so applicants know.

**Static SEO pages are stale.** They're written by the generator. Re-run `python3 generate_feed.py`.

---

## Testing locally before pushing

```bash
cd /Users/<you>/Documents/GitHub/artificialnouveau.github.io
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000/smalltools/grants/index.html` in your browser. The page fetches `grants.json` from the same origin, so the local server is enough — no API key, no auth.

For SEO-page checks, open `http://127.0.0.1:8000/smalltools/grants/<region-or-category>/`.
