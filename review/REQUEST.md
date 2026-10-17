# 当前版本独立复核任务

只审查本项目公开候选文件，不读取私人笔记、账号、凭据或其他工程。不发布、不修改生成器，不覆盖现有成品。报告写到review/cursor-final-review.md，复现文件放local/independent-final/。

## 输入

- SKILL.md、references/、README.md、requirements.txt及scripts/。
- 原文local/waypoint-opd-v1.pdf（arXiv:2610.21601v1）；缺少时运行scripts/fetch_example.py。
- examples/waypoint-opd/annotations.json（44条）。
- output/waypoint-opd-v1-annotated.pdf、waypoint-opd-v1-reading-brief.pdf、waypoint-opd-mobile.html。
- review/ACADEMIC-REGRESSION.md和STATUS.md。

## 实际要做

1. 先记录各输入SHA256、所用工具和实际阅读范围。
2. 独立对照原文核查全部44条、导览的核心观点及五项路径：术语、长句逻辑、公式逐项解释、结果数字、比较对象、限制条件；四类前缀不混淆定义、实验、作者主张和整理者解释。特别核查a11/a26/a27/a28/a30为推导、a31为实测、a42为解读，及用户新增的机制/14B/中间点结论。
3. 检查导览8个内部链接和3个背景入口；印刷页码与物理页码区分。核查p3–4不扩边时完整词组、9pt下限、遮挡和重叠；有条件时逐页渲染检查。
4. 在独立输出位置按README重建，并独立复现原文p1、p4、p7（语言/方法/结果）。明确是关键页复现，不声称重做全文语义分析。不能执行或看图时逐项记未完成。
5. 输出“位置—问题—原文依据—建议修改”，区分关键错误、非关键建议和无问题；不要因测试通过宣称解释正确。

45分钟仅为预算；旧版32条审查不能代替本轮。报告结尾给实际完成范围、未完成项和是否存在阻止预览发布的错误。
