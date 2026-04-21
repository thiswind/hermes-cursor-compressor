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
echo "Note: Remember to update your config.yaml ($HERMES_DIR/config.yaml):"
echo "  - Remove or change: context.engine: \"cursor_style\""
echo "  - Hermes Agent will fall back to the built-in compressor"
