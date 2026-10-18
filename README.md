# Source Annotations

**Read the paper, not just the summary.**

把阅读导览、原文旁注和证据入口放在一起，**帮你亲自读进原论文**。

[先读导览 PDF](output/waypoint-opd-v1-reading-brief.pdf) · [看标注 PDF](output/waypoint-opd-v1-annotated.pdf) · [三种用法与依赖](#快速开始) · [完整说明](docs/usage.md)

<a href="examples/waypoint-opd/showcase/hero.png">
<picture>
  <source media="(max-width: 600px)" srcset="examples/waypoint-opd/showcase/hero-mobile.png">
  <img src="examples/waypoint-opd/showcase/hero.png" alt="真实论文局部：英文正文保留在中间，术语、长句和结论边界的解释就在两侧。" width="1440">
</picture>
</a>

*真实 PDF 局部，非整页缩略图。中文解释与标记由本项目添加。*

## 摘要看懂了，正文却读不下去

一个陌生术语让你打开搜索页，一段长句又把你带进聊天窗口。回到公式时，你已经忘了它要解决哪个问题；看到提升数字，还得往回找比较对象和实验条件。

摘要适合筛选论文，AI 总结也能提示方向；要弄清方法和证据，仍要自己读原文。这里做的，是把背景、阅读路径和必要解释带回论文现场，**减少来回找资料、重新接上思路的阻力**。

## 围绕读原文，做好四件事

<a href="examples/waypoint-opd/showcase/framework-overview.png">
<picture>
  <source media="(max-width: 600px)" srcset="examples/waypoint-opd/showcase/framework-mobile.png">
  <img src="examples/waypoint-opd/showcase/framework-overview.png" alt="四角阅读框架：左上阅读导览，右上原文旁注，左下证据追溯，右下可复现产物；中心是亲自读原论文。" width="1440">
</picture>
</a>

导览带你进入正文，旁注帮助理解，证据入口让判断可回查，文件让结果可保存。这不是把全文换成中文或另写一份摘要，也不只是在 PDF 上涂颜色。

## 快速开始

### 依赖与环境

| 需要什么 | 实际要求 |
|---|---|
| Python 与 PDF 引擎 | **Python 3.11+**；`PyMuPDF==1.26.5`，用 `requirements.txt` 安装 |
| 字体 | Noto CJK 已随完整仓库放在 `assets/` |
| 模型与 API Key | 复现已有记录**不需要**；新论文需要能读 PDF、写文件和执行 Python 的智能体，是否需 API Key 取决于工具 |
| 下载 | ZIP 或 Git；首次安装依赖和下载原论文需网络 |
| 已验收环境 | **Windows / Python 3.13.5**；macOS/Linux 尚未完整验收 |

### 方式一：直接读样例

下载[阅读导览 PDF](output/waypoint-opd-v1-reading-brief.pdf)，从第一页的问题、先修知识和路线进入原文；或读[标注 PDF](output/waypoint-opd-v1-annotated.pdf)，看正文旁的解释。内部跳转需使用支持该功能的 PDF 阅读器。

[手机 HTML](output/waypoint-opd-mobile.html)内嵌页图，可单独离线打开，窄屏需要缩放；使用“打开 PDF”按钮时，将标注 PDF 按原文件名放在同目录。GitHub 文件页不会运行 HTML。

### 方式二：本地复现样例

Windows PowerShell：

```powershell
git clone https://github.com/Levinesjob/source-annotations.git
cd source-annotations
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/fetch_example.py
.\.venv\Scripts\python.exe scripts/prepend_guide.py local/waypoint-opd-v1.pdf examples/waypoint-opd/annotations.json local/reproduced-guide.pdf
.\.venv\Scripts\python.exe scripts/annotate.py local/waypoint-opd-v1.pdf examples/waypoint-opd/annotations.json local/reproduced.pdf
.\.venv\Scripts\python.exe scripts/verify.py local/waypoint-opd-v1.pdf examples/waypoint-opd/annotations.json local/reproduced.pdf
```

这是用**现成 JSON 重建导览、旁注和定位**，不会重新理解论文。两种 PDF 都含原文：本例是 1 页导览＋20 页论文。手机输出、测试与其他系统命令见[使用说明](docs/usage.md)。

### 方式三：用 Skill 读自己的论文

把完整目录安装到工具可发现的技能位置，不能只复制 `SKILL.md`。Codex、Cursor、Claude Code 的[目录与调用方式](docs/usage.md#安装为-skill)分别说明。

> 使用 `$source-annotations` 精读这篇论文。先做一页导览，讲清问题、前置知识和阅读路径，链接到原文证据；再为难词、长句、关键公式和结论添加少量旁注。保留原论文，报告未核验的解释。

新论文需要智能体重新通读和生成记录，不能只替换样例 PDF 路径。[通用文字指令](docs/plain-prompt.md)可用于其他聊天工具，但不保证能导出 PDF。

## 读起来是什么样

**读到术语，解释就留在旁边。** 下图上方是同页、同坐标的原句；右下是原有旁注放大，没有重写论文文字。

[![原句与同页术语解释的前后对比](examples/waypoint-opd/showcase/before-after.png)](examples/waypoint-opd/showcase/before-after.png)

**读到一个判断，继续看它的依据和边界。** 导览入口可跳向真实原句、公式或图表；无法精确定位时明确使用整页入口。

<a href="examples/waypoint-opd/showcase/evidence-navigation.png">
<picture>
  <source media="(max-width: 600px)" srcset="examples/waypoint-opd/showcase/evidence-mobile.png">
  <img src="examples/waypoint-opd/showcase/evidence-navigation.png" alt="导览中的正确性限制入口跳到原论文第4页对应原句，并展示同页解释。" width="1440">
</picture>
</a>

*真实 GoTo 位置的静态组合，并非操作录屏；请在 PDF 中点击体验。实测、推导、作者主张、导读解释分开标记，不把辅助解释当作作者结论。*

## 验证与边界

当前为 [v0.1.0-preview.1](https://github.com/Levinesjob/source-annotations/releases/tag/v0.1.0-preview.1) 公开预览。样例有 **44 条标注**，已有 **23 项自动测试**记录；只插导览路径在三类论文、共44页原研究内容上做过回归。

智能体起草解释，脚本负责版本校验、原句定位、绘制与机械检查，人工或独立模型审查内容。**机械检查通过不代表解释正确**。新版完整独立复核、全部逐条专业审查和最新真实手机完整操作仍未完成；45分钟是阅读预算，**没有量化提速结果**。

只插导览与正文旁注是两条路径：前者验证了原页内容及部分结构保留；后者重建研究页，遇到原有人工批注或表单会拒绝，不能假定完整保留交互对象。扫描、旋转、异常裁剪及复杂结构的范围见[工程说明](docs/architecture.md)。

[实际验收](review/STATUS.md) · [回归记录](review/ACADEMIC-REGRESSION.md) · [真实标注 JSON](examples/waypoint-opd/annotations.json) · [本轮展示来源与检查](docs/readme-framework-review.md)

## 许可与反馈

新增代码、指令和中文解释采用 [MIT](LICENSE)；论文原内容为 **CC BY 4.0**，Noto 字体为 **SIL OFL 1.1**。PyMuPDF 适用 **AGPL／商业双许可**，本项目 MIT 不覆盖依赖条款。见[第三方说明](THIRD_PARTY_NOTICES.md)。

欢迎[报告具体阅读卡点或错误](https://github.com/Levinesjob/source-annotations/issues/new?template=feedback.yml)：论文版本、页码、哪条解释或跳转出了问题。请移除私人和公司材料。
