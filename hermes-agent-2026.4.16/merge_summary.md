此次合并将完整的Hermes Agent项目结构引入到主分支，包含核心代理逻辑、插件系统、技能库和相关工具脚本，为AI代理提供了完整的工具调用能力和扩展架构。项目结构完整，包含多种内存管理插件、上下文引擎和丰富的技能模块，支持多种AI模型和工具集成。
| 文件 | 变更 |
|------|---------|
| package.json | - 新增项目配置文件，定义了项目依赖和脚本<br>- 包含agent-browser和camofox-browser依赖，支持浏览器工具功能<br>- 设置了Node.js版本要求为20.0.0以上 |
| run_agent.py | - 新增AI代理核心实现文件，包含工具调用、对话管理和模型集成功能<br>- 支持多模型提供商、错误处理和消息历史管理<br>- 实现了自动工具调用循环和配置化模型参数 |
| plugins/__init__.py | - 新增插件系统包初始化文件 |
| plugins/context_engine/__init__.py | - 新增上下文引擎插件发现机制<br>- 支持扫描和加载不同的上下文引擎实现<br>- 提供引擎可用性检查和加载功能 |
| plugins/memory/__init__.py | - 新增内存管理插件系统<br>- 支持多种内存管理实现，包括byterover、hindsight、holographic等<br>- 提供统一的内存插件接口 |
| skills/apple/ | - 新增Apple相关技能，包括Notes、Reminders、FindMy和iMessage功能 |
| skills/autonomous-ai-agents/ | - 新增自主AI代理技能，包括Claude Code、Codex、Hermes Agent和OpenCode |
| skills/creative/ | - 新增创意技能，包括架构图、ASCII艺术、视频生成、Excalidraw、Manim视频、P5.js和流行网页设计 |
| scripts/ | - 新增多种工具脚本，包括构建技能索引、贡献者审计、Discord语音处理、WhatsApp桥接等<br>- 提供安装脚本和发布工具 |
| optional-skills/security/ | - 新增安全相关技能，包括OSS取证和Sherlock安全工具 |
| packaging/homebrew/ | - 新增Homebrew打包配置，支持通过Homebrew安装Hermes Agent |
| plans/gemini-oauth-provider.md | - 新增Gemini OAuth提供商配置计划 |