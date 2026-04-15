#!/usr/bin/env bash
# install.sh — Install cursor_style plugin into Hermes Agent
#
# Usage:
#   bash install.sh                          # default: ~/.hermes
#   bash install.sh /path/to/hermes-agent    # custom path
#   bash <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.sh) [PATH]

set -euo pipefail

HERMES_DIR="${1:-$HOME/.hermes}"
REPO="thiswind/hermes-cursor-compressor"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/$REPO/$BRANCH"

PLUGIN_FILES=(
    "cursor_style/__init__.py"
    "cursor_style/plugin.yaml"
    "cursor_style/engine.py"
    "cursor_style/token_counter.py"
    "cursor_style/summarizer.py"
    "cursor_style/history_file.py"
)

if [ ! -d "$HERMES_DIR" ]; then
    echo "Error: $HERMES_DIR does not exist."
    echo "Usage: bash install.sh [PATH_TO_HERMES]"
    echo "  Default path: ~/.hermes"
    exit 1
fi

PLUGIN_DIR="$HERMES_DIR/plugins/context_engine/cursor_style"

if [ -d "$PLUGIN_DIR" ]; then
    echo "Removing existing cursor_style plugin..."
    rm -rf "$PLUGIN_DIR"
fi

mkdir -p "$PLUGIN_DIR"

echo "Downloading plugin files from GitHub..."
for f in "${PLUGIN_FILES[@]}"; do
    curl -fsSL "$BASE_URL/$f" -o "$PLUGIN_DIR/$(basename "$f")"
done

echo "✓ cursor_style plugin installed to $PLUGIN_DIR"
echo ""
echo "Next steps:"
echo "  1. Make sure tiktoken is installed: pip install tiktoken"
echo "  2. Add to your cli-config.yaml ($HERMES_DIR/cli-config.yaml):"
echo ""
echo "     context:"
echo "       engine: \"cursor_style\""
echo ""
echo "  3. Restart Hermes Agent"
