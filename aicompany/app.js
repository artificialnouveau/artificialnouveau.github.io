const FACE_SIZE = 300;
const MODEL_URL = "https://cdn.jsdelivr.net/npm/@vladmandic/face-api@1.7.14/model/";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

let modelsLoaded = false;
let allEntries = []; // { img, company, name, faces[], included, _detected }
let alignedFaces = []; // { canvas, company }
let activeFilter = "all"; // which company tab is active

// ── Initialise ──────────────────────────────────────────────

async function init() {
  const status = $("#status");

  try {
    status.textContent = "Loading face detection models…";

    await Promise.all([
      faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL),
      faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
    ]);
    modelsLoaded = true;

    // Load embedded photos from photo-data.js
    if (typeof PHOTO_DATA !== "undefined") {
      await loadEmbeddedPhotos();
    }

    if (allEntries.length > 0) {
      status.textContent = `Ready — ${allEntries.length} photos loaded. Click "Analyze Faces" to detect faces.`;
      status.classList.add("ready");
      $("#analyze-btn").disabled = false;
    } else {
      status.textContent = "Models loaded — upload photos or run the scraper first";
      status.classList.add("ready");
    }

    $("#drop-zone").classList.remove("hidden");
    setupDragDrop();
  } catch (err) {
    status.textContent = "Error loading: " + err.message;
    status.classList.add("error");
    console.error(err);
  }
}

// ── Load embedded base64 photos from PHOTO_DATA ─────────────

async function loadEmbeddedPhotos() {
  const companies = Object.keys(PHOTO_DATA);
  const totalPhotos = companies.reduce((sum, c) => sum + PHOTO_DATA[c].length, 0);
  let loaded = 0;

  showProgress(0);

  for (const company of companies) {
    for (const photo of PHOTO_DATA[company]) {
      try {
        const img = await loadImage(photo.dataUrl);
        allEntries.push({
          img,
          company,
          name: photo.name,
          faces: [],
          included: true,
          _detected: false,
        });
      } catch {
        console.warn("Failed to load", company, photo.name);
      }
      loaded++;
      showProgress(loaded / totalPhotos);
    }
  }

  hideProgress();
  buildCompanyTabs();
  renderGallery();
  updateButtons();
}

// ── Company tabs ────────────────────────────────────────────

function buildCompanyTabs() {
  const tabContainer = $("#company-tabs");
  tabContainer.classList.remove("hidden");

  const companies = [...new Set(allEntries.map((e) => e.company))];
  for (const company of companies) {
    const btn = document.createElement("button");
    btn.className = "tab";
    btn.dataset.company = company;
    btn.textContent = formatCompanyName(company);
    tabContainer.appendChild(btn);
  }

  tabContainer.addEventListener("click", (e) => {
    const tab = e.target.closest(".tab");
    if (!tab) return;
    activeFilter = tab.dataset.company;
    $$(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    renderGallery();
  });
}

function formatCompanyName(key) {
  const names = { shell: "Shell", heineken: "Heineken", philips: "Philips", ing: "ING" };
  return names[key] || key.charAt(0).toUpperCase() + key.slice(1);
}

// ── Drag & Drop ─────────────────────────────────────────────

function setupDragDrop() {
  const dropZone = $("#drop-zone");
  const fileInput = $("#file-input");

  dropZone.addEventListener("click", (e) => {
    if (e.target === fileInput) return;
    fileInput.click();
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const files = [...e.dataTransfer.files].filter((f) => f.type.startsWith("image/"));
    if (files.length) addFiles(files);
  });

  fileInput.addEventListener("change", () => {
    const files = [...fileInput.files];
    if (files.length) addFiles(files);
    fileInput.value = "";
  });
}

async function addFiles(files) {
  const status = $("#status");
  status.textContent = `Loading ${files.length} file(s)…`;
  status.className = "status";
  showProgress(0);

  for (let i = 0; i < files.length; i++) {
    const img = await loadImageFromFile(files[i]);
    allEntries.push({
      img,
      company: "uploaded",
      name: files[i].name.replace(/\.[^.]+$/, ""),
      faces: [],
      included: true,
      _detected: false,
    });
    showProgress((i + 1) / files.length);
  }

  hideProgress();
  buildCompanyTabs();
  renderGallery();
  updateButtons();
  status.textContent = `${allEntries.length} photos loaded. Click "Analyze Faces" to detect faces.`;
  status.classList.add("ready");
}

// ── Image loading helpers ───────────────────────────────────

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
}

function loadImageFromFile(file) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(img.src);
      resolve(img);
    };
    img.src = URL.createObjectURL(file);
  });
}

// ── Gallery rendering ───────────────────────────────────────

function renderGallery() {
  const gallery = $("#gallery");
  gallery.innerHTML = "";
  $("#gallery-title").classList.toggle("hidden", allEntries.length === 0);

  const filtered = activeFilter === "all"
    ? allEntries
    : allEntries.filter((e) => e.company === activeFilter);

  filtered.forEach((entry) => {
    const idx = allEntries.indexOf(entry);
    const div = document.createElement("div");
    div.className = "gallery-item" + (entry.included ? "" : " excluded");
    div.dataset.index = idx;

    const img = document.createElement("img");
    img.src = entry.img.src;
    img.alt = entry.name;
    div.appendChild(img);

    // Company badge
    const compBadge = document.createElement("span");
    compBadge.className = "company-badge";
    compBadge.textContent = formatCompanyName(entry.company);
    div.appendChild(compBadge);

    // Name badge
    if (entry.name) {
      const nameBadge = document.createElement("span");
      nameBadge.className = "name-badge";
      nameBadge.textContent = entry.name;
      div.appendChild(nameBadge);
    }

    if (entry.faces.length > 0) {
      const badge = document.createElement("span");
      badge.className = "face-count";
      badge.textContent = `${entry.faces.length} face${entry.faces.length > 1 ? "s" : ""}`;
      div.appendChild(badge);
    } else if (entry._detected) {
      const badge = document.createElement("span");
      badge.className = "face-count zero";
      badge.textContent = "0 faces";
      div.appendChild(badge);
    }

    div.addEventListener("click", () => {
      entry.included = !entry.included;
      div.classList.toggle("excluded", !entry.included);
    });

    gallery.appendChild(div);
  });
}

function updateButtons() {
  const hasEntries = allEntries.length > 0;
  $("#analyze-btn").disabled = !hasEntries || !modelsLoaded;
  $("#clear-btn").disabled = !hasEntries;
}

// ── Analyze: detect faces + generate averages ───────────────

async function analyzeAll() {
  if (!modelsLoaded || allEntries.length === 0) return;

  const status = $("#status");
  const btn = $("#analyze-btn");
  btn.disabled = true;

  status.textContent = "Detecting faces…";
  status.className = "status";
  showProgress(0);

  alignedFaces = [];
  let totalFaces = 0;

  for (let i = 0; i < allEntries.length; i++) {
    const entry = allEntries[i];
    if (!entry.included) {
      showProgress((i + 1) / allEntries.length);
      continue;
    }

    const detections = await faceapi
      .detectAllFaces(entry.img)
      .withFaceLandmarks();

    entry.faces = detections;
    entry._detected = true;

    for (const det of detections) {
      const aligned = alignFace(entry.img, det.landmarks);
      alignedFaces.push({ canvas: aligned, company: entry.company });
      totalFaces++;
    }

    showProgress((i + 1) / allEntries.length);
  }

  hideProgress();
  renderGallery();
  renderFaceStrip();

  status.textContent = `Found ${totalFaces} face(s). Generating averages…`;

  // Generate per-company averages
  generateCompanyAverages();

  // Generate combined average
  generateCombinedAverage();

  status.textContent = `Done — averaged ${totalFaces} face(s) from ${allEntries.filter((e) => e.included).length} photo(s)`;
  status.classList.add("ready");
  btn.disabled = false;
}

// ── Face alignment using similarity transform ───────────────

function alignFace(img, landmarks) {
  const pts = landmarks.positions;

  const leftEye = avgPoint(pts.slice(36, 42));
  const rightEye = avgPoint(pts.slice(42, 48));

  const targetLeftEye = { x: FACE_SIZE * 0.3, y: FACE_SIZE * 0.35 };
  const targetRightEye = { x: FACE_SIZE * 0.7, y: FACE_SIZE * 0.35 };

  const angle = Math.atan2(rightEye.y - leftEye.y, rightEye.x - leftEye.x);
  const targetAngle = Math.atan2(
    targetRightEye.y - targetLeftEye.y,
    targetRightEye.x - targetLeftEye.x
  );
  const rot = targetAngle - angle;

  const dist = Math.hypot(rightEye.x - leftEye.x, rightEye.y - leftEye.y);
  const targetDist = Math.hypot(
    targetRightEye.x - targetLeftEye.x,
    targetRightEye.y - targetLeftEye.y
  );
  const scale = targetDist / dist;

  const canvas = document.createElement("canvas");
  canvas.width = FACE_SIZE;
  canvas.height = FACE_SIZE;
  const ctx = canvas.getContext("2d");

  ctx.save();
  ctx.translate(targetLeftEye.x, targetLeftEye.y);
  ctx.rotate(rot);
  ctx.scale(scale, scale);
  ctx.translate(-leftEye.x, -leftEye.y);
  ctx.drawImage(img, 0, 0);
  ctx.restore();

  return canvas;
}

function avgPoint(points) {
  let x = 0, y = 0;
  for (const p of points) { x += p.x; y += p.y; }
  return { x: x / points.length, y: y / points.length };
}

// ── Face strip ──────────────────────────────────────────────

function renderFaceStrip() {
  const section = $("#faces-section");
  const strip = $("#face-strip");
  strip.innerHTML = "";

  if (alignedFaces.length === 0) {
    section.classList.add("hidden");
    return;
  }

  section.classList.remove("hidden");

  for (const face of alignedFaces) {
    const display = document.createElement("canvas");
    display.width = 80;
    display.height = 80;
    const ctx = display.getContext("2d");
    ctx.drawImage(face.canvas, 0, 0, 80, 80);
    strip.appendChild(display);
  }
}

// ── Generate per-company averages ───────────────────────────

function generateCompanyAverages() {
  const container = $("#company-averages");
  container.innerHTML = "";

  const companies = [...new Set(alignedFaces.map((f) => f.company))];

  if (companies.length === 0) {
    $("#company-results").classList.add("hidden");
    return;
  }

  $("#company-results").classList.remove("hidden");

  for (const company of companies) {
    const faces = alignedFaces
      .filter((f) => f.company === company)
      .map((f) => f.canvas);

    if (faces.length === 0) continue;

    const card = document.createElement("div");
    card.className = "company-average-card";

    const title = document.createElement("h3");
    title.textContent = formatCompanyName(company);
    card.appendChild(title);

    const canvas = document.createElement("canvas");
    canvas.width = FACE_SIZE;
    canvas.height = FACE_SIZE;
    averageFacesOntoCanvas(faces, canvas);
    card.appendChild(canvas);

    const meta = document.createElement("p");
    meta.className = "card-meta";
    const photoCount = allEntries.filter((e) => e.company === company && e.included).length;
    meta.textContent = `${faces.length} face(s) from ${photoCount} photo(s)`;
    card.appendChild(meta);

    container.appendChild(card);
  }
}

// ── Generate combined average ───────────────────────────────

function generateCombinedAverage() {
  const allCanvases = alignedFaces.map((f) => f.canvas);

  if (allCanvases.length === 0) {
    $("#result-section").classList.add("hidden");
    return;
  }

  const resultCanvas = $("#average-canvas");
  resultCanvas.width = FACE_SIZE;
  resultCanvas.height = FACE_SIZE;
  averageFacesOntoCanvas(allCanvases, resultCanvas);

  $("#result-section").classList.remove("hidden");
  const includedCount = allEntries.filter((e) => e.included).length;
  $("#result-meta").textContent = `Averaged ${allCanvases.length} face(s) from ${includedCount} photo(s) across all companies`;
}

// ── Shared pixel-averaging function ─────────────────────────

function averageFacesOntoCanvas(faceCanvases, targetCanvas) {
  const ctx = targetCanvas.getContext("2d");
  const accum = new Float64Array(FACE_SIZE * FACE_SIZE * 4);
  const count = faceCanvases.length;

  for (const faceCanvas of faceCanvases) {
    const tempCtx = faceCanvas.getContext("2d");
    const data = tempCtx.getImageData(0, 0, FACE_SIZE, FACE_SIZE).data;
    for (let i = 0; i < data.length; i++) {
      accum[i] += data[i];
    }
  }

  const output = ctx.createImageData(FACE_SIZE, FACE_SIZE);
  for (let i = 0; i < accum.length; i++) {
    output.data[i] = Math.round(accum[i] / count);
  }
  for (let i = 3; i < output.data.length; i += 4) {
    output.data[i] = 255;
  }
  ctx.putImageData(output, 0, 0);
}

// ── Clear all ───────────────────────────────────────────────

function clearResults() {
  alignedFaces = [];
  allEntries.forEach((e) => { e.faces = []; e._detected = false; });
  $("#face-strip").innerHTML = "";
  $("#faces-section").classList.add("hidden");
  $("#company-results").classList.add("hidden");
  $("#company-averages").innerHTML = "";
  $("#result-section").classList.add("hidden");
  renderGallery();
  updateButtons();
  $("#status").textContent = `${allEntries.length} photos loaded. Click "Analyze Faces" to detect faces.`;
  $("#status").className = "status ready";
}

// ── Progress bar ────────────────────────────────────────────

function showProgress(frac) {
  const wrap = $("#progress-wrap");
  const bar = $("#progress-bar");
  wrap.classList.remove("hidden");
  bar.style.width = (frac * 100).toFixed(1) + "%";
}

function hideProgress() {
  $("#progress-wrap").classList.add("hidden");
  $("#progress-bar").style.width = "0%";
}

// ── Event bindings ──────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  init();
  $("#analyze-btn").addEventListener("click", analyzeAll);
  $("#clear-btn").addEventListener("click", clearResults);
});
