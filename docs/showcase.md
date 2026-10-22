# 功能总览与真实成果

先用一张功能总览解释阅读导览、同页旁注、证据追溯和可复现产物；再用《Attention Is All You Need》固定 v1 的真实成果核对效果。

| 素材 | 用途 |
|---|---|
| [功能总览](../examples/attention-is-all-you-need/showcase/overview.png) | 沿用用户提供海报的视觉，重排为横版；图中页面是功能示意，不是实际 PDF 截图。35条标注、11个内部入口、24项测试对应2026-10-22记录 |
| [阅读导览](../examples/attention-is-all-you-need/showcase/preview-guide.png) | 最终PDF新增首页的实际渲染 |
| [原文与同页旁注](../examples/attention-is-all-you-need/showcase/reading-poster.png) | 真实原句局部及对应中文旁注的静态组合 |
| [机制说明](../examples/attention-is-all-you-need/showcase/attention-explained.png) | 依据固定v1制作的导读示意，非实验可视化 |
| [证据路径](../examples/attention-is-all-you-need/showcase/evidence-trace.png) | 依据真实GoTo展示导览到第8页表2的对应关系 |
| [来源清单](../examples/attention-is-all-you-need/showcase/static-manifest.json) | 裁片坐标与哈希 |

要复现真实截图，先按[案例说明](../examples/attention-is-all-you-need/README.md)生成本地PDF，再安装requirements-showcase.txt并运行`python scripts/reading_showcase.py`。此脚本不生成或覆盖功能总览海报。静态图不能代替在PDF/HTML中的真实操作；完整Attention全文仅本地生成。

建议依次查看功能总览、阅读导览、原文旁注和证据路径。功能示意必须明确标注，不能冒充真实成品；真实裁片来源见 static-manifest.json。统计依据见[当前验证记录](../review/RELEASE-2026-10-22.md)，不使用过时统计或未验证的效率数字。
