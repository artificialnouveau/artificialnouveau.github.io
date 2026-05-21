#!/usr/bin/env bash
# Voice mixer setup. Run from the voice_mixer/ directory:
#   bash setup.sh
# Then:
#   source venv/bin/activate
#   python app.py
set -euo pipefail

PYTHON=${PYTHON:-python3}

if [ ! -d "venv" ]; then
    "$PYTHON" -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

pip install --upgrade pip wheel

if [ ! -d "OpenVoice" ]; then
    git clone https://github.com/myshell-ai/OpenVoice.git
fi
pip install -e ./OpenVoice
pip install git+https://github.com/myshell-ai/MeloTTS.git
python -m unidic download

pip install -r requirements.txt

if [ ! -d "checkpoints_v2" ]; then
    echo "Downloading OpenVoice v2 checkpoints..."
    curl -L -o checkpoints_v2.zip \
        https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip
    unzip checkpoints_v2.zip
    rm checkpoints_v2.zip
fi

echo
echo "Done. Run:"
echo "  source venv/bin/activate"
echo "  python app.py"
