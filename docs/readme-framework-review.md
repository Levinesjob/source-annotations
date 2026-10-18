# README 四角框架与故事化改版

## 改了什么

首屏压缩为一句读者用途、阅读入口和真实PDF局部，接一个查术语/回读/找证据的短场景；再用四角图解释导览、旁注、证据与可复现结果。快速开始和依赖紧接框架图，深入演示放后面，避免正文介绍越来越长。

- README.md：主线、展示顺序与三种用法；保留实际命令和验证边界。
- scripts/framework_overview.py：PNG与可编辑SVG共用场景，生成桌面/窄屏框架。
- examples/waypoint-opd/showcase/framework-overview.png、framework-mobile.png、同名SVG及framework-manifest.json：新增5个文件。
- scripts/showcase.py、hero-mobile.png、manifest.json：只调整手机主图外围标题，保留真实原文与旁注。
- docs/showcase.md、THIRD_PARTY_NOTICES.md及本记录：素材生成、来源和范围。

## 实现对应

四角分别对应已有reading_guide、annotations/正文绘制、GoTo/来源类别、JSON/PDF/HTML与哈希校验。没有新增在线服务、自动理解模块或内容正确性保证；两条PDF路径的保留范围继续区分。图是阅读价值示意，不是声称存在这些独立运行模块。

## 核验结果

- PNG与SVG各有桌面/窄屏版本；PNG已目视检查，SVG在Chromium中检查20/25个文字对象，均无越界。SVG字体替换的字形差异仍按下文说明。
- GitHub GFM接口渲染后在本地Chromium检查830px桌面内容、390px手机视口，浅/深色各一次；四张展示图均加载，无页面水平溢出。已查看首屏、手机主图和实际显示尺寸的框架图。
- 修复了原有HTML结构问题：连写的a/picture会被GitHub拆开，使source离开picture。改成独立HTML块后，检查浏览器实际naturalWidth：桌面为1440/1440/1440/1440，窄屏为780/780/1440/780，确认主图、框架、证据图都切换到窄屏版本；前后对比仍可点击大图。
- Markdown解析为11个标题、3种使用方式、1张依赖表及1个PowerShell代码块；33个本地链接、图片路径与标题片段检查通过，git diff --check通过。
- README生成命令的可执行行与上一轮已实际跑通的版本逐行一致；本轮重新运行固定v1缓存校验及verify，20页/44条几何和文字检查通过，pip check无依赖冲突。不把这些机械检查写成学术内容或真实手机验收。
- 公开版本页、两种PDF下载入口及依赖许可入口HEAD返回200。未复测新平台或声称阅读效率提升。
- 核心PDF脚本与标注JSON的Git规范化内容未变，两份已发布PDF字节未变；仅展示生成脚本更换一处手机图外围标题，并新增框架绘图脚本。
- README总文件从10788字节减至7326字节（后续HTML分行只增加少量字节）；不是阅读速度测量，也不声称完成5秒理解验证。

## 未完成或无法保证

5秒内理解是设计目标，未做陌生读者计时实验；阅读更顺畅是产品目标，未证明提速或理解提升。预览不是实际手机验收，也不新增跨工具/跨平台认证。SVG是可编辑文本来源，字体不内嵌；PNG是稳定展示版本。没有制作交互录屏，实际GoTo演示仍使用已有静态组合。
