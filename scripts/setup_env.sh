#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
REQUIREMENTS_FILE="$ROOT_DIR/requirements.txt"

if ! command -v python3.13 >/dev/null 2>&1; then
  echo "Python 3.13 is required but was not found in PATH." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment with python3.13..."
  python3.13 -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at $VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install -U -r "$REQUIREMENTS_FILE"

ENV_SAMPLE=""
if [ -f "$ROOT_DIR/.env.example" ]; then
  ENV_SAMPLE="$ROOT_DIR/.env.example"
elif [ -f "$ROOT_DIR/.env_example" ]; then
  ENV_SAMPLE="$ROOT_DIR/.env_example"
fi

if [ -z "$ENV_SAMPLE" ]; then
  echo "Could not find .env.example (or .env_example) to copy from." >&2
  exit 1
fi

if [ ! -f "$ROOT_DIR/.env" ]; then
  cp "$ENV_SAMPLE" "$ROOT_DIR/.env"
  echo "Copied $(basename "$ENV_SAMPLE") to .env"
else
  echo ".env already exists, leaving it unchanged"
fi

python -m kratos.initmem

echo
echo "All set! Run 'langgraph dev --allow-blocking' to start the dev server when you're ready."
