---
title: "Believe the Feed: The Deepfake Archive"
thumbnail: /assets/deepfake-archive-preview/thumbnails/video-by-realdonaldtrump-2026.jpg
excerpt: "Believe the Feed is an online interactive archive of synthetic media artifacts, organized by intent at creation into 25 folders under ten headings."
indexing: false
category: "Archive"
---

Believe the Feed is an online interactive archive of synthetic media artifacts, organized as a network graph. The editorial spine is intent at creation, not technique. The archive holds 25 folders grouped under ten headings:

- **Political:** Slopaganda; The Trump Administration
- **Abuse:** Race: Erasure & Hypervisibility; Porn & Intimate Partner Violence; Harassment and Bullying
- **Sell:** Faking Yourself for a Living; AI LARP; Demos; Synthetic Performers; The Slop Economy
- **Steal:** Scam, Fraud, and Social Engineering; Higgsfield + Plagiarism
- **Evidence:** A Day in Court; News and Documentaries
- **Resurrect:** Death in the Feed; History and Faith
- **Restore:** Care; Grief
- **Entertain:** Hollywood & Gaming; Humor & Satire
- **Art:** Video Art; Music Videos
- **?:** Well, wtf?; Is it Porn?; Is it Activism?

Each artifact carries a curatorial panel that names the toolchain, the consent status, and the concrete consequence to the people involved, in a register that is allergic to both AI-hype credulity and moral-panic credulity.

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

