# Cursor-Style Context Compression Engine for Hermes Agent

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

### Option A: One-click install (recommended)

```bash
# Download and run the install script
curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.sh -o /tmp/install.sh
bash /tmp/install.sh                    # default: ~/.hermes
# bash /tmp/install.sh /custom/path     # custom Hermes path
rm /tmp/install.sh
```

### Option B: Manual install

```bash
# 1. Clone this repository
git clone https://github.com/thiswind/hermes-cursor-compressor.git

# 2. Copy the plugin to Hermes Agent's plugin directory
#    (default: ~/.hermes/plugins/context_engine/cursor_style/)
cp -r hermes-cursor-compressor/cursor_style/ \
      ~/.hermes/plugins/context_engine/cursor_style/

# 3. Enable in Hermes Agent config (see Configuration below)
```

## Uninstall

```bash
# Default: removes from ~/.hermes
bash <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.sh)

# Or specify a custom path
bash <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.sh) /custom/path/to/hermes-agent
```

Then remove or change `context.engine` in your `cli-config.yaml`. Hermes Agent
will fall back to the built-in compressor.

## Configuration

Add to your `~/.hermes/config.yaml` (this is the single config file shared
by all channels — CLI, Feishu, Discord, Telegram, etc.):

```yaml
context:
  engine: "cursor_style"
```

No other configuration is required. The engine inherits model/provider
settings from Hermes Agent's main configuration.

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
