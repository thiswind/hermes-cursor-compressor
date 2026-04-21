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

# Install tiktoken dependency
echo "Installing tiktoken dependency..."
pip install tiktoken >/dev/null 2>&1 || pip3 install tiktoken >/dev/null 2>&1
echo "✓ tiktoken installed"

# Update config.yaml
echo "Updating config.yaml..."
CONFIG_FILE="$HERMES_DIR/config.yaml"

# Check if config.yaml exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: $CONFIG_FILE does not exist."
    echo "Please create the config file first."
    exit 1
fi

# Check if context section exists
if grep -q "^context:" "$CONFIG_FILE"; then
    # Check if engine is already set
    if grep -q "^context:\s*$" "$CONFIG_FILE" -A 1 | grep -q "engine:"; then
        # Update existing engine setting
        sed -i 's/^\s*engine:\s*.*/  engine: "cursor_style"/' "$CONFIG_FILE"
    else
        # Add engine to existing context section
        sed -i '/^context:/a \  engine: "cursor_style"' "$CONFIG_FILE"
    fi
else
    # Add context section
    echo -e "\ncontext:\n  engine: \"cursor_style\"" >> "$CONFIG_FILE"
fi
echo "✓ config.yaml updated"

# Restart Hermes Agent gateway
echo "Restarting Hermes Agent gateway..."
# Check if hermes gateway is running and restart it
if command -v hermes &> /dev/null; then
    hermes gateway restart >/dev/null 2>&1 || echo "Note: Could not restart gateway automatically. Please restart it manually."
elif [ -f "$HERMES_DIR/bin/hermes" ]; then
    "$HERMES_DIR/bin/hermes" gateway restart >/dev/null 2>&1 || echo "Note: Could not restart gateway automatically. Please restart it manually."
else
    echo "Note: Could not find hermes command. Please restart the gateway manually."
fi
echo ""
echo "✓ Installation complete!"
echo "Cursor-style context compression engine is now active."
