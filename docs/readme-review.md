# README 改稿核验 · 2026-10-18

本轮以用户提供的`source-annotations-README-proposed.md`为主要改稿，调整README和对应使用文档，不改变PDF核心生成逻辑、截图或已发布PDF。保留论文版本、许可和未完成验收说明。

## 采用的叙事

以“帮助读者亲自理解原论文”为首屏定位；说明摘要用于判断阅读价值，原文承载方法、实验条件与边界。顺序为阅读导览/证据跳转 → 原文旁注/前后对比 → 机制职责 → 三种使用方式 → 实际支持范围。

## 与提供改稿的差异

| 改稿表述 | 按实际实现调整 |
|---|---|
| 手机HTML需要与PDF一起下载才可使用 | mobile.py内嵌页图，HTML可单独阅读；只有“打开PDF”按钮依赖同目录、原文件名的标注PDF。同步修正docs/usage.md |
| “先只生成一页导览” | prepend_guide.py在原论文前插一页；本例输出21页，而不是仅一页 |
| Codex统一写为~/.codex/skills/ | 按[当前OpenAI官方目录](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)，推荐用户~/.agents/skills/或项目.agents/skills/；本机历史安装记录保留 |
| “重点”或“原文入口”可能被理解为全部精确定位 | 说明能精确时直达位置，无法精确时明确降级整页入口；不伪装精确引用 |
| “很多时间”花在查词等辅助环节 | 改为这些操作“可能打断阅读”，不以未测量判断宣传效率 |
| “仓库中仓库预置”及泛指Preview | 修正文案重复，并链接实际发布的v0.1.0-preview.1 |

## 命令与工程检查

- 检查requirements.txt、三个CLI解析器及mobile.py实现：Python3.11+，固定PyMuPDF1.26.5；Noto字体随完整仓库。重建展示图的Pillow为可选依赖。
- prepend_guide.py、annotate.py、verify.py的`--help`均返回成功；pip check无依赖冲突。
- fetch_example.py使用缓存原文，固定v1哈希校验通过。本轮未重新网络下载论文，也未新建虚拟环境。
- 实际运行README中的两个生成入口，只有输出路径换为`local/readme-check-20261018/`，以免覆盖成品。只插导览输出21页，原20页保留检查通过；正文标注输出21页、44条定位。
- verify.py返回20页/44条、geometry_and_text=passed；semantic/human/phone仍为not assessed。没有把生成成功当作学术准确性验证。
- 本轮是文档修改，不重复扩大算法测试；已有23项测试记录保留，未声称本轮重新完成独立学术复核。

## Markdown、链接与预览

- marked解析结果为11个标题、3种使用方式、2张表和1个PowerShell代码块；表格列数一致，代码块包含所有实际脚本。
- 36个本地文档/图片/片段链接检查无缺失；Markdown代码围栏、picture和a标签成对，README内及跨文档标题锚点均找到对应标题。
- GitHub GFM接口成功渲染，保留picture与窄屏source；使用返回HTML在本地Chromium预览830px桌面内容/390px窄屏，浅深背景各一次。三张图片均加载，页面无横向溢出；导览/证据图位于旁注与对比图之前。
- 已打开桌面浅/深首屏及手机首屏检查；这不是GitHub实时UI或真实手机验收。GitHub接口不补全站点标题锚点，仅保留链接和标题，本轮另做标题片段静态核对。
- 公开版本和两种PDF下载入口HEAD返回200，依赖许可入口HEAD返回200；Codex、Cursor、Claude三份外部安装文档均返回200；Issues入口返回200并重定向GitHub登录，未提交Issue。
- git差异只包含README、docs/usage.md和本记录；既有图片、成品PDF、原始输入、标注JSON、SKILL.md与scripts/均未改动。

## 许可与未验证范围

MIT仅覆盖本项目新增代码、指令与解释；论文CC BY4.0、Noto字体SIL OFL1.1及PyMuPDF的AGPL/商业双许可分开说明，既有LICENSE和第三方许可未改。Windows为实际验证环境；其他平台、全部Agent执行、最新真实手机完整交互、新版全部解释独立审查和阅读效率对照仍未完成，未提高原有认证范围。
