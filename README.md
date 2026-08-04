# artificialnouveau.com

Personal site and portfolio of Ahnjili ZhuParris (artificialnouveau.com), plus
"The Grant Desk", a hand-curated database of paid grants, fellowships and
residencies for artists, researchers and technologists
(/smalltools/grants/).

Jekyll site, hosted on GitHub Pages.

## Updating the site

### Deploying

Push to `master`. That is the whole deploy process. The
`Deploy Jekyll site to Pages` workflow (`.github/workflows/jekyll.yml`) runs on
every push to `master` and publishes the built site. Recent runs take about a
minute. You can also trigger it by hand from the Actions tab.

Check a deploy with:

```bash
gh run list --limit 3 --workflow=jekyll.yml
```

### Running it locally

```bash
bundle install
bundle exec jekyll serve --port 4000
```

Then open http://127.0.0.1:4000/.

Serving the files with anything other than Jekyll (a plain `python3 -m
http.server`, say) will make most pages look broken. Almost every page starts
with YAML frontmatter and uses `layout: default`, so without Jekyll you see the
raw `---` block and no theme.

On Ruby 3.4 and newer, `bigdecimal`, `csv`, `base64` and `logger` are no longer
default gems but Jekyll and Liquid still need them. They are declared in the
`Gemfile` for this reason. If `bundle exec jekyll serve` dies with
`cannot load such file -- bigdecimal`, that is what is missing.

`Gemfile.lock` is gitignored, so your local gem versions do not affect the
deploy.

### Where things live

| What | Where |
|---|---|
| Homepage | `index.html` (standalone HTML with its own inline `<style>`, not a Jekyll layout) |
| Shared `<head>`, including stylesheets | `_includes/head.html` |
| Page templates | `_layouts/` (`default`, `page`, `post`, `blog`, `gallery`) |
| Site-wide CSS | `assets/css/styles.css` (theme base) then `assets/css/custom-theme.css` (the site's own look) |
| Self-hosted fonts | `assets/fonts/` |
| Grant Desk data | `smalltools/grants/grants.json` |
| Blog posts | `_posts/` |

The homepage is the exception worth remembering: it does not go through
`_layouts/`, so a change to the shared layout will not affect it, and a change
to `index.html` will not affect anything else.

Stylesheets load in the order listed in `_includes/head.html`, and later files
win. To restyle the whole site, add a stylesheet after the existing two rather
than editing them. The theme is token-driven, so overriding the `:root`
variables in `custom-theme.css` (`--color-bg`, `--color-text`, `--color-accent`,
`--font-display`, `--font-mono`) retones most pages at once.

### Adding content

Most content pages are hand-edited HTML with frontmatter. To add a page, create
`some-section/index.html` with:

```yaml
---
layout: default
title: Page Title
permalink: /some-section/
---
```

Homepage sections (education, awards, exhibitions, residencies) are `<details>`
accordions inside `index.html`. Each entry is a `div.content-block` with an
`<h3>` holding a `span.year-label`, and an optional `p.location`.

### Keeping drafts out of search results

New drafts, prototypes and internal mockups should be non-indexable from the
moment they are created, not retroactively.

- Jekyll page or post: add `indexing: false` to the frontmatter.
- Standalone HTML file: add `<meta name="robots" content="noindex, nofollow">`.

`robots.txt` is deliberately permissive and should stay that way. Blocking a
page there does not remove it from an index, and it prevents search engines from
ever seeing a `noindex` tag on a page that is already indexed. See `CLAUDE.md`
for the full reasoning and the removal procedure for already-indexed pages.

### The Grant Desk automation

Four scheduled workflows maintain `smalltools/grants/grants.json` and push
directly to `master`. All four can also be run manually from the Actions tab.

| Workflow | Schedule (UTC) | Does |
|---|---|---|
| `grants-bot.yml` | Sundays 09:00 | Finds and adds new opportunities |
| `recheck-grants.yml` | Mondays 08:30 | Re-checks existing entries |
| `publish-grants.yml` | Daily 06:00 | Releases entries to the RSS and calendar feeds |
| `prune-grants.yml` | 1st of the month, 03:00 | Removes expired entries |

Because the bot pushes to `master` on its own schedule, a `git push` can be
rejected as out of date even when you changed nothing related to grants. Fetch
and rebase your own commits on top rather than merging, and never resolve a
conflict by hand-merging generated feed files.

## Copyright

© 2024-2026 Ahnjili ZhuParris. All rights reserved.

The site's original content, including written text, artwork, images, and the
selection, wording and curation of the grant listings, is the original work of
Ahnjili ZhuParris and is not licensed for reuse, republication, redistribution
or scraping without prior written permission (artificialnouveau@gmail.com).
Individual facts (such as a grant deadline or amount) are not owned, but the
descriptions and the compilation as a whole are. See `LICENSE.txt` for the full
content notice and the third-party theme's MIT license.
