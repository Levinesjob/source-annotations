# 仓库展示改版 · 2026-10-18

## 审查与取舍

三个最强卖点是：在原文旁解释、将观点链接到证据及限制、固定版本和定位数据可核查。现有README先解释实现和验收状态，再展示整页小字，读者很难发现阅读体验；多次改版叙述与运行命令混在首页。原方法页仍可作为完整样例，但不适合作为首屏主视觉。

复用Waypoint-OPD v1原PDF、最终21页标注PDF、44条JSON、定位报告和导览GoTo。展示不生成新论文内容，不重排论文中的字，也不改PDF算法。不能宣传自动保证解释正确、已量化提速、全部论文全文标注验证、跨平台已实测或手机全部验收。

采用学术编辑式展示：黑灰文字、白纸与中性外框、蓝色入口、原成品的黄色重点。相比整页截图，选择局部放大；相比虚构软件界面，使用真实PDF片段并明确标注静态组合。首图保留原文/旁注空间关系；对比图同版本同坐标；证据图由真实GoTo导出，不声称是真实操作录像。手机使用单独放大的片段而非继续缩小桌面全图。

## 信息架构

定位与样例入口 → Hero → 同位置前后对比 → 三个价值 → 职责流程 → 最短复现与Skill请求 → 验证范围/两条路径 → 许可/反馈。详细命令移到docs/usage.md，架构和失败条件移到docs/architecture.md，素材来源与生成命令移到docs/showcase.md。复用review/STATUS.md和回归报告。

## 验证与交付

新增可重跑的PNG生成脚本和来源清单；记录输入SHA256、PDF页序/裁剪框、实际GoTo目的地。生成桌面和窄屏素材，检查缩放后的图片与浅/深背景Markdown预览。运行现有23项测试、verify与本地链接检查，核对PDF哈希未改变。更新已发布状态和TODO；只提交这轮文档和展示素材，保留v0.1.0-preview.1历史版本。

参考仅用于展示方式，不复制视觉资产：[Zotero](https://www.zotero.org/)的场景与实际截图、[PyMuPDF](https://github.com/pymupdf/PyMuPDF)的价值与安装顺序、[whisper.cpp](https://github.com/ggml-org/whisper.cpp)的可运行入口、[LiquidText](https://www.liquidtext.net/)的原文与证据空间联系。许可依据[PyMuPDF官方说明](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)。
