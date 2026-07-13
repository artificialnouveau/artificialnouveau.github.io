# The Grant Desk — maintainer's README

This folder contains the data and code for [The Grant Desk](https://www.artificialnouveau.com/smalltools/grants/), a curated database of paid open calls, fellowships, residencies and grants.

Everything is plain HTML, JSON and Python. No build tool, no framework. You can update the site by hand in a text editor.

## What's in here

| File | What it does |
|---|---|
| `grants.json` | The source of truth. Every grant is one object in the `grants` array. Edit this file to add, change or remove a grant. |
| `index.html` | The single-page app. Loads `grants.json` and renders the cards. Also holds the FAQ, the Watch for next round drawer, and the filter UI. |
| `generate_feed.py` | Reads `grants.json` and writes the RSS feeds, ICS calendars, static SEO pages, JSON-LD inside `index.html`, and the root `sitemap.xml`. Run it after any change to `grants.json` or to the static-page region/category lists. |
| `prune_grants.py` | Optional cleanup helper. |
| `feed-*.xml`, `calendar-*.ics` | Generated. Do not edit by hand. |
| `<region>/index.html`, `<category>/index.html`, `<category>-<region>/index.html` | Generated SEO landing pages. Do not edit by hand. |
| `mockups/` | Local-only sketches. Not deployed. |

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
  "addedDate": "2026-05-17",
  "feedDate": null,
  "category": "arts",
  "applicant": "individuals",
  "description": "Long-form description: what the call is, eligibility, support, application process. This is the only field that supports multi-sentence prose.",
  "url": "https://...",
  "tags": ["region-tag", "topic-tag", "type-tag"],
  "fee": false,
  "featured": false
}
```

### Field rules

- **`id`** — Lowercase kebab-case slug, unique. Pick something descriptive (`gasworks-residency-greece-2026`).
- **`title`** — How the card renders. Convention is `Funder: Programme Name (year/round)`.
- **`location`** — Where the work happens, plus any geographic eligibility restriction. Free text.
- **`region`** — Must be exactly one of: `EU`, `US`, `UK`, `NL`, `Switzerland`, `Asia`, `Africa`, `Canada`, `Australia`, `LatAm`, `Remote`, `Worldwide`. Drives the Region filter and the static-page generation. If you need a new region, see "Adding a new region" below. Note: `Switzerland` is its own region; do not file Swiss calls under `EU`.
- **`amount`** — Free text. Include currency, range, what's covered. If there's no artist fee/honorarium and only travel is covered, flag that explicitly (e.g., "NO artist fee, stipend or honorarium. Travel and accommodation covered.").
- **`startDate`** — ISO `YYYY-MM-DD` or `null`.
- **`deadline`** — ISO `YYYY-MM-DD` for fixed deadlines. `null` for rolling/continuous calls (the card lands in "Rolling or Continuous Calls"). Categorisation into Hot / Soon / Long / Rolling / Filed Away is automatic from this field.
- **`addedDate`** — ISO `YYYY-MM-DD`, the true day you added the entry. Drives the website's "NEW since last visit" badge and RSS ordering. Use today's date; do NOT future-date it (that is what `feedDate` is for).
- **`feedDate`** — Optional ISO `YYYY-MM-DD` or `null`. The RSS-release date, used ONLY to throttle the RSS feeds: batch-add grants and stagger their `feedDate`s into the future (e.g. ~3 per day) so each tranche enters the feeds on its date. It is independent of `addedDate`, so throttling the feeds does NOT make grants look perpetually NEW on the website. If omitted or `null`, the feed falls back to `addedDate`. The website, SEO pages and calendars ignore `feedDate` and show every grant immediately. On top of any manual staggering, `generate_feed.py` enforces a hard cap of `FEED_MAX_PER_DAY` (5) feed releases per day for release dates from `FEED_CAP_START` onward: overflow spills to the next free day, soonest deadlines keep their slots first, and a grant is never pushed past its own deadline. The cap is computed in memory on every run (deterministic, anchored to the fixed `FEED_CAP_START` date, never the run date) and does not modify `grants.json`.
- **`category`** — Must be exactly one of: `ai`, `tech`, `research`, `writers`, `film`, `arts`, `cross`. If you need a new category, see "Adding a new category" below.
- **`applicant`** — Must be exactly one of: `individuals`, `organizations`, `both`. Drives the "Who can apply" filter. When the user filters to Individuals, cards tagged `individuals` AND `both` show; same logic for Organizations. So default ambiguous cases to `individuals` (this site is individual-focused) or `both` if a grant is genuinely open to either.
- **`description`** — Long prose. Include eligibility, what's funded, application process, deadline restated, contact email if relevant.
- **`url`** — Funder's primary application page if possible. Avoid aggregator URLs (TransArtists, On The Move) unless the funder doesn't have a public page.
- **`tags`** — Free-text tags for search and the card's tab label. Lowercase, hyphen-separated. The first tag becomes the card's coloured tab label.
- **`fee`** — Boolean. `false` means no application fee charged to the applicant. `true` means there IS an application fee (skip these unless you have a strong reason — the desk's mission excludes pay-to-play submissions).
- **`featured`** — Boolean. Currently unused for visual emphasis; safe to leave `false`.
- **`suggestedBy`** — *Optional.* String like `@handle` or `Jane Doe`. Renders a small "Suggested by ..." credit line on the card. Only set this if the submitter explicitly opted in via the Suggest a grant form.

### Selection criteria

What qualifies for the desk, and what gets rejected, regardless of how prestigious the host is:

- **Relevance bar.** Only opportunities that are genuinely tech or art related. Paid civic/ops fellowships (the FUSE Corps type) do not qualify.
- **No self-funded or pay-to-attend programs.** If the artist pays program, tuition or participation fees, it is out, unless the program is also funded (a stipend or award on top of the fee).
- **Free housing alone is not enough.** Do not add residencies that offer only free lodging and nothing else (no stipend, no board, no production support). Existing free-housing-only entries are grandfathered in and should not be removed. Full hosting (room + board + studio) or housing plus a real professional program does qualify.
- **Festival and prize submission fees are acceptable** but must be flagged with `"fee": true` and stated in the `amount` field.
- **No generic photography award contests** (pay-per-image photo prizes), even if they have an aerial category. Drone/aerial-centric calls are the exception.
- **Audio category** is tech-x-music and experimental/sound-art only, not pure/popular/classical music showcases.
- **Dedupe before adding.** Grep `grants.json` by organization and title first; the bot auto-adds, so duplicates are common. When researching new opportunities, skip organizations already tracked.
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

## Running the feed generator

```bash
cd smalltools/grants
python3 generate_feed.py
```

This regenerates ~270 files:

- One RSS feed per region, per category, per timeline window (`feed-*.xml`).
- One ICS calendar per region and per category combination (`calendar-*.ics`).
- One static SEO page per region, per category, per region+category combination (`<region>/index.html`, `<category>/index.html`, etc.).
- The JSON-LD `<script type="application/ld+json">` block injected into `index.html`.
- The repo-root `sitemap.xml`, `robots.txt` and `llms.txt`.

The generator is idempotent and pure Python stdlib. No dependencies to install.

You can run it as often as you like. The output diff will be empty if `grants.json` hasn't changed.

---

## Committing and pushing

The repo is hosted on GitHub Pages. Pushing to `master` is the deploy.

```bash
git add grants.json index.html
git add *.xml *.ics                 # the regenerated feeds and calendars
git add */index.html                # the regenerated static SEO pages
git add ../../sitemap.xml           # repo-root sitemap
git commit -m "Grant Desk: short summary of the change"
git push
```

Or stage everything tracked in one go:

```bash
git add -u . && git add ../../sitemap.xml
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
