# De-AI Rewriting Strategy Guide / 去AI化改写策略指南

This guide covers **how** to rewrite text so it reads naturally without changing its meaning. It is not a guarantee against any detector. For pattern dictionaries of specific words and phrases to review, see `PATTERNS_ZH.md` and `PATTERNS_EN.md`.

---

## Core Insight / 核心认知

AIGC detectors often react to **sentence-structure fingerprints** (skeleton repetition), not individual words. Repeated skeletons are a review cue; no fixed repetition count applies across genres.

> **Evidence note:** Detector behavior varies by tool, language, genre, and revision history. Treat these patterns as heuristics, not validated universal thresholds.

AIGC检测器常对**句式结构指纹**（骨架重复）敏感，而非只看单个词汇。重复骨架只是复核线索，不同体裁没有统一次数阈值。

**Priority order / 改写优先级:**

1. Skeleton repetition (structure) / 骨架重复（句式结构）
2. Template expressions / 模板化表达
3. AI vocabulary / AI高频词汇

Swapping synonyms while keeping the same skeleton is like changing the paint on a car the police are tracking by shape. Fix the shape first.

只换近义词而保留骨架，就像警察根据车型追踪时你只换了车漆。先改车型。

## Guardrails before style / 先保真，再谈风格

Before rewriting, note the genre and user constraints. Technical, status, and academic text usually needs minimal edits; chat and public prose allow more structural freedom. “Do not delete / keep sentence count” forbids sentence deletion, merging, and reordering.

先看体裁和用户约束。技术、状态和学术文本通常只做小改；聊天和公开写作可有更大结构自由。“一句不删/保留句数”即禁止删句、合句、调序。“保长度”是硬约束：按用户指定的字符数、词数或句数及容差验收；未指定容差时，中文字符数、英文词数和句数均须与原文相等。报告前后计数与 `PASS`/`FAIL`，超差不得默称完成。

Protect these spans before changing prose: code fences, inline code, URLs, paths, commands, identifiers, LaTeX/Typst and math, citations and labels, quoted text, names, versions, dates, ranges, units, status codes, metrics, and formal terms. Keep them byte-for-byte unless the user explicitly asks for edits. Around them, preserve the actor, target, condition, scope, polarity, modality, completion state, direction, intensity, and cause/effect.

改写前先锁定：代码块、行内代码、URL、路径、命令、标识符、LaTeX/Typst 与公式、引用和标签、引文、人名、版本、日期、区间、单位、状态码、指标、正式术语。除非用户明确要求，否则逐字不动；其周围的主体、对象、条件、范围、否定、情态、完成态、方向、强度和因果关系也须保留。

Use tiers as a filter, not an automatic rewrite command: Tier 1 is usually removable; Tier 2 needs paragraph-level clustering; Tier 3 needs unusual document-level density. Do not ban all adverbs, passive voice, dashes, headings, or three-item lists. Keep a form when grammar, genre, technical meaning, quotation, or the writer's sample supports it. Do not use synonyms merely to hide repetition.

分级只用于筛选，不等于自动改写：Tier 1 通常可删，Tier 2 看段落聚集，Tier 3 看全文异常密度。不可一刀切禁副词、被动、破折号、标题或三项列举；语法、体裁、技术含义、引文或作者样本需要时应保留。不得靠同义词轮换躲重复。

### Unsourced claims / 无源论断

Never invent a source, citation key, author, year, sample size, or result. In `chat`/`public-writing`, remove an unsupported authority wrapper only when the remaining claim stands on its own; otherwise flag or remove the whole claim. In `docs`/`status`/`academic`, prefer `audit-only`: identify the missing attribution and preserve the claim unless the user asks to delete it. Put `[PENDING]` or `[SOURCE NEEDED]` in notes, not in final prose, unless the user explicitly requests placeholders.

不得编造来源、citation key、作者、年份、样本量或结果。`chat`/`public-writing` 中，仅当去掉权威套话后原判断仍独立成立，才删套话留判断；否则整条标记或删除。`docs`/`status`/`academic` 默认 `audit-only`：指出缺少归属，除非用户要求删除，否则保留原论断。`[PENDING]`、`[SOURCE NEEDED]` 默认写在备注，不写进正文。

---

## Strategy 1: Skeleton Diversification / 骨架多样化

Check adjacent paragraphs and sections for repeated sentence structures. Rewrite only when the same opening or skeleton is unusually dense; consistent structure is valid in procedures, specifications, and deliberate rhetoric.

检查相邻段落和章节是否出现异常密集的同一骨架。只有重复已经造成模板感时才改；步骤、规范和刻意修辞中的一致结构可以保留。

### Chinese Examples / 中文示例

**Bad / 差 -- 三章共用同一骨架:**

```
第三章 首先分析了温度对材料性能的影响，其次介绍了湿度的作用，此外说明了光照的效果，最后评估了综合因素。
第四章 首先分析了传感器布局方案，其次介绍了数据采集流程，此外说明了预处理方法，最后评估了整体精度。
第五章 首先分析了模型参数选择，其次介绍了训练策略，此外说明了验证方法，最后评估了泛化能力。
```

Three chapters all follow "首先分析...其次介绍...此外说明...最后评估..." -- this is a detection magnet.

**Good / 好 -- 每章不同骨架:**

```
第三章 围绕温度、湿度、光照三类环境因子展开，逐一量化其对材料劣化速率的贡献。
第四章 聚焦多源传感数据的融合问题。针对布局稀疏、采样不同步两个瓶颈，提出分级校准策略。
第五章 面向小样本场景下的泛化问题，对比了三种正则化路径，给出适用条件与局限。
```

Ch3 uses "围绕...展开", Ch4 uses "聚焦...针对...瓶颈", Ch5 uses "面向...问题". No two chapters share the same skeleton.

### English Examples

**Bad -- repeated parallel structure across sections:**

```
Section 3 first analyzes the temperature effects, then introduces the humidity model, additionally describes the light exposure protocol, and finally evaluates the combined impact.
Section 4 first analyzes the sensor layout, then introduces the data pipeline, additionally describes the preprocessing steps, and finally evaluates the overall accuracy.
```

**Good -- varied structure per section:**

```
Section 3 quantifies how three environmental factors -- temperature, humidity, and light -- each accelerate material degradation at different rates.
Section 4 tackles the fusion problem head-on. Two bottlenecks dominate: sparse sensor placement and asynchronous sampling. A tiered calibration strategy addresses both.
Section 5 asks whether regularization alone can solve the small-sample generalization problem. Three approaches are compared, with conditions and limitations noted for each.
```

### Practical rule / 实操规则

Before submitting, scan paragraph openings and adjacent skeletons. Rewrite only when a pattern clusters unusually and creates template feel; do not enforce a numeric quota.

提交前，扫描段落开头和相邻骨架。只有重复异常聚集并造成模板感时才改，不设统一次数阈值。

**Failure mode:** Over-varying structure can make text feel incoherent; readers expect some structural consistency within a genre.

---

## Strategy 2: Implicit Causality / 隐式因果

Delete connector words when context already makes the causal relationship obvious. AI text over-signposts; human text trusts the reader.

当上下文已经让因果关系显而易见时，删除连接词。AI文本过度标注路标；人类文本信任读者的理解力。

### Chinese / 中文

**Delete these when causality is clear / 因果明显时直接删除:**

- 因此 / 从而 / 这意味着 / 也正因如此 / 换言之 / 由此可见

**Before / 改前:**
> 温度每升高10°C，反应速率提高约一倍。**因此**，高温环境下的材料劣化速度显著加快。

**After / 改后:**
> 温度每升高10°C，反应速率提高约一倍。高温环境下材料劣化速度显著加快——这在户外暴露试验中已被反复验证。

The causal link is self-evident. Removing "因此" and adding a concrete grounding detail makes it sound more human.

### English

**Delete these when causality is clear:**

- thereby / thus / hence / consequently / as a result / it follows that / this means that

**Before:**
> The learning rate was reduced by a factor of 10 at epoch 50. **Consequently**, the loss curve stabilized.

**After:**
> The learning rate dropped by 10x at epoch 50. The loss curve stabilized within three epochs.

**Key rule / 关键规则:** Don't replace one AI connector with another. If you swap "因此" for "由此可见", the detection score doesn't change. Just delete.

不要用一个AI连接词替换另一个。把"因此"换成"由此可见"不会降低检测分数。直接删。

**Failure mode:** Deleting too many connectors makes reasoning feel jumpy; keep connectors where the causal link is non-obvious or crosses paragraph boundaries.

---

## Strategy 3: Concrete Over Vague / 具体化替代

Vague praise and empty intensifiers are useful review signals. Replace them with specific metrics, numbers, or observable facts only when those details exist in the source. If they do not, flag the gap or remove the unsupported claim; never invent a number.

模糊赞美和空洞的程度副词可作为复核信号。只有原文已有具体内容时，才用指标、数字或可观察事实替代。没有依据就标记缺口或删去无支撑论断，不得编数。

### Chinese / 中文

| Vague / 模糊 | Concrete / 具体 |
|---|---|
| 显著提升了性能 | 将MAE从0.23降低至0.12（降幅48%） |
| 取得了良好的效果 | 在三组对比实验中均排名第一 |
| 具有广泛的应用前景 | 已在XX电网的12个变电站部署试运行 |
| 有效解决了该问题 | 将误报率从17%压缩至3.2% |

If you cannot verify a claim, do not invent a number. In technical, status, and academic text, keep it with an `audit-only` note; in chat/public prose, flag or remove it when it cannot stand independently.

### English

| Vague | Concrete |
|---|---|
| significantly improved | reduced MAE from 0.23 to 0.12 (48% decrease) |
| achieved promising results | ranked first across all three benchmark datasets |
| has broad applications | deployed at 12 substations in XX power grid |
| effectively addresses the problem | cut false positive rate from 17% to 3.2% |

Keep `[PENDING]`/`[SOURCE NEEDED]` outside final prose unless the user explicitly requests placeholders.

### Rule / 规则

Every claim should pass the "what source-grounded detail?" test. Use an existing number, condition, object, or mechanism when available; otherwise flag the evidence gap. Never invent a number.

每个主张都应通过“原文可核对的具体细节？”测试。若没有数字，可保留已有的条件、对象或机制；若证据不足则标注待补，不得编造。

**Failure mode:** Fabricating specific numbers to replace vague claims is worse than leaving vague claims; only concretize when you have real data.

---

## Strategy 4: Vary Enumeration Structures / 列举结构差异化

When listing 3+ items, check whether the same list format is becoming mechanical. Change it only when the repetition harms readability; technical specifications and parallel comparisons may keep one format.

列举三项以上内容时，检查格式是否已经机械重复。只有影响可读性时才改；技术规格和并列比较可以保持统一格式。

### Possible formats / 可选格式

**Format A: Numbered list with periods / 编号句点式**

```
本文的主要贡献包括三个方面。(1) 提出了一种基于图注意力的多源融合框架。
(2) 设计了自适应权重分配机制。(3) 在三个公开数据集上验证了方法有效性。
```

**Format B: Semicolon-separated flow / 分号流式**

```
该方法具备三项特性：支持异步数据流输入；可在线调整融合权重；
对传感器故障具有鲁棒性。
```

**Format C: Natural narrative / 自然叙述式**

```
框架的核心在于图注意力机制（GAT），配合自适应权重模块完成多源信号的
实时融合。验证工作覆盖了 Dataset-A、B、C 三个基准集。
```

### English example

**Format A -- numbered:**

> This work makes three contributions. (1) A graph-attention fusion framework for multi-source data. (2) An adaptive weight allocation mechanism. (3) Validation on three public benchmarks.

**Format B -- semicolons in flow:**

> The method handles asynchronous inputs; adjusts fusion weights online; and degrades gracefully under sensor failure.

**Format C -- narrative:**

> At its core, the framework relies on graph attention (GAT) paired with an adaptive weighting module. We validated it on Dataset-A, B, and C.

### Rule / 规则

If adjacent blocks use the same format and the repetition feels mechanical, vary one block. Do not change a format merely to satisfy a detector.

相邻块使用同一格式且读起来机械时，改其中一块；不要为了迎合检测器强行换格式。

**Failure mode:** Forcing different structures on naturally parallel items hurts readability; technical specs and method comparisons benefit from consistent format.

---

## Strategy 5: Break Mechanical Parallelism / 打破机械排比

Parallel structures like "不仅X，还Y" or "It is not only X but also Y" are AI fingerprints when overused. Break them.

"不仅X，还Y" 或 "It is not only X but also Y" 这样的排比结构在过度使用时就是AI指纹。打破它们。

### Chinese / 中文

| Mechanical / 机械排比 | Natural / 自然改写 |
|---|---|
| 不仅需要考虑精度，还需要兼顾效率 | 精度是首要指标，但部署时的推理速度同样不可忽视 |
| 不仅提升了检测率，还降低了误报率 | 检测率从82%提升至95%，误报率同步从12%降至3% |
| 不仅适用于A场景，还可推广至B场景 | 除A场景外，该方法在B场景中也通过了验证（见表4） |

### English

| Mechanical | Natural |
|---|---|
| It not only improves accuracy but also reduces latency | Accuracy goes up; latency goes down -- the two are not in tension here |
| The system is not just fast, it is also reliable | Speed and reliability usually trade off. Here they don't: median response time is 12ms at 99.97% uptime |
| This approach addresses not only X but also Y | The approach handles X. It also turns out to work for Y, though that was not the original design goal |

### Mixed cutting approaches / 混合切割方式

When describing multiple aspects, vary the angle:

- **Scene-based / 场景切入:** "在户外环境中..."
- **Classification-based / 分类切入:** "按数据类型划分..."
- **Method-based / 方法切入:** "采用分层策略..."

Don't let every paragraph start with the same type of framing.

不要让每段都以同一种框架开头。

**Failure mode:** Breaking parallelism in formal/legal/regulatory documents destroys precision; only apply in narrative prose.

---

## Strategy 6: Delete Generic Endings / 删除万金油结尾

AI loves to end sections and papers with grand, unfalsifiable statements. These are detection magnets.

AI喜欢用宏大的、不可证伪的陈述来结束章节和论文。这些是检测磁铁。

### Chinese / 中文

**Delete or replace / 删除或替换:**

| Generic ending / 万金油结尾 | Action / 处理 |
|---|---|
| 具有重要的理论意义和工程价值 | 删除，或替换为具体成果："该方法已集成至XX系统v2.1" |
| 为该领域的发展提供了新的思路 | 删除，或改为具体后续计划："下一步将在YY数据集上测试迁移性" |
| 对推动XX事业发展具有深远影响 | 直接删除 |
| 未来可期 | 直接删除 |

### English

| Generic ending | Action |
|---|---|
| The future looks bright for this field | Delete, or replace with a specific next step |
| This work opens new avenues for research | Delete, or name the specific avenue: "The logical next step is testing on out-of-distribution data" |
| has significant theoretical and practical implications | Delete, or state what the implication actually is |
| paves the way for future breakthroughs | Delete |

### Rule / 规则

If an ending sentence could appear unchanged in any paper from any field, it should be deleted or replaced with something field-specific.

如果一个结尾句可以原封不动地出现在任何领域的任何论文中，它应该被删除或替换为领域相关的具体内容。

**Failure mode:** Some genres require formulaic conclusions (grant proposals, compliance reports); know your audience before cutting.

---

## Strategy 7: Add Voice and Personality / 注入个性

This strategy applies mainly to English writing, and to Chinese writing in non-formal contexts (blogs, reports, commentary).

本策略主要适用于英文写作，以及中文非正式语境（博客、报告、评论）。

### English

Human writing has opinions, rhythm variation, and acknowledgment of complexity. Match those qualities only when the genre and source support them.

**Practical tips:**

- **State supported judgments.** Prefer a clear comparison when the input contains one; do not invent a view to make text feel human.
- **Vary rhythm.** Follow a long analytical sentence with a short punchy one. "This works. Here's why it shouldn't."
- **Acknowledge supplied limits.** Keep uncertainty and anomalies already present in the source.
- **Use first person only when appropriate.** Do not replace passive voice with a new narrator or change responsibility.
- **Be specific about uncertainty.** Not "further research is needed" but "we don't know whether this holds above 200°C."

### Chinese / 中文

在允许主观表达的语境中：

- **表达立场：** "X方法在本场景中明显优于Y" 比 "X方法和Y方法各有优势" 更自然。
- **承认局限：** "第三组实验的结果不太理想，原因尚不完全清楚" 比 "实验结果有待进一步分析" 更像人写的。
- **混合长短句：** 不要每句都是30字。偶尔来一句7字的短句。

### Rule / 规则

Perfectly uniform structure can feel algorithmic. Vary it only where the scene allows; reproducible technical steps should stay reproducible.

完美的结构可能像算法；仅在体裁允许且重复确实造成模板感时调整。步骤、规范和作者样本中的一致结构保留。

**Failure mode:** Injecting personal voice into third-person academic writing violates style norms; only for blogs, essays, and informal contexts.

---

## Strategy 8: Natural rhythm / 自然节奏

Sentence-length variation can make prose easier to read, but it is not a target score and should not drive content changes.

句长变化有助于阅读，但不是需要优化的检测分数。

### Perplexity / 困惑度

Do not optimize “perplexity” or insert surprising words. Choose the clearest word that fits the writer and scene.

**衡量什么：** 给定前面的词，下一个词有多不可预测。


### Burstiness / 突发性

**What it measures:** How much sentence complexity varies within a passage.

**衡量什么：** 一段文字中句子复杂度的变化程度。

**How to vary rhythm / 如何变化节奏:**

- Mix sentence lengths deliberately. After a complex sentence, write a short one.
- 刻意混合句子长度。复杂句之后写一个短句。
- Vary paragraph lengths. Not every paragraph needs to be 4-5 sentences.
- 变化段落长度。不是每段都需要4-5句话。
- Use fragments only when the genre already permits them.
- 只有体裁本来允许时才使用碎句。

### Practical test / 实操检验

Read your text aloud. If every sentence takes roughly the same number of breaths, check whether the rhythm is too uniform. Do not add odd words or details merely to create surprise.

大声朗读文本。如果每句话几乎需要相同呼吸次数，检查节奏是否过匀。不要为了制造“意外”而加入生僻词或新细节。

**Failure mode:** Artificially increasing word unpredictability can produce gibberish; the goal is natural variation, not maximum entropy.

---

## Fidelity reread / 保真回读

After editing, compare protected spans and every changed fact, number, actor/target pair, condition, scope, negation, modality, and result. Check requested sentence/character/word counts when constrained.

改写后核对保护区，以及每个变动事实、数字、主体/对象、条件、范围、否定、情态和结果。用户有限长或限句时，核对对应计数。

Also check for rewrite artifacts: a newly repeated skeleton, connector chain, unnaturally uniform sentence length, or needless synonym cycling. If obvious template residue remains, make one small cleanup pass. Stop when the next edit would change meaning, technical precision, formal register, or the writer's voice; there is no benefit in chasing zero AI traces.

同时检查改写副作用：是否新增骨架重复、连接词链、句长齐整化或无意义的同义词轮换。若仍有明显套话，可再做一次小修。下一处修改会改变含义、技术精度、正式语域或作者声音时即停；不必追求“零 AI 痕迹”。

---

## Section-specific strategies / 分章节策略

Different sections have different AI-trace profiles. Apply targeted strategies.

不同章节有不同的AI痕迹特征。采用针对性策略。

### Abstract / 摘要

- **Main risk / 主要风险:** Template structure ("In this paper, we propose... We evaluate... Results show... Our method achieves...")
- **Fix:** Vary the information order. Lead with the problem or the result, not "In this paper."
- **中文修复：** 不要以"本文提出了..."开头。可以从问题、结果或方法切入。

### Introduction / 引言

- **Main risk / 主要风险:** Paragraph-level skeleton repetition (each paragraph: topic sentence → context → gap → contribution)
- **Fix:** Mix paragraph structures. One paragraph can start with a question. Another can start with a concrete example.
- **中文修复：** 不是每段都需要"总分"结构。可以用问题开头、用案例开头、用数据开头。

### Related Work / 相关工作

- **Main risk / 主要风险:** "X et al. [1] proposed... Y et al. [2] proposed... Z et al. [3] proposed..."
- **Fix:** Group by theme, not by citation. Discuss what the approaches share and where they differ, rather than summarizing each paper sequentially.
- **中文修复：** 按主题而非按引用顺序组织。讨论方法的共性和差异，而非逐篇摘要。

### Methodology / 方法

- **Main risk / 主要风险:** Excessive signposting ("First, we define... Then, we construct... Next, we apply... Finally, we optimize...")
- **Fix:** Let the method flow naturally. Use subsection headings instead of connectors to organize steps.
- **中文修复：** 让方法自然流动。用小节标题代替"首先...然后...最后..."来组织步骤。

### Results / 结果

- **Main risk / 主要风险:** Repetitive comparison sentences ("Our method outperforms X by Y%. Compared to Z, our method achieves...")
- **Fix:** Vary comparison framing. Use tables for numbers, prose for insights. Lead with a notable result already present in the source.
- **中文修复：** 变化比较的表达方式。数字放表格，见解用文字。先说原文已有的重要发现。

### Discussion / 讨论

- **Main risk / 主要风险:** Generic hedging and future work boilerplate.
- **Fix:** Be specific about limitations ("fails when N < 50") and future work ("next step: test on dataset X").
- **中文修复：** 具体说明局限（"当N<50时失效"）和下一步计划（"计划在X数据集上测试"）。

### Conclusion / 结论

- **Main risk / 主要风险:** Restating the abstract with slight paraphrase + generic ending.
- **Fix:** If the source contains a caveat or recommendation, state it directly. Do not add new reflection or advice merely to avoid repetition; cut generic endings.
- **中文修复：** 若原文已有反思、注意事项或具体建议，直接说明；不补新内容。删除万金油结尾。

**Failure mode:** Applying narrative strategies to methods/results sections hurts reproducibility; keep technical sections precise.

---

## Anti-Patterns: What NOT to Do / 不该做的事

These are common mistakes that make rewriting ineffective or counterproductive.

以下是使改写无效或适得其反的常见错误。

### 1. Don't just swap synonyms / 不要只做近义词替换

Detectors analyze sentence structure, not individual words. Changing "utilize" to "use" while keeping the same skeleton achieves nothing.

检测器分析的是句式结构，不是单个词。在保持相同骨架的情况下把"utilize"改成"use"毫无意义。

### 2. Don't delete technical content / 不要删除技术内容

Only change **how** something is expressed, not **what** is expressed. Data, methods, formulas, citations, and reasoning steps are untouchable.

只改变表达**方式**，不改变表达**内容**。数据、方法、公式、引用和推理步骤不可触碰。

### 3. Don't over-compress / 不要过度压缩

Removing too many reasoning steps makes text feel jumpy and disconnected. The reader needs enough logical scaffolding to follow the argument.

删除太多推理步骤会让文本感觉跳跃和断裂。读者需要足够的逻辑支撑来跟上论证。

### 4. Don't replace one AI connector with another / 不要用AI连接词替换另一个AI连接词

Swapping "因此" for "由此可见" or "therefore" for "consequently" does not reduce detection. Delete the connector entirely when causality is obvious.

把"因此"换成"由此可见"，或"therefore"换成"consequently"，不会降低检测分数。因果关系明显时直接删除连接词。

### 5. Don't make all sentences the same length / 不要让所有句子一样长

A common side effect of careful editing is regularizing sentence length. After rewriting, check that sentence lengths still vary naturally.

仔细编辑的一个常见副作用是句子长度趋于一致。改写后，检查句子长度是否仍然自然变化。

### 6. Don't remove all section introductions / 不要删除所有章节引言

Section-level introductory sentences that orient the reader are useful and expected in academic writing. Don't confuse them with AI template sentences. The difference: a good intro is specific to the content that follows; an AI template intro could precede any content.

章节级的引导句对读者有帮助，在学术写作中是预期存在的。不要把它们和AI模板句混淆。区别在于：好的引言针对后续具体内容；AI模板引言可以放在任何内容前面。

---

## Quick Reference Checklist / 快速检查清单

Before finalizing any rewrite, verify:

改写定稿前，确认以下各项：

- [ ] Repeated sentence skeletons are reviewed at paragraph/genre level; valid procedural repetition is kept / 已按段落和体裁复核重复骨架；合理的步骤重复予以保留
- [ ] Enumeration format changes only when repetition harms readability / 仅在格式重复影响可读性时调整列举方式
- [ ] Connector words deleted (not replaced) where causality is obvious / 因果明显处的连接词已删除（而非替换）
- [ ] Vague claims use source-provided specifics, or the missing evidence is noted outside final prose / 模糊主张仅使用原文已有具体信息；缺证据写在正文外备注
- [ ] Generic endings deleted or replaced with specifics / 万金油结尾已删除或替换为具体内容
- [ ] Sentence lengths vary naturally (mix of short and long) / 句子长度自然变化（长短句混合）
- [ ] Paragraph lengths vary (not all 4-5 sentences) / 段落长度有变化（不是都4-5句）
- [ ] Technical content fully preserved / 技术内容完整保留
- [ ] Fidelity reread completed; residual pass run only if needed / 已完成保真回读；仅在必要时做残留复核
- [ ] Read aloud test passed / 通过了朗读测试

---

## Style samples / 参考文风

When the user supplies one to three samples, use them as a voice constraint. The `style_profile.py` output is optional guidance across eight dimensions: sentence patterns, word choice, rhetoric, structure, narrative perspective, emotion, rhythm, and punctuation. Preserve the sample's register without cloning signature phrases or adding personal facts. One profile pass plus the fidelity reread is enough unless the user asks for more.

---

## Optional notes / 可选说明

Use one well-scoped model by default; switching models is unnecessary unless the user asks for comparison. Model-specific cues and punctuation guidance live in the language pattern files.

### Model-specific and punctuation notes / 模型与标点

Treat model-specific traits as hypotheses, not bans. Use the selected `--profile` and the language pattern file only when local evidence supports a cue; never apply a fixed blacklist.

Review punctuation only when it is unusually dense or inconsistent with the scene. Keep punctuation inside protected spans, quotations, and supplied style samples; normalize outside them only when readability or project format improves. No fixed quota.

Punctuation examples: keep definitions and quoted terms; replace structural dashes or normalize spacing only when meaning, voice, and project format permit.
