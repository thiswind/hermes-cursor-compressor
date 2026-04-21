#!/usr/bin/env bash
# uninstall.sh — Remove cursor_style plugin from Hermes Agent
#
# Usage:
#   bash uninstall.sh                          # default: ~/.hermes
#   bash uninstall.sh /path/to/hermes-agent    # custom path
#   bash <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.sh) [PATH]

set -euo pipefail

HERMES_DIR="${1:-$HOME/.hermes}"

PLUGIN_DIR="$HERMES_DIR/plugins/context_engine/cursor_style"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "cursor_style plugin is not installed at $PLUGIN_DIR"
    exit 0
fi

rm -rf "$PLUGIN_DIR"
echo "✓ cursor_style plugin removed from $PLUGIN_DIR"
echo ""

# Update config.yaml
echo "Updating config.yaml..."
CONFIG_FILE="$HERMES_DIR/config.yaml"

# Check if config.yaml exists
if [ -f "$CONFIG_FILE" ]; then
    # Remove engine setting
    if grep -q "^context:" "$CONFIG_FILE"; then
        # Remove engine line
        sed -i '/^\s*engine:\s*"cursor_style"/d' "$CONFIG_FILE"
        # Remove context section if it's empty
        if grep -q "^context:" "$CONFIG_FILE" -A 1 | grep -E "^\s*$" -A 1 | grep -v "^context:" | grep -q "^\s*$"; then
            sed -i '/^context:/d' "$CONFIG_FILE"
        fi
        echo "✓ config.yaml updated"
    else
        echo "Note: context section not found in config.yaml"
    fi
else
    echo "Note: $CONFIG_FILE does not exist"
fi

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
echo "✓ Uninstallation complete!"
echo "Hermes Agent will now use the built-in context compressor."
