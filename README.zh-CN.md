# Corpus → Knowledge Engineering（语料知识工程）

**English** | [简体中文](README.zh-CN.md)

![License](https://img.shields.io/github/license/gootf/corpus-knowledge-engineering)
![Release](https://img.shields.io/github/v/release/gootf/corpus-knowledge-engineering)
![Stars](https://img.shields.io/github/stars/gootf/corpus-knowledge-engineering)

**把一堆书变成一小撮可审计的 agent 技能——并且能证明每条结论出自哪里。**

把原始语料（几百本书、合并 TXT、EPUB/PDF、OCR 扫描件）交给 AI 建知识库，通常得到两种结果：一份与源文本毫无可核查关系的目录式摘要，或一份建立在幻觉页码上的漂亮综合。两者都不能作为知识资产使用。

本仓库提供一条把语料当作**工程对象而非摘要对象**的管线：确定性规范化 → 按书切分 → 从作者自己的目录恢复章节地图 → 带完整 provenance 坐标的 claims → 路由进一个知道自己*不*包含什么的知识系统。

## 没有它会怎样

| 故障 | 没有它 | 有了它 |
|---|---|---|
| **无法验证的出处**——claims 引用"第 27 页"却无处可查 | 漂亮的引用，虚构的基础 | 坐标：`source → chapter → section → 印刷页码 → OCR 页码 → 行号`；两种页码都保留（二者偏移因书而异） |
| **每本书都像新发现**——300 本书 → 300 个"技能"，无人审计 | 无限膨胀的书摘库 | 决策价值路由：SKILL / EVIDENCE / TOOL / REJECT / STOP + Merge Test + 注册表漂移政策（实测约 10:1 压缩） |
| **提取器的章节检测是噪声**——目录条目、脚注、重复的页眉都比真实标题先命中 | 章节地图错位，所有下游 claims 全部错位 | 五路结构恢复，以作者自己的目录 + 页码标记为准；LLM 只补缺口 |
| **合并文件被当成一本书**——`Merged-A+B+C.txt` 是三部作品粘在一起，各有各的目录和页码 | 转换器把三部作品"概括"成一部；跨书结论张冠李戴 | 先按每书标记确定性切分（L2） |
| **残缺文件被 LLM 补全**——只有扉页 + 目录 + 参考文献，正文全缺 | 模型凭空"写"出缺失章节；provenance 永久污染 | Completeness Gate 在生成前拒绝（S1–S4 信号） |
| **脏 OCR 凭文件名误判**——名为 "scan" 的文件其实很干净（反之亦然） | 每个 300 项语料误拒约 20 个可用文件 | 定量噪音指标，而非命名启发 |

## 核心思想

N 本书的语料最终变成**远少于 N 的知识单元**。管线的工作是对每份材料判定它属于哪一类：

```
SKILL    — 新的决策原语（判断规则族）→ 带 provenance 编译
EVIDENCE — 支撑既有原语 → 登记，按 primitive_id 索引
TOOL     — 可形式化调用的规则（逻辑检查、计算器）→ 独立工具层
REJECT   — 残缺、不可验证或冗余 → 记录在案，绝不静默丢弃
```

```
Book A ──┐
Book B ──┼──→  Merge Test：新决策原语？  ──→  1 个家族技能
Book C ──┘          （同作者、同问题）            （而不是 3 份摘要）
```

**压缩就是成功指标**：几百项 → 一小撮可运行技能，是逐项可追踪的结果（每项的 merge/evidence/archive/reject 去向都有记录），不是缩水。

## 为谁而做

| 你 | 场景 | 本仓库给你 |
|---|---|---|
| **知识工程师** | 从书/文档/OCR 语料构建知识库或技能库 | 经过验证的 L0→L5 管线 + 确定性结构恢复 + freeze 基线纪律 |
| **AI agent 开发者** | 想把书编译成 agent 真正会加载的技能 | 两类编译模板、安装与验证步骤、draft- 与正式版命名陷阱 |
| **研究者 / 分析师** | 综合多来源并保持归因诚实 | 三层 claim 分类（source / agent / cross-source）、每条坐标含双页码、编者导言与正文分离 |

## 为什么是这条管线

1. **确定性优先，LLM 其次。** 作者自己的目录和页码标记胜过任何提取器的自动检测（实测：朴素 grep 4/9 章 vs page-anchor 9/9）。LLM 补缺口，绝不发明结构。
2. **防膨胀是工程化的，不是指望的。** Merge Test + novelty 评分（0–3）+ 注册表漂移率（<5% → <1%）+ Stop Condition：每份材料都可以合法地什么都不是。没有这些，规模化必然膨胀成摘要库。
3. **拒绝是一等公民。** 残缺 → 生成前 REJECT；脏样本 → 定量指标；用户优先指定的材料也不能推翻门禁。系统知道什么时候*不*编译。
4. **SOP 是状态机，且经过测试。** 六个终态（FREEZE / SKILL / EVIDENCE / TOOL / REJECT / STOP），DFA 式确定性，历史样本可回放；v3 形态用 13 分量特征向量替换语义守卫（LLM 当传感器、计算当控制器）。
5. **开箱即用的脚本。** 六个轻依赖工具（`scripts/`）：结构扫描、page-anchor 章节地图、EPUB→文本（纯标准库）、PDF→文本、分块 PDF 提取、窗口化 claims 分解助手——外加章节地图模板。

## 快速开始

```bash
git clone https://github.com/gootf/corpus-knowledge-engineering.git

# 把 skill 复制进你的 agent 技能目录
# （SKILL.md + references/ + scripts/ + templates/ 是一个自包含 skill）

# 写章节地图前先扫描一本书的标题格式：
python scripts/structure-scan.py path/to/book.txt

# 零依赖提取 EPUB：
python scripts/epub-to-text.py book.epub book.txt
```

然后按 SKILL.md 走：L0 原始（不可变）→ L1 规范化 → L2 切分 → L3 章节地图 → L4 编译 → L5 路由。完整工作方法（格式状态、陷阱、评估门、发布标准）在 skill 的 `references/` 里。

## 诚实的边界

- **不是自动摘要器。** 管线是确定性 + agent 引导；策展决策（重复、合并、拒绝）需要人工门禁。
- **不是 RAG 索引器。** 产出的是带 provenance 的技能，不是对原始语料的检索——语料始终是事实来源，技能是编译后的视图。
- **不给你的语料打保票。** 压缩率和成本模型是在一个大型语料上测得的；当作校准先验，不是承诺。
- **含大量逐字摘录的章节不进入任何公开发布**（版权）；短引用与衍生摘要保留。

## 结构

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 管线手册——阶段、原则、陷阱、门禁、发布标准 |
| `references/` | 协议细节：向量机 SOP、窗口化 claims 分解、评估门、发布标准 |
| `scripts/` | 六个工具（结构扫描、章节地图、EPUB/PDF 提取、claims 助手） |
| `templates/chapter-map.yaml` | 确定性章节地图骨架 |

## License

MIT — 见 [LICENSE](LICENSE)。

## 相关

方法论被用作 [EACKS](https://github.com/gootf/eacks) 的摄取参考（S0 摄取 / S1 分解 / S5 整合）。
