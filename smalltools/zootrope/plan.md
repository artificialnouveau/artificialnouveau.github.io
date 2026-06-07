# Zoötrope: content-aware stitching plan

Goal: move from "blend pixels and hope" to "analyse what is in each live feed, then let
the content decide placement, timing, grouping, and depth." Everything runs client-side
(static GitHub Pages page), using in-browser ML.

## In-browser analysis toolbox

| Tool | Gives you | Notes |
|------|-----------|-------|
| MediaPipe Tasks (Web) Object Detector | bounding boxes + class labels | EfficientDet-Lite, COCO classes incl. bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe. Fast, GPU delegate. |
| MediaPipe Image Segmenter (DeepLab) | multi-class pixel masks | clean subject masks |
| transformers.js MobileSAM / SlimSAM | promptable precise masks | feed it a detector box -> exact animal silhouette |
| transformers.js CLIP | image + text embeddings | semantic similarity / grouping / text query |
| transformers.js Depth Anything Small | per-pixel depth | depth-ordered compositing |
| TensorFlow.js COCO-SSD / DeepLab | boxes / semantic masks | alt to MediaPipe |
| OpenCV.js | optical flow, histograms, ORB+homography | motion vectors, colour match, true panorama stitch |

## Stitching strategies (content drives composition)

1. **Real subject masks** instead of motion-diff. Detect the animal, then segment it (SAM/DeepLab).
   Cutout = "the bird," present whether or not it moves. Biggest legibility jump.
2. **Geometry-aware placement.** Align every animal's box-bottom ("feet") to one shared ground
   line; normalise scale via box size + class prior. Animals look like they share earth.
3. **Depth-ordered shared habitat.** Monocular depth per feed; composite back-to-front so nearer
   animals occlude farther ones. The "single shared scene" done properly.
4. **Event-driven auto-editing.** Score each feed each moment by detection confidence + motion
   energy; foreground whichever feed has an animal actively doing something, idle the empty ones.
   Live vision-mixer (Natalie Bookchin choreography logic).
5. **Semantic grouping (CLIP).** Embed each feed/animal crop; arrange grid so similar scenes sit
   adjacent, cluster by meaning, or pair opposites. Text-drivable ("show feed most like 'drinking'").
6. **Motion-direction choreography.** Optical flow dominant vector per feed; place left-moving
   animal on the right heading to centre, sync entrances/exits, reveal on flow spikes.
7. **Colour harmonisation.** Match each cutout's LAB histogram to a shared palette so feeds from
   different cameras/lighting do not clash. Cheap, classical, unifying.
8. **Taxonomy layout.** Detector labels route animals into bands/zones (birds stratum, mammals
   stratum). Semantic grid.

## Architecture: two loops at different rates

- **Fast loop (rAF, ~30fps):** cheap pixel work (alpha, drawing). Reads metadata only.
- **Slow loop (~200-600ms):** one shared model instance, round-robin feeds, updates each feed's
  metadata (box, mask, label, depth, embedding, flow).
- Use WebGPU / GPU delegate; run inference at low res (256-320px); never one model per feed.

Limit: COCO/VOC are coarse (chickadee + cardinal = "bird"). Species needs a fine-grained
iNaturalist classifier, heavier, run occasionally on a cropped box.

## Staged rollout

- [x] **Step 0:** motion background-subtraction cutout + multi-feed remix compositor (done).
- [~] **Step 1 (wiring in now):** MediaPipe Object Detector. Run detection in the slow loop,
      store boxes+labels per feed. New "Detect objects" mode gates the cutout to detected boxes
      and draws labels; "Animals only" class filter; NOW SHOWING shows what is detected.
- [ ] **Step 2:** MobileSAM / DeepLab segmentation -> replace motion-diff with true subject masks.
- [ ] **Step 3:** Depth Anything -> depth-ordered shared-habitat compositing.
- [ ] **Step 4:** CLIP embeddings -> semantic grouping / event-driven auto-editing.

## Source reality (context)

Famous animal cams (Explore.org, Cornell, zoos) are YouTube = cross-origin, CORS-tainted,
no pixel access. Usable pool = self-hosted HLS, mainly ipcamlive (sends ACAO:*). The app
resolves stable ipcamlive aliases at runtime (streamids rotate). Confirmed-live test feeds
currently: Flagler Pier FL (beach), Timmins ON (intersection). Osprey/bird-nest cams found but
offline at last check; swap in via one line in FEEDS when live.
