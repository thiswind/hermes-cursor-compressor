#!/usr/bin/env python3
"""
uninstall.py — Remove cursor_style plugin from Hermes Agent

Usage:
    python uninstall.py                          # default: ~/.hermes
    python uninstall.py /path/to/hermes-agent    # custom path

This script removes the plugin files, updates config, and restarts Hermes Agent.
"""

import os
import sys
import shutil
import subprocess
import re


def main():
    # Get Hermes directory
    if len(sys.argv) > 1:
        hermes_dir = sys.argv[1]
    else:
        hermes_dir = os.path.expanduser("~/.hermes")

    plugin_dir = os.path.join(hermes_dir, "plugins", "context_engine", "cursor_style")

    # Check if plugin is installed
    if not os.path.exists(plugin_dir):
        print(f"cursor_style plugin is not installed at {plugin_dir}")
        sys.exit(0)

    # Remove plugin files
    shutil.rmtree(plugin_dir)
    print(f"✓ cursor_style plugin removed from {plugin_dir}")
    print()

    # Update config.yaml
    print("Updating config.yaml...")
    config_file = os.path.join(hermes_dir, "config.yaml")

    # Check if config.yaml exists
    if os.path.exists(config_file):
        # Read config file
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = f.read()

        # Check if context section exists
        if re.search(r'^context:', config_content, re.MULTILINE):
            # Remove engine line
            new_config = re.sub(r'^\s*engine:\s*"cursor_style"\s*$\n?', '', config_content, flags=re.MULTILINE)
            
            # Remove context section if it's empty
            if re.search(r'^context:\s*$\n\s*$', new_config, re.MULTILINE):
                new_config = re.sub(r'^context:\s*$\n\s*$\n?', '', new_config, flags=re.MULTILINE)
            elif re.search(r'^context:\s*$', new_config, re.MULTILINE):
                new_config = re.sub(r'^context:\s*$\n?', '', new_config, flags=re.MULTILINE)

            # Write back to config file
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_config)

            print("✓ config.yaml updated")
        else:
            print("Note: context section not found in config.yaml")
    else:
        print(f"Note: {config_file} does not exist")

    # Restart Hermes Agent gateway
    print("Restarting Hermes Agent gateway...")
    # Check if hermes gateway is running and restart it
    hermes_command = None
    if shutil.which("hermes"):
        hermes_command = "hermes"
    elif os.path.exists(os.path.join(hermes_dir, "bin", "hermes")):
        hermes_command = os.path.join(hermes_dir, "bin", "hermes")

    if hermes_command:
        try:
            subprocess.run([hermes_command, "gateway", "restart"], capture_output=True)
            print("✓ Gateway restarted")
        except subprocess.CalledProcessError:
            print("Note: Could not restart gateway automatically. Please restart it manually.")
    else:
        print("Note: Could not find hermes command. Please restart the gateway manually.")

    print()
    print("✓ Uninstallation complete!")
    print("Hermes Agent will now use the built-in context compressor.")


if __name__ == "__main__":
    main()
