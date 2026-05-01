# Cursor-style Context Compression Engine for Hermes Agent

**[English](README.md)** | **[中文](README.zh-CN.md)** | **[العربية](README.ar.md)**

A drop-in plugin that replaces Hermes Agent's built-in ContextCompressor with a Cursor-inspired approach.

## Problem Solved

Hermes Agent's built-in context compressor has a critical bug: it permanently anchors the first 3 messages (system prompt + initial user/assistant conversation). When a project progresses and context compression triggers, the model always sees the original request at the top of the context window, causing **infinite topic drift back to the origin**. Long projects can never be completed.

## How It Works

Inspired by Cursor IDE's context management strategy:

1. **No initial conversation anchoring** — Only the system prompt is protected. All user/assistant messages are compressed equally. This is the core fix.

2. **Minimal summarization prompt** — Uses a simple "Please summarize the conversation" approach instead of Hermes' 11-part structured template that can be misinterpreted as instructions by the model.

3. **Two-tier memory** — Saves complete conversation history to a JSONL file before compression. The summary includes the file path so the agent can search to recover lost details.

4. **Precise token counting** — Uses `tiktoken` (cl100k_base) for accurate multi-language token estimation, fixing the severe undercounting issue for Chinese/CJK languages with `len(text)//4`.

5. **Tool output pruning** — Old tool outputs are replaced with one-line summaries before LLM summarization, reducing noise and cost.

## Prerequisites

- Python 3.9+
- Hermes Agent installed (default location: `~/.hermes`)
- `tiktoken` (required for precise token counting):

  ```bash
  pip install tiktoken
  ```

## Installation

### Automatic Installation (Recommended)

```bash
# Run the install script directly
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.py)

# Or if you have already cloned the repository
python install.py
```

The script will:
1. Install plugin files to the correct location
2. Install the tiktoken dependency
3. Automatically update your `config.yaml`
4. Restart the Hermes Agent gateway

### Manual Installation

```bash
# 1. Clone the repository
git clone https://github.com/thiswind/hermes-cursor-compressor.git

# 2. Copy plugin files to the CORRECT location (IMPORTANT: hermes-agent subdirectory)
cp -r hermes-cursor-compressor/cursor_style/ ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/

# 3. Install tiktoken
pip install tiktoken

# 4. Update ~/.hermes/config.yaml with:
#    context:
#      engine: "cursor_style"

# 5. Restart Hermes Agent
hermes gateway restart
```

### Verify Installation

After installation, verify the engine loads correctly:

```bash
cd ~/.hermes/hermes-agent
python -c "
from plugins.context_engine import discover_context_engines, load_context_engine
print('Available engines:')
for name, desc, avail in discover_context_engines():
    print(f'  - {name}: {\"✅ AVAILABLE\" if avail else \"❌ UNAVAILABLE\"}')

engine = load_context_engine('cursor_style')
if engine:
    print('\\n✅ cursor_style engine loaded successfully!')
else:
    print('\\n❌ cursor_style engine failed to load')
"
```

You should see:
```
Available engines:
  - cursor_style: ✅ AVAILABLE

✅ cursor_style engine loaded successfully!
```

## Uninstallation

### Automatic Uninstallation (Recommended)

```bash
# Run the uninstall script directly
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.py)

# Or if you have already cloned the repository
python uninstall.py
```

### Manual Uninstallation

```bash
rm -rf ~/.hermes/hermes-agent/plugins/context_engine/cursor_style
# Then remove "context.engine: cursor_style" from ~/.hermes/config.yaml
# Restart Hermes Agent
```

## Optional: Custom Summary Model

The engine defaults to Hermes Agent's auxiliary compression model (e.g., Gemini Flash). To override, use the `auxiliary.compression` config:

```yaml
auxiliary:
  compression:
    model: "gemini-2.5-flash"
    provider: "auto"
    timeout: 30
```

## Project Structure

```
cursor_style/
├── __init__.py          # Package initialization + register function export
├── plugin.yaml          # Plugin metadata
├── engine.py            # CursorStyleEngine (ContextEngine ABC implementation)
├── token_counter.py     # Precise multi-language token counting (tiktoken)
├── summarizer.py        # Cursor-style minimal summarization
├── history_file.py      # Two-tier memory (JSONL history files)
└── tests/
    ├── conftest.py      # Shared fixtures
    ├── stubs/           # ContextEngine ABC stubs for unit testing
    ├── unit/            # Unit tests (no Hermes Agent required)
    └── integration/     # Integration tests (requires Hermes Agent)
```

## Running Tests

```bash
# Unit tests only (no Hermes Agent required)
cd hermes-cursor-compressor
PYTHONPATH=. python -m pytest cursor_style/tests/unit/ -v

# All tests (including integration tests, requires Hermes Agent)
PYTHONPATH=.:/path/to/hermes-agent python -m pytest cursor_style/tests/ -v
```

## Comparison with Hermes Built-in Compressor

| Feature | Hermes Built-in | Cursor Style |
|---------|----------------|--------------|
| Protected messages | 3 (system + initial conversation) | 1 (system only) |
| Topic drift bug | Yes — initial request always visible | Fixed — all messages compressed equally |
| Summary prompt | 11-part structured template | Minimal (~1000 tokens output) |
| Token estimation | `len(text)//4` (inaccurate for CJK) | tiktoken cl100k_base |
| History file | None | Yes (JSONL, searchable) |
| Summary output | ~5000 tokens | ~1000 tokens |
| Trigger threshold | 50% of context | 50% of context |

## Troubleshooting

### Engine Fails to Load

If the engine fails to load after installation:

1. Confirm files are in the correct location:
   ```bash
   ls -la ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/
   ```

2. Confirm `__init__.py` exports the `register` function

3. Restart the Hermes Gateway:
   ```bash
   hermes gateway restart
   ```

4. Check the logs:
   ```bash
   hermes logs --level ERROR
   ```

### Configuration Issues

If you see duplicate `engine` keys in your `config.yaml`:

```yaml
# ❌ Wrong (duplicate keys)
context:
  engine: "cursor_style"
  engine: compressor

# ✅ Correct
context:
  engine: "cursor_style"
```

The latest `install.py` fixes this issue.

## License

MIT
