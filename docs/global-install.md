# 本机全局技能固化

2026-10-17曾将21个必需文件安装到本机Codex全局、共享Agent Skills和Claude Code全局目录；2026-10-18再同步过53个公开文件。这是当时的同步记录，不代表之后所有文档仍逐字一致。

Cursor按[官方目录规则](https://cursor.com/help/customization/skills)可发现用户级共享`~/.agents/skills/`；Claude Code按[个人技能规则](https://code.claude.com/docs/en/skills)使用`~/.claude/skills/`。Codex沿用当前可发现的`~/.codex/skills/`。

新一轮对话或新会话使用“使用 source-annotations 处理这份论文”。Codex可显式写`$source-annotations`，Claude Code可写`/source-annotations`。安装可发现不等于已在每个工具完成PDF生成；需要Python与requirements.txt依赖，聊天工具无文件执行能力时只能使用文字指令。

维护源为本仓库。后续修改应先验证再同步这些副本，不能只改一处后宣称全部已更新。该安装仅影响本机当前用户，不自动覆盖云端、其他用户和其他设备。

2026-10-21清理只调整本工程，没有改动全局安装。旧安装清单与备份已移入本机工程外归档，未公开；可发现性仍不等于各工具已完成独立生成验收。
