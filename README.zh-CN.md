# Hermes Agent 的 Cursor 风格上下文压缩引擎

**[English](README.md)** | **[中文](README.zh-CN.md)** | **[العربية](README.ar.md)**

一个即插即用的插件，用 Cursor IDE 的思路替换 Hermes Agent 内置的上下文压缩器。

## 解决的问题

Hermes Agent 内置的上下文压缩器有一个严重 bug：它会永久保留最初的 3 条消息（系统提示 + 首轮用户/助手对话）。当项目推进到一定程度、上下文过长触发压缩时，模型会在上下文顶部看到最初的请求，**话题漂移回原点**，导致长项目永远无法完成。

## 工作原理

借鉴 Cursor IDE 的上下文管理策略：

1. **不锚定初始对话** — 只保护系统提示，所有用户/助手消息平等压缩。这是核心修复。

2. **极简摘要提示词** — 采用 Cursor 的方式：一句"请总结对话"，而非 Hermes 的 11 段结构化模板（容易被模型误解为指令）。

3. **两层记忆** — 压缩前将完整对话保存为 JSONL 文件，摘要中附带文件路径，agent 可通过搜索恢复丢失的细节。

4. **精确 token 计算** — 使用 `tiktoken`（cl100k_base）进行精确的多语言 token 估算，修复了 `len(text)//4` 对中文/CJK 严重低估的问题。

5. **工具输出修剪** — 旧的工具输出在 LLM 摘要前被替换为一行摘要，减少噪音和成本。

## 前置要求

- Python 3.9+
- 已安装 Hermes Agent（默认位置：`~/.hermes`）
- `tiktoken`（精确 token 计算所需）：

  ```bash
  pip install tiktoken
  ```

## 安装

### 自动安装（推荐）

```bash
# 直接运行安装脚本
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.py)

# 或者如果你已经克隆了仓库
python install.py
```

脚本会：
1. 将插件文件安装到正确位置
2. 安装 tiktoken 依赖
3. 自动更新你的 `config.yaml`
4. 重启 Hermes Agent gateway

### 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/thiswind/hermes-cursor-compressor.git

# 2. 将插件文件复制到正确位置（重要：hermes-agent 子目录）
cp -r hermes-cursor-compressor/cursor_style/ ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/

# 3. 安装 tiktoken
pip install tiktoken

# 4. 在 ~/.hermes/config.yaml 中添加:
#    context:
#      engine: "cursor_style"

# 5. 重启 Hermes Agent
hermes gateway restart
```

### 验证安装

安装完成后，验证引擎是否正确加载：

```bash
cd ~/.hermes/hermes-agent
python -c "
from plugins.context_engine import discover_context_engines, load_context_engine
print('可用的引擎:')
for name, desc, avail in discover_context_engines():
    print(f'  - {name}: {\"✅ 可用\" if avail else \"❌ 不可用\"}')

engine = load_context_engine('cursor_style')
if engine:
    print('\\n✅ cursor_style 引擎加载成功！')
else:
    print('\\n❌ cursor_style 引擎加载失败')
"
```

你应该看到：
```
可用的引擎:
  - cursor_style: ✅ 可用

✅ cursor_style 引擎加载成功！
```

## 卸载

### 自动卸载（推荐）

```bash
# 直接运行卸载脚本
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.py)

# 或者如果你已经克隆了仓库
python uninstall.py
```

### 手动卸载

```bash
rm -rf ~/.hermes/hermes-agent/plugins/context_engine/cursor_style
# 然后从 ~/.hermes/config.yaml 中删除 "context.engine: cursor_style"
# 重启 Hermes Agent
```

## 可选：自定义摘要模型

默认使用 Hermes Agent 的辅助压缩模型（如 Gemini Flash）。如需覆盖，通过 `auxiliary.compression` 配置：

```yaml
auxiliary:
  compression:
    model: "gemini-2.5-flash"
    provider: "auto"
    timeout: 30
```

## 项目结构

```
cursor_style/
├── __init__.py          # 包初始化 + register 函数导出
├── plugin.yaml          # 插件元数据
├── engine.py            # CursorStyleEngine（ContextEngine ABC 实现）
├── token_counter.py     # 精确多语言 token 计算（tiktoken）
├── summarizer.py        # Cursor 风格极简摘要
├── history_file.py      # 两层记忆（JSONL 历史文件）
└── tests/
    ├── conftest.py      # 共享 fixtures
    ├── stubs/           # ContextEngine ABC 存根（用于单元测试）
    ├── unit/            # 单元测试（无需 Hermes Agent）
    └── integration/     # 集成测试（需要 Hermes Agent）
```

## 运行测试

```bash
# 仅单元测试（无需 Hermes Agent）
cd hermes-cursor-compressor
PYTHONPATH=. python -m pytest cursor_style/tests/unit/ -v

# 全部测试（含集成测试，需要 Hermes Agent）
PYTHONPATH=.:/path/to/hermes-agent python -m pytest cursor_style/tests/ -v
```

## 与 Hermes 内置压缩器对比

| 特性 | Hermes 内置 | Cursor 风格 |
|------|------------|------------|
| 受保护消息 | 3 条（系统提示 + 初始对话） | 1 条（仅系统提示） |
| 话题漂移 bug | 有 — 初始请求永远可见 | 已修复 — 所有消息平等压缩 |
| 摘要提示词 | 11 段结构化模板 | 极简（约 1000 token 输出） |
| Token 估算 | `len(text)//4`（对 CJK 不准确） | tiktoken cl100k_base |
| 历史文件 | 无 | 有（JSONL，可搜索） |
| 摘要输出 | 约 5000 token | 约 1000 token |
| 触发阈值 | 上下文的 50% | 上下文的 50% |

## Troubleshooting

### 引擎加载失败

如果安装后引擎无法加载：

1. 确认文件在正确位置：
   ```bash
   ls -la ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/
   ```

2. 确认 `__init__.py` 导出了 `register` 函数

3. 重启 Hermes Gateway：
   ```bash
   hermes gateway restart
   ```

4. 查看日志：
   ```bash
   hermes logs --level ERROR
   ```

### 配置问题

如果你的 `config.yaml` 中有重复的 `engine` 键：

```yaml
# ❌ 错误（重复键）
context:
  engine: "cursor_style"
  engine: compressor

# ✅ 正确
context:
  engine: "cursor_style"
```

最新的 `install.py` 已修复此问题。

## 许可证

MIT
