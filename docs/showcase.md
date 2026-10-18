# README 展示素材

本轮只重组产品说明和展示图片，未修改原始论文、批注记录、已有PDF、手机阅读HTML或PDF算法。

## 来源与生成

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-showcase.txt
.\.venv\Scripts\python.exe scripts/fetch_example.py
.\.venv\Scripts\python.exe scripts/showcase.py
```

需要已有且哈希匹配的`output/waypoint-opd-v1-annotated.pdf`及报告；本轮沿用已发布的21页44条成品。输出在`examples/waypoint-opd/showcase/`。展示脚本只读PDF，使用PyMuPDF 4倍渲染和Pillow裁剪组合，不重新排论文文字，不调用图像模型。

| 文件 | 读者看到什么 | 真实来源 |
|---|---|---|
| hero.png | 原文与旁注保持同一空间关系 | 标注PDF物理第2页，即原文第1页 |
| before-after.png | 相同原句的原始/标注对比，右下为同页旁注放大 | 原文第3页，上方原句使用相同裁剪框和缩放；场景提问属于外围说明 |
| evidence-navigation.png | 阅读导览 → 作者原句 → 同页解释 | 实际GoTo“第4页·正确性限制”及a12定位框 |
| hero-mobile.png | 术语原句与同页旁注分区放大 | 相同PDF中a02对应位置，不是新界面 |
| evidence-mobile.png | 窄屏的导览和证据放大 | 与桌面证据图相同GoTo和旁注 |

上述5张论文展示图是**静态PDF裁图组合**，不是阅读器界面截图或操作录像。裁剪会省略周边内容，但不重写可见正文；查看完整语境请打开样例PDF。证据图的终点通过成品真实GoTo和报告交叉验证，不凭文案编造位置。

[manifest.json](../examples/waypoint-opd/showcase/manifest.json)记录输入SHA256、每张图尺寸、物理页序、PDF点坐标和图像SHA256。原论文页码与PDF物理页码不同，前置导览使原文第4页对应物理第5页。原内容按[CC BY 4.0及第三方说明](../THIRD_PARTY_NOTICES.md)归属，展示不暗示论文作者认可项目。

## 尺寸与可读性

主图1440×760；前后对比1440×680；证据图1440×880。移动版本分别780×1040和780×1130。PNG采用不透明中性背景，深色页面不会反转真实论文文字。README使用picture的媒体条件在600px以下选择放大素材；不支持该条件的客户端仍可点击PNG和PDF查看大图。

宽屏优先保留空间关系；窄屏优先显示完整术语和中文解释，明确标为同页分区放大。前后对比在手机缩小显示时不能保证所有小字可读，README明示点击大图，并另有手机主图；不宣称一张整页图能在所有屏幕直接读清。

完整生成和缩放检查结果见[本轮展示验收](../review/SHOWCASE-2026-10-18.md)。5秒/30秒理解是信息架构目标，尚未做陌生用户计时测试。

## 本轮文件清单

- 重组：README.md。
- 新增文档：docs/usage.md、docs/architecture.md、docs/showcase.md、docs/plans/2026-10-18-repository-showcase.md。
- 新增素材：examples/waypoint-opd/showcase/下5张PNG与manifest.json。
- 生成与打包：scripts/showcase.py、requirements-showcase.txt；scripts/package_preview.py补充白名单。
- 状态与来源：review/SHOWCASE-2026-10-18.md、review/STATUS.md、TODO.md、CHANGELOG.md、THIRD_PARTY_NOTICES.md。

共19个新增或修改文件；已有LICENSE、SKILL.md、必需依赖与PDF算法不变。


## 四角阅读框架（后续改版）

`framework-overview.png`（1440×860）与`framework-mobile.png`（780×1040）围绕亲自读原论文说明阅读导览、原文旁注、证据追溯和可复现产物。它们是**阅读价值说明图，不是软件界面截图或技术模块依赖图**。关键词来自已有SKILL、JSON和导出脚本；“两种PDF”指只插导览与正文旁注两条不同路径，不代表结构保留保证相同。

```powershell
.\.venv\Scripts\python.exe scripts/framework_overview.py
```

同一次运行输出两张PNG、两份可编辑SVG和`framework-manifest.json`。PNG使用随包Noto字体并不透明渲染，作为README的稳定预览；SVG保留可编辑文字，未嵌入字体，单独打开时依赖Noto或系统中文字体，不保证不同系统的字形完全一致。两种格式共用同一绘图场景，生成时检查文本越界。

手机主图只将外围标题从“AI学术精读助手”改为“把解释放回正在读的原文旁”；论文裁图、原句、批注没有改写。阅读体验和差异通过真实局部展示，不靠抽象工具名称说明。新版记录见[四角改版验收](readme-framework-review.md)。

本次后续改版共13个文件：README.md、THIRD_PARTY_NOTICES.md、docs/showcase.md、docs/readme-framework-review.md、scripts/showcase.py、scripts/framework_overview.py；showcase目录的hero-mobile.png、manifest.json，以及新增的framework-overview.png/.svg、framework-mobile.png/.svg、framework-manifest.json。上一节19文件为前一轮历史清单。

## 用动作展示阅读过程

README首图改用标题到核心观点的动画；正文分别展示补背景、回查原文两个动作，保留四角总览与原文/旁注对比。旧静态图仍在仓库，不覆盖或删除。

```powershell
.\.venv\Scripts\python.exe scripts/reading_motion.py
```

沿用本页的可选依赖，无需FFmpeg、浏览器、模型或API Key。生成六张GIF（桌面1200×740、窄屏780×1000）、六张静态末帧，以及[motion-manifest.json](../examples/waypoint-opd/showcase/motion-manifest.json)。中间三阶段检查图只放入被忽略的local/motion/，不进入发布包。

| 动图 | 动作与来源 |
|---|---|
| motion-concept.gif | 固定v1真实标题裁图 → 已有导览标题与问题 → core_view；导览文本按屏宽重排，非重新生成理解 |
| motion-background.gif | 先修知识 → 成品PDF三个真实外链 → 第一条外链的目标内容摘记；摘记依据Spinning Up Policies，不是网页截图 |
| motion-evidence.gif | 导览第五项边界 → 真实GoTo入口 → a12原句；目标是原文第4页、PDF物理第5页，交叉核对报告坐标与原句 |

每项都有对应的-mobile.gif与-still.png。每圈约12–13秒，关键画面停留2.6–5秒，单张GIF约0.38–0.56MB。没有闪烁或声音；README提供静态链接，并用picture的prefers-reduced-motion在系统选择减少动态效果时选静态末帧。不支持该媒体条件的客户端可手动打开静态版。

**它们是基于真实内容与目标位置制作的动作示意，不是阅读器录屏。** 动图里的指针不能点击；README整张背景图链接到真实资料，其他两张链接到对应PDF。PDF里的链接可实际使用。动画速度不代表生成耗时或阅读提速。

输入PDF、JSON与报告的SHA256必须匹配才会生成；脚本校验裁剪边界、文字越界、链接目的地与最终GIF时长/大小，记录输入及GIF/静态末帧哈希。它只读取已有产物，不修改PDF生成逻辑。见[动图验收记录](readme-motion-review.md)。
