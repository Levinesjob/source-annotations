# 来源、许可与修改

## 原论文

Waypoint-OPD: Transferring RL-Induced Policy Shifts via Gated On-Policy Distillation.
Bingxi Hou, Guochao Jiang, Guofeng Quan, Weiqing Li, Wenfeng Feng, Guohua Liu, Yuewei Zhang.
arXiv:2610.21601v1，2026-10-15。

- 原文：https://arxiv.org/abs/2610.21601v1
- 固定PDF：https://arxiv.org/pdf/2610.21601v1
- 许可：https://creativecommons.org/licenses/by/4.0/
- 许可来源：arXiv v1 页面及其 HTML 版标明 CC BY 4.0（2026-10-17核查）。

标注副本和预览图片包含原论文内容，已增加中文解释、高亮、下划线和必要页边距。原正文和图表不改写，不暗示原作者认可本工具。原论文内容的权利不由本仓库MIT许可覆盖。

## 中文字体

学术导览使用 Noto Serif CJK SC Regular，Google / Adobe，SIL OFL 1.1。

- [官方字体来源](https://github.com/notofonts/noto-cjk/blob/main/Serif/OTF/SimplifiedChinese/NotoSerifCJKsc-Regular.otf)
- 许可全文：`assets/OFL-serif.txt`；原文件不修改。
- 英文使用PDF引擎内置Nimbus Roman并嵌入PDF；见[URW Base35许可及PDF字体嵌入例外](https://github.com/ArtifexSoftware/urw-base35-fonts/blob/master/LICENSE)。不分发独立Nimbus字体文件。

Noto Sans CJK SC Regular，Google / Adobe，SIL Open Font License 1.1。

- 来源：https://github.com/notofonts/noto-cjk/blob/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf
- 许可全文：`assets/OFL.txt`；本项目不修改字体。
- PDF中嵌入字体，保证离线中文显示。

## PDF 引擎

PyMuPDF 1.26.5：https://pymupdf.readthedocs.io/en/latest/about.html

采用 AGPL 或商业许可；本包以依赖形式安装，不重新分发其二进制。新写的脚本采用MIT不代表可以忽略依赖条款。若以后做闭源在线服务，应单独确定适用许可。
# 本轮版式修改

按用户要求，标注副本移除了首页竖排arXiv版本条；原论文版本链接、作者归属和许可仍保留。原始下载文件不变。


## README展示素材与可选工具

`examples/waypoint-opd/showcase/`中的论文截图及动图裁片来自同一固定v1论文及标注副本，包含原论文CC BY 4.0内容；框架图是本项目的阅读价值说明图，不含论文裁图；外围说明、重排的导览内容与构图由本项目添加，见[素材清单](docs/showcase.md)。使用随包Noto字体，不复制第三方产品截图或生成虚构界面。动图是动作示意，不是录屏或即时生成演示。

背景动图中“策略是一条规则……”为本项目对[Spinning Up / Policies](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html#policies)开头定义的中文转述（2026-10-18核对），用于说明现有链接的阅读去向；不包含该网站的截图，也不暗示其作者认可本项目。

展示脚本可选依赖Pillow 12.3.0，按[官方许可](https://pillow.readthedocs.io/en/stable/about.html#license)适用MIT-CMU；仅通过依赖安装，不随仓库重新分发二进制。它不加入PDF运行必需依赖。
