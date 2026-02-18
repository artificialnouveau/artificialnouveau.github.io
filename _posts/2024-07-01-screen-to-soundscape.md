---
title: "Screen-to-Soundscape"
image: /assets/portfolio/STS_D1.jpg
---
Screen-to-Soundscape adopts an experimental approach to re-imaging screen readers, by addressing the current limitations for blind and visually impaired users. Our goal is to develop a free and open-source explorative tool that transforms a screen into an immersive soundscape, with a strong focus on providing rich, descriptive alt-text for images and maps. Using open-source computer vision algorithms, our system will analyze visual elements to generate detailed and customizable alt-text tailored to user preferences, offering a more comprehensive understanding of visual content. Additionally, the prototype will feature spatial audio, using multiple layered voices to read out the content, which ideally would enhance the users' navigation and interaction with digital content.

Our motivation is to provide a more intuitive and engaging navigation experience. Traditional screen readers often skip images, videos, and maps, and offer limited customization, especially in voice diversity. By incorporating spatial audio, novel computer vision algorithms, diverse voice options, and a customizable alt-text tool, our tool ensures all content is accessible and allows users to personalize their auditory experience, making digital navigation more natural and comprehensive.

Screen-to-Soundscape is supported by the Constant Foundation, The Processing Foundation, and the Stimuleringsfonds.

Read more about Screen-to-Soundscape on [www.screentosoundscape.com](https://www.screentosoundscape.com)

---

<div id="hear-this-page" style="margin-top: 2rem; padding: 1.5rem; background: rgba(0,240,255,0.03); border: 1px solid rgba(0,240,255,0.2);">

<h2 style="text-align:center; margin-top:0;">Try It: Hear This Page</h2>

<p style="text-align:center; color: #b8a8d8; font-size: 0.8rem;">
Enable spatial audio, then hover over any text block below. You'll hear a spatialized tone from the block's position in 3D space, followed by the text being read aloud. Left blocks sound from your left ear, right from your right. Top blocks are farther away, bottom blocks are closer.
</p>

<div style="text-align:center; margin: 1rem 0;">
  <button id="spatial-toggle" style="background:#000; border:2px solid #00f0ff; color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.8rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1.2rem; cursor:pointer;">[ Enable Spatial Audio ]</button>
</div>

<div id="spatial-status" style="text-align:center; font-size:0.65rem; color:#b8a8d8; margin-bottom:1.5rem;"></div>

<div id="soundscape-demo" style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem; opacity: 0.5; pointer-events: none;">

  <div class="spatial-block" data-freq="330" style="grid-column: 1; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Top Left</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Screen readers often skip images, videos, and maps, leaving blind users with an incomplete picture of digital content.">Screen readers often skip images, videos, and maps, leaving blind users with an incomplete picture of digital content.</p>
  </div>

  <div class="spatial-block" data-freq="392" style="grid-column: 2; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Top Right</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Our tool uses computer vision to generate rich, descriptive alt-text for images, making visual content accessible through sound.">Our tool uses computer vision to generate rich, descriptive alt-text for images, making visual content accessible through sound.</p>
  </div>

  <div class="spatial-block" data-freq="262" style="grid-column: 1 / -1; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Center</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Spatial audio uses multiple layered voices positioned in three-dimensional space, so content on the left of the screen sounds like it comes from your left ear.">Spatial audio uses multiple layered voices positioned in 3D space, so content on the left of the screen sounds like it comes from your left ear.</p>
  </div>

  <div class="spatial-block" data-freq="440" style="grid-column: 1; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Bottom Left</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Traditional screen readers offer a single monotone voice. We provide diverse voice options and customizable narration styles.">Traditional screen readers offer a single monotone voice. We provide diverse voice options and customizable narration styles.</p>
  </div>

  <div class="spatial-block" data-freq="523" style="grid-column: 2; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3); cursor:pointer; transition: all 0.2s;">
    <div style="font-size:0.6rem; color:#ff10f0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Bottom Right</div>
    <p style="font-size:0.75rem; margin:0;" data-speak="Screen-to-Soundscape is free and open-source, supported by Constant, The Processing Foundation, and the Stimuleringsfonds.">Screen-to-Soundscape is free and open-source, supported by Constant, The Processing Foundation, and the Stimuleringsfonds.</p>
  </div>

</div>

<p style="text-align:center; font-size:0.6rem; color:#b8a8d8; opacity:0.6; margin-top:1rem;">Best experienced with headphones for full spatial effect. Each block has a unique tone positioned in 3D space.</p>

</div>

<script>
(function() {
  var audioCtx = null;
  var spatialEnabled = false;
  var activeOscillator = null;
  var activeGain = null;

  var toggle = document.getElementById('spatial-toggle');
  var status = document.getElementById('spatial-status');
  var demo = document.getElementById('soundscape-demo');
  var blocks = document.querySelectorAll('.spatial-block');

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
      stopSpatialAudio();
      speechSynthesis.cancel();
      toggle.textContent = '[ Enable Spatial Audio ]';
      toggle.style.borderColor = '#00f0ff';
      toggle.style.color = '#00f0ff';
      demo.style.opacity = '0.5';
      demo.style.pointerEvents = 'none';
      status.textContent = '';
    }
  });

  function stopAllAudio() {
    stopSpatialAudio();
    speechSynthesis.cancel();
    blocks.forEach(function(b) {
      b.style.borderColor = 'rgba(0,240,255,0.15)';
      b.style.boxShadow = 'none';
      b.style.background = 'rgba(0,0,0,0.3)';
    });
  }

  function stopSpatialAudio() {
    if (activeGain) {
      try { activeGain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1); } catch(e) {}
    }
    if (activeOscillator) {
      if (activeOscillator._osc2) { try { activeOscillator._osc2.stop(); } catch(e) {} }
      if (activeOscillator._gain2) { try { activeOscillator._gain2.gain.value = 0; } catch(e) {} }
      try { activeOscillator.stop(audioCtx.currentTime + 0.15); } catch(e) {}
      activeOscillator = null;
      activeGain = null;
    }
  }

  // Stop all audio when clicking outside the demo area
  document.addEventListener('click', function(e) {
    if (!spatialEnabled) return;
    var demoArea = document.getElementById('hear-this-page');
    if (!demoArea.contains(e.target)) {
      stopAllAudio();
    }
  });

  // Stop all audio when leaving the page
  window.addEventListener('beforeunload', function() { stopAllAudio(); });
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) stopAllAudio();
  });

  function playSpatialTone(block) {
    stopSpatialAudio();

    var rect = block.getBoundingClientRect();
    var viewW = window.innerWidth;
    var viewH = window.innerHeight;

    // Map block position to 3D coordinates
    // X: -5 (far left) to 5 (far right)
    var posX = ((rect.left + rect.width / 2) / viewW) * 10 - 5;
    // Y: 0 (always ear level)
    var posY = 0;
    // Z: top of page = far (-8), bottom of page = near (-1)
    var posZ = -1 - ((1 - (rect.top + rect.height / 2) / viewH) * 7);

    var freq = parseFloat(block.getAttribute('data-freq')) || 440;

    // Create oscillator -> gain -> panner -> destination
    var osc = audioCtx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq;

    var gain = audioCtx.createGain();
    gain.gain.value = 0.001;

    // HRTF panner for true 3D spatial audio
    var panner = audioCtx.createPanner();
    panner.panningModel = 'HRTF';
    panner.distanceModel = 'inverse';
    panner.refDistance = 1;
    panner.maxDistance = 20;
    panner.rolloffFactor = 1.5;
    panner.coneInnerAngle = 360;
    panner.coneOuterAngle = 0;
    panner.coneOuterGain = 0;
    panner.positionX.setValueAtTime(posX, audioCtx.currentTime);
    panner.positionY.setValueAtTime(posY, audioCtx.currentTime);
    panner.positionZ.setValueAtTime(posZ, audioCtx.currentTime);

    // Also add a subtle ambient pad for each block
    var osc2 = audioCtx.createOscillator();
    osc2.type = 'triangle';
    osc2.frequency.value = freq * 0.5;

    var gain2 = audioCtx.createGain();
    gain2.gain.value = 0.001;

    // Second panner at same position
    var panner2 = audioCtx.createPanner();
    panner2.panningModel = 'HRTF';
    panner2.distanceModel = 'inverse';
    panner2.refDistance = 1;
    panner2.maxDistance = 20;
    panner2.rolloffFactor = 1.5;
    panner2.positionX.setValueAtTime(posX, audioCtx.currentTime);
    panner2.positionY.setValueAtTime(posY, audioCtx.currentTime);
    panner2.positionZ.setValueAtTime(posZ, audioCtx.currentTime);

    osc.connect(gain);
    gain.connect(panner);
    panner.connect(audioCtx.destination);

    osc2.connect(gain2);
    gain2.connect(panner2);
    panner2.connect(audioCtx.destination);

    osc.start();
    osc2.start();

    // Fade in
    gain.gain.exponentialRampToValueAtTime(0.15, audioCtx.currentTime + 0.3);
    gain2.gain.exponentialRampToValueAtTime(0.06, audioCtx.currentTime + 0.5);

    // Gentle pulse on the main tone
    var now = audioCtx.currentTime;
    for (var i = 0; i < 20; i++) {
      gain.gain.setValueAtTime(0.15, now + 0.5 + i * 0.6);
      gain.gain.exponentialRampToValueAtTime(0.06, now + 0.5 + i * 0.6 + 0.3);
      gain.gain.exponentialRampToValueAtTime(0.15, now + 0.5 + i * 0.6 + 0.6);
    }

    activeOscillator = osc;
    activeGain = gain;

    // Store second oscillator for cleanup
    osc._osc2 = osc2;
    osc._gain2 = gain2;

    return { posX: posX, posZ: posZ };
  }

  blocks.forEach(function(block) {
    block.addEventListener('mouseenter', function() {
      if (!spatialEnabled) return;

      speechSynthesis.cancel();

      var textEl = block.querySelector('[data-speak]');
      if (!textEl) return;

      var text = textEl.getAttribute('data-speak');

      // Visual feedback
      block.style.borderColor = '#ff10f0';
      block.style.boxShadow = '0 0 15px rgba(255,16,240,0.3)';
      block.style.background = 'rgba(255,16,240,0.05)';

      // Play spatialized tone from block position
      var pos = playSpatialTone(block);

      // Also speak the text (non-spatialized, but the tone gives directional cue)
      var utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.volume = 0.8;

      utterance.onend = function() {
        // Fade out tone when speech ends
        if (activeGain) {
          try { activeGain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5); } catch(e) {}
        }
      };

      // Status
      var side = pos.posX < -1.5 ? 'FAR LEFT' : pos.posX < -0.5 ? 'LEFT' : pos.posX > 1.5 ? 'FAR RIGHT' : pos.posX > 0.5 ? 'RIGHT' : 'CENTER';
      var depth = pos.posZ > -3 ? 'NEAR' : pos.posZ > -5 ? 'MID' : 'FAR';
      status.textContent = '> READING: Position [' + side + ' / ' + depth + '] — 3D: (' + pos.posX.toFixed(1) + ', 0, ' + pos.posZ.toFixed(1) + ')';

      // Small delay so tone is heard first
      setTimeout(function() {
        speechSynthesis.speak(utterance);
      }, 400);
    });

    block.addEventListener('mouseleave', function() {
      if (!spatialEnabled) return;
      speechSynthesis.cancel();
      stopSpatialAudio();

      // Cleanup second oscillator
      if (activeOscillator && activeOscillator._osc2) {
        try { activeOscillator._osc2.stop(); } catch(e) {}
      }

      block.style.borderColor = 'rgba(0,240,255,0.15)';
      block.style.boxShadow = 'none';
      block.style.background = 'rgba(0,0,0,0.3)';
      status.textContent = '> SPATIAL AUDIO ACTIVE — Hover over text blocks to hear them';
    });
  });
})();
</script>

---

<div style="margin-top: 2rem; padding: 1.5rem; background: rgba(0,240,255,0.03); border: 1px solid rgba(0,240,255,0.2);">

<h2 style="text-align:center; margin-top:0;">Phase 1 Prototype: Wikipedia Spatial Audio Explorer</h2>

<p style="text-align:center; color: #b8a8d8; font-size: 0.8rem;">
Enter a Wikipedia article to explore it as a 3D soundscape. Walk through sections with arrow keys, hear singing bowl beacons from each element's position, and listen to spatial text-to-speech. Best with headphones.
</p>

<iframe src="https://www.screentosoundscape.com/scripts/realtime.html"
  style="width:100%; height:600px; border:1px solid rgba(0,240,255,0.2); border-radius:6px; background:#1a1a2e;"
  allow="autoplay; microphone"
  loading="lazy"
  title="Screen-to-Soundscape Phase 1 Prototype">
</iframe>

<p style="text-align:center; font-size:0.6rem; color:#b8a8d8; opacity:0.6; margin-top:0.5rem;">
<a href="https://www.screentosoundscape.com/scripts/realtime.html" target="_blank" style="color:#00f0ff;">Open full-screen</a> for the best experience.
</p>

</div>
