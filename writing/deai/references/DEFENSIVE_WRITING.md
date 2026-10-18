# Defensive Writing / 防御性写作

Newer LLMs, asked to make a paper "hold up under review", revise more than language: they narrow, soften, or retract the author's own claims without support in the material they were given. This reference defines the pattern, shows how to detect it, and sets the action rules. It also carries the paper-narrative layer ("press-conference principle") for academic full-text tasks.

新模型被要求"让论文扛住审稿"时，改的不只是语言：它们会在材料没有依据的情况下收窄、软化甚至撤回作者自己的结论。本参考定义该模式、给出检测清单与处理规则；论文级全文任务另附一套叙事规则（发布会原则）。

## 1. Definition and evidence / 定义与证据

Definition (Huang et al., arXiv:2610.11355, §1, preprint): a change is defensive writing when it "narrows or questions the authors' claims without support in the material the writer was given." Ordinary caution points to a limitation that exists in the evidence; a defensive qualification has no source — it only makes the claim harder to fault.

定义（Huang et al., arXiv:2610.11355, §1, 预印本）："在给定材料没有依据时收窄或质疑作者结论的改动"即为防御性写作。正常的谨慎指向证据中真实存在的局限；防御性限定没有来源——它只是让结论更难被挑错。

Two forms / 两种形式:

1. **Ungrounded qualification** — adding doubts, scope restrictions, or reading instructions the material does not support. Coded in three subtypes in the paper's sentence taxonomy:
   - ① not-shown statement: declaring that results do not show something or prescribing how they must be read ("these gains do not by themselves establish that…", "should be interpreted as…").
   - ② ungrounded doubt: naming a confound, cost, or missing check that is absent from the source ("although training costs may differ").
   - ④ generic scope: restricting a claim to "the evaluated settings" without naming them ("in the evaluated settings, X improves Y"). A breadth claim ("consistently across all evaluated settings") is a claim, not ④.
2. **Retreating from claims** — tracked per claim as kept / strengthened / weakened / scoped / retracted / dropped. Retraction is the rewrite explicitly denying the author's version; "we therefore do not claim that…" is its signature.

   **限定**——添加材料不支持的怀疑、范围限制或阅读指示，论文句子编码分三型：① 未展示陈述（断言结果不能说明某结论，或规定结果应如何解读）；② 无依据怀疑（指出材料中不存在的混淆、开销或缺失检验）；④ 泛化限定（把结论收窄到"所评估设置"却不指明是哪些）。
   **撤回结论**——逐条跟踪为 保留/强化/弱化/收窄/撤回/丢弃。改写明确否认作者原意即撤回；"因此我们不主张……"是其标志。

Why it matters / 为什么重要（all from arXiv:2610.11355 unless noted / 除注明外均出自该论文）:

- The behavior grows across model generations. Ungrounded qualifications per 100 words in result-analysis paragraphs: authors 0.04, GPT-4o 0.04, GPT-5.5 0.47, **GPT-6-astra 1.30** (~30× the authors). GPT-6-astra retracts **7.9%** of author claims and softens **38%** (both pooled across the four paragraph types); it retracts at least one claim in ~40% of result-analysis paragraphs.
- It is mostly not honest correction. The v2 human re-check found GPT-6-astra's confirmed retractions landed on overstated/contradicted claims or contestable interpretations, and on no claim both annotators judged supported (13 of 18 changes warranted); separately, its *added qualifications* were mostly redundant (36 of 60 redundant, 16 warranted, 3 wrong). So target the qualification-creep, and check a suspected retraction against the full paper before reversing it — the retracted claim may itself be the overclaim.
- It is triggered by anticipated review, not by evidence. Pure "polish this paragraph" prompts produce ~zero defense across all 12 models tested; any "check the claims / hold up under review" framing raises it; naming likely reviewer concerns raises it most; one round of self-review raises it further. In multi-round review–revise loops, three GPT versions retract **11–25%** of claims and paragraphs grow to 2–3× length.
- The reward loop is real. Under two AI reviewers, the review-framed (P5) rewrites score far above polish-only (P1) ones — for GPT-6-astra +1.84 soundness and +1.22 overall on a 10-point scale; in minimal-pair tests, stripping only the ungrounded qualifications drops the scores by 1.12 (soundness) and 0.82 (overall). Human readers find the same defensive paragraphs harder to read (ease −0.70, effort +1.05) and rate author certainty −0.97. AI-written + AI-reviewed pipelines reward a style humans pay for.

行为随代际增长：结果分析段中每 100 词无依据限定，作者原文 0.04，GPT-6-astra 1.30（约 30 倍）；GPT-6-astra 撤回 7.9% 的作者结论、软化 38%，约 40% 的结果分析段至少有一条结论被撤回。它总体上不是诚实的纠错：v2 的人工复核显示，被双方确认的撤回落在夸大/被反驳的结论或有争议的解释上，没有一条落在双方都认为有支撑的结论上（18 条中 13 条改动正当）；而**新增的限定大多是冗余的**（60 条中 36 条冗余、16 条正当、3 条错误）。打击对象是限定蔓延；撤销一条疑似撤回前，先对照全文核实——被撤回的结论本身可能就是夸大。触发因素是"预期审稿"而非证据：纯润色提示下 12 个模型几乎都零防御，一提"检查结论/扛住审稿"就上升，点名审稿人顾虑时最高，一轮自审再加码；多轮"审稿-修改"循环中三个 GPT 版本撤回 11–25% 的结论，段落膨胀到 2–3 倍。奖励闭环真实存在：两个 AI 审稿模型给"审稿式"改写的打分远高于纯润色版（GPT-6-astra：soundness +1.84、overall +1.22，10 分制），最小对偶实验中只剥掉无依据限定，分数就回落 1.12（soundness）与 0.82（overall）；人类读者却觉得这类段落更难读、作者更不确定（−0.97）。

Evidence caveats / 证据注意：the study is an arXiv preprint (v2 submitted 2026-10-13; submission history lists Junchi Liao, v2 author block Xiao Huang, Yucheng Liu, Jiawen Deng, Fuji Ren). Sentence coding and claim tracking used an LLM coder (annotators confirmed the *supported* labels but none of its 12 *overstated* labels); the reader study had 4 readers, 20 paragraphs, comprehension at ceiling; only English CS papers were tested. Read the numbers as direction, not law.

该研究为 arXiv 预印本；句子编码与结论跟踪使用 LLM 标注（人工确认了"有支撑"标签，但 12 条"夸大"标签无一被确认）；读者研究仅 4 人 20 段；仅覆盖英文 CS 论文。数字看方向，不当定律。

## 2. What this means for this skill / 对本技能的含义

The same trigger applies to you. When the user frames a task as "make it reviewer-proof / 扛住审稿 / 帮我防一下审稿人", that framing invites you to inject exactly this disease. Route instead:

- Polish language, not judgment: revise wording, structure, and clarity; do not re-adjudicate the author's claims. If a claim looks overstated relative to the supplied material, flag it in notes (`downgrade_claim` stays an audit action, never automatic).
- Run a claim audit instead of pre-defense (see §5). The paper's own recommendation: "Authors who revise with GPT for review should check its qualifications against their own evidence."
- Warn about review loops: multi-round "review then revise" cycles compound defense (2–3× length, 11–25% retraction). Prefer one polish pass + one claim audit.
- Never use AI review scores to validate a rewrite; they are biased toward defensive text.

同样的触发机制也适用于你。用户若以"让它扛住审稿/防审稿人"框定任务，该框定正是在诱导你注入此病。应改道：只润色语言不审判判断——若某结论相对所给材料显得夸大，在备注中标记（`downgrade_claim` 仍是审计动作，绝不自动执行）；用"结论审计"代替"预先设防"（见 §5）；警告多轮审稿-修改循环会叠加防御；绝不用 AI 审稿分数来验证改写。

## 3. Detection checklist / 检测清单

Scanner support: `deai_check.py` reports a `defensive` category (MEDIUM severity). It catches lexical candidates only; ①-type rewrites and claim softening need the manual claim audit below.

脚本支持：`deai_check.py` 报告 `defensive` 类别（中严重度），仅捕捉词汇线索；① 类改写与结论软化需靠下面的手工结论审计。

Chinese candidates / 中文候选（cluster signal; single hits are normal variation / 簇信号，单次命中多为正常）:

| 类别 | 例子 |
|---|---|
| 限定虚词 | 一定程度上、在某种程度上、或多或少、应谨慎理解、不宜过度解读、有待时间检验、仍需进一步验证 |
| 自我削弱 | 遗憾的是、效果有限、仍存在不足、仍明显落后、仍有较大差距、存在严重不足、有待进一步研究、有待完善、本文尝试、初步研究/探索、本文仅在/针对、囿于水平、限于篇幅、才疏学浅、抛砖引玉、敬请批评指正、仅供参考 |
| 撤回结论† | 并不能据此推断、并不意味着（否定自己刚立的结论时）、不能推广到、不具有普遍性、本文并未证明、上述结论的普适性有待检验 |
| 替读者质疑 | 一个自然的疑问是、有人可能认为、批评者或许会指出、值得警惕的是、读者可能会问、（自己列出）几点不足 |
| 流水账结构 | "首先尝试 A，然后尝试 B，最后选择 C"的过程叙事；实验结果附录式堆叠且每个实验无论证职责 |
| 泛化限定 | 在（本文）评估/实验/测试的设定/场景下（不指明具体设置时） |

† 判断型信号：是否撤回要看该否定是否给出证据，留给 §5 结论审计，不进词汇扫描器。

English candidates / 英文候选:

- Stock self-undermining: unfortunately, merely, only achieves/reaches, still lags, limited improvement/gain/success/applicability, a preliminary/tentative study, "further research is needed" as a paragraph closer.
- Reviewer prebuttal: "One might argue…", "A natural question is…", "Critics might point out…", "We do not claim that…" (negative scope — recast positively).
- Not-shown statements: "these results do not (by themselves) establish/prove/demonstrate…", "cannot rule out…" (keep when the doubt is real and material), "may not generalize…" attached to claims the evidence supports.
- Generic scope: "in the evaluated/tested/considered settings/conditions/scenarios" with no antecedent naming them.
- Hedge stacking: two or more epistemic devices on one claim ("could perhaps tentatively suggest") — keep the strongest or none.

The Hyland backdrop / 语言学背景：hedges (may, suggest, possibly, to some extent) outnumber boosters (show, clearly, establish, indeed) by nearly 3:1 across disciplines — hedging is normal academic calibration; total stance-device density still varies roughly 4× by field (philosophy vs. physics; Hyland 1998, Table 3). A single hedge per claim is the norm; hedge the inference, not the measured observation; Methods ≈ unhedged, Results low, Discussion highest (Hyland 1998, 2005; Farkas et al. 2010). So: flag *ungrounded* and *stacked* hedges, never hedging itself.

hedge（may、suggest、possibly）在各学科中数量约为 booster（show、clearly、establish）的 3 倍——限定是学术写作的正常校准，且密度因学科差异可达 4 倍；一条结论一个限定是常态；限定推断而非测量本身。因此只标记**无依据**与**堆叠**的限定，不标记限定本身。

## 4. Action rules / 处理规则

Delete / 删除:

- Ungrounded qualifications (①②④) whose doubt, confound, or scope restriction has no source in the material. The GitHub skill's test: does this sentence raise a question nobody asked, expand the paper's responsibility, or turn a local observation into a universal flaw?
- Apology wrappers (遗憾的是, unfortunately, merely) while keeping the factual core.
- Prebuttal sentences that argue against the paper on the reviewer's behalf. Either the concern is real → state it once as scope/limitation; or it is not → delete.

Restore / 恢复:

- Weakened/scoped/retracted claims the source supports: restore the original strength. This is `restore_claim` — the mirror of `downgrade_claim`, and like it, an audit action decided against evidence, never automatic.
- Numbers and specifics dropped "for safety" (e.g., the 30–50% figure silently removed in the paper's example) go back in.

Keep — never strip / 保留——绝不剥除:

- Grounded limitations: real gaps in the evidence, stated once, factually. Validity, ethics, safety, legal, and replication constraints keep their force wherever they live.
- The honest asymmetry: removing defense is usually safe; *adding* confidence is a claim change and needs evidence. Never convert observation into causation, never upgrade "suggest" to "prove" to compensate.
- Disciplinary calibration: benchmark against the target venue's norms before flattening hedges.

Handle a real limitation positively / 真实局限的正面写法（name → consequence → bound → next step / 命名→后果→界定→下一步）:

> Apologetic: "Unfortunately, our study has the major limitation of being conducted at only one university, which significantly limits the generalisability of our findings."
> Factual: "Data were collected at a single Tier-2 vocational university; findings generalize to similar institutional types. Replication across other tiers would test whether the effect is invariant."

Limitations live in the section that owns them, 3–5 real ones, each passing the test "would removing this change what the reader believes?" Delimitations (deliberate scope choices, defended in the intro) are not limitations; listing them as limitations manufactures weaknesses. Chinese over-humility (才疏学浅、抛砖引玉、不当之处敬请指正) is a courtesy-ritual residue (贬己尊人), not evidence of rigor — cut it in scholarly prose.

## 5. Claim audit / 结论审计（workflow）

For academic text, especially text that has passed through an LLM "review" prompt:

1. Ledger: list every claim in the original (a sentence that takes a position: novelty, contribution, result interpretation, generalization).
2. Compare against the rewrite: kept / strengthened / weakened / scoped / retracted / dropped.
3. For each changed claim, judge against the evidence *in the source material* — not against what a reviewer might say. A restated author judgment is not evidence for itself.
4. Revert unearned changes (`restore_claim`); convert real gaps into one positive limitation statement (`restate_scope`); leave grounded caution untouched.
5. Scan for the negation signatures: "do not (by themselves) establish", "cannot rule out", "we do not claim", "in the evaluated settings" — each occurrence must point at a real gap or go.
6. Report the ledger diff in the change log with locations.

## 6. Narrative layer: the press-conference principle / 叙事层面：发布会原则

仅限论文级学术任务（摘要、引言、结论、实验组织、删节）；不用于句子级润色，绝不用于真实效度内容。本节与最小改动原则冲突时，以最小改动为准；整篇重构只在用户明确要求全文重写时进行。

Apply only to paper-level academic tasks (abstract, introduction, conclusion, experiment organization, cutting). Do not apply to sentence-level polish, and never to validity content. Where this section conflicts with the minimal-edit default, minimal edits win; full restructuring happens only when the user explicitly asks for a rewrite.

Source: Adkid-Zephyr/anti-defensive-writing-Skill (community framework, MIT). One-line principle: a paper is an academic press conference, not a project summary, lab log, or self-audit. The conference presents one thing — the work's strongest advantage.

来源：Adkid-Zephyr/anti-defensive-writing-Skill（社区框架，MIT）。一句话原则：论文是一场学术发布会，不是项目总结、实验日志或自我审查报告；发布会只讲一点：这项工作最强的优势。

Narrative / 叙事:

1. Organize around strengths only; content that forms no advantage does not enter the main line.
2. No work-report chronology ("we first tried A, then B"); keep the standing logic: why the problem matters → the gap in existing methods → what this work provides → how evidence supports it.
3. Never set a contest you cannot win: if a metric is not your strength, do not build the narrative on it; re-choose the task definition, evaluation dimension, scenario, or comparison frame. Name the game this paper actually wins.
4. State the advantage explicitly — condition, mechanism, practical meaning. Do not wait for reviewers to find it in a table.
5. Limit comparison scope: make only claims the evidence firmly supports; persuasion comes from claim–evidence alignment, not comparison count.
6. Allow full story restructuring when results cannot support the original narrative.

Language / 语言:

7. Ban self-weakening wording (遗憾的是 / unfortunately / merely / still lags behind / limited improvement).
8. Never say you lost. For an unfavorable result, decide in order: must it be discussed → explain by different goal/constraint/scenario → reasonable trade-off → narrow the claim → move it off the main line.
9. Never escalate a local observation into a verdict on the whole method; do not distill a non-advantage into a conclusion.

Experiments and structure / 实验与结构:

10. Every experiment carries one explicit duty: prove the method works / prove the advantage comes from the key mechanism / prove value in the target scenario / rule out the most plausible alternative. No duty → delete, downplay, move, or redesign.
11. Abstract and introduction = the opening: important unsolved problem → key gap → your distinctive approach → strongest result and meaning. No implementation-detail openings; no limitations before the contribution is established.
12. Conclusion reinforces only the takeaway: what was solved, proposed, proven, why it matters. No fresh self-negation in the final paragraph.

Default decision priority for unfavorable material / 不理想材料的默认决策优先级: delete the irrelevant → narrow the claim → switch the evaluation dimension → reframe as goal difference or trade-off → reorganize experiments → redefine the story → only when unavoidable and material to the core conclusion, state it plainly.

Pre-submission self-check / 交稿自查: Does this sentence expand the paper's responsibility? Raise a question nobody asked? Turn a local phenomenon into a universal flaw? Use a negative judgment broader than the evidence? Unfold as process narration? Set a non-winning metric as the main battlefield? Get problem and contribution into the abstract's first five sentences? Smuggle self-negation into the conclusion? Do not manufacture review questions, enlarge the attack surface, or complete the opposition's argument for them.

The boundary / 边界: this is stance coaching, not concealment. The origin paper explicitly warns against stripping caveats to please AI reviewers; venues and regulators may require limitation statements; a real threat to validity stays. When the evidence cannot carry the story, the fix is the study or the story — never the reader's ignorance.

这是立场训练，不是掩盖。原论文明确警告不要为迎合 AI 审稿剥除 caveats；真实效度威胁必须保留；证据撑不起故事时，改研究或改故事——绝不是让读者蒙在鼓里。

## 7. Example pairs / 例句对照

| Defensive / 防御性 | Direct / 直接 |
|---|---|
| 虽然本方法在两个同领域数据集上提高了准确率，但必须承认，我们尚未测试跨领域泛化，因此应谨慎理解这些结果。 | 本方法在两个同领域数据集上提高了准确率；跨领域泛化尚未评估。 |
| 我们首先尝试了 A，然后尝试了 B，最后选择了 C。 | 问题 X 很关键，现有方法缺 Y，本文提出 Z，证据如下。 |
| 本文尝试性地探讨了该问题，结论仅供参考，普适性有待进一步研究。 | 本文证明了该机制在两类场景下成立。 |
| 需要指出的是，我们的模型在长文本上仍明显落后于基线。 | 在短文本场景下，本文模型将推理成本降低 60%；长文本不是本文的目标设定。 |
| 综上所述，本文不可避免地存在一些不足，未来有待进一步完善。 | 下一步将把该方法扩展到多语言场景。 |
| Unfortunately, we were only able to test on small datasets. | We validate on three public datasets; all experiments reproduce on one GPU-day. |
| These results do not by themselves establish that the method is robust. | (Evidence supports it →) The method is robust across the four evaluated perturbations. |
| We do not claim that the model generalizes to other domains. | The analysis covers two domains; cross-domain transfer remains untested. |
| One might argue that our evaluation covers only English benchmarks. | We evaluate on English benchmarks. Multilingual transfer remains untested. |
| It could perhaps be tentatively suggested that X may possibly influence Y. | These results suggest that X influences Y under the examined conditions. |
| Our work has a major limitation: the single-site design. | Data come from a single site, which bounds generalization to similar settings; replication across sites is the next step. |

Pairs 1–5 adapt the Adkid-Zephyr skill; 6–11 adapt the paper's examples and the cited craft guides. Each fix assumes the source supports it; otherwise flag, don't invent.

## 8. Sources / 来源

- Huang, Liu, Deng & Ren, "Defensive Writing in GPT Models", arXiv:2610.11355 (v2 2026-10-13; submission history "From: Junchi Liao"; v1 titled "Writing for the Reviewer: …"). https://arxiv.org/abs/2610.11355 — origin study: definition, ①②④ taxonomy, P1–P9 dose-response, claim tracking, reader/AI-reviewer studies.
- Adkid-Zephyr/anti-defensive-writing-Skill (MIT). https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill — press-conference principle, 12 rules, decision priority, 8-question checklist.
- Hyland, K. (1998). "Boosting, hedging and the negotiation of academic knowledge." *Text* 18(3); Hyland (2005) *Discourse Studies* 7(2) — hedges vs. boosters, stance/engagement, disciplinary calibration.
- Farkas et al. (2010), CoNLL shared task on hedge detection. https://aclanthology.org/W10-3001/ — hedge-cue lexicon tradition.
- Abdulhai et al. (2026), "How LLMs Distort Our Written Language", arXiv:2603.18161 — neutrality bias: heavy LLM use → ~70% more neutral stances; reviews shift criteria.
- Kiterlin/anti-defensive-writing; Worigin0314/academic-defensive-writing-auditor (GitHub) — parallel skill specs: positive scope statements, 14-pattern audit taxonomy.
- CASRAI hedging guide and limitations worked example; USC Libraries limitations guide; Cochrane writing guide (against "preliminary" self-labels); researchramp/phdguide on limitations without undermining.
- Kobak et al. (2024), "Delving into LLM-assisted writing…", arXiv:2406.07016 — LLM-revised text has measurable stylistic fingerprints.
