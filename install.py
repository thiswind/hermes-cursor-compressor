#!/usr/bin/env python3
"""
install.py — Install cursor_style plugin into Hermes Agent

Usage:
    python install.py                          # default: ~/.hermes
    python install.py /path/to/hermes-agent    # custom path

This script clones the repo to a temp dir, copies plugin files,
installs dependencies, updates config, and restarts Hermes Agent.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import re
from urllib.request import urlretrieve


def main():
    # Get Hermes directory
    if len(sys.argv) > 1:
        hermes_dir = sys.argv[1]
    else:
        hermes_dir = os.path.expanduser("~/.hermes")

    repo_url = "https://github.com/thiswind/hermes-cursor-compressor.git"
    plugin_files = [
        "cursor_style/__init__.py",
        "cursor_style/plugin.yaml",
        "cursor_style/engine.py",
        "cursor_style/token_counter.py",
        "cursor_style/summarizer.py",
        "cursor_style/history_file.py"
    ]

    # Check if Hermes directory exists
    if not os.path.exists(hermes_dir):
        print(f"Error: {hermes_dir} does not exist.")
        print("Usage: python install.py [PATH_TO_HERMES]")
        print("  Default path: ~/.hermes")
        sys.exit(1)

    plugin_dir = os.path.join(hermes_dir, "plugins", "context_engine", "cursor_style")

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        print("Cloning repository...")
        # Clone repository
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, os.path.join(tmp_dir, "hermes-cursor-compressor")],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            print("Error: Failed to clone repository.")
            sys.exit(1)

        src_dir = os.path.join(tmp_dir, "hermes-cursor-compressor")
        if not os.path.exists(src_dir):
            print("Error: Failed to clone repository.")
            sys.exit(1)

        # Remove existing plugin
        if os.path.exists(plugin_dir):
            print("Removing existing cursor_style plugin...")
            shutil.rmtree(plugin_dir)

        # Create plugin directory
        os.makedirs(plugin_dir, exist_ok=True)

        # Copy plugin files
        for f in plugin_files:
            src_file = os.path.join(src_dir, f)
            dest_file = os.path.join(plugin_dir, os.path.basename(f))
            shutil.copy2(src_file, dest_file)

    print(f"✓ cursor_style plugin installed to {plugin_dir}")
    print()

    # Install tiktoken dependency
    print("Installing tiktoken dependency...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "tiktoken"], check=True, capture_output=True)
        print("✓ tiktoken installed")
    except subprocess.CalledProcessError:
        print("Note: Failed to install tiktoken. Please install it manually with 'pip install tiktoken'")

    # Update config.yaml
    print("Updating config.yaml...")
    config_file = os.path.join(hermes_dir, "config.yaml")

    # Check if config.yaml exists
    if not os.path.exists(config_file):
        print(f"Error: {config_file} does not exist.")
        print("Please create the config file first.")
        sys.exit(1)

    # Read config file
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()

    # Check if context section exists
    if re.search(r'^context:', config_content, re.MULTILINE):
        # Check if engine is already set
        if re.search(r'^context:\s*$[^\n]*engine:', config_content, re.MULTILINE | re.DOTALL):
            # Update existing engine setting
            new_config = re.sub(r'(^\s*engine:\s*).*', r'\1"cursor_style"', config_content, flags=re.MULTILINE)
        else:
            # Add engine to existing context section
            new_config = re.sub(r'^context:', r'context:\n  engine: "cursor_style"', config_content, flags=re.MULTILINE)
    else:
        # Add context section
        new_config = config_content + '\n\ncontext:\n  engine: "cursor_style"'

    # Write back to config file
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_config)

    print("✓ config.yaml updated")

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
    print("✓ Installation complete!")
    print("Cursor-style context compression engine is now active.")


if __name__ == "__main__":
    main()
