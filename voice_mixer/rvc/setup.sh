#!/usr/bin/env bash
# RVC training bootstrap. Run from voice_mixer/rvc/ directory:
#   bash setup.sh
#
# This clones the official RVC WebUI in a SEPARATE venv from the OpenVoice
# mixer (RVC pulls fairseq/faiss/specific torch versions and conflicts are
# common).
#
# After training, copy your trained model into ../models/:
#   cp Retrieval-based-Voice-Conversion-WebUI/assets/weights/<name>.pth ./models/
#   cp Retrieval-based-Voice-Conversion-WebUI/logs/<name>/added_*.index ./models/<name>.index
# Then in the mixer app, click "Rescan rvc/models/" and your model appears in
# the RVC post-pass dropdown.
set -euo pipefail

PYTHON=${PYTHON:-python3}

if [ ! -d "Retrieval-based-Voice-Conversion-WebUI" ]; then
    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
fi
cd Retrieval-based-Voice-Conversion-WebUI

if [ ! -d "venv" ]; then
    "$PYTHON" -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

pip install --upgrade pip wheel
pip install -r requirements.txt

# Pretrained base models (~2GB). Skip if already downloaded.
if [ ! -f "assets/pretrained_v2/G48k.pth" ] && [ -f "tools/download_models.py" ]; then
    echo "Downloading pretrained base models (~2GB)..."
    python tools/download_models.py
fi

mkdir -p ../models

cat <<'EOF'

RVC ready. To train a voice:
  cd Retrieval-based-Voice-Conversion-WebUI
  source venv/bin/activate
  python infer-web.py

Open the URL it prints. Use the "Train" tab. You need ~10-30 minutes of clean
audio of one speaker. Training takes ~30-90 min on a decent GPU; CPU training
is impractically slow.

After training, the model lands in:
  Retrieval-based-Voice-Conversion-WebUI/assets/weights/<name>.pth
And the index file in:
  Retrieval-based-Voice-Conversion-WebUI/logs/<name>/added_*.index

Copy both into voice_mixer/rvc/models/ (rename the index to <name>.index) so
the mixer app can find them.

For real-time voice-to-voice (microphone -> mixed voice -> speakers/OBS):
  1. Train at least two RVC models (above).
  2. In the mixer app's "RVC Merge" tab, pick 2-3 models, set weights, and
     bake a merged .pth into voice_mixer/rvc/models/.
  3. Install w-okada/voice-changer:
       https://github.com/w-okada/voice-changer
     (download the prebuilt installer for your OS - building from source is
     painful and unnecessary)
  4. In voice-changer's UI, load the merged .pth as your model and pick your
     mic + output device. Latency is typically <300ms on a decent GPU.

The split: this Gradio app is for *finding* a voice mix you like (instant
slider feedback via embedding interpolation). Voice-changer is for *performing*
with the mix you picked (sub-300ms real-time audio loop). Each tool stays in
its lane.
EOF
