# Cursor-style Context Compression Engine for Hermes Agent

**[English](README.md)** | **[中文](README.zh-CN.md)** | **[العربية](README.ar.md)**

---

Ever watched Hermes Agent slowly drift back to the very first request, no matter how far the project has progressed? That’s not random — it’s a bug in the built-in context compressor.

**hermes-cursor-compressor** fixes it. It replaces Hermes Agent’s built-in compressor with a Cursor-inspired engine that treats all conversation history equally, counts tokens accurately for CJK text, and keeps a searchable history file before every compression.

Drop-in replacement. One command to install. No changes to your existing workflows.

---

## Quick Start

```bash
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.py)
```

That’s it. The script installs the plugin, adds `tiktoken`, updates your `config.yaml`, and restarts the Hermes gateway.

---

## The bug this fixes

Hermes Agent’s built-in compressor permanently anchors the **first 3 messages** (system prompt + initial user/assistant exchange). When compression triggers mid-project, the model always sees the original request at the top of the context window — pulling it back toward where you started, not where you are now.

**This compressor protects only the system prompt.** All user/assistant messages are compressed equally. The original request disappears into the summary just like everything else.

---

## What changes

| Feature | Hermes Built-in | Cursor Style (this plugin) |
|---------|----------------|---------------------------|
| Protected messages | 3 (system + initial conversation) | 1 (system prompt only) |
| Topic drift bug | ✗ Always drifts back to origin | ✓ Fixed |
| Summary prompt | 11-part structured template (~5000 tokens) | Minimal prompt (~1000 tokens) |
| Token counting | `len(text)//4` — undercounts CJK severely | `tiktoken` cl100k_base — accurate |
| Conversation history | None saved | JSONL file, searchable |
| Trigger threshold | 50% of context | 50% of context |

---

## Prerequisites

- Python 3.9+
- Hermes Agent installed (default: `~/.hermes`)
- `tiktoken` (installed automatically by the install script)

---

## Installation

### Automatic (recommended)

```bash
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.py)
```

The script will:
1. Install plugin files to the correct location
2. Install `tiktoken`
3. Update `config.yaml` automatically
4. Restart the Hermes Agent gateway

### Manual

```bash
git clone https://github.com/thiswind/hermes-cursor-compressor.git

cp -r hermes-cursor-compressor/cursor_style/ \
      ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/

pip install tiktoken
```

Then add to `~/.hermes/config.yaml`:
```yaml
context:
  engine: "cursor_style"
```

Restart: `hermes gateway restart`

### Verify

```bash
cd ~/.hermes/hermes-agent
python -c "
from plugins.context_engine import discover_context_engines, load_context_engine
for name, desc, avail in discover_context_engines():
    print(f'  - {name}: {\"\u2705\" if avail else \"\u274c\"}')
engine = load_context_engine('cursor_style')
print('\u2705 cursor_style loaded!' if engine else '\u274c failed to load')
"
```

---

## Uninstall

```bash
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.py)
```

---

## Optional: custom compression model

```yaml
auxiliary:
  compression:
    model: "gemini-2.5-flash"
    provider: "auto"
    timeout: 30
```

---

## Project structure

```
cursor_style/
├── __init__.py       # Package init + register export
├── plugin.yaml       # Plugin metadata
├── engine.py         # CursorStyleEngine (ContextEngine ABC)
├── token_counter.py  # Precise multi-language token counting (tiktoken)
├── summarizer.py     # Cursor-style minimal summarization
├── history_file.py   # Two-tier memory (JSONL history files)
└── tests/
    ├── conftest.py
    ├── stubs/        # ContextEngine stubs for unit testing
    ├── unit/         # Unit tests (no Hermes Agent required)
    └── integration/  # Integration tests (requires Hermes Agent)
```

---

## Running tests

```bash
# Unit tests only
cd hermes-cursor-compressor
PYTHONPATH=. python -m pytest cursor_style/tests/unit/ -v

# All tests (requires Hermes Agent)
PYTHONPATH=.:/path/to/hermes-agent python -m pytest cursor_style/tests/ -v
```

---

## Troubleshooting

**Engine fails to load after install:**
```bash
ls -la ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/
hermes gateway restart
hermes logs --level ERROR
```

**Duplicate `engine` keys in config.yaml:**
```yaml
# ✅ Correct
context:
  engine: "cursor_style"
```

---

## License

MIT
