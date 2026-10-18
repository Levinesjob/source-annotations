# 展示素材

当前只展示《Attention Is All You Need》，固定arXiv:1706.03762v1。参考用户海报的层级与原文现场感，不复制其错误页码、章节和旧案例统计。所有图片均为静态图。

| 素材 | 说明 |
|---|---|
| [reading-poster.png](../examples/attention-is-all-you-need/showcase/reading-poster.png) | 真实导览、原文加权汇总定义与同页旁注；下方给出四项阅读辅助 |
| [attention-explained.png](../examples/attention-is-all-you-need/showcase/attention-explained.png) | 三步计算、三种Q/K/V来源；人工绘制的导读图，不是实验注意力分布 |
| [evidence-trace.png](../examples/attention-is-all-you-need/showcase/evidence-trace.png) | 导览到第8页表2；依据真实GoTo，保留v1实验设置与比较边界 |
| [preview-guide.png](../examples/attention-is-all-you-need/showcase/preview-guide.png) | 最终PDF新增首页的真实渲染 |

前三张各有-mobile.png，README用picture按屏宽选择；两种布局共用内容和真实裁片。静态图不承担点击交互，真实入口在PDF/HTML中操作。

先按[样例说明](../examples/attention-is-all-you-need/README.md)生成本地PDF，再安装requirements-showcase.txt并运行`python scripts/reading_showcase.py`。脚本会拒绝来源、JSON或PDF哈希不匹配，检查文字边界及裁片边界。[来源清单](../examples/attention-is-all-you-need/showcase/static-manifest.json)记录物理页序、坐标、文件哈希。不会公开完整研究页，不从参考海报生成虚构论文截图。

原文节选与新增解释分别归属，见[第三方说明](../THIRD_PARTY_NOTICES.md)。没有将展示图当作阅读效率、手机实机或专业正确性证明。
