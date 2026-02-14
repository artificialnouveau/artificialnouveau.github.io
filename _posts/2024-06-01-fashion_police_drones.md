---
title: "Fashion Police Drones"
image: /assets/portfolio/drone_1.jpeg
---

<style>
.fpd-layout { display: flex; gap: 2rem; align-items: flex-start; }
.fpd-content { flex: 1; min-width: 0; }
.fpd-sidebar { flex: 0 0 380px; position: sticky; top: 2rem; }
@media (max-width: 900px) {
  .fpd-layout { flex-direction: column; }
  .fpd-sidebar { flex: none; width: 100%; position: static; }
}
</style>

<div class="fpd-layout">
<div class="fpd-content" markdown="1">

Fashion Police Drones transforms drones into arbiters of fashion, inviting the audience to set the criteria for fashion norms through an interactive platform. As these drones patrol the gallery, they actively scan for and monitor attendees whose attire matches the audience-defined standards of fashion faux pas, ranging from light-hearted to culturally contentious. This setup provides a unique opportunity for participants to engage directly with the technology, experiencing the implications of surveillance and societal judgment firsthand. The installation not only highlights the whimsical aspects of fashion norms but also prompts serious reflection on the societal and cultural impacts of fashion choices, mirroring real-world issues of discrimination and privacy.

In a space over 6 x 6 meters, a primary drone publicly judges outfits, while "stalker" drones quietly scan for style infractions. But these are no ordinary fashion faux pas—infractions fall into three categories:

- [Corporate Fashion Crimes](https://youtube.com/shorts/QwhF7XVgr5Q), targeting fast fashion giants like Zara and H&M for their environmental and labor abuses;

- [Ahnjili's Crimes](https://youtube.com/shorts/_TywTP3kjwc), enforcing the artist's own pet peeves with unapologetic flair;

- [Country-Specific Crimes](https://youtube.com/shorts/FmHWW-h6G5E), where drones emulate government-enforced dress codes, spotlighting fashion as a tool of political control.

On May 31st 2024, I was invited by the Privacy Salon to present at the [CPDP conference](https://www.cpdpconferences.org/archive) in Brussels.

On June 29th 2024, I will also present my Fashion Police Drones at the [New Media Art Conference (2024)](https://cicamuseum.com/new-media-art-2024/) at the CICA Museum in Korea.

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/crossdress.jpg" alt="CICA magazine image 1" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">CICA magazine image 1. Illustration done by Peter van Dijk (wwww.petervandijkcomics.com)</figcaption>
  </figure>
</div>

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/hijab.jpg" alt="CICA magazine image 2" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">CICA magazine image 2. Illustration done by Peter van Dijk (wwww.petervandijkcomics.com)</figcaption>
  </figure>
</div>

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/burka.jpg" alt="CICA magazine image 3" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">CICA magazine image 3. Illustration done by Peter van Dijk (wwww.petervandijkcomics.com)</figcaption>
  </figure>
</div>

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/socksnsandals.jpg" alt="CICA magazine image 4" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">CICA magazine image 4. Illustration done by Peter van Dijk (wwww.petervandijkcomics.com)</figcaption>
  </figure>
</div>

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/drone_5.png" alt="Fashion Police Drones at CPDP" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">Fashion Police Drones at CPDP</figcaption>
  </figure>
</div>

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/drone_1.jpeg" alt="Fashion Police Drones at CPDP" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">Fashion Police Drones at CPDP</figcaption>
  </figure>
</div>

<div class="row justify-content-center">
  <figure class="col-6">
    <img class="img-fluid rounded-left rounded-right shadow-sm mx-auto d-block" src="../../../assets/portfolio/drone_2.jpeg" alt="Fashion Police Drones at CPDP" style="max-height: 400px; width: auto;">
    <figcaption class="mt-2 text-center image-caption">Fashion Police Drones at CPDP</figcaption>
  </figure>
</div>

</div><!-- end fpd-content -->

<div class="fpd-sidebar">
<div id="try-me-section" style="padding: 1.5rem; background: rgba(0,240,255,0.03); border: 1px solid rgba(0,240,255,0.2);">

<h3 style="text-align:center; font-size: 1.1rem; margin-top:0;">TRY ME: Are You a Fashion Criminal?</h3>

<p style="text-align:center; color: #b8a8d8; font-size: 0.75rem;">Upload a photo of yourself (make sure your face is visible — it's important for the scan).<br><span style="font-size: 0.65rem; opacity: 0.7;">Don't worry — your images won't be saved or held as evidence.</span></p>

<div style="text-align:center; margin: 1rem 0;">
  <label for="suspect-upload" style="display:inline-block; background:#000; border:2px solid #00f0ff; color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1rem; cursor:pointer;">[ Upload Suspect Photo ]</label>
  <input type="file" id="suspect-upload" accept="image/*" style="display:none;">
</div>

<!-- Scan area -->
<div id="scan-area" style="display:none;">
  <!-- Uploaded image -->
  <div style="position:relative; text-align:center;">
    <img id="suspect-img" style="max-width:100%; max-height:300px; border: 2px solid #00f0ff; display:block; margin:0 auto;">
    <div id="scan-overlay" style="display:none; position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;">
      <div id="scan-line" style="position:absolute; top:0; left:0; width:100%; height:3px; background: linear-gradient(90deg, transparent, #00f0ff, #ff10f0, #00f0ff, transparent); box-shadow: 0 0 15px #00f0ff; transition: top 0.05s linear;"></div>
    </div>
  </div>

  <!-- Status log -->
  <div id="scan-log" style="margin-top:0.75rem; font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#00f0ff; line-height:1.8; max-height: 200px; overflow-y:auto; background:rgba(0,0,0,0.5); padding:0.75rem; border:1px solid rgba(0,240,255,0.15);"></div>

  <!-- Results -->
  <div id="scan-results" style="display:none;">
    <!-- Face comparison grid -->
    <div id="comparison-grid" style="margin-top: 1rem;">
      <p style="font-size: 0.6rem; color: #b8a8d8; text-transform: uppercase; letter-spacing:0.1em; margin-bottom: 0.75rem; text-align:center;">Cross-referencing against known fashion criminals...</p>
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.5rem;">
        <div style="text-align:center;">
          <img src="/fashionpolluters/shein.jpeg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid #ff10f0; filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:#ff10f0; margin-top:0.2rem;">SHEIN</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/zara.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid #ff10f0; filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:#ff10f0; margin-top:0.2rem;">ZARA</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/hm.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid #ff10f0; filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:#ff10f0; margin-top:0.2rem;">H&M</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/nike.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid #ff10f0; filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:#ff10f0; margin-top:0.2rem;">NIKE</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
        <div style="text-align:center;">
          <img src="/fashionpolluters/adidas.jpg" style="width:100%; aspect-ratio:1; object-fit:cover; border:2px solid #ff10f0; filter: contrast(1.2);">
          <div style="font-size:0.55rem; color:#ff10f0; margin-top:0.2rem;">ADIDAS</div>
          <div style="font-size:0.5rem; color:#b8a8d8;">NO MATCH</div>
        </div>
      </div>
    </div>

    <!-- Verdict -->
    <div id="verdict" style="margin-top: 1.5rem; text-align:center; padding: 1.5rem; border: 2px solid #00f0ff; background: rgba(0,240,255,0.05);">
      <div style="font-size: 0.6rem; color: #b8a8d8; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.3rem;">Verdict</div>
      <div style="font-size: 2rem; color: #00f0ff; text-shadow: 0 0 20px rgba(0,240,255,0.6); font-weight: 700; letter-spacing: 0.1em;">INNOCENT</div>
      <p style="color: #b8a8d8; font-size: 0.7rem; margin-top: 0.75rem;">No match found in the Fashion Criminal Database.<br>You're free to go... <em>for now.</em></p>
      <p style="color: #ff10f0; font-size: 0.75rem; margin-top: 1rem; font-weight: 700;">We're only looking for the <em>real</em> fashion criminals.</p>
    </div>

    <!-- Environmental Impact Info -->
    <div style="margin-top: 1.5rem; padding: 1rem; border-left: 3px solid #ff10f0; background: rgba(255,16,240,0.03);">
      <h4 style="color: #ff10f0; font-size: 0.85rem; margin-bottom: 0.75rem; margin-top: 0;">The Real Fashion Criminals</h4>
      <p style="font-size: 0.7rem;">Shein is currently identified as the largest polluter in the fast fashion industry, with emissions nearly doubling in 2023 due to rapid, AI-driven production. Other top polluting brands include Zara, H&M, Nike, and Adidas. The industry is responsible for 8–10% of global carbon emissions, primarily driven by synthetic fiber production and coal-powered manufacturing in China, Bangladesh, and India.</p>

      <h5 style="color: #00f0ff; font-size: 0.75rem; margin-top: 1rem;">Key Polluters and Environmental Impact</h5>
      <ul style="font-size: 0.65rem; color: #b8a8d8; line-height: 1.8; padding-left: 1.2rem;">
        <li><strong style="color:#00f0ff;">Top Polluting Companies:</strong> Shein, Zara, H&M, UNIQLO, Nike, and Adidas are leading contributors to the industry's massive carbon footprint.</li>
        <li><strong style="color:#00f0ff;">Primary Pollutants:</strong> The reliance on synthetic fibers (polyester, nylon, acrylic) derived from fossil fuels is a major contributor to pollution.</li>
        <li><strong style="color:#00f0ff;">Emissions & Waste:</strong> The fashion industry is responsible for 8–10% of global carbon emissions, exceeding the combined impact of international flights and maritime shipping.</li>
        <li><strong style="color:#00f0ff;">Water Usage & Pollution:</strong> The industry is the second-largest consumer of water globally, responsible for 20% of wastewater.</li>
        <li><strong style="color:#00f0ff;">Production Hotspots:</strong> China and the USA are the highest producers of fashion waste, while manufacturing is concentrated in countries relying on coal-powered energy, such as China, Bangladesh, and India.</li>
      </ul>

      <h5 style="color: #00f0ff; font-size: 0.75rem; margin-top: 1rem;">Factors Driving Pollution</h5>
      <ul style="font-size: 0.65rem; color: #b8a8d8; line-height: 1.8; padding-left: 1.2rem;">
        <li><strong style="color:#00f0ff;">Overproduction & Fast Fashion:</strong> The business model relies on low-quality, high-volume production, which causes significant textile waste.</li>
        <li><strong style="color:#00f0ff;">Synthetic Fibers:</strong> Over 60% of clothing is made from synthetic materials, which take hundreds of years to biodegrade.</li>
        <li><strong style="color:#00f0ff;">Chemical Use:</strong> The industry uses thousands of harmful chemicals for dyeing and finishing fabrics.</li>
      </ul>

      <h5 style="color: #00f0ff; font-size: 0.75rem; margin-top: 1rem;">References</h5>
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
    line.style.color = color || '#00f0ff';
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
    log('SUSPECT PHOTO RECEIVED', '#00f0ff');
    await delay(800);
    log('Initializing Fashion Crime Detection System v4.2.0...', '#b8a8d8');
    await delay(600);
    log('Loading Fashion Criminal Database...', '#b8a8d8');
    await delay(1000);
    log('Database loaded: 5 known fashion criminals on file', '#ff10f0');

    await delay(700);
    log('', '#000');
    log('━━━ PHASE 1: FASHION ITEM SCAN ━━━', '#ff10f0');
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
    log('Fashion item scan complete.', '#00f0ff');

    await delay(600);
    log('', '#000');
    log('━━━ PHASE 2: FACIAL RECOGNITION ━━━', '#ff10f0');
    await delay(500);

    const scanPromise2 = animateScanLine(1500);
    log('Detecting face in uploaded image...', '#b8a8d8');
    await delay(1000);
    log('Face detected. Extracting biometric features...', '#00f0ff');
    await delay(700);
    log('Mapping 468 facial landmarks...', '#b8a8d8');
    await delay(600);
    log('Generating facial signature hash...', '#b8a8d8');
    await delay(500);
    log('Facial signature: 0x' + Math.random().toString(16).slice(2, 18).toUpperCase(), '#b010ff');
    await scanPromise2;

    await delay(600);
    log('', '#000');
    log('━━━ PHASE 3: DATABASE COMPARISON ━━━', '#ff10f0');
    await delay(500);

    const criminals = ['SHEIN (Xu Yangtian)', 'ZARA (Amancio Ortega)', 'H&M (Stefan Persson)', 'NIKE (John Donahoe)', 'ADIDAS (Bjorn Gulden)'];
    for (const criminal of criminals) {
      log('Comparing against ' + criminal + '...', '#b8a8d8');
      await delay(600 + Math.random() * 500);
      const similarity = (Math.random() * 12 + 1).toFixed(1);
      log('  Similarity: ' + similarity + '% — NO MATCH', '#00f0ff');
      await delay(300);
    }

    await delay(800);
    log('', '#000');
    log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '#00f0ff');
    log('SCAN COMPLETE', '#00f0ff');
    log('VERDICT: INNOCENT — No match found in Fashion Criminal Database', '#00f0ff');
    log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '#00f0ff');

    await delay(500);
    scanResults.style.display = 'block';
    scanResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
</script>

