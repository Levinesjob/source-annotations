# 来源、许可与修改

## 原论文：Attention Is All You Need

Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin。固定[arXiv:1706.03762v1](https://arxiv.org/abs/1706.03762v1)，2017-06-12，15页。

该版本页面链接的是[arXiv非独占分发许可](https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html)（2026-10-18核对），不是CC BY 4.0。本仓库没有取得完整研究页的通用再分发授权；完整标注PDF、导览插页PDF和内嵌全文HTML只在本地生成，不进入公开仓库。公开导览由本项目编写；标题、少量原句与选择性证据引文归原作者，均不由MIT重新授权。展示不暗示原作者认可本项目。

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
## 展示素材与可选工具

`examples/attention-is-all-you-need/showcase/`包含本项目导览、说明图、用户提供海报的修订版和少量原句/表格节选，不包含完整研究页；原文内容归原作者，新增中文解释和绘图脚本归本项目。图片不暗示原作者认可本项目。`overview.png`沿用用户提供的视觉并经AI重排为横版，图中页面明确标为功能示意，不是实际PDF截图；案例及统计改为当前Attention记录。不能将其作为成品版式、论文原句或阅读效率的验证依据。

真实截图的裁片、坐标及哈希，以及功能示意图的范围见[素材说明](docs/showcase.md)。不生成动图，不把示意页面说成实际截图。

可选Pillow 12.3.0按[官方许可](https://pillow.readthedocs.io/en/stable/about.html#license)适用MIT-CMU，不加入PDF必需运行依赖。
