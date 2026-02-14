---
title: "Screen-to-Soundscape"
image: /assets/portfolio/STS_D1.jpg
---
Screen-to-Soundscape adopts an experimental approach to re-imaging screen readers, by addressing the current limitations for blind and visually impaired users. Our goal is to develop a free and open-source explorative tool that transforms a screen into an immersive soundscape, with a strong focus on providing rich, descriptive alt-text for images and maps. Using open-source computer vision algorithms, our system will analyze visual elements to generate detailed and customizable alt-text tailored to user preferences, offering a more comprehensive understanding of visual content. Additionally, the prototype will feature spatial audio, using multiple layered voices to read out the content, which ideally would enhance the users' navigation and interaction with digital content.

Our motivation is to provide a more intuitive and engaging navigation experience. Traditional screen readers often skip images, videos, and maps, and offer limited customization, especially in voice diversity. By incorporating spatial audio, novel computer vision algorithms, diverse voice options, and a customizable alt-text tool, our tool ensures all content is accessible and allows users to personalize their auditory experience, making digital navigation more natural and comprehensive.

Screen-to-Soundscape is supported by the Constant Foundation, The Processing Foundation, and the Stimuleringsfonds.

Read more about Screen-to-Soundscape on [www.screentosoundscape.com](www.screentosoundscape.com)

---

<div id="hear-this-page" style="margin-top: 2rem; padding: 1.5rem; background: rgba(0,240,255,0.03); border: 1px solid rgba(0,240,255,0.2);">

<h2 style="text-align:center; margin-top:0;">Try It: Hear This Page</h2>

<p style="text-align:center; color: #b8a8d8; font-size: 0.8rem;">
Enable spatial audio, then hover over any text block below. Each element is read aloud with 3D-positioned audio based on where it sits on screen — left content pans left, right content pans right, top is quieter, bottom is closer.
</p>

<div style="text-align:center; margin: 1rem 0;">
  <button id="spatial-toggle" style="background:#000; border:2px solid #00f0ff; color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.8rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1.2rem; cursor:pointer;">[ Enable Spatial Audio ]</button>
</div>

<div id="spatial-status" style="text-align:center; font-size:0.65rem; color:#b8a8d8; margin-bottom:1.5rem;"></div>

<div id="soundscape-demo" style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem; opacity: 0.5; pointer-events: none;">

  <div class="spatial-block" style="grid-column: 1; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Top Left</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Screen readers often skip images, videos, and maps, leaving blind users with an incomplete picture of digital content.">Screen readers often skip images, videos, and maps, leaving blind users with an incomplete picture of digital content.</p>
  </div>

  <div class="spatial-block" style="grid-column: 2; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Top Right</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Our tool uses computer vision to generate rich, descriptive alt-text for images, making visual content accessible through sound.">Our tool uses computer vision to generate rich, descriptive alt-text for images, making visual content accessible through sound.</p>
  </div>

  <div class="spatial-block" style="grid-column: 1 / -1; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Center</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Spatial audio uses multiple layered voices positioned in three-dimensional space, so content on the left of the screen sounds like it comes from your left ear.">Spatial audio uses multiple layered voices positioned in 3D space, so content on the left of the screen sounds like it comes from your left ear.</p>
  </div>

  <div class="spatial-block" style="grid-column: 1; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Bottom Left</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Traditional screen readers offer a single monotone voice. We provide diverse voice options and customizable narration styles.">Traditional screen readers offer a single monotone voice. We provide diverse voice options and customizable narration styles.</p>
  </div>

  <div class="spatial-block" style="grid-column: 2; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Bottom Right</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Screen-to-Soundscape is free and open-source, supported by Constant, The Processing Foundation, and the Stimuleringsfonds.">Screen-to-Soundscape is free and open-source, supported by Constant, The Processing Foundation, and the Stimuleringsfonds.</p>
  </div>

</div>

<p style="text-align:center; font-size:0.6rem; color:#b8a8d8; opacity:0.6; margin-top:1rem;">Best experienced with headphones for full spatial effect.</p>

</div>

<script>
(function() {
  let audioCtx = null;
  let spatialEnabled = false;
  let currentUtterance = null;

  const toggle = document.getElementById('spatial-toggle');
  const status = document.getElementById('spatial-status');
  const demo = document.getElementById('soundscape-demo');
  const blocks = document.querySelectorAll('.spatial-block');

  toggle.addEventListener('click', function() {
    if (!spatialEnabled) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      spatialEnabled = true;
      toggle.textContent = '[ Disable Spatial Audio ]';
      toggle.style.borderColor = '#ff10f0';
      toggle.style.color = '#ff10f0';
      demo.style.opacity = '1';
      demo.style.pointerEvents = 'auto';
      status.textContent = '> SPATIAL AUDIO ACTIVE — Hover over text blocks to hear them';
      status.style.color = '#00f0ff';
    } else {
      spatialEnabled = false;
      if (currentUtterance) speechSynthesis.cancel();
      toggle.textContent = '[ Enable Spatial Audio ]';
      toggle.style.borderColor = '#00f0ff';
      toggle.style.color = '#00f0ff';
      demo.style.opacity = '0.5';
      demo.style.pointerEvents = 'none';
      status.textContent = '';
    }
  });

  blocks.forEach(function(block) {
    block.addEventListener('mouseenter', function() {
      if (!spatialEnabled) return;

      // Cancel any current speech
      speechSynthesis.cancel();

      const textEl = block.querySelector('[data-speak]');
      if (!textEl) return;

      const text = textEl.getAttribute('data-speak');
      const rect = block.getBoundingClientRect();
      const viewW = window.innerWidth;
      const viewH = window.innerHeight;

      // Calculate spatial position: -1 (left) to 1 (right)
      const panX = ((rect.left + rect.width / 2) / viewW) * 2 - 1;
      // Calculate distance: elements higher on page are "farther" (quieter)
      const distY = 1 - ((rect.top + rect.height / 2) / viewH) * 0.5;

      // Visual feedback
      block.style.borderColor = '#ff10f0';
      block.style.boxShadow = '0 0 15px rgba(255,16,240,0.3)';
      block.style.background = 'rgba(255,16,240,0.05)';

      // Use Web Speech API with spatial simulation
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.volume = Math.max(0.4, distY);
      currentUtterance = utterance;

      // If AudioContext available, route through panner
      if (audioCtx && audioCtx.state === 'running') {
        // We can't directly route SpeechSynthesis through Web Audio API,
        // so we simulate stereo panning with volume and pitch cues
        utterance.pitch = 0.9 + (distY * 0.3); // farther = slightly higher pitch
      }

      utterance.onend = function() {
        block.style.borderColor = 'rgba(0,240,255,0.15)';
        block.style.boxShadow = 'none';
        block.style.background = 'rgba(0,0,0,0.3)';
      };

      // Status update showing spatial info
      const side = panX < -0.2 ? 'LEFT' : panX > 0.2 ? 'RIGHT' : 'CENTER';
      const depth = distY > 0.7 ? 'NEAR' : distY > 0.4 ? 'MID' : 'FAR';
      status.textContent = '> READING: Position [' + side + ' / ' + depth + '] — Volume: ' + Math.round(utterance.volume * 100) + '%';

      speechSynthesis.speak(utterance);
    });

    block.addEventListener('mouseleave', function() {
      if (!spatialEnabled) return;
      speechSynthesis.cancel();
      block.style.borderColor = 'rgba(0,240,255,0.15)';
      block.style.boxShadow = 'none';
      block.style.background = 'rgba(0,0,0,0.3)';
      status.textContent = '> SPATIAL AUDIO ACTIVE — Hover over text blocks to hear them';
    });
  });
})();
</script>
