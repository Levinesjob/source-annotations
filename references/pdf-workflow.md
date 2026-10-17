# PDF 记录与运行

前置导览的当前规范见[academic-native](academic-style.md)及[导览字段](reading-guide-schema.md)。只插导览执行`python scripts/prepend_guide.py 原文.pdf 数据.json 新文件.pdf`，保留原研究页；现有正文注释继续使用下述annotate路径。两者不能混用结构保留结论。

Python 3.11+，先安装 `requirements.txt`。依赖和中文字体均随包说明；脚本无模型 API、无遥测、无后台联网。

```sh
python -m pip install -r requirements.txt
python scripts/fetch_example.py
python scripts/annotate.py local/waypoint-opd-v1.pdf examples/waypoint-opd/annotations.json output/waypoint-opd-v1-annotated.pdf
python scripts/render.py output/waypoint-opd-v1-annotated.pdf local/render
python -m unittest discover -s tests -v
```

## 里面存什么

`paper` 记录标题、作者、版本链接、许可和原 PDF 的 SHA256。哈希用于防止套错版本，不代表论文可信。

`annotations` 每条记录：

| 字段 | 里面存什么、怎么用 |
|---|---|
| id | 不重复的短编号，用于修订与反馈 |
| page | 从1开始的PDF页序，不是印刷页码 |
| quote | 需在该页准确定位的原句或原词；不使用省略号 |
| occurrence | 原句重复时明确第几次；从1开始，默认不允许歧义 |
| kind | term词义、sentence长句直译、key重点、note额外解释、formula公式 |
| evidence / tag | 显示给读者的证据类别与固定内容标签；不显示内部ID |
| limitation | 紧随对应发现显示的限制条件 |
| symbols / design / example | 公式每项含义、设计理由和注明出处的原文例子 |
| source_image_rect | 公式原图局部坐标，用于单栏版保留准确符号；需目视核对裁图 |
| side | left用于词句解释，right用于重点及补充说明 |
| text | 实际显示的中文解释；词义写成“原词：本文义” |
| reason | 为什么选择这处，留给审查者，不印在页边 |
| nature | 标明作者主张、条件、实验结果、限制或整理者推断 |

新论文先确定原文，再自行生成记录，不复用示例的哈希与页码。文本提取与公式可能有误，判断以原PDF为准。

词义必须显示完整 `quote` 对应的词组，不能把 student-generated trajectories 缩成 trajectories。中文批注默认9.5pt，最低9pt；英文单词不能完整容纳时会尝试其他字号/必要扩边，而不从词中间强行拆开。

## 时间路线（可选）

用户需要按时间抓重点时，加入 `reading_guide`：`target_minutes`为预算，`goal`为本轮理解目标，`audience`为基础要求，`steps`每项包含`title/minutes/read/question/pages`，`defer`说明先跳过什么，`checkpoint`说明到点如何自查。各步时间必须加总为目标时间；`status`标记`budget_not_measured`，不能冒充实测。

前置仅一页：`problem`存一句问题，步骤存原页码与建议时长，末尾放一行图例；不展示答案、核心发现或免责段落。公式的symbols/design/example直接排在原公式旁。`--pages`复现指定原页时不加导读页。

最新阅读地图使用`headline`直接显示核心观点、`plain_method`用一句话说明方法；步骤title/read直接解释问题、方法、机制、证据与边界。每步targets可以引用annotation定位原句，也可指定page/point定位图表与公式，label显示清楚的原页和对象名；导出为PDF内部跳转，手机页面保留同一坐标目标。详细推导留在原文，不再用任务式提示吊读者胃口。

需要背景铺垫时，`background.paragraphs`放简短任务背景，`background.links`以label/url记录已核对的基础和直接前序资料；PDF和单栏共用。词义类型不显示分类前缀。

明确要求删除首页竖排版本条时，`presentation.omit_first_page_vertical_stamp`填写完整准确文字。只在内存中删除唯一匹配的竖排条并记录修改，横排原文有任何变化即失败；不覆盖原始PDF。未配置时不改原文。

`core_findings`保存3–5条发现及主证据标注ID；每条必须标黄并附限制。`coverage`记录实验领域、主图表和标注的关系；`main_source_pages`说明正文范围。脚本对照实际Figure/Table标题清点正文主图表并要求同页标注；人工继续检查相关性。附录范围和例外需另行说明。

手机原页入口：先生成最终标注PDF，再执行`python scripts/mobile.py 原文.pdf 标注.json output/waypoint-opd-mobile.html`。默认读取输出目录的`waypoint-opd-v1-annotated.pdf`，其他名称用`--pdf`指定。页面直接由该PDF渲染，嵌入图片可离线阅读；哈希不一致会拒绝生成，避免两端版本分裂。外部资料链接需要网络。

## 输出与失败

输出 PDF 保留原页内容和正文尺寸，必要时增加页边。与其同名的 `.report.json` 记录匹配框、批注框、字号和扩边情况。

找不到原句、原句歧义、版本不符、空间不足时，命令非零退出，不以猜测定位生成成品。需要先修改记录或适配工具后重试。

`--pages 1,4,7` 只导出指定原页，供复现检查；可见标签与全稿保持一致。
