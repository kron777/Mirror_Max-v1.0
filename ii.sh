#!/usr/bin/env bash
#
# Updated ii.sh — MirrorMax full setup helper (free OpenRouter focus)
# Run from anywhere — it will cd to ~/Desktop/MirrorMax

set -euo pipefail

PROJECT="$HOME/Desktop/MirrorMax"
VENV=".venv"

echo "┌────────────────────────────────────────────────────────────┐"
echo "│ Mirror Max FULL setup helper (updated)                     │"
echo "│ Target project: $PROJECT                                   │"
echo "└────────────────────────────────────────────────────────────┘"
echo

# Create project if missing
mkdir -p "$PROJECT"
cd "$PROJECT" || { echo "Cannot cd to $PROJECT"; exit 1; }

# Create folders & files
echo "Creating structure…"
mkdir -p backend/{core,api} frontend/static logs tests

touch backend/main.py backend/requirements.txt
touch backend/core/{context.py,protocol.py,analyzer.py}
touch backend/api/{deepseek_client.py,grok_client.py}
touch frontend/app.py README.md test_dotenv.py

# .gitignore
cat > .gitignore << 'EOF'
.venv/
__pycache__/
*.pyc
.env
logs/*
EOF

# Virtual env
if [[ ! -d "$VENV" ]]; then
    echo "Creating venv…"
    python3 -m venv "$VENV"
fi

# Activate & install
echo "Activating venv + installing deps…"
source "$VENV/bin/activate"

pip install --upgrade pip
pip install httpx python-dotenv nicegui pydantic

pip freeze > backend/requirements.txt

# Create .env template if missing
if [[ ! -f .env ]]; then
    cat > .env << 'EOF'
# Paste your OpenRouter key here (free tier for DeepSeek)
OPENROUTER_API_KEY=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

# Optional - paid keys if you want to use them later
# GROK_API_KEY=xai-...
# DEEPSEEK_API_KEY=sk-...
EOF
    echo "Created .env template — ready for your key"
fi

# Create quick test script
cat > test_dotenv.py << 'EOF'
import os
from dotenv import load_dotenv, find_dotenv

print("Current working directory:", os.getcwd())
print("Found .env at:", find_dotenv())

load_dotenv(override=True)

print("OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY"))
print("GROK_API_KEY:", os.getenv("GROK_API_KEY"))
print("DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY"))
EOF

echo
echo "Installed packages:"
pip list | grep -E "httpx|dotenv|nicegui|pydantic"
echo

echo "============================================================="
echo "               Almost done — final manual steps"
echo "============================================================="
cat << 'EOF'

1. Open .env and confirm/add your OpenRouter key if needed:

   nano .env

   It should contain:
   OPENROUTER_API_KEY=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

2. Update backend/api/deepseek_client.py to use OpenRouter free tier
   (replace whole file with the version I gave earlier — the one with openrouter.ai endpoint)

3. Test the key loads:

   python test_dotenv.py

   Should show your key (not None)

4. Launch the debate (when ready):

   python backend/main.py

EOF

echo "Script finished."
echo "You can now edit .env (if needed) and update deepseek_client.py"
echo "Then run: python test_dotenv.py"
echo "And finally: python backend/main.py"
echo
