---
name: artificialnouveau.com
description: A printed artifact on screen; paper stock, press ink, one spot colour, letterpress depth.
colors:
  paper-stock: "#efe9dc"
  press-ink: "#14100c"
  faded-ink: "#4a4238"
  registration-red: "#c0330f"
  card-stock: "#e7e0d0"
typography:
  display:
    fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif"
    fontSize: "clamp(2.2rem, 6vw, 4rem)"
    fontWeight: 700
    lineHeight: 1.03
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif"
    fontSize: "clamp(1.5rem, 3.6vw, 2.3rem)"
    fontWeight: 700
    lineHeight: 1.03
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif"
    fontSize: "clamp(1.15rem, 2.2vw, 1.4rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.022em"
  body:
    fontFamily: "Young Serif, Georgia, serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, Menlo, monospace"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "0.14em"
rounded:
  card: "14px"
  legacy: "4px"
  chip: "2px"
spacing:
  section: "52px"
  gap: "20px"
  gutter: "118px"
components:
  button-letterpress:
    backgroundColor: "{colors.press-ink}"
    textColor: "{colors.paper-stock}"
    padding: "12px 20px"
    height: "46px"
  button-letterpress-hover:
    backgroundColor: "{colors.registration-red}"
    textColor: "{colors.paper-stock}"
  card-bento:
    backgroundColor: "{colors.paper-stock}"
    textColor: "{colors.faded-ink}"
    rounded: "{rounded.card}"
  tag-nav:
    backgroundColor: "{colors.paper-stock}"
    textColor: "{colors.press-ink}"
    padding: "18px 18px 16px"
  tag-nav-hover:
    backgroundColor: "{colors.press-ink}"
    textColor: "{colors.paper-stock}"
  chip-citation:
    backgroundColor: "transparent"
    textColor: "{colors.faded-ink}"
    rounded: "{rounded.chip}"
    padding: "2px 7px"
---

# Design System: artificialnouveau.com

## Overview

**Creative North Star: "The Print Object"**

The site is a printed artifact. The page is paper stock with a subtle two-layer radial-gradient dot grain, the text is press ink, hierarchy is drawn with ink rules of three weights, and a single spot colour (Registration Red) carries every interactive accent. Interactive elements are letterpress blocks: solid ink with the label knocked out in paper, pressed into the stock rather than floating above it. The codebase itself named this world print-object; even the cursor is a printer's registration mark, drawn in paper-and-ink at rest and closing up in Registration Red over interactive elements.

Density is editorial: full-width uppercase grotesk mastheads, serif prose at a comfortable measure, and mono metadata in gutters and labels. There is no dark mode; the one dark surface is the near-black (#0b0b0b) background behind canvases and video, kept so media output is not washed out by the paper. The system rejects the site's former vaporwave theme outright: no neon glow, no scanlines, no terminal window chrome, no cyan borders.

Every Jekyll page and standalone subsite loads the single stylesheet `assets/css/paper.css`; the homepage `index.html` carries its own inline copy of the token values, and when a token changes it must change in both places.

**Key Characteristics:**
- Paper ground (#efe9dc) with dot-grain texture; ink (#14100c) does all structural work.
- One spot colour (#c0330f) for links, hovers, focus rings, and accents.
- Three-face type system: grotesk display, serif prose, mono chrome.
- Flat by default; depth only as letterpress insets and soft bento-card lift.
- Hierarchy drawn with rules (6px / 2px / 1px), not boxes or colour fields.

## Colors

A warm single-hue paper-and-ink palette with one chromatic voice.

### Primary
- **Registration Red** (#c0330f): the single spot colour. Links, hover states, focus rings (3px outline), list markers, citation-chip hover borders, the inked-in interactive cursor, the caret colour in inputs, and the 2px entry-title underline. It never fills large surfaces; it registers.

### Neutral
- **Paper Stock** (#efe9dc): the page background everywhere, textured with a two-layer radial-gradient dot grain (7px and 11px tiles at ~1.5-1.8% black). Also the knockout label colour on ink blocks and the selection text colour.
- **Press Ink** (#14100c): all primary text, headings, rules of every weight, solid button blocks, the nav shelf's hairline grid, and the selection background. Low-alpha washes of it (3-6%) tint code blocks, hover rows, and image wells.
- **Faded Ink** (#4a4238): secondary voice. All mono metadata (years, SKUs, venues, captions, table headers), excerpt text, and the footer smallprint.
- **Card Stock** (#e7e0d0): image placeholder surfaces behind card thumbnails and profile images.

Media surfaces (canvas, video, tool viewports) sit on near-black (#0b0b0b) so projected output reads true; this is a utility surface, not a palette member.

### Named Rules
**The One Spot Colour Rule.** Registration Red is the only chromatic accent in the system. If a second hue appears anywhere outside photographic content, it is a defect.

## Typography

**Display Font:** Helvetica Neue (with Helvetica, Arial fallback)
**Body Font:** Young Serif (self-hosted woff2/ttf, with Georgia fallback)
**Label/Mono Font:** JetBrains Mono (with ui-monospace, SF Mono, Menlo fallback)

**Character:** A grotesk shouting in uppercase over a calm bookish serif, with a typewriter voice for the machinery around the edges. Display is heavy, tight, and compressed in line; prose is relaxed and readable.

### Hierarchy
- **Display** (700, clamp(2.2rem, 6vw, 4rem), line-height 1.03, letter-spacing -0.025em, uppercase): page h1. The homepage masthead pushes the same voice larger (clamp(2.6rem, 8.5vw, 6rem), line-height 0.9, -0.038em).
- **Headline** (700, clamp(1.5rem, 3.6vw, 2.3rem), uppercase, -0.025em): section h2, always closed with a 6px ink rule below (12px padding-bottom).
- **Title** (700, clamp(1.15rem, 2.2vw, 1.4rem), uppercase): h3 and work-card titles (1.35rem on homepage items). Bento gallery card titles are the one normal-case title (600, 1.05-1.25rem).
- **Body** (400 Young Serif, 1rem, line-height 1.6; project posts run 1.8): all prose, list items, excerpts, blockquotes, table cells. Abstracts cap at a 62em measure.
- **Label** (JetBrains Mono, 11px, letter-spacing 0.14-0.18em, uppercase): short mono labels only, in Faded Ink; years, SKUs, table headers, fold controls. Long meta lines (venues, author lists) keep the mono face and 11px size but run normal case with tight tracking (0.04-0.08em).

### Named Rules
**The Eleven-Pixel Floor Rule.** No functional text sits below 11px. The mono metadata voice bottoms out there; it never shrinks further.

**The Short-Caps Rule.** Uppercase is reserved for display type and short mono labels. Long meta strings (venues, author lists) run normal case; caps at length are unreadable.

## Layout

Centered single column: the homepage wraps at 1180px (24px side padding); interior pages use a stepped container (540 / 720 / 960 / 1140px at 576 / 768 / 992 / 1200px breakpoints, 15px side padding). Sections stack with 52px top padding on the homepage (3rem vertical on interior pages), each opened by a 6px-ruled heading.

Recurring spatial devices, all drawn with ink rules rather than boxes:
- **The nav shelf**: a 4-column grid of SKU-tag cells whose 1px gap is an ink background showing through, bounded by 2px rules top and bottom; collapses to 2 columns under 900px.
- **The 118px gutter**: publications and entry lists run a 118px mono-year gutter beside a 1fr content column (20px gap). The year is sticky (top: 12px) so it rides beside its group as it scrolls; under 640px the gutter collapses and the year returns above its group.
- **The bento gallery**: a 6-column grid (gap 1.25rem, dense flow) of 14px-radius cards spanning 2 (standard), 3 (wide), or 4 (feature) columns; auto lists repeat a 3,3,2,2,2 rhythm. Drops to 4 columns at 1100px and a single column at 768px.
- **The work grid**: homepage cards in an auto-fit grid (400px floor) with shared 1px hairline borders under a 2px top rule.

Rows (publication items, entries) are separated by 1px hairlines; row hover is a 3.5% ink wash with an inset 3px Registration Red left edge.

### Named Rules
**The Ink Rule Rule.** Hierarchy is drawn with rules and weight, not boxes or colour: 6px rules close section headings, 2px heavy rules bound page headers, shelves, and footers, 1px hairlines separate rows and cells.

## Elevation & Depth

Flat by default. The page is one sheet of paper; nothing floats over it. Depth exists in exactly two sanctioned forms: letterpress insets that press interactive ink blocks *into* the stock, and a soft ambient lift reserved for bento gallery cards on hover. The legacy neutralizer in `paper.css` actively strips every other shadow (`box-shadow: none !important` on headings, cards, images, tables).

### Shadow Vocabulary
- **Letterpress rest** (`box-shadow: inset 0 1px 0 rgba(255,255,255,0.14), inset 0 -1px 0 rgba(0,0,0,0.5)`): the default button state; a hairline highlight along the top edge, shadow along the bottom.
- **Letterpress pressed** (`box-shadow: inset 0 2px 3px rgba(0,0,0,0.45), inset 0 -1px 0 rgba(255,255,255,0.12)`): hover/focus; the press deepens as the block turns Registration Red.
- **Bento ambient** (`box-shadow: 0 1px 2px rgba(20,16,12,0.05), 0 6px 16px rgba(20,16,12,0.06)`): gallery cards at rest; barely-there ink-tinted lift.
- **Bento lift** (`box-shadow: 0 2px 4px rgba(20,16,12,0.07), 0 16px 32px rgba(20,16,12,0.11)`): gallery card hover, paired with a 4px rise.
- **Legacy image lift** (`box-shadow: 0 1px 2px rgba(20,16,12,0.08), 0 4px 12px rgba(20,16,12,0.07)`): the `.shadow-sm` shim for older post images only.

Motion is as restrained as the depth: colour and shadow transitions run 0.12s ease; bento cards lift 4px over 0.28s cubic-bezier(0.22, 1, 0.36, 1) with a 0.4s image drift (scale 1.03). Reduced-motion keeps the state changes and drops the movement.

### Named Rules
**The Letterpress Rule.** Interactive ink blocks read as pressed into the stock, never floating above it. Shadows on buttons are always inset; outward shadows belong to bento cards alone.

## Shapes

Square by conviction. Buttons, inputs, cards, blocks, and panels all run border-radius 0; the form language is the hard edge of set type. Three exceptions are shipped: bento gallery cards round to 14px (the one soft object in the system), citation chips take a 2px radius, and older post images keep the 4px legacy `.rounded` shim. Badges and tool tags are the sole pill forms (999px), drawn as 2px Registration Red outlines on transparent ground. Arrows (→) terminate buttons, nav tags, and entry links as a recurring glyph.

## Components

### Buttons
- **Character:** a block of set type, pressed into the paper.
- **Shape:** hard-edged (border-radius 0), no border.
- **Primary:** Press Ink block (#14100c) with the label knocked out in Paper Stock (#efe9dc); grotesk 700, normal case, 12px 20px padding, 46px min-height, letterpress-rest inset shadow; homepage buttons append an → glyph.
- **Hover / Focus:** background turns Registration Red (#c0330f) and the press deepens to the letterpress-pressed inset; 0.12s ease. Focus-visible adds the 3px Registration Red outline (2px offset).
- **Bare `<button>` fallback:** same treatment at a smaller scale (38px min-height, 8px 14px padding).

### Chips (citation tallies)
- **Style:** transparent ground, 1px Press Ink hairline border, 2px radius, 2px 7px padding; mono 11px, 0.08em tracking, Faded Ink.
- **State:** on row hover, border and text turn Registration Red.

### Badges / Tool tags
- **Style:** pill (999px), 2px Registration Red border (tool tags at 50% alpha), Registration Red text, 11px, transparent ground.

### Cards / Containers
- **Bento gallery card:** 14px radius, Paper Stock ground, 1px border at rgba(20,16,12,0.35), bento-ambient shadow; 16/10 image well (16/9 on feature) on a 3.5% ink wash with a hairline below; 1.25rem content padding. Hover: 4px lift, border turns Registration Red, bento-lift shadow, image drifts to 1.03 scale. Focus-visible: 3px Registration Red outline, 3px offset.
- **Flat card / content block:** Paper Stock ground, 1px ink hairline, radius 0; image tops sit on Card Stock (#e7e0d0) over a hairline.
- **Note / callout blocks:** 5% ink wash with a hairline border; never a dark panel.

### Inputs / Fields
- **Style:** Paper Stock ground, 1px ink hairline, radius 0, 38px min-height, grotesk face; caret in Registration Red; placeholder in Faded Ink at 75% alpha.
- **Focus:** 3px Registration Red outline, 2px offset.

### Navigation (the SKU-tag shelf)
- **Style:** grid cells on Paper Stock separated by 1px ink (the grid gap over an ink background), bounded by 2px rules; each tag stacks a mono SKU label (11px, 0.18em, uppercase, Faded Ink) over a 700-weight name with a trailing →.
- **Hover / Focus:** the cell inverts, ink ground with paper text, 0.12s ease; focus-visible adds the standard red outline. Back-links on interior pages reuse the letterpress button.

### Tables
- **Style:** collapsed borders; mono 11px uppercase headers in Faded Ink over a 2px rule; serif cells over 1px hairlines; row hover is a 3% ink wash.

### Registration-Mark Cursor (signature)
The cursor is a printer's registration mark (26px SVG data-URI) drawn twice, a 3.5px paper stroke under a 1.3px ink stroke, so it survives paper, photographs, and dark canvases. Over interactive elements it closes up and inks in: tighter crosshairs, a 2.6px filled centre, strokes in Registration Red. Text fields keep the native text caret.

## Do's and Don'ts

### Do:
- **Do** keep Registration Red (#c0330f) as the only chromatic accent; links, hovers, focus rings, markers, and nothing else carries hue (The One Spot Colour Rule).
- **Do** draw hierarchy with ink rules: 6px under section headings, 2px around page headers and footers, 1px between rows (The Ink Rule Rule).
- **Do** keep button depth inset; hover deepens the press and turns the block Registration Red (The Letterpress Rule).
- **Do** keep all transitions at 0.12s ease for colour and shadow, 0.28s cubic-bezier(0.22,1,0.36,1) for the bento lift, and honor prefers-reduced-motion by keeping state changes while dropping movement.
- **Do** keep mono metadata at 11px or above, uppercase only when the string is short; long venue and author lines run normal case.
- **Do** change token values in both `assets/css/paper.css` and the inline `<style>` in `index.html`; they are the same system in two files.

### Don't:
- **Don't** put cyan (or any second hue) borders on images, or any border-radius on buttons, inputs, or flat cards; the system is square except bento cards (14px), chips (2px), and the pill badges.
- **Don't** add typing animations, scanlines, glow, text-shadow, or terminal window chrome; the legacy neutralizer exists to kill exactly these.
- **Don't** set functional text below 11px, and never run long meta strings in uppercase.
- **Don't** float elements with outward drop shadows; outward shadow belongs to bento gallery cards alone, and even there it stays ink-tinted and soft.
- **Don't** box content to create hierarchy; use rule weight and type weight instead of panels and background fields.
