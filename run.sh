#!/usr/bin/env bash
set -e

# ───────────────────────────────────────────────────────────────────────
# Meta Personal Data Collector — Launcher
# Double-click this file. That's it.
# ───────────────────────────────────────────────────────────────────────

cd "$(dirname "$0")"

echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║    Meta Personal Data Collector                     ║"
echo "  ║    One-click launcher                               ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Install uv if missing ────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "📦 Installing uv (package manager)…"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # reload PATH so uv is found
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
    if ! command -v uv &>/dev/null; then
        echo ""
        echo "❌ Failed to install uv automatically."
        echo "   Please install it manually:  https://docs.astral.sh/uv/#installation"
        read -rp "Press Enter to close…"
        exit 1
    fi
fi

# ── 2. Install dependencies ─────────────────────────────────────────────
echo "📦 Installing dependencies…"
uv sync 2>&1 | tail -n 1

echo ""

# ── 3. Launch the app ──────────────────────────────────────────────────
echo "🚀 Opening your browser…"
uv run streamlit run src/fb_image_extractor/app.py &
STREAMLIT_PID=$!

# Wait for server to start, then open browser
sleep 4
xdg-open http://localhost:8501 2>/dev/null || \
    open http://localhost:8501 2>/dev/null || \
    echo "   Open http://localhost:8501 in your browser."

echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║    App is running at http://localhost:8501           ║"
echo "  ║    Close this terminal to stop the app.              ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""

# Wait for the background process
wait $STREAMLIT_PID
