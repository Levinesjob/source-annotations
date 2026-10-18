# 当前版本独立复核任务

只审查公开候选，不读取私人笔记、凭据或其他工程；不发布、不覆盖成品。报告放review/cursor-final-review.md，复现文件放local/independent-final/。

## 输入

- SKILL.md、references/、README.md、requirements.txt及scripts/。
- local/attention-is-all-you-need-v1.pdf；缺少时运行scripts/fetch_example.py。
- examples/attention-is-all-you-need/annotations.json（35条）；本地生成的两种PDF、报告和HTML，步骤见案例README。
- review/STATUS.md、review/ATTENTION-STATIC-2026-10-18.md。

## 审查范围

1. 记录全部输入SHA256、工具和实际阅读范围。
2. 核对35条、导览核心观点与五项路径：任务、输入输出、Q/K/V计算、三种注意力、因果遮罩、多头、结果与条件。注意力不是本论文首次提出，核心贡献不能缩成训练速度。
3. 特别核对v1英法41.0与后续版本数字的区别、单模型与集成、测试与开发集、v1多头公式和图2的写法差别、FFN维度正文与表3不一致；不要替作者静默修改。
4. 核对11个内部入口、3个背景链接及静态图来源；检查所有页面可读、词组完整、最小9pt、p3–5不扩边。
5. 独立复现原文p2（长句）、p3–4（机制/公式）、p8（结果）。只能做文字审查时如实记录，不能声称已复现或全面重做。

输出“位置—问题—原文依据—建议修改”；机械测试不替代内容审查。45分钟是预算，无提速证明。
