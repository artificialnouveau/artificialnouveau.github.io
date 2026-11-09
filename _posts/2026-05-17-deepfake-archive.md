---
title: "Believe the Feed: The Deepfake Archive"
thumbnail: /assets/deepfake-archive-preview/btf-overview-2026-11.jpg
thumbnail_position: center
excerpt: "An active archive of deepfakes and synthetic media, from scams and grief to advertising, satire and the courtroom. Premiered at MozFest 2026."
indexing: false
category: "Archive"
---

Welcome to Believe the Feed, an active archive of deepfakes and synthetic media, sourced and curated by me, Ahnjili ZhuParris. Believe the Feed premiered at [MozFest 2026](https://www.mozillafestival.org/) in Barcelona.

Much of the discourse and legislation around deepfakes focuses on porn and political disinformation. Ever since the first deepfake was uploaded to Reddit in 2017, synthetic media has also moved into scams, grief, care, advertising, fake lifestyles, music videos, satire and the courtroom. The archive gathers these uses so we can think together about how this technology should be regulated.

Since making [DEEPFAKE: A Video Essay](/gallery/deepfake/), I have been cataloguing the unusual and emerging ways deepfakes and synthetic media are being used. New tools, genres and harms appear every few months, and most of them scroll out of the feed before anyone has had the chance to name them. Policy tends to be written for the cases that make headlines; this archive is an attempt to keep a record of everything else.

The archive is organised by intent at creation rather than by technique: who made a piece, and what it was made to do. Each artifact carries a curatorial panel that names the toolchain, the consent status and the concrete consequence for the people involved, steering clear of both AI-hype credulity and moral panic.

I hope the archive is useful to researchers and legislators trying to understand the current and still developing ecosystem of AI-generated social media.

<figure class="btf-clip">
  <video src="/assets/deepfake-archive-preview/bby-wow-dance.mp4" poster="/assets/deepfake-archive-preview/bby-wow-dance-poster.jpg" autoplay muted loop playsinline preload="metadata"></video>
  <figcaption><a href="/deepfakearchive/?item=bby-wow-dance-genjutsu-copies-2026" target="_blank" rel="noopener">View in the archive &rarr;</a></figcaption>
</figure>

<div class="btf-embed">
  <iframe id="btf-frame" src="/deepfakearchive/" title="Believe the Feed: The Deepfake Archive" allow="fullscreen; autoplay" allowfullscreen loading="lazy"></iframe>
</div>
<p class="btf-actions">
  <button type="button" id="btf-fullscreen">Full screen</button>
  <a href="/deepfakearchive/" target="_blank" rel="noopener">Open in a new tab &rarr;</a>
</p>

<style>
  .btf-embed { position: relative; width: 100%; aspect-ratio: 16 / 10; margin: 2rem 0 0.75rem; background: #0a0a0f; border: 1px solid #2a2a35; }
  .btf-embed iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
  .btf-clip { max-width: 460px; margin: 2rem auto; }
  .project-content .btf-clip video { width: 100%; max-width: none; display: block; margin: 0; border: none; background: #000; }
  .btf-clip figcaption { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; line-height: 1.5; letter-spacing: 0.04em; color: var(--color-muted); margin-top: 0.5rem; }
  .btf-actions { display: flex; gap: 1.25rem; align-items: center; font-size: 0.85rem; }
  .btf-actions button { font: inherit; padding: 0.4rem 0.8rem; border: 1px solid currentColor; background: transparent; color: inherit; cursor: pointer; }
  @media (max-width: 640px) { .btf-embed { aspect-ratio: 3 / 4; } }
</style>

<script>
(function () {
  var frame = document.getElementById("btf-frame");
  var btn = document.getElementById("btf-fullscreen");
  if (!frame.requestFullscreen) { btn.hidden = true; return; }
  btn.addEventListener("click", function () { frame.requestFullscreen().catch(function () {}); });
})();
</script>

