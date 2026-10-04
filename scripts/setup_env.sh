#!/usr/bin/env bash
# Create one Python environment per model under envs/. Each model pins library versions that conflict
# with the others, so they are kept apart; the pipeline starts each model with its own interpreter.
#
#   bash scripts/setup_env.sh pipeline      the pipeline itself (analysis, tables, figures)
#   bash scripts/setup_env.sh imajev        imajev server and trainer (also used for the untuned base model)
#   bash scripts/setup_env.sh specialist    the specialist classifier (torch + torchvision)
#   bash scripts/setup_env.sh neohorse | jev_omni | visual_jev | glance | jev27b
#   bash scripts/setup_env.sh all
#
# UNTESTED: written from each project's documentation for the DGX Spark (Arm, CUDA 13). Package builds for
# this machine change quickly; when a step fails, fix it here and rerun. After each one, run `drjev doctor`.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
TORCH_INDEX=${TORCH_INDEX:-$(python3 - <<'PY'
import re, pathlib
t = pathlib.Path("config/study.yaml").read_text()
m = re.search(r"^machine:\s*(\S+)", t, re.M)
p = pathlib.Path(m.group(1)) if m else pathlib.Path("config/machines/generic.yaml")
u = re.search(r"^torch_index_url:\s*(\S+)", p.read_text(), re.M)
print(u.group(1).strip('"') if u else "")
PY
)}
PYVER=${PYVER:-3.12}

venv() {   # venv <name> [python version]
  local dir="$ROOT/envs/$1" ver="${2:-$PYVER}"
  if [ ! -x "$dir/bin/python" ]; then
    if command -v uv >/dev/null; then uv venv --python "$ver" "$dir"; else "python$ver" -m venv "$dir"; fi
  fi
  command -v uv >/dev/null && PIP="uv pip install --python $dir/bin/python" || PIP="$dir/bin/python -m pip install"
}
torch_install() {   # CUDA 13 wheels for Arm come from PyTorch's own index, not PyPI
  if [ -n "$TORCH_INDEX" ]; then $PIP "$@" --index-url "$TORCH_INDEX"; else $PIP "$@"; fi
}
freeze() { "envs/$1/bin/python" -m pip freeze > "envs/$1.freeze.txt" 2>/dev/null || uv pip freeze --python "envs/$1/bin/python" > "envs/$1.freeze.txt"; echo "environment envs/$1 ready; versions recorded in envs/$1.freeze.txt"; }

setup_pipeline() {
  venv pipeline; $PIP -e ".[test]"; freeze pipeline
  echo "activate with: source envs/pipeline/bin/activate"
}
setup_specialist() {
  venv specialist; torch_install torch torchvision; $PIP numpy pandas pillow pyyaml scipy; freeze specialist
}
setup_imajev() {
  [ -d ../imajev ] || git clone https://github.com/mohit67890/imajev ../imajev
  venv imajev; torch_install torch torchvision
  (cd ../imajev && $PIP -e ".[serve,torch]")
  (cd ../imajev && $ROOT/envs/imajev/bin/python scripts/download_model.py --model 4b && $ROOT/envs/imajev/bin/hf download mohit67890/imajev-4b --local-dir adapters/imajev-4b)
  freeze imajev
  echo "Do NOT pass --fast to the server until it has been checked on this machine: it compiles GPU kernels at start-up."
}
setup_neohorse() {
  venv neohorse; torch_install torch torchvision
  $PIP "transformers==5.17.0" pillow huggingface_hub
  envs/neohorse/bin/hf download TokenRhythm/NeoHorse-Jev-4B --local-dir models/NeoHorse-Jev-4B
  $PIP --no-deps models/NeoHorse-Jev-4B/dist/neohorse_decision-1.0.0-py3-none-any.whl
  freeze neohorse     # its card records torch 2.8.0 and triton 3.7.1; a CUDA 13 torch build is used here instead
}
setup_jev_omni() {
  venv jev_omni; torch_install "torch>=2.10" torchvision
  $PIP -r https://huggingface.co/akhilaaa3/Jev-Omni/resolve/main/requirements.txt huggingface_hub
  freeze jev_omni
}
setup_visual_jev() {
  [ -d ../Visual-Jev ] || git clone https://github.com/guanxuyu-sv/Visual-Jev.git ../Visual-Jev
  venv visual_jev; torch_install torch torchvision
  $PIP -r ../Visual-Jev/code/requirements.txt
  freeze visual_jev
}
setup_glance() {
  venv glance 3.11; torch_install torch torchvision
  $PIP glance-vlm
  freeze glance
}
setup_jev27b() {
  venv jev27b; torch_install torch torchvision
  # The model card asks for a September 2026 development build of vLLM; on CUDA 13 use vLLM's cu130 nightly wheels.
  $PIP vllm --pre --extra-index-url https://wheels.vllm.ai/nightly/cu130
  $PIP huggingface_hub
  envs/jev27b/bin/hf download autotrust/JEV-27B-VL --local-dir models/JEV-27B-VL
  freeze jev27b
}

case "${1:-}" in
  pipeline|specialist|imajev|neohorse|jev_omni|visual_jev|glance|jev27b) "setup_$1" ;;
  all) for m in pipeline specialist imajev neohorse jev_omni visual_jev glance jev27b; do "setup_$m" || echo "FAILED: $m (continuing)"; done ;;
  *) sed -n '2,12p' "$0"; exit 1 ;;
esac
