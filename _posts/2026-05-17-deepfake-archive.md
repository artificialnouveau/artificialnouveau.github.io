---
title: "Deepfake Archive"
image: /assets/deepfake-archive-preview/thumbnails/video-by-realdonaldtrump-2026.jpg
excerpt: "An online archive of synthetic media artifacts, organized as an interactive network graph by intent at creation. Preview only, the full corpus targets several hundred artifacts."
indexing: false
---

An online, interactive archive of synthetic media artifacts, organized as a network graph. The editorial spine is intent at creation, not technique. Twelve rooms: propaganda, activism?, everyone is catfishing, entertainment and artworks, Hollywood deepfakes, AI sex workers, scam and fraud and social engineering, identity protection and pseudonymity, image-based abuse and harassment, blackface and whitewashing, awareness and self-reference, everyone is a commercial.

Each artifact carries a curatorial panel that names the toolchain, the consent status, and the concrete consequence to the people involved, in a register that is allergic to both AI-hype credulity and moral-panic credulity. The room that handles image-based abuse exhibits no media; its panels link to journalism and court documents instead.

<style>
  .dfa-preview {
    background: #0a0a0f;
    color: #f0e8d4;
    font-family: 'JetBrains Mono', monospace;
    padding: 1.5rem;
    margin: 2rem 0;
    border: 1px solid #2a2a35;
  }
  .dfa-preview * { box-sizing: border-box; }
  .dfa-preview h3 {
    font-family: Georgia, 'Times New Roman', serif;
    font-weight: 400;
    font-size: 1.4rem;
    color: #f0e8d4;
    margin: 0 0 0.4rem;
    letter-spacing: 0.02em;
  }
  .dfa-preview .dfa-sub {
    font-size: 0.7rem;
    color: #8a8377;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
  }
  .dfa-notice {
    border: 1px solid #ff10f0;
    background: rgba(255, 16, 240, 0.06);
    color: #f0e8d4;
    padding: 0.85rem 1rem;
    font-size: 0.78rem;
    margin-bottom: 1.5rem;
    line-height: 1.5;
  }
  .dfa-notice strong { color: #ff10f0; }
  .dfa-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #2a2a35;
  }
  .dfa-filter {
    background: transparent;
    border: 1px solid #3a3a45;
    color: #8a8377;
    font-family: inherit;
    font-size: 0.7rem;
    padding: 0.35rem 0.65rem;
    cursor: pointer;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    transition: all 0.15s;
  }
  .dfa-filter:hover { color: #f0e8d4; border-color: #6a6356; }
  .dfa-filter.active { background: #f0e8d4; color: #0a0a0f; border-color: #f0e8d4; }
  .dfa-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 0.85rem;
    align-items: center;
    font-size: 0.68rem;
    color: #8a8377;
    margin-bottom: 1.25rem;
  }
  .dfa-legend strong {
    color: #8a8377;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 600;
  }
  .dfa-legend-item { display: flex; align-items: center; gap: 0.4rem; }
  .dfa-legend-dot {
    width: 10px; height: 10px; border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }
  .dfa-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 0.6rem;
  }
  .dfa-card {
    position: relative;
    aspect-ratio: 1 / 1;
    background: #1a1a22;
    border: 2px solid transparent;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.15s, border-color 0.15s;
  }
  .dfa-card:hover { transform: translateY(-2px); }
  .dfa-card img {
    width: 100%; height: 100%; object-fit: cover;
    display: block;
    filter: saturate(0.7);
  }
  .dfa-card.no-thumb {
    display: flex; align-items: center; justify-content: center;
    background: repeating-linear-gradient(45deg, #1a1a22, #1a1a22 8px, #22222e 8px, #22222e 16px);
    color: #6a6356;
    font-size: 0.6rem;
    text-align: center;
    padding: 1rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .dfa-card-meta {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(10,10,15,0.95) 40%);
    padding: 2rem 0.5rem 0.5rem;
    opacity: 0;
    transition: opacity 0.15s;
    font-size: 0.65rem;
    color: #f0e8d4;
  }
  .dfa-card:hover .dfa-card-meta { opacity: 1; }
  .dfa-card-room {
    color: #8a8377;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.55rem;
    margin-top: 0.15rem;
  }
  .dfa-modal {
    position: fixed;
    inset: 0;
    background: rgba(10, 10, 15, 0.95);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 2rem 1rem;
    overflow-y: auto;
  }
  .dfa-modal.open { display: flex; }
  .dfa-modal-inner {
    background: #0a0a0f;
    border: 1px solid #3a3a45;
    max-width: 720px;
    width: 100%;
    padding: 1.5rem;
    color: #f0e8d4;
    position: relative;
    max-height: 90vh;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
  }
  .dfa-modal-close {
    position: absolute;
    top: 0.75rem; right: 0.75rem;
    background: transparent;
    border: 1px solid #3a3a45;
    color: #8a8377;
    font-family: inherit;
    width: 28px; height: 28px;
    cursor: pointer;
    font-size: 0.9rem;
    line-height: 1;
  }
  .dfa-modal-close:hover { color: #f0e8d4; border-color: #6a6356; }
  .dfa-modal img {
    width: 100%;
    max-height: 360px;
    object-fit: cover;
    margin-bottom: 1rem;
    filter: saturate(0.7);
  }
  .dfa-modal h2 {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.4rem;
    color: #f0e8d4;
    margin: 0 0 0.25rem;
    font-weight: 400;
  }
  .dfa-modal-meta {
    font-size: 0.7rem;
    color: #8a8377;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1rem;
  }
  .dfa-modal-meta span { display: flex; align-items: center; gap: 0.3rem; }
  .dfa-modal-panel {
    font-size: 0.85rem;
    line-height: 1.65;
    color: #d4c4a0;
    margin-bottom: 1rem;
    white-space: pre-line;
  }
  .dfa-modal-stub {
    border: 1px dashed #3a3a45;
    padding: 0.85rem;
    font-size: 0.75rem;
    color: #8a8377;
    margin-bottom: 1rem;
    line-height: 1.5;
  }
  .dfa-modal-link {
    display: inline-block;
    color: #00f0ff;
    text-decoration: none;
    font-size: 0.75rem;
    border-bottom: 1px solid #00f0ff;
    padding-bottom: 1px;
    word-break: break-all;
  }
  .dfa-modal-link:hover { color: #ff10f0; border-bottom-color: #ff10f0; }
  .dfa-empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem 1rem;
    color: #8a8377;
    font-size: 0.85rem;
  }
</style>

<div class="dfa-preview">

  <h3>Interactive Preview</h3>
  <div class="dfa-sub">Working build, May 2026.</div>

  <div class="dfa-notice">
    <strong>[ PREVIEW ONLY ]</strong> A small public preview of an in-progress project. The working build currently contains 37 artifacts. The full corpus targets several hundred. Curatorial text is locked for a handful of seed nodes (Cruise, Bourdain, Almendralejo); the rest of the editorial pass is in progress.
  </div>

  <div class="dfa-filters" id="dfa-filters"></div>

  <div class="dfa-grid" id="dfa-grid"></div>

  <div class="dfa-modal" id="dfa-modal">
    <div class="dfa-modal-inner">
      <button class="dfa-modal-close" id="dfa-modal-close" aria-label="Close">x</button>
      <div id="dfa-modal-body"></div>
    </div>
  </div>

</div>

<script>
(function() {
  const ROOMS = {
    1: "Propaganda",
    2: "Activism?",
    3: "Everyone is Catfishing",
    4: "Entertainment and Artworks",
    5: "Hollywood deepfakes",
    6: "AI sex workers",
    7: "Scam, Fraud, and Social Engineering",
    8: "Identity protection and pseudonymity",
    9: "Image-based abuse and harassment",
    10: "Blackface and Whitewashing",
    11: "Awareness and Self-Reference",
    12: "Everyone is a Commercial"
  };
  const CONSENT_COLOR = {
    "yes": "#00ff9c",
    "no": "#ff0080",
    "unknown": "#666666",
    "posthumous-with-estate": "#b366ff",
    "posthumous-without": "#ff8000"
  };
  const PANEL_NODES = new Set([
    "deeptomcruise-2021",
    "bourdain-roadrunner-2021",
    "almendralejo-2023"
  ]);
  const THUMB_BASE = "/assets/deepfake-archive-preview/thumbnails/";
  const THUMB_EXT = {
    "fake-ai-influencers-bbc-2026": ".webp"
  };
  function thumbUrl(id) {
    return THUMB_BASE + id + (THUMB_EXT[id] || ".jpg");
  }
  let allNodes = [];
  let activeRoom = "all";

  fetch("/assets/deepfake-archive-preview/nodes.json")
    .then(r => r.json())
    .then(nodes => {
      allNodes = nodes.sort((a, b) => a.intent_room - b.intent_room);
      renderFilters();
      renderGrid();
    });

  function renderFilters() {
    const counts = { all: allNodes.length };
    allNodes.forEach(n => { counts[n.intent_room] = (counts[n.intent_room] || 0) + 1; });
    const container = document.getElementById("dfa-filters");
    const buttons = [["all", "All (" + counts.all + ")"]];
    Object.keys(ROOMS).forEach(k => {
      if (counts[k]) buttons.push([k, k + ". " + ROOMS[k] + " (" + counts[k] + ")"]);
    });
    container.innerHTML = buttons.map(([k, label]) =>
      '<button class="dfa-filter' + (k === activeRoom ? ' active' : '') + '" data-room="' + k + '">' + label + '</button>'
    ).join("");
    container.querySelectorAll(".dfa-filter").forEach(btn => {
      btn.addEventListener("click", () => {
        activeRoom = btn.dataset.room;
        renderFilters();
        renderGrid();
      });
    });
  }

  function renderGrid() {
    const grid = document.getElementById("dfa-grid");
    const filtered = activeRoom === "all"
      ? allNodes
      : allNodes.filter(n => String(n.intent_room) === activeRoom);
    if (filtered.length === 0) {
      grid.innerHTML = '<div class="dfa-empty">No artifacts in this room yet.</div>';
      return;
    }
    grid.innerHTML = filtered.map(n => {
      const hasThumb = n.showable === "host";
      const year = (n.date || "").slice(0, 4);
      const placeholder = n.showable === "describe-only"
        ? '[ describe only<br>no media exhibited ]'
        : '[ link out<br>not hosted ]';
      const inner = hasThumb
        ? '<img src="' + thumbUrl(n.id) + '" alt="" loading="lazy">'
        : '<div>' + placeholder + '</div>';
      const cardClass = hasThumb ? "dfa-card" : "dfa-card no-thumb";
      return '<div class="' + cardClass + '" data-id="' + n.id + '">' +
        inner +
        '<div class="dfa-card-meta">' +
        '<div>' + escapeHtml(n.title) + '</div>' +
        '<div class="dfa-card-room">' + year + ' &middot; room ' + n.intent_room + '</div>' +
        '</div></div>';
    }).join("");
    grid.querySelectorAll(".dfa-card").forEach(card => {
      card.addEventListener("click", () => openModal(card.dataset.id));
    });
  }

  function openModal(id) {
    const node = allNodes.find(n => n.id === id);
    if (!node) return;
    const body = document.getElementById("dfa-modal-body");
    const hasThumb = node.showable === "host";
    const year = (node.date || "").slice(0, 4);
    const room = ROOMS[node.intent_room];
    const subjects = (node.subjects || []).join(", ");
    const showPanel = PANEL_NODES.has(node.id);
    let html = "";
    if (hasThumb) {
      html += '<img src="' + thumbUrl(node.id) + '" alt="">';
    }
    html += '<h2>' + escapeHtml(node.title) + '</h2>';
    html += '<div class="dfa-modal-meta">';
    html += '<span>' + year + '</span>';
    html += '<span>room ' + node.intent_room + ': ' + escapeHtml(room) + '</span>';
    html += '<span>consent: ' + escapeHtml(node.consent) + '</span>';
    if (subjects) html += '<span>subjects: ' + escapeHtml(subjects) + '</span>';
    html += '</div>';
    if (showPanel && node.curatorial_text) {
      html += '<div class="dfa-modal-panel">' + escapeHtml(node.curatorial_text) + '</div>';
    } else {
      html += '<div class="dfa-modal-stub">Curatorial panel in progress. Editorial pass on this artifact has not been completed for the public preview.</div>';
    }
    if (node.external_url) {
      html += '<a class="dfa-modal-link" href="' + node.external_url + '" target="_blank" rel="noopener">source &rarr;</a>';
    }
    body.innerHTML = html;
    document.getElementById("dfa-modal").classList.add("open");
  }

  function closeModal() {
    document.getElementById("dfa-modal").classList.remove("open");
  }

  document.getElementById("dfa-modal-close").addEventListener("click", closeModal);
  document.getElementById("dfa-modal").addEventListener("click", e => {
    if (e.target.id === "dfa-modal") closeModal();
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeModal();
  });

  function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
})();
</script>

