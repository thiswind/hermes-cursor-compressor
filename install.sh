#!/usr/bin/env bash
# install.sh — Install cursor_style plugin into Hermes Agent
#
# Usage:
#   bash install.sh                          # default: ~/.hermes
#   bash install.sh /path/to/hermes-agent    # custom path
#   bash <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.sh) [PATH]

set -euo pipefail

HERMES_DIR="${1:-$HOME/.hermes}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

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

# Copy plugin files (exclude tests and non-plugin files)
cp "$SCRIPT_DIR/cursor_style/__init__.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/cursor_style/plugin.yaml" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/cursor_style/engine.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/cursor_style/token_counter.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/cursor_style/summarizer.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/cursor_style/history_file.py" "$PLUGIN_DIR/"

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
