# 三类论文插页回归

2026-10-18当前运行：Attention v1（单栏，15页）、ResNet CVPR官方版（双栏，9页）、Adam v9（公式密集，15页），共39页原文。只验证导览排版、插入及结构保留，不把回归样例作为其他公开精读案例。原文均存local/，不对外分发。

运行`python scripts/fetch_example.py`后执行`python scripts/regression_academic.py --fetch`；已有匹配哈希缓存可省略--fetch。版本和哈希在脚本中锁定。每页原文像素/文字与链接、书签等按prepend_guide验证，输出local/academic-regression/results.json。ResNet末项找不到精确标题，明确降为整页入口。

结构保留结论只适用于只插导览路径。人工批注、表单、附件、页标签由专门测试样本覆盖，不冒充真实论文包含这些对象；完整PDF/UA、XFA与富媒体仍未验收。实际环境Windows/Python3.13.5/PyMuPDF1.26.5。
