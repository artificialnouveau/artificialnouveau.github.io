---
title: "Future Wake"
image: /assets/portfolio/deepfake1.jpg
---
"Future Wake" (www.futurewake.com) is an interactive website that scrutinizes the present state of predictive policing with a specific focus on forecasting police brutality. Awarded the Mozilla 2021 Creative Media Award, the project leverages Artificial Intelligence to scrutinize data regarding fatal police encounters in the U.S., aiming to foresee future incidents. It generates computer-simulated avatars that represent composite victims, narrating each of their stories. By presenting potential future victims to its audience, "Future Wake" provokes critical thought about the efficacy and ethics of predictive policing. It challenges viewers to ponder the true meaning of societal safety, how it is defined, and importantly, who is marginalized or overlooked within these systems.

<figure>
  <img class="img-fluid rounded-left rounded-right shadow-sm" src="../../../assets/portfolio/deepfake1.jpg" alt="Future Wake Face 1" style="max-height: 400px; width: 100%;">
  <figcaption class="mt-2 text-center image-caption">Image: Future Wake Face 1</figcaption>
</figure>

<figure>
  <img class="img-fluid rounded-left rounded-right shadow-sm" src="../../../assets/portfolio/deepfake2.jpg" alt="Future Wake Face 2" style="max-height: 400px; width: 100%;">
  <figcaption class="mt-2 text-center image-caption">Image: Future Wake Face 2</figcaption>
</figure>

---

<div id="predict-section" style="margin-top: 2rem; padding: 1.5rem; background: rgba(0,240,255,0.03); border: 1px solid rgba(0,240,255,0.2);">

<h2 style="text-align:center; margin-top:0;">Predict Your Risk</h2>

<p style="text-align:center; color: #b8a8d8; font-size: 0.8rem;">
Enter your zip code and demographics below. The system will estimate your likelihood of facing a fatal police encounter based on real data.<br>
<span style="font-size: 0.65rem; opacity: 0.7;">No data is stored or transmitted. All calculations happen in your browser.</span>
</p>

<div style="max-width: 500px; margin: 0 auto;">
  <div style="margin-bottom: 1rem;">
    <label style="font-size:0.7rem; color:#00f0ff; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.3rem;">Zip Code <span style="color:#b8a8d8; font-size:0.6rem; text-transform:none;">(or select state below)</span></label>
    <input type="text" id="fw-zip" maxlength="5" placeholder="e.g. 90210" style="width:100%; padding:0.6rem; background:#000; border:1px solid rgba(0,240,255,0.3); color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
    <div id="fw-zip-state-hint" style="font-size:0.6rem; color:#b8a8d8; margin-top:0.2rem; min-height:1em;"></div>
  </div>

  <div id="fw-state-row" style="margin-bottom: 1rem;">
    <label style="font-size:0.7rem; color:#00f0ff; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.3rem;">State <span style="color:#b8a8d8; font-size:0.6rem; text-transform:none;">(auto-filled from zip code if provided)</span></label>
    <select id="fw-state" style="width:100%; padding:0.6rem; background:#000; border:1px solid rgba(0,240,255,0.3); color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
      <option value="">Select state...</option>
    </select>
  </div>

  <div style="margin-bottom: 1rem;">
    <label style="font-size:0.7rem; color:#00f0ff; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.3rem;">Race / Ethnicity</label>
    <select id="fw-race" style="width:100%; padding:0.6rem; background:#000; border:1px solid rgba(0,240,255,0.3); color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
      <option value="">Select...</option>
      <option value="White">White</option>
      <option value="Black">Black</option>
      <option value="Hispanic">Hispanic</option>
      <option value="Asian">Asian</option>
      <option value="American Indian and Alaska Native">American Indian / Alaska Native</option>
      <option value="Native Hawaiian and Pacific Islander">Native Hawaiian / Pacific Islander</option>
    </select>
  </div>

  <div style="margin-bottom: 1rem;">
    <label style="font-size:0.7rem; color:#00f0ff; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.3rem;">Gender</label>
    <select id="fw-gender" style="width:100%; padding:0.6rem; background:#000; border:1px solid rgba(0,240,255,0.3); color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
      <option value="">Select...</option>
      <option value="Male">Male</option>
      <option value="Female">Female</option>
    </select>
  </div>

  <div style="margin-bottom: 1.5rem;">
    <label style="font-size:0.7rem; color:#00f0ff; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.3rem;">Age Group</label>
    <select id="fw-age-group" style="width:100%; padding:0.6rem; background:#000; border:1px solid rgba(0,240,255,0.3); color:#00f0ff; font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
      <option value="">Select...</option>
      <option value="Under 18">Under 18</option>
      <option value="18-24">18–24</option>
      <option value="25-34">25–34</option>
      <option value="35-44">35–44</option>
      <option value="45-54">45–54</option>
      <option value="55-64">55–64</option>
      <option value="65+">65+</option>
    </select>
  </div>

  <div style="text-align:center;">
    <button id="fw-predict-btn" style="background:#000; border:2px solid #ff10f0; color:#ff10f0; font-family:'JetBrains Mono',monospace; font-size:0.85rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.7rem 2rem; cursor:pointer;">[ Run Prediction ]</button>
  </div>
</div>

<!-- Processing log -->
<div id="fw-log" style="display:none; margin-top:1.5rem; font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#00f0ff; line-height:1.8; max-height:200px; overflow-y:auto; background:rgba(0,0,0,0.5); padding:0.75rem; border:1px solid rgba(0,240,255,0.15);"></div>

<!-- Results -->
<div id="fw-results" style="display:none; margin-top:1.5rem;">

  <div id="fw-risk-display" style="text-align:center; padding:2rem; border:2px solid #ff10f0; background:rgba(255,16,240,0.03);">
    <div style="font-size:0.65rem; color:#b8a8d8; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:0.5rem;">Estimated Annual Risk of Fatal Police Encounter</div>
    <div id="fw-risk-number" style="font-size:clamp(2rem,5vw,3.5rem); font-weight:700; letter-spacing:0.05em;"></div>
    <div id="fw-risk-label" style="font-size:0.75rem; color:#b8a8d8; margin-top:0.5rem;"></div>
  </div>

  <!-- Breakdown -->
  <div id="fw-breakdown" style="margin-top:1.5rem; padding:1rem; border-left:3px solid #00f0ff; background:rgba(0,240,255,0.03);"></div>

  <!-- Cause of death -->
  <div id="fw-cause-of-death" style="margin-top:1.5rem;"></div>

  <!-- Comparison bars -->
  <div id="fw-comparisons" style="margin-top:1.5rem;"></div>

  <!-- Data credit -->
  <div style="margin-top:2rem; padding:1rem; border:1px solid rgba(0,240,255,0.15); background:rgba(0,0,0,0.3);">
    <p style="font-size:0.7rem; color:#b8a8d8; margin:0;">This prediction is based on data from <a href="https://mappingpoliceviolence.org/" target="_blank" style="color:#00f0ff;">Mapping Police Violence</a> covering <strong style="color:#00f0ff;">January 1, 2013</strong> to <strong style="color:#00f0ff;">September 9, 2025</strong> — a total of <strong style="color:#ff10f0;">15,419</strong> documented fatal police encounters in the United States.</p>
    <p style="font-size:0.6rem; color:#b8a8d8; margin-top:0.5rem; opacity:0.7;">Risk estimates are statistical projections based on historical data aggregated by demographic group and geography. They do not predict individual outcomes. This tool is intended to illustrate systemic patterns in policing, not to assess personal danger.</p>
  </div>

</div>

</div>

<script>
(function() {
  var stats = null;
  var logEl = document.getElementById('fw-log');
  var resultsEl = document.getElementById('fw-results');
  var stateSelect = document.getElementById('fw-state');

  var states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District of Columbia','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'];
  states.forEach(function(s) {
    var opt = document.createElement('option');
    opt.value = s;
    opt.textContent = s;
    stateSelect.appendChild(opt);
  });

  var zipInput = document.getElementById('fw-zip');
  var zipHint = document.getElementById('fw-zip-state-hint');

  // Load stats
  fetch('/futurewake/mpv_stats.json').then(function(r) { return r.json(); }).then(function(d) {
    stats = d;
  });

  // Auto-fill state from zip code as user types
  zipInput.addEventListener('input', function() {
    if (!stats) return;
    var zip = zipInput.value.trim();
    var foundState = null;

    if (zip.length === 5 && stats.zip_to_state && stats.zip_to_state[zip]) {
      foundState = stats.zip_to_state[zip];
    } else if (zip.length >= 3 && stats.zip_prefix_to_state && stats.zip_prefix_to_state[zip.substring(0, 3)]) {
      foundState = stats.zip_prefix_to_state[zip.substring(0, 3)];
    }

    if (foundState) {
      stateSelect.value = foundState;
      zipHint.textContent = '> Detected state: ' + foundState;
      zipHint.style.color = '#00f0ff';
    } else if (zip.length >= 3) {
      zipHint.textContent = '> State not detected from zip';
      zipHint.style.color = '#b8a8d8';
    } else {
      zipHint.textContent = '';
    }
  });

  function log(msg, color) {
    logEl.style.display = 'block';
    var line = document.createElement('div');
    line.style.color = color || '#00f0ff';
    line.textContent = '> ' + msg;
    logEl.appendChild(line);
    logEl.scrollTop = logEl.scrollHeight;
  }

  function delay(ms) { return new Promise(function(r) { setTimeout(r, ms); }); }

  function riskColor(rate) {
    if (rate > 8) return '#ff10f0';
    if (rate > 5) return '#ff6040';
    if (rate > 3) return '#ffaa00';
    return '#00f0ff';
  }

  function makeBar(label, rate, maxRate, color) {
    var pct = Math.min(100, (rate / maxRate) * 100);
    return '<div style="margin-bottom:0.6rem;">' +
      '<div style="display:flex; justify-content:space-between; font-size:0.6rem; margin-bottom:0.2rem;">' +
      '<span style="color:#b8a8d8;">' + label + '</span>' +
      '<span style="color:' + color + ';">' + rate.toFixed(2) + ' per million</span>' +
      '</div>' +
      '<div style="background:rgba(0,240,255,0.1); height:8px; width:100%;">' +
      '<div style="background:' + color + '; height:100%; width:' + pct + '%; transition:width 0.5s;"></div>' +
      '</div></div>';
  }

  document.getElementById('fw-predict-btn').addEventListener('click', async function() {
    if (!stats) { alert('Data still loading, please try again.'); return; }

    var zip = document.getElementById('fw-zip').value.trim();
    var state = document.getElementById('fw-state').value;
    var race = document.getElementById('fw-race').value;
    var gender = document.getElementById('fw-gender').value;
    var ageBracket = document.getElementById('fw-age-group').value;

    // Auto-resolve state from zip if state not selected
    if (!state && zip.length === 5 && stats.zip_to_state && stats.zip_to_state[zip]) {
      state = stats.zip_to_state[zip];
    } else if (!state && zip.length >= 3 && stats.zip_prefix_to_state && stats.zip_prefix_to_state[zip.substring(0, 3)]) {
      state = stats.zip_prefix_to_state[zip.substring(0, 3)];
    }

    if (!state && !zip) {
      alert('Please enter a zip code or select a state.');
      return;
    }
    if (!race || !gender || !ageBracket) {
      alert('Please fill in all demographic fields.');
      return;
    }

    logEl.innerHTML = '';
    resultsEl.style.display = 'none';

    log('FUTURE WAKE PREDICTION ENGINE v2.0', '#ff10f0');
    await delay(400);
    log('Loading Mapping Police Violence dataset...', '#b8a8d8');
    await delay(600);
    log('Dataset: ' + stats.total.toLocaleString() + ' fatal police encounters', '#b8a8d8');
    log('Period: January 1, 2013 — September 9, 2025', '#b8a8d8');
    await delay(500);

    log('', '#000');
    log('━━━ ANALYZING DEMOGRAPHIC RISK FACTORS ━━━', '#ff10f0');
    await delay(400);

    var stateRate = stats.state_rates[state] || 0;
    var raceRate = stats.race_rates[race] || 0;
    var genderRate = stats.gender_rates[gender] || 0;
    var ageRate = stats.age_rates[ageBracket] || 0;

    log('State: ' + state + ' — ' + stateRate.toFixed(2) + ' per million per year', '#b8a8d8');
    await delay(300);
    log('Race: ' + race + ' — ' + raceRate.toFixed(2) + ' per million per year', '#b8a8d8');
    await delay(300);
    log('Gender: ' + gender + ' — ' + genderRate.toFixed(2) + ' per million per year', '#b8a8d8');
    await delay(300);
    log('Age bracket: ' + ageBracket + ' — ' + ageRate.toFixed(2) + ' per million per year', '#b8a8d8');
    await delay(400);

    // Check zip code
    var zipIncidents = stats.zip_counts[zip] || 0;
    if (zip && zipIncidents > 0) {
      log('Zip code ' + zip + ': ' + zipIncidents + ' incidents in database', '#ff10f0');
    } else if (zip) {
      log('Zip code ' + zip + ': No incidents recorded in this zip code', '#00f0ff');
    }
    await delay(400);

    log('', '#000');
    log('━━━ CAUSE OF DEATH ANALYSIS ━━━', '#ff10f0');
    await delay(400);
    if (stats.cause_of_death) {
      var codTotal = stats.cause_of_death_total || 1;
      var causes = Object.entries(stats.cause_of_death).sort(function(a,b) { return b[1] - a[1]; });
      for (var ci = 0; ci < causes.length; ci++) {
        var pct = (causes[ci][1] / codTotal * 100).toFixed(1);
        log('  ' + causes[ci][0] + ': ' + pct + '% (' + causes[ci][1].toLocaleString() + ' cases)', '#b8a8d8');
        await delay(200);
      }
    }
    await delay(400);

    log('', '#000');
    log('━━━ COMPUTING COMPOSITE RISK SCORE ━━━', '#ff10f0');
    await delay(500);

    // National baseline: ~3.8 per million per year overall
    var nationalBaseline = stats.total / 330000000 * 1000000 / 12.7;

    // Composite risk: weighted combination of factors relative to baseline
    var stateMultiplier = stateRate > 0 ? stateRate / nationalBaseline : 1;
    var raceMultiplier = raceRate > 0 ? raceRate / nationalBaseline : 1;
    var genderMultiplier = genderRate > 0 ? genderRate / nationalBaseline : 1;
    var ageMultiplier = ageRate > 0 ? ageRate / nationalBaseline : 1;

    // Geometric mean of multipliers applied to baseline
    var compositeMultiplier = Math.pow(stateMultiplier * raceMultiplier * genderMultiplier * ageMultiplier, 0.25);
    var compositeRate = nationalBaseline * compositeMultiplier;

    // Zip code bonus
    if (zipIncidents > 5) {
      compositeRate *= 1.3;
      log('High-incident zip code adjustment: +30%', '#ff10f0');
    } else if (zipIncidents > 0) {
      compositeRate *= 1.1;
      log('Zip code incident adjustment: +10%', '#b8a8d8');
    }

    await delay(300);
    log('National baseline: ' + nationalBaseline.toFixed(2) + ' per million per year', '#b8a8d8');
    log('Your composite multiplier: ' + compositeMultiplier.toFixed(2) + 'x', '#b8a8d8');
    await delay(400);

    var lifetimeRate = compositeRate * 75 / 1000000;
    var oneInX = Math.round(1000000 / compositeRate);

    log('', '#000');
    log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '#00f0ff');
    log('ESTIMATED ANNUAL RISK: ' + compositeRate.toFixed(2) + ' per million', riskColor(compositeRate));
    log('Approximate lifetime risk (75 yrs): 1 in ' + Math.round(1/lifetimeRate).toLocaleString(), '#b8a8d8');
    log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '#00f0ff');

    await delay(300);

    // Display results
    var color = riskColor(compositeRate);
    document.getElementById('fw-risk-number').style.color = color;
    document.getElementById('fw-risk-number').textContent = compositeRate.toFixed(2) + ' per million';
    document.getElementById('fw-risk-label').innerHTML = 'Approximately <strong style="color:' + color + ';">1 in ' + oneInX.toLocaleString() + '</strong> chance per year &mdash; Lifetime risk (75 yrs): <strong style="color:' + color + ';">1 in ' + Math.round(1/lifetimeRate).toLocaleString() + '</strong>';

    // Breakdown
    var bd = document.getElementById('fw-breakdown');
    bd.innerHTML = '<h4 style="color:#00f0ff; font-size:0.8rem; margin-top:0; margin-bottom:0.75rem;">Risk Factor Breakdown</h4>' +
      '<div style="font-size:0.7rem; color:#b8a8d8; line-height:2;">' +
      '<div><span style="color:#00f0ff;">State (' + state + '):</span> ' + stateRate.toFixed(2) + ' per million/yr — <span style="color:' + (stateMultiplier > 1.2 ? '#ff10f0' : '#00f0ff') + '">' + stateMultiplier.toFixed(2) + 'x national avg</span></div>' +
      '<div><span style="color:#00f0ff;">Race (' + race + '):</span> ' + raceRate.toFixed(2) + ' per million/yr — <span style="color:' + (raceMultiplier > 1.2 ? '#ff10f0' : '#00f0ff') + '">' + raceMultiplier.toFixed(2) + 'x national avg</span></div>' +
      '<div><span style="color:#00f0ff;">Gender (' + gender + '):</span> ' + genderRate.toFixed(2) + ' per million/yr — <span style="color:' + (genderMultiplier > 1.2 ? '#ff10f0' : '#00f0ff') + '">' + genderMultiplier.toFixed(2) + 'x national avg</span></div>' +
      '<div><span style="color:#00f0ff;">Age (' + ageBracket + '):</span> ' + ageRate.toFixed(2) + ' per million/yr — <span style="color:' + (ageMultiplier > 1.2 ? '#ff10f0' : '#00f0ff') + '">' + ageMultiplier.toFixed(2) + 'x national avg</span></div>' +
      (zip && zipIncidents > 0 ? '<div><span style="color:#00f0ff;">Zip (' + zip + '):</span> ' + zipIncidents + ' incidents recorded</div>' : '') +
      '</div>';

    // Cause of death breakdown
    var codEl = document.getElementById('fw-cause-of-death');
    if (stats.cause_of_death) {
      var codTotal = stats.cause_of_death_total || 1;
      var codIcons = { 'Gunshot': '&#x1F52B;', 'Vehicle': '&#x1F697;', 'Taser': '&#x26A1;', 'Physical Restraint': '&#x1F6D1;', 'Beaten': '&#x270A;', 'Other': '&#x2753;' };
      var codHtml = '<h4 style="color:#ff10f0; font-size:0.8rem; margin-bottom:0.75rem;">Cause of Death Breakdown</h4>';
      var causes = Object.entries(stats.cause_of_death).sort(function(a,b) { return b[1] - a[1]; });
      causes.forEach(function(entry) {
        var cause = entry[0], count = entry[1];
        var pct = (count / codTotal * 100);
        var barColor = cause === 'Gunshot' ? '#ff10f0' : cause === 'Vehicle' ? '#ffaa00' : cause === 'Taser' ? '#b010ff' : '#00f0ff';
        codHtml += '<div style="margin-bottom:0.5rem;">' +
          '<div style="display:flex; justify-content:space-between; font-size:0.6rem; margin-bottom:0.2rem;">' +
          '<span style="color:#b8a8d8;">' + cause + '</span>' +
          '<span style="color:' + barColor + ';">' + count.toLocaleString() + ' (' + pct.toFixed(1) + '%)</span>' +
          '</div>' +
          '<div style="background:rgba(0,240,255,0.1); height:8px; width:100%;">' +
          '<div style="background:' + barColor + '; height:100%; width:' + pct + '%; transition:width 0.5s;"></div>' +
          '</div></div>';
      });
      codEl.innerHTML = codHtml;
    }

    // Comparison bars
    var comp = document.getElementById('fw-comparisons');
    var maxRate = Math.max(raceRate, stateRate, genderRate, ageRate, compositeRate, nationalBaseline) * 1.1;

    comp.innerHTML = '<h4 style="color:#00f0ff; font-size:0.8rem; margin-bottom:0.75rem;">Comparative Rates (per million per year)</h4>' +
      makeBar('National Average', nationalBaseline, maxRate, '#b8a8d8') +
      makeBar('Your Composite Risk', compositeRate, maxRate, color) +
      makeBar(race, raceRate, maxRate, riskColor(raceRate)) +
      makeBar(state, stateRate, maxRate, riskColor(stateRate)) +
      makeBar(gender, genderRate, maxRate, riskColor(genderRate)) +
      makeBar(ageBracket, ageRate, maxRate, riskColor(ageRate));

    resultsEl.style.display = 'block';
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
</script>

---

<div style="margin-top: 3rem;">

<h2 style="text-align:center;">Selected Publications</h2>

<div style="margin: 1.5rem 0; padding: 1.5rem; background: rgba(0,240,255,0.03); border-left: 3px solid #ff10f0;">
<h4 style="margin-top:0;"><span style="color:#ff10f0;">[2024]</span> Embodying Data, Shifting Perspective</h4>
<p style="font-size:0.8rem; color:#b8a8d8; margin-bottom:0.5rem;">Book &bull; Amsterdam: Amsterdam University Press &bull; Wevers, R Edited by Ponzanesi, S. and Leurs, Koen.</p>
<p style="font-size:0.8rem;">This chapter discusses the artistic project Future Wake (2021) by Ahnjili Zhuparris and Tim van Ommeren that examines predictive policing. By shifting the focus from possible future crime offenders to possible future victims of fatal police encounters, using visual and affective means rather than expert knowledge and statistics, the artwork activates critical reflection on the politics and logics of predictive policing systems. The chapter first situates predictive policing in a context of securitization, and discusses how it enhances structures of discrimination. In the second part, Wevers interviews artist Zhuparris about the aims of Future Wake, discussing the artistic and technical process of creating the project, the politics of data, and the role of art in critical discussion on surveillance and AI.</p>
<p style="font-size:0.75rem;"><a href="https://research.hanze.nl/en/publications/embodying-data-shifting-perspective-a-conversation-with-ahnjili-z" target="_blank">You can find the full PDF here</a></p>
</div>

<div style="margin: 1.5rem 0; padding: 1.5rem; background: rgba(0,240,255,0.03); border-left: 3px solid #00f0ff;">
<h4 style="margin-top:0;"><span style="color:#ff10f0;">[2022]</span> Can AI imagine the next victims of police violence?</h4>
<p style="font-size:0.8rem; color:#b8a8d8; margin-bottom:0.5rem;">It's Nice That &bull; London, United Kingdom</p>
<p style="font-size:0.8rem;">What are the issues with using AI for predictive policing? Could it reduce crime or does it reinforce racial biases in the criminal justice system? The co-founder of art project Future Wake examines unjust policing using AI and storytelling.</p>
<p style="font-size:0.75rem;"><a href="http://www.itsnicethat.com/articles/future-wake-can-ai-imagine-police-violence-digital-opinion-120122" target="_blank">You can find the full article on the Its Nice That website</a></p>
</div>

<div style="margin: 1.5rem 0; padding: 1.5rem; background: rgba(0,240,255,0.03); border-left: 3px solid #00f0ff;">
<h4 style="margin-top:0;"><span style="color:#ff10f0;">[2021]</span> This horrifying AI model predicts future instances of police brutality</h4>
<p style="font-size:0.8rem; color:#b8a8d8; margin-bottom:0.5rem;">Fast Company &bull; Mark Sullivan &bull; United States</p>
<p style="font-size:0.8rem;">A searing critique of predictive policing, Future Wake uses past data on police violence to predict where it might occur in the future&mdash;and who will be targeted.</p>
<p style="font-size:0.75rem;"><a href="http://www.fastcompany.com/90689806/ai-police-brutality-predictions-future-wake" target="_blank">You can find the full article on the Fast Company website</a></p>
</div>

<div style="margin: 1.5rem 0; padding: 1.5rem; background: rgba(0,240,255,0.03); border-left: 3px solid #00f0ff;">
<h4 style="margin-top:0;"><span style="color:#ff10f0;">[2021]</span> Future Wake: the AI art project that predicts police violence</h4>
<p style="font-size:0.8rem; color:#b8a8d8; margin-bottom:0.5rem;">Coda Story &bull; Caitlin Thompson &bull; United States</p>
<p style="font-size:0.8rem;">Winner of the Mozilla Creative Media award for 2021, an interactive website calculates when and where fatal encounters with law enforcement will occur &mdash; and tells the stories of the victims.</p>
<p style="font-size:0.75rem;"><a href="http://www.codastory.com/authoritarian-tech/future-wake-predictive-policing/" target="_blank">You can find the full article on the Coda Story website</a></p>
</div>

<div style="margin: 1.5rem 0; padding: 1.5rem; background: rgba(0,240,255,0.03); border-left: 3px solid #00f0ff;">
<h4 style="margin-top:0;"><span style="color:#ff10f0;">[2021]</span> Artists create AI that predicts who the police will kill next</h4>
<p style="font-size:0.8rem; color:#b8a8d8; margin-bottom:0.5rem;">The Next Web &bull; Thomas Macaulay &bull; Netherlands</p>
<p style="font-size:0.8rem;">Future Wake tells the stories of potential victims.</p>
<p style="font-size:0.75rem;"><a href="http://thenextweb.com/news/future-wake-ai-predicts-who-police-will-kill-next" target="_blank">You can find the full article on The Next Web website</a></p>
</div>

</div>
