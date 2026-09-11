#!/usr/bin/env bash
# Sets up an isolated Python 3.11 environment with everything TripoSR needs.
# Usage: bash scripts/setup_env.sh [env_dir]
set -euo pipefail

ENV_DIR="${1:-/content/triposr_env}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔧 Creating virtual environment at $ENV_DIR ..."
rm -rf "$ENV_DIR"
python3.11 -m venv "$ENV_DIR"

PY="$ENV_DIR/bin/python"
"$PY" -m pip install --upgrade pip setuptools wheel

echo "🔧 Installing PyTorch (CUDA 12.1 build) ..."
"$PY" -m pip install torch==2.5.1 torchvision==0.20.1 \
    --index-url https://download.pytorch.org/whl/cu121

echo "🔧 Installing project dependencies ..."
"$PY" -m pip install -r "$PROJECT_DIR/requirements.txt"

echo "🔧 Installing torchmcubes ..."
"$PY" -m pip install "git+https://github.com/tatsy/torchmcubes.git"

echo "🔧 Cloning TripoSR ..."
if [ ! -d "$PROJECT_DIR/triposr" ]; then
    git clone https://github.com/VAST-AI-Research/TripoSR.git "$PROJECT_DIR/triposr"
    rm -rf "$PROJECT_DIR/triposr/.git"
fi

echo "✅ Environment ready. Python: $PY"
