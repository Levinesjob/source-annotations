# 使用与复现

## 查看现成样例

先看[中文导览](../examples/attention-is-all-you-need/showcase/preview-guide.png)与[静态展示](showcase.md)，再对照[原论文v1](https://arxiv.org/abs/1706.03762v1)。完整标注PDF、导览插页PDF和HTML仅在本地生成；原文许可未提供本仓库分发全文的通用授权。HTML直接显示最终PDF页面，需缩放阅读；打开PDF按钮需要同名PDF位于同一目录，无需后台服务。

## 本地生成

克隆完整仓库，保留assets/字体、JSON、脚本。Python 3.11+；实际验证Windows / Python 3.13.5 / PyMuPDF 1.26.5。

```powershell
git clone https://github.com/Levinesjob/source-annotations.git
cd source-annotations
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/fetch_example.py
.\.venv\Scripts\python.exe scripts/annotate.py local/attention-is-all-you-need-v1.pdf examples/attention-is-all-you-need/annotations.json local/reproduced.pdf
.\.venv\Scripts\python.exe scripts/verify.py local/attention-is-all-you-need-v1.pdf examples/attention-is-all-you-need/annotations.json local/reproduced.pdf
.\.venv\Scripts\python.exe scripts/mobile.py local/attention-is-all-you-need-v1.pdf examples/attention-is-all-you-need/annotations.json local/reproduced-mobile.html --pdf local/reproduced.pdf
.\.venv\Scripts\python.exe scripts/prepend_guide.py local/attention-is-all-you-need-v1.pdf examples/attention-is-all-you-need/annotations.json local/reproduced-guide.pdf
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

首次安装与下载需要网络；fetch脚本固定v1并校验哈希，不下载模型。已有数据只复现排版，脚本不会重新分析论文、不调用模型、无需API密钥；智能体生成新记录的费用另计，当前无完整费用及人工计时。

macOS/Linux将解释器换为`.venv/bin/python`，其他参数相同；**命令为使用建议，未实际验收这些系统**。

只复现关键页：

```powershell
.\.venv\Scripts\python.exe scripts/annotate.py local/attention-is-all-you-need-v1.pdf examples/attention-is-all-you-need/annotations.json local/key-pages.pdf --pages 1,4,7
```

指定页导出不带前置导览。三类插页回归执行`python scripts/regression_academic.py --fetch`，需先下载Attention样例；ResNet与Adam的原文和回归文件只保存在local/。

## 安装为 Skill

把**完整目录**复制到工具的技能目录，不能只复制SKILL.md。需要具备文件读写、Python执行及依赖安装能力的智能体；格式可发现不等于生成已经跨工具实测。

- Codex：按[当前官方目录](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)，用户级`~/.agents/skills/source-annotations/`，项目级`.agents/skills/source-annotations/`，调用`$source-annotations`。本机历史`~/.codex/skills/`安装记录仍保留，不作为所有版本的通用推荐。
- Cursor：项目级`.cursor/skills/source-annotations/`，或用户级`~/.agents/skills/source-annotations/`；以[官方发现规则](https://cursor.com/help/customization/skills)为准。
- Claude Code：个人级`~/.claude/skills/source-annotations/`，以[官方技能说明](https://code.claude.com/docs/en/skills)为准。

本机安装记录见[全局入口](global-install.md)，不是向其他设备或云端自动同步。其他聊天工具使用[通用指令](plain-prompt.md)，只承诺文字工作流，不保证PDF定位与导出。

## 用于新论文

智能体先确认版本、读者基础和范围，通读正文，再准备记录。关键发现必须有原句证据与限制；词义保留完整词组；公式解释符号、设计与例子。数据字段见[PDF工作流](../references/pdf-workflow.md)；前置导览见[导览字段](../references/reading-guide-schema.md)。不能只替换样例文件路径和哈希。

## 检查阅读结果

对照原文核查否定、条件、比较对象、证据类型和结论范围；逐页检查正文、图表与批注是否遮挡。机器图表清点只证明有同页关联，不证明解释相关或正确。手机打开同版文件，记录具体设备与交互结果。

45分钟仅是样例主线预算；不包括全部推导、附录和复现代码。验证阅读帮助需要同时记录实际时间与能否讲清问题、机制、证据和边界；没有对照不宣称提速。
