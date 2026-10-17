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

所有图是**静态PDF裁图组合**，不是阅读器界面截图或操作录像。裁剪会省略周边内容，但不重写可见正文；查看完整语境请打开样例PDF。证据图的终点通过成品真实GoTo和报告交叉验证，不凭文案编造位置。

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
