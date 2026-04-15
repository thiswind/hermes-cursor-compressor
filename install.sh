#!/usr/bin/env bash
# install.sh — Install cursor_style plugin into Hermes Agent
#
# Usage:
#   bash install.sh                          # default: ~/.hermes
#   bash install.sh /path/to/hermes-agent    # custom path
#
# This script clones the repo to a temp dir, copies plugin files,
# then cleans up.

set -euo pipefail

HERMES_DIR="${1:-$HOME/.hermes}"
REPO_URL="https://github.com/thiswind/hermes-cursor-compressor.git"

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

# Clone to temp dir
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Cloning repository..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR/hermes-cursor-compressor" 2>/dev/null

SRC_DIR="$TMP_DIR/hermes-cursor-compressor"
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Failed to clone repository."
    exit 1
fi

# Remove existing plugin
if [ -d "$PLUGIN_DIR" ]; then
    echo "Removing existing cursor_style plugin..."
    rm -rf "$PLUGIN_DIR"
fi

mkdir -p "$PLUGIN_DIR"

# Copy plugin files
for f in "${PLUGIN_FILES[@]}"; do
    cp "$SRC_DIR/$f" "$PLUGIN_DIR/"
done

echo "✓ cursor_style plugin installed to $PLUGIN_DIR"
echo ""
echo "Next steps:"
echo "  1. Make sure tiktoken is installed: pip install tiktoken"
echo "  2. Add to your config.yaml ($HERMES_DIR/config.yaml):"
echo ""
echo "     context:"
echo "       engine: \"cursor_style\""
echo ""
echo "  3. Restart Hermes Agent"
