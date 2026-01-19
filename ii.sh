#!/usr/bin/env bash
#
# ii.sh — Mirror Max SAFE setup helper (censored keys, no secrets in git)
# Run from ~/Desktop — creates everything safely

set -euo pipefail

PROJECT="$HOME/Desktop/MirrorMax"
VENV=".venv"

echo "┌────────────────────────────────────────────────────────────┐"
echo "│ Mirror Max SAFE setup helper (censored keys)               │"
echo "│ Target: $PROJECT                                           │"
echo "└────────────────────────────────────────────────────────────┘"
echo

# Create project
mkdir -p "$PROJECT"
cd "$PROJECT" || exit 1

# Structure
echo "Creating folders & files..."
mkdir -p backend/{core,api} frontend/static logs tests

touch backend/main.py backend/requirements.txt
touch backend/core/{context.py,protocol.py,analyzer.py}
touch backend/api/{deepseek_client.py,grok_client.py}
touch frontend/app.py README.md LICENSE test_dotenv.py

# .gitignore - NEVER commit secrets
cat > .gitignore << 'EOF'
.venv/
__pycache__/
*.pyc
.env
logs/*
*.key
*.secret
EOF

# Virtual env
if [[ ! -d "$VENV" ]]; then
    echo "Creating venv..."
    python3 -m venv "$VENV"
fi

# Activate & install
echo "Activating venv + installing deps..."
source "$VENV/bin/activate"

pip install --upgrade pip
pip install httpx python-dotenv nicegui pydantic

pip freeze > backend/requirements.txt

# Safe env.example (censored - no real keys ever in git)
cat > .env.example << 'EOF'
# ==================================================
# Mirror Max - .env.example (copy to .env and edit)
# NEVER commit .env to git!
# ==================================================

OPENROUTER_API_KEY=sk-or-v1-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# DEEPSEEK_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Add your real keys here - do NOT use the example ones!
EOF

# Quick test script
cat > test_dotenv.py << 'EOF'
import os
from dotenv import load_dotenv, find_dotenv

print("CWD:", os.getcwd())
print("Found .env:", find_dotenv())

load_dotenv(override=True)

print("OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY") or "Not found")
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY") or "Not found")
print("DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY") or "Not found")
EOF

# Starter README
cat > README.md << 'EOF'
# Mirror Max v1.0

Cognitive Differential Engine — AI debate simulator to expose reasoning differences and converge on solutions.

## Quick Start

1. Clone repo
2. `cp .env.example .env`
3. Edit `.env` — add your real OpenRouter / Groq keys
4. `python backend/main.py`
5. Enter topic → watch debate → check ~/Desktop/solution.txt

## License

MIT (see LICENSE file)

Built in Cape Town, 2026. 🪞
EOF

# MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Jon (@ObiterThe)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

echo
echo "Installed:"
pip list | grep -E "httpx|dotenv|nicegui|pydantic"
echo

echo "============================================================="
echo "               FINAL STEPS (manual, safe)                   "
echo "============================================================="
cat << 'EOF'

1. Add your REAL keys to .env (NEVER commit this file!)

   nano .env

   Example:
   OPENROUTER_API_KEY=sk-or-v1-your-real-key-here...
   GROQ_API_KEY=gsk_your-groq-key-if-you-have...

2. Test keys load:

   python test_dotenv.py

   Should show your real keys (not "Not found")

3. Run the debate:

   python backend/main.py

   Enter topic → get full debate → solution.txt on Desktop

4. Push to GitHub (SSH already set up):

   git add .
   git commit -m "Initial safe commit - keys censored"
   git push origin main

EOF

echo "Setup finished safely — no secrets in git."
echo "Now add your real keys to .env and run the engine!"
echo
