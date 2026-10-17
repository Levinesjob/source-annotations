# Source Annotations

**Read the paper, understand it in place.**

### 原文旁的 AI 学术精读助手

把**难词、长句、公式和关键证据**的解释放回原论文，帮助有一定领域基础的研究人员和工程师保持阅读上下文。

**原文现场理解 · 观点追溯证据 · 可复现 PDF**

[查看标注 PDF](https://github.com/Levinesjob/source-annotations/raw/refs/heads/main/output/waypoint-opd-v1-annotated.pdf) · [下载试用版](https://github.com/Levinesjob/source-annotations/releases/tag/v0.1.0-preview.1) · [快速开始](#快速开始) · [Skill 说明](SKILL.md)

<a href="examples/waypoint-opd/showcase/hero.png"><picture>
  <source media="(max-width: 600px)" srcset="examples/waypoint-opd/showcase/hero-mobile.png">
  <img src="examples/waypoint-opd/showcase/hero.png" alt="真实论文第1页局部：原文段落保留在中间，完整术语、长句解释和结论限制位于两侧。手机显示原句与同页旁注的分区放大图。" width="1440">
</picture></a>

*Waypoint-OPD v1 的真实 PDF 裁图，中文解释与标记由本项目添加。当前为公开预览版。*

## 看看阅读时有什么不同

读到陌生术语时，不必先整理一份脱离正文的词表；遇到复杂机制时，可以在对应段落旁看解释；看到结论时，能继续回到作者写下的证据和限制。

保留英文正文并精选解释，区别于整篇翻译；保留证据入口，区别于独立摘要；加入语境解释和审查规则，超出单纯高亮与笔记管理。目标是帮助你继续阅读原论文。

[![同版本、同坐标的原文与标注对比](examples/waypoint-opd/showcase/before-after.png)](examples/waypoint-opd/showcase/before-after.png)

*上方原句：同页、同坐标、同缩放；右下：原有旁注单独放大，不改写原文。左下的问题用于说明阅读场景。手机请点击大图，或看下方放大示例与 PDF。*

## 三个核心价值

### 01 · 在原文现场理解

**Understand in Context.** 完整术语保留本文义，长句解释保留条件与否定，公式说明符号、设计理由和原文例子。解释和原句一起呈现，让你接着读原论文。

### 02 · 让观点回到证据

**Trace Every Insight.** 阅读导览的入口跳到实际原句、公式或图表；四类标记区分**实测、推导、作者主张、导读解释**。观点与适用条件一起读，避免把作者判断、实验结果和 AI 解释混为一谈。

<a href="examples/waypoint-opd/showcase/evidence-navigation.png"><picture>
  <source media="(max-width: 600px)" srcset="examples/waypoint-opd/showcase/evidence-mobile.png">
  <img src="examples/waypoint-opd/showcase/evidence-navigation.png" alt="阅读导览的正确性限制入口，连接到原论文第4页方向一致不保证监督有益的高亮原句，并展示同页中文解释。静态组合，目标读取自真实PDF GoTo。" width="1440">
</picture></a>

*阅读导览 → 原文位置 → 支持证据 → 适用边界。上图是静态组合，跳转目的地直接读取成品 PDF；实际点击请打开 PDF。AI 辅助解释仍需内容审查。*

### 03 · 可复现、可核查

**Reproducible by Design.** 固定原文版本和 SHA256，JSON 保存原句与解释，脚本将引文映射到 PDF 字符位置。版本不符、定位歧义或旁注放不下时会停止；原始输入保留。

[查看真实标注数据](examples/waypoint-opd/annotations.json) · [查看图片来源与跳转记录](examples/waypoint-opd/showcase/manifest.json) · [工程职责与两条 PDF 路径](docs/architecture.md)

## 如何工作

**原始 PDF → AI 通读与分析 → 结构化批注 → PDF 绘制与机械检查 → 标注 PDF／同版手机页**

智能体负责理解原文、选择重点和起草解释；确定性脚本负责匹配、坐标、排版及机械验证；人工或独立模型负责审查内容。**生成成功不代表解释正确**，本地脚本本身不调用模型。

## 快速开始

**先看效果，不必安装：** [标注 PDF](https://github.com/Levinesjob/source-annotations/raw/refs/heads/main/output/waypoint-opd-v1-annotated.pdf) · [只加导览的 PDF](https://github.com/Levinesjob/source-annotations/raw/refs/heads/main/output/waypoint-opd-v1-reading-brief.pdf) · [手机阅读文件](output/waypoint-opd-mobile.html)

手机阅读文件需与标注 PDF 一起下载后打开，保持原页排版并提供缩放；GitHub 文件页不会运行它，也没有托管的在线阅读服务。

### 在本地复现样例

下载完整仓库，使用 **Python 3.11+**。以下在 Windows PowerShell 的仓库根目录执行；已实测环境为 Windows / Python 3.13.5 / PyMuPDF 1.26.5。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/fetch_example.py
.\.venv\Scripts\python.exe scripts/annotate.py local/waypoint-opd-v1.pdf examples/waypoint-opd/annotations.json local/reproduced.pdf
.\.venv\Scripts\python.exe scripts/verify.py local/waypoint-opd-v1.pdf examples/waypoint-opd/annotations.json local/reproduced.pdf
```

这会用**已提供的批注数据复现排版**，不重新理解论文，也无需模型 API 密钥。首次安装和下载原文需要网络。手机输出、只加导览、测试及其他系统命令见[完整使用说明](docs/usage.md)；macOS/Linux 尚未实际验收。

### 用 Skill 读新论文

将完整目录放入支持 Agent Skills 的工具的技能目录。Codex 可调用：

> 使用 $source-annotations 精读这份论文。先通读正文，再标注重点、完整术语、长句和公式；需要时添加阅读导览。保留原文件，核对关键证据和限制，报告尚未完成的审查。

新论文需要智能体重新阅读和生成记录，不是把已有样例换一个 PDF。安装位置与工具能力边界见[使用说明](docs/usage.md#安装为-skill)；无文件执行能力的聊天工具可用[通用文字指令](docs/plain-prompt.md)，不保证 PDF 排版。

## 验证范围与限制

| 已有结果 | 尚未由这些结果证明 |
|---|---|
| **23 项自动测试**；Waypoint-OPD 44条定位及几何检查 | 全部解释正确、完成全部逐条专业审查 |
| 只加导览路径：单栏 Waypoint、双栏 CVPR ResNet、公式密集 Adam，共 **44 页原文回归** | 三篇都经过全文标注和独立学术审查；任意复杂 PDF 均兼容 |
| 手机页从最终 PDF 渲染，共用定位和版本哈希 | 最新真实手机的全部链接、缩放与阅读体验已验收 |
| Windows 本地生成及独立目录复现 | macOS/Linux、其他机器及所有 Agent 已执行通过 |

两条 PDF 路径分开看：**只加导览**保留原研究页，并验证已有链接、书签等；**正文旁注**会重建页面，已有人工批注或表单会拒绝处理，不能沿用前者的结构保留结论。

扫描、旋转、异常裁剪 PDF 不在自动处理范围。完整标签语义、XFA、作品集、富媒体未认证；两条路径的其他限制见[工程说明](docs/architecture.md#两条-pdf-路径)。**45分钟仅是阅读预算，没有量化提速结论。**

[实际验收记录](review/STATUS.md) · [三类论文回归](review/ACADEMIC-REGRESSION.md) · [集中待办](TODO.md)

## 许可与反馈

本项目新增代码、指令和中文解释采用 [MIT](LICENSE)。论文原内容为 **CC BY 4.0**，Noto 字体为 **SIL OFL 1.1**；**PyMuPDF 适用 AGPL／商业双许可**，本项目的 MIT 不改变依赖义务。详见[第三方说明](THIRD_PARTY_NOTICES.md)与[PyMuPDF 官方许可说明](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)。

欢迎[报告一个具体问题](https://github.com/Levinesjob/source-annotations/issues/new?template=feedback.yml)：论文版本、页码、预期和实际结果，比单纯点赞更能帮助改进。请移除私人和公司材料。
