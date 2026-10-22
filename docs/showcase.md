# 真实成果展示

只展示《Attention Is All You Need》固定v1的实际阅读成果。

| 素材 | 用途 |
|---|---|
| [阅读导览](../examples/attention-is-all-you-need/showcase/preview-guide.png) | 最终PDF新增首页的实际渲染 |
| [原文与同页旁注](../examples/attention-is-all-you-need/showcase/reading-poster.png) | 真实原句局部及对应中文旁注的静态组合 |
| [机制说明](../examples/attention-is-all-you-need/showcase/attention-explained.png) | 依据固定v1制作的导读示意，非实验可视化 |
| [证据路径](../examples/attention-is-all-you-need/showcase/evidence-trace.png) | 依据真实GoTo展示导览到第8页表2的对应关系 |
| [来源清单](../examples/attention-is-all-you-need/showcase/static-manifest.json) | 裁片坐标与哈希 |

先按[案例说明](../examples/attention-is-all-you-need/README.md)生成本地PDF，再安装requirements-showcase.txt并运行`python scripts/reading_showcase.py`。静态图不能代替在PDF/HTML中的真实操作；完整Attention全文仅本地生成。

建议依次查看阅读导览、原文旁注和证据路径：先看如何建立背景与阅读顺序，再看解释怎样接回原句。页面宣传不能使用虚构截图、过时统计或未验证的效率数字。
