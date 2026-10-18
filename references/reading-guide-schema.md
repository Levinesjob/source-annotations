# 导览数据与模块边界

`paper`保存原论文身份；`reading_guide`保存由读者/智能体依据原文写出的中文导览。脚本不进行内容提取后的自动总结，不把版式成功当作语义正确。

| 字段 | 里面存什么、怎么用 |
|---|---|
| paper.title / authors | 原论文英文标题和作者；导览中单列，不伪装成中文概括 |
| paper.identifier / url / sha256 | DOI或arXiv版本标识、真实来源链接和文件指纹；标识缺失用 `/` |
| reading_guide.headline | 16–19pt的中文核心观点标题，不是作者原始标题 |
| core_view | 两三句：问题、关键方法、最重要且有依据的发现/贡献 |
| mechanism_flow（可选） | 三个有原文依据的计算步骤，每步含expression和meaning；以可检索文字画成简图。不适合三步表达时省略，不强迫套用 |
| prerequisites | 简短先修概念与本文中的用法，不写百科长文 |
| background.links | label、可选short_label和真实url；没有核对过的知识库路径不能添加 |
| target_minutes / steps[].minutes | 建议预算与每项分配，必须加总相等，不是实测提速 |
| steps[].title | “类别：一句解释”，类别按论文调整，不强制固定问题分类 |
| steps[].targets | 原句标注ID，或原PDF页序page和point；label说明具体章节/图表/公式 |
| target.printed_page（可选） | 已人工核对的印刷页码；不用于计算PDF目的地 |

页级入口使用point `[0,0]` 并在label写“整页入口”；不得伪称精确定位。`page`从原始PDF第一页计为1，不含新导览。原句ID先在原始文字层匹配；实际插页后由映射转换为页面对象与坐标，偏移只应用一次。页边扩展仅在既有标注导出中加上对应横向偏移。

证据类别保持原Skill中的四类：实测、推导、作者主张、导读解释。显示名称可完整展开，数据中的`主张/解读`仍兼容。不能因为作者在摘要中写了判断就标成实测。

工程职责：

- `analyze_pdf`：读取纸张和排版特征。
- `compile_content`：整理人工提供的导览字段及缺省行为。
- `plan_brief`：仅计算布局与链接区域，先确认整页可容纳。
- `render_brief`：绘制原生文字和细线，嵌入字体。
- `resolve_links`：根据真实页对象建立GoTo。
- `prepend_guide.prepend`：插页、保留书签/标签、保存新文件。
- `verify_inserted`：保存后重新打开，逐页比对并核查目的地。

`*.guide-report.json`包含风格分析、使用字号、原始与成品哈希、目标位置、实际通过项目和限制。机器不验证观点是否正确；公开前仍需对照原论文审查。
