# Cursor-Style Context Compression Engine for Hermes Agent

**[English](README.md)** | **[中文](README.zh-CN.md)** | **[العربية](README.ar.md)**

A drop-in plugin that replaces Hermes Agent's built-in ContextCompressor
with a Cursor IDE-inspired approach.

## Problem It Solves

Hermes Agent's built-in context compressor has a critical bug: it permanently
anchors the initial 3 messages (system prompt + first user/assistant exchange).
When compression fires after the project has progressed significantly, the
model sees the original request at the top of context and **drifts back to the
initial topic**, making long projects impossible to complete.

## How It Works

Inspired by Cursor IDE's context management:

1. **No initial conversation anchoring** — Only the system prompt is protected.
   All user/assistant messages are compressed equally. This is the key fix.

2. **Minimal summarization prompt** — Uses Cursor's approach: a simple
   "Please summarize the conversation" instead of Hermes' 11-section
   structured template that gets misinterpreted as instructions.

3. **Two-tier memory** — Before compression, the full conversation is saved
   to a JSONL file. The summary includes a reference to this file so the
   agent can grep/search for lost details.

4. **Precise token counting** — Uses `tiktoken` (cl100k_base) for accurate
   multi-language token estimation. Fixes the `len(text)//4` bug that
   severely underestimates Chinese/CJK tokens.

5. **Tool output pruning** — Old tool outputs are replaced with 1-line
   summaries before LLM summarization, reducing noise and cost.

## Prerequisites

- Python 3.9+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent/) installed
  (default location: `~/.hermes`)
- `tiktoken` (required for precise token counting):

```bash
pip install tiktoken
```

## Installation

### Automatic Installation (Recommended)

```bash
# Run the install script
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.py)

# Or if you have the repo cloned locally
python install.py
```

The script will:
1. Install the plugin files
2. Install tiktoken dependency
3. Update your config.yaml automatically
4. Restart Hermes Agent gateway

### Manual Installation

```bash
# 1. Install plugin
git clone https://github.com/thiswind/hermes-cursor-compressor.git
cp -r hermes-cursor-compressor/cursor_style/ ~/.hermes/plugins/context_engine/cursor_style/

# 2. Install tiktoken
pip install tiktoken

# 3. Enable in ~/.hermes/config.yaml — add these 2 lines:
#    context:
#      engine: "cursor_style"

# 4. Restart Hermes Agent
```

## Uninstall

### Automatic Uninstallation (Recommended)

```bash
# Run the uninstall script
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.py)

# Or if you have the repo cloned locally
python uninstall.py
```

The script will:
1. Remove the plugin files
2. Update your config.yaml automatically
3. Restart Hermes Agent gateway

### Manual Uninstallation

```bash
rm -rf ~/.hermes/plugins/context_engine/cursor_style
# Then remove "context.engine: cursor_style" from ~/.hermes/config.yaml
# Restart Hermes Agent
```

### Optional: Summary Model Override

By default, the engine uses Hermes Agent's auxiliary compression model
(e.g. Gemini Flash). To override, configure via Hermes' `auxiliary.compression`:

```yaml
auxiliary:
  compression:
    model: "gemini-2.5-flash"
    provider: "auto"
    timeout: 30
```

## Architecture

```
cursor_style/
├── __init__.py          # Package init, version
├── plugin.yaml          # Plugin metadata
├── engine.py            # CursorStyleEngine (ContextEngine ABC implementation)
├── token_counter.py     # Precise multi-language token counting (tiktoken)
├── summarizer.py        # Cursor-style minimal summarization
├── history_file.py      # Two-tier memory (JSONL history files)
└── tests/
    ├── conftest.py      # Shared fixtures
    ├── stubs/           # ContextEngine ABC stub for unit tests
    ├── unit/            # Unit tests (no Hermes dependency)
    └── integration/     # Integration tests (require Hermes Agent)
```

## Running Tests

```bash
# Unit tests only (no Hermes Agent needed)
cd hermes-cursor-compressor
PYTHONPATH=. python -m pytest cursor_style/tests/unit/ -v

# All tests including integration (needs Hermes Agent)
PYTHONPATH=.:/path/to/hermes-agent python -m pytest cursor_style/tests/ -v
```

## Comparison with Hermes' Built-in Compressor

| Feature | Hermes Built-in | Cursor-Style |
|---------|----------------|--------------|
| Protected messages | 3 (system + initial exchange) | 1 (system only) |
| Topic drift bug | Yes — initial request always visible | Fixed — all messages compressed equally |
| Summary prompt | 11-section structured template | Minimal (~1000 tokens) |
| Token estimation | `len(text)//4` (bad for CJK) | tiktoken cl100k_base |
| History file | No | Yes (JSONL, searchable) |
| Summary output | ~5000 tokens | ~1000 tokens |
| Trigger threshold | 50% of context | 50% of context |

## License

MIT
