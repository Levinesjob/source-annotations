# 本机全局技能固化

2026-10-17已将当前技能的21个必需文件安装到本机Codex全局、共享Agent Skills和Claude Code全局目录，逐文件SHA256相同。旧版备份保留在本工程local/skill-backups/；安装清单local/global-install.json不对外分发。

Cursor按[官方目录规则](https://cursor.com/help/customization/skills)可发现用户级共享`~/.agents/skills/`；Claude Code按[个人技能规则](https://code.claude.com/docs/en/skills)使用`~/.claude/skills/`。Codex沿用当前可发现的`~/.codex/skills/`。

新一轮对话或新会话使用“使用 source-annotations 处理这份论文”。Codex可显式写`$source-annotations`，Claude Code可写`/source-annotations`。安装可发现不等于已在每个工具完成PDF生成；需要Python与requirements.txt依赖，聊天工具无文件执行能力时只能使用文字指令。

维护源为本仓库。后续修改应先验证再同步这些副本，不能只改一处后宣称全部已更新。该安装仅影响本机当前用户，不自动覆盖云端、其他用户和其他设备。

2026-10-18本轮已同步当前53文件完整白名单（含唯一Attention样例与静态说明），三处均逐文件比对SHA256。旧文件先在本工程local/skill-backups/备份；不再只拷贝21个运行文件，避免样例命令缺少JSON。实际同步结果记录在本机清单，工具发现仍不等于每个工具已完成独立生成验收。
