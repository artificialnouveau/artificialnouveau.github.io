---
title: "Fashion Police Drones"
thumbnail: /assets/portfolio/fpd/prada-panel.gif
excerpt: "Fashion Police Drones transforms drones into arbiters of fashion, inviting the audience to set the criteria for fashion norms through an interactive platform."
---

<style>
.fpd-layout { display: flex; gap: 2rem; align-items: flex-start; }
.fpd-content { flex: 1; min-width: 0; }
.fpd-sidebar { flex: 0 0 380px; position: sticky; top: 2rem; }

/* The three infraction categories, self-hosted so no player branding shows */
.fpd-videos { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0; }
.fpd-videos figure { margin: 0; }
.project-content .fpd-videos img {
  width: 100%;
  aspect-ratio: 9 / 16;
  object-fit: cover;
  background: #000;
  display: block;
  margin: 0;
  border: none;
}

/* Booking sticker */
.fpd-sticker {
  display: block;
  transform: rotate(-2.5deg);
  border: 2px solid var(--color-accent);
  background: rgba(192, 51, 15, 0.07);
  padding: 1rem 1.1rem 0.9rem;
  margin: 0 0 1.75rem;
  text-decoration: none !important;
  color: var(--color-text);
  transition: transform 0.18s ease, background 0.18s ease;
}
.fpd-sticker:hover, .fpd-sticker:focus-visible { transform: rotate(0deg); background: rgba(192, 51, 15, 0.14); }
.fpd-sticker .s-top {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--color-accent);
}
.fpd-sticker strong { display: block; font-size: 0.98rem; line-height: 1.35; margin: 0.45rem 0 0.6rem; }
.fpd-sticker .s-cta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-accent);
}
.fpd-sticker .s-cta::after { content: ' \2192'; }

/* Verdict panel from the drone feed, portrait */
.fpd-panel { max-width: 320px; margin: 2rem 0; }
.fpd-sidebar .fpd-panel { max-width: none; margin: 1.25rem 0 0; }
.project-content .fpd-panel video { width: 100%; max-width: none; display: block; margin: 0; border: none; }

/* Documentation and illustrations, as a grid rather than a stack */
.fpd-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin: 2rem 0; align-items: start; }
.fpd-grid figure { margin: 0; }
.project-content .fpd-grid img { width: 100%; height: auto; margin: 0; border: none; display: block; }
/* uniform tiles so the rows line up: illustrations are shown whole, photos are cropped */
.project-content .fpd-grid.art img { aspect-ratio: 3 / 4; object-fit: contain; background: rgba(20, 16, 12, 0.04); }
.fpd-videos figcaption,
.fpd-grid figcaption {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  line-height: 1.5;
  letter-spacing: 0.04em;
  color: var(--color-muted);
  margin-top: 0.5rem;
  text-align: left;
}

@media (max-width: 900px) {
  .fpd-layout { flex-direction: column; }
  .fpd-sidebar { flex: none; width: 100%; position: static; }
  .fpd-videos { grid-template-columns: 1fr; max-width: 320px; }
}
</style>

<div class="fpd-layout">
<div class="fpd-content" markdown="1">

Fashion Police Drones transforms drones into arbiters of fashion, inviting the audience to set the criteria for fashion norms through an interactive platform. As these drones patrol the gallery, they actively scan for and monitor attendees whose attire matches the audience-defined standards of fashion faux pas, ranging from light-hearted to culturally contentious. This setup provides a unique opportunity for participants to engage directly with the technology, experiencing the implications of surveillance and societal judgment firsthand. The installation not only highlights the whimsical aspects of fashion norms but also prompts serious reflection on the societal and cultural impacts of fashion choices, mirroring real-world issues of discrimination and privacy.

- **Corporate fashion crimes**, targeting fast fashion giants like Zara and H&M for their environmental and labor abuses;

- **Ahnjili's crimes**, enforcing the artist's own pet peeves with unapologetic flair;

- **Country-specific crimes**, where drones emulate government-enforced dress codes, spotlighting fashion as a tool of political control.

<div class="fpd-videos">
  <figure>
    <img src="/assets/portfolio/fpd/short-corporate.gif" alt="Corporate fashion crimes: the drone scanning an outfit, staged as a social feed" loading="lazy">
    <figcaption>Corporate fashion crimes</figcaption>
  </figure>
  <figure>
    <img src="/assets/portfolio/fpd/short-ahnjili.gif" alt="Ahnjili's crimes: the drone scanning an outfit, staged as a social feed" loading="lazy">
    <figcaption>Ahnjili's crimes</figcaption>
  </figure>
  <figure>
    <img src="/assets/portfolio/fpd/short-country.gif" alt="Country-specific crimes: the drone scanning an outfit, staged as a social feed" loading="lazy">
    <figcaption>Country-specific crimes</figcaption>
  </figure>
</div>

On May 31st 2024, I was invited by the Privacy Salon to present at the [CPDP conference](https://www.cpdpconferences.org/archive) in Brussels.

On June 29th 2024, I will also present my Fashion Police Drones at the [New Media Art Conference (2024)](https://cicamuseum.com/new-media-art-2024/) at the CICA Museum in Korea.

The work was also showcased at [AIAIAI.art](https://aiaiai.art/fashion-police), and in May 2024 I was interviewed by dublab about the project: [Artificial Nouveau — Fashion Police Drones](http://dublab.de/broadcasts/artificial-nouveau-fashion-police-drones-may-2024/).

After exhibiting this work for the first time, I came across a BBC report that Iran had deployed real drones to enforce its hijab law on the streets. The piece was made as satire and critique of how surveillance technology amplifies the enforcement of fashion and dress codes. Reading that report made the satire feel very thin. [BBC: Iran using drones to enforce hijab law, says rights group (2024)](https://www.bbc.com/news/articles/c0kg15jkpdeo)

<div class="fpd-grid art">
  <figure>
    <img src="../../../assets/portfolio/crossdress.jpg" alt="Illustration of a drone citing a person for cross-dressing" loading="lazy">
    <figcaption>CICA magazine, 1. Illustration by Peter van Dijk (petervandijkcomics.com)</figcaption>
  </figure>
  <figure>
    <img src="../../../assets/portfolio/hijab.jpg" alt="Illustration of a drone enforcing a hijab law" loading="lazy">
    <figcaption>CICA magazine, 2. Illustration by Peter van Dijk (petervandijkcomics.com)</figcaption>
  </figure>
  <figure>
    <img src="../../../assets/portfolio/burka.jpg" alt="Illustration of a drone enforcing a burka ban" loading="lazy">
    <figcaption>CICA magazine, 3. Illustration by Peter van Dijk (petervandijkcomics.com)</figcaption>
  </figure>
  <figure>
    <img src="../../../assets/portfolio/socksnsandals.jpg" alt="Illustration of a drone citing socks worn with sandals" loading="lazy">
    <figcaption>CICA magazine, 4. Illustration by Peter van Dijk (petervandijkcomics.com)</figcaption>
  </figure>
</div>

</div><!-- end fpd-content -->

<div class="fpd-sidebar">
<a class="fpd-sticker" href="mailto:artificialnouveau@gmail.com?subject=Fashion%20Police%20Drones%20booking">
  <span class="s-top">Available for booking</span>
  <strong>Bring the Fashion Police Drones to a venue near you</strong>
  <span class="s-cta">Get in touch</span>
</a>

<div id="try-me-section" style="padding: 1.5rem; background: rgba(20, 16, 12, 0.03); border: 1px solid rgba(20, 16, 12, 0.2);">

<h3 style="text-align:center; font-size: 1.1rem; margin-top:0;">TRY ME: Are You a Fashion Criminal?</h3>

<p style="text-align:center; color: #b8a8d8; font-size: 0.75rem;">Upload a photo of yourself (make sure your face is visible — it's important for the scan).<br><span style="font-size: 0.65rem; opacity: 0.7;">Don't worry — your images won't be saved or held as evidence.</span></p>

<div style="text-align:center; margin: 1rem 0;">
  <label for="suspect-upload" style="display:inline-block; background:var(--color-card-bg); border:2px solid var(--color-accent-cyan); color:var(--color-accent-cyan); font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1rem; cursor:pointer;">[ Upload Suspect Photo ]</label>
  <input type="file" id="suspect-upload" accept="image/*" style="display:none;">
</div>

<!-- Scan area -->
<div id="scan-area" style="display:none;">
  <!-- Uploaded image -->
  <div style="position:relative; text-align:center;">
    <img id="suspect-img" style="max-width:100%; max-height:300px; border: 2px solid var(--color-accent-cyan); display:block; margin:0 auto;">
    <div id="scan-overlay" style="display:none; position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;">
      <div id="scan-line" style="position:absolute; top:0; left:0; width:100%; height:3px; background: linear-gradient(90deg, transparent, var(--color-accent-cyan), var(--color-accent), var(--color-accent-cyan), transparent); box-shadow: 0 0 15px var(--color-accent-cyan); transition: top 0.05s linear;"></div>
    </div>
  </div>

  <!-- Status log -->
  <div id="scan-log" style="margin-top:0.75rem; font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--color-accent-cyan); line-height:1.8; max-height: 200px; overflow-y:auto; background:rgba(0,0,0,0.5); padding:0.75rem; border:1px solid rgba(20, 16, 12, 0.15);"></div>

  <!-- Results -->
  <div id="scan-results" style="display:none;">
    <!-- Face comparison grid -->
    <div id="comparison-grid" style="margin-top: 1rem;">
      <p style="font-size: 0.6rem; color: #b8a8d8; text-transform: uppercase; letter-spacing:0.1em; margin-bottom: 0.75rem; text-align:center;">Cross-referencing against known fashion criminals...</p>
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.5rem;">
        <div style="text-align:center;">
          <img src="/fashionpolluters/shein.jpeg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid var(--color-accent); filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:var(--color-accent); margin-top:0.2rem;">SHEIN</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/zara.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid var(--color-accent); filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:var(--color-accent); margin-top:0.2rem;">ZARA</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/hm.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid var(--color-accent); filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:var(--color-accent); margin-top:0.2rem;">H&M</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/nike.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid var(--color-accent); filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:var(--color-accent); margin-top:0.2rem;">NIKE</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/adidas.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid var(--color-accent); filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:var(--color-accent); margin-top:0.2rem;">ADIDAS</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
      </div>
    </div>

    <!-- Verdict -->
    <div id="verdict" style="margin-top: 1.5rem; text-align:center; padding: 1.5rem; border: 2px solid var(--color-accent-cyan); background: rgba(20, 16, 12, 0.05);">
      <div style="font-size: 0.6rem; color: #b8a8d8; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.3rem;">Verdict</div>
      <div style="font-size: 2rem; color: var(--color-accent-cyan); text-shadow: 0 0 20px rgba(20, 16, 12, 0.6); font-weight: 700; letter-spacing: 0.1em;">INNOCENT</div>
      <p style="color: #b8a8d8; font-size: 0.7rem; margin-top: 0.75rem;">No match found in the Fashion Criminal Database.<br>You're free to go... <em>for now.</em></p>
      <p style="color: var(--color-accent); font-size: 0.75rem; margin-top: 1rem; font-weight: 700;">We're only looking for the <em>real</em> fashion criminals.</p>
    </div>

    <!-- Environmental Impact Info -->
    <div style="margin-top: 1.5rem; padding: 1rem; border-left: 3px solid var(--color-accent); background: rgba(192, 51, 15, 0.03);">
      <h4 style="color: var(--color-accent); font-size: 0.85rem; margin-bottom: 0.75rem; margin-top: 0;">The Real Fashion Criminals</h4>
      <p style="font-size: 0.7rem;">Shein is currently identified as the largest polluter in the fast fashion industry, with emissions nearly doubling in 2023 due to rapid, AI-driven production. Other top polluting brands include Zara, H&M, Nike, and Adidas. The industry is responsible for 8–10% of global carbon emissions, primarily driven by synthetic fiber production and coal-powered manufacturing in China, Bangladesh, and India.</p>

      <h5 style="color: var(--color-accent-cyan); font-size: 0.75rem; margin-top: 1rem;">Key Polluters and Environmental Impact</h5>
      <ul style="font-size: 0.65rem; color: #b8a8d8; line-height: 1.8; padding-left: 1.2rem;">
        <li><strong style="color:var(--color-accent-cyan);">Top Polluting Companies:</strong> Shein, Zara, H&M, UNIQLO, Nike, and Adidas are leading contributors to the industry's massive carbon footprint.</li>
        <li><strong style="color:var(--color-accent-cyan);">Primary Pollutants:</strong> The reliance on synthetic fibers (polyester, nylon, acrylic) derived from fossil fuels is a major contributor to pollution.</li>
        <li><strong style="color:var(--color-accent-cyan);">Emissions & Waste:</strong> The fashion industry is responsible for 8–10% of global carbon emissions, exceeding the combined impact of international flights and maritime shipping.</li>
        <li><strong style="color:var(--color-accent-cyan);">Water Usage & Pollution:</strong> The industry is the second-largest consumer of water globally, responsible for 20% of wastewater.</li>
        <li><strong style="color:var(--color-accent-cyan);">Production Hotspots:</strong> China and the USA are the highest producers of fashion waste, while manufacturing is concentrated in countries relying on coal-powered energy, such as China, Bangladesh, and India.</li>
      </ul>

      <h5 style="color: var(--color-accent-cyan); font-size: 0.75rem; margin-top: 1rem;">Factors Driving Pollution</h5>
      <ul style="font-size: 0.65rem; color: #b8a8d8; line-height: 1.8; padding-left: 1.2rem;">
        <li><strong style="color:var(--color-accent-cyan);">Overproduction & Fast Fashion:</strong> The business model relies on low-quality, high-volume production, which causes significant textile waste.</li>
        <li><strong style="color:var(--color-accent-cyan);">Synthetic Fibers:</strong> Over 60% of clothing is made from synthetic materials, which take hundreds of years to biodegrade.</li>
        <li><strong style="color:var(--color-accent-cyan);">Chemical Use:</strong> The industry uses thousands of harmful chemicals for dyeing and finishing fabrics.</li>
      </ul>

      <h5 style="color: var(--color-accent-cyan); font-size: 0.75rem; margin-top: 1rem;">References</h5>
      <ul style="font-size: 0.55rem; color: #b8a8d8; line-height: 1.8; word-break: break-all; padding-left: 1.2rem;">
        <li><a href="https://grist.org/technology/as-fast-fashion-giant-shein-embraces-ai-its-emissions-are-soaring/">Grist — As fast fashion giant Shein embraces AI, its emissions are soaring</a></li>
        <li><a href="https://yaleclimateconnections.org/2024/09/shein-is-officially-the-biggest-polluter-in-fast-fashion-ai-is-making-things-worse/">Yale Climate Connections — Shein is officially the biggest polluter in fast fashion</a></li>
        <li><a href="https://davidsuzuki.org/living-green/the-environmental-cost-of-fast-fashion/">David Suzuki Foundation — The environmental cost of fast fashion</a></li>
        <li><a href="https://www.visualcapitalist.com/cp/carbon-emissions-of-the-worlds-biggest-fashion-brands/">Visual Capitalist — Carbon emissions of the world's biggest fashion brands</a></li>
        <li><a href="https://www.sustainyourstyle.org/en/whats-wrong-with-the-fashion-industry">Sustain Your Style — What's wrong with the fashion industry</a></li>
        <li><a href="https://news.un.org/en/story/2025/03/1161636">UN News — Fast fashion's environmental toll</a></li>
      </ul>
    </div>
  </div>
</div>

</div><!-- end try-me-section -->

<figure class="fpd-panel">
  <video src="/assets/portfolio/fpd/prada-panel.mp4" poster="/assets/portfolio/print/fpd-panel.jpg" autoplay muted loop playsinline preload="metadata"></video>
  <figcaption>A verdict panel from the drone feed: the outfit is itemised garment by garment, then sentenced.</figcaption>
</figure>
</div><!-- end fpd-sidebar -->
</div><!-- end fpd-layout -->

<script>
(function() {
  const upload = document.getElementById('suspect-upload');
  const suspectImg = document.getElementById('suspect-img');
  const scanArea = document.getElementById('scan-area');
  const scanOverlay = document.getElementById('scan-overlay');
  const scanLine = document.getElementById('scan-line');
  const scanLog = document.getElementById('scan-log');
  const scanResults = document.getElementById('scan-results');

  function log(msg, color) {
    const line = document.createElement('div');
    line.style.color = color || 'var(--color-accent-cyan)';
    line.textContent = '> ' + msg;
    scanLog.appendChild(line);
    scanLog.scrollTop = scanLog.scrollHeight;
  }

  function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  async function animateScanLine(duration) {
    scanOverlay.style.display = 'block';
    const start = Date.now();
    return new Promise(resolve => {
      function frame() {
        const elapsed = Date.now() - start;
        const progress = (elapsed % duration) / duration;
        scanLine.style.top = (progress * 100) + '%';
        if (elapsed < duration * 2) {
          requestAnimationFrame(frame);
        } else {
          scanOverlay.style.display = 'none';
          resolve();
        }
      }
      frame();
    });
  }

  upload.addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    suspectImg.src = url;
    scanArea.style.display = 'block';
    scanLog.innerHTML = '';
    scanResults.style.display = 'none';

    await delay(500);
    log('SUSPECT PHOTO RECEIVED', 'var(--color-accent-cyan)');
    await delay(800);
    log('Initializing Fashion Crime Detection System v4.2.0...', '#b8a8d8');
    await delay(600);
    log('Loading Fashion Criminal Database...', '#b8a8d8');
    await delay(1000);
    log('Database loaded: 5 known fashion criminals on file', 'var(--color-accent)');

    await delay(700);
    log('', '#000');
    log('━━━ PHASE 1: FASHION ITEM SCAN ━━━', 'var(--color-accent)');
    await delay(500);

    const scanPromise = animateScanLine(2000);

    await delay(400);
    log('Scanning for fashion items...', '#b8a8d8');
    await delay(800);

    const items = [
      'Detecting garment outlines...',
      'Analyzing fabric texture patterns...',
      'Cross-referencing brand logos...',
      'Checking for counterfeit labels...',
      'Evaluating color palette compliance...',
      'Scanning for polyester content...',
      'Measuring carbon footprint signature...'
    ];
    for (const item of items) {
      log(item, '#b8a8d8');
      await delay(400 + Math.random() * 400);
    }

    await scanPromise;
    log('Fashion item scan complete.', 'var(--color-accent-cyan)');

    await delay(600);
    log('', '#000');
    log('━━━ PHASE 2: FACIAL RECOGNITION ━━━', 'var(--color-accent)');
    await delay(500);

    const scanPromise2 = animateScanLine(1500);
    log('Detecting face in uploaded image...', '#b8a8d8');
    await delay(1000);
    log('Face detected. Extracting biometric features...', 'var(--color-accent-cyan)');
    await delay(700);
    log('Mapping 468 facial landmarks...', '#b8a8d8');
    await delay(600);
    log('Generating facial signature hash...', '#b8a8d8');
    await delay(500);
    log('Facial signature: 0x' + Math.random().toString(16).slice(2, 18).toUpperCase(), 'var(--color-accent-purple)');
    await scanPromise2;

    await delay(600);
    log('', '#000');
    log('━━━ PHASE 3: DATABASE COMPARISON ━━━', 'var(--color-accent)');
    await delay(500);

    const criminals = ['SHEIN (Xu Yangtian)', 'ZARA (Amancio Ortega)', 'H&M (Stefan Persson)', 'NIKE (John Donahoe)', 'ADIDAS (Bjorn Gulden)'];
    for (const criminal of criminals) {
      log('Comparing against ' + criminal + '...', '#b8a8d8');
      await delay(600 + Math.random() * 500);
      const similarity = (Math.random() * 12 + 1).toFixed(1);
      log('  Similarity: ' + similarity + '% — NO MATCH', 'var(--color-accent-cyan)');
      await delay(300);
    }

    await delay(800);
    log('', '#000');
    log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'var(--color-accent-cyan)');
    log('SCAN COMPLETE', 'var(--color-accent-cyan)');
    log('VERDICT: INNOCENT — No match found in Fashion Criminal Database', 'var(--color-accent-cyan)');
    log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'var(--color-accent-cyan)');

    await delay(500);
    scanResults.style.display = 'block';
    scanResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
</script>

