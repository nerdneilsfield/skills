# Chinese Prose Rules / 中文行文规则

House rules for Chinese prose in this repository. They apply to rewriting,
reviewing, and drafting Chinese text. English prose follows
`PATTERNS_EN.md` instead.

## 1. Prohibition-led sentences / 禁令式开头

A sentence that opens with 不能、不得、禁止、不要、不应、不允许、不可 reads
as a ban list rather than a description of what the system does.

> 不要在未评测时把设计目标写成已验证性能。

The main line of a document should be what the system does, in what order, and
what it skips when an input is missing. Prohibitions stay only where
correctness depends on them.

Every prohibition opening is reported. The scanner does not decide which
prohibitions the document owns — that is a judgement call, and a table of
exceptions would only hide it.

| Case | Action |
| --- | --- |
| The document does not own the decision | Rewrite. State the behavior positively: 「未完成评测时，性能状态记为"尚未实测"」 |
| The document owns it, and violating it has a consequence | Keep the force. Say the consequence once: 「删除注册表项会导致系统无法启动」 |
| Repeated across a document | The document is managing the reader, not explaining the system. Move the rule to the owning artifact. |

Do not build an exception list of "safe" prohibition words. Ask instead: does
this document own this decision, and what happens if it is violated?

## 2. Balanced contrast templates / 平衡句式

不是……而是……、不仅……更是……、与其说……不如说…… force the writer into a
symmetric frame the source may not support. Delete the part before the pivot,
or split the sentence into two paragraphs.

> 这不是一个组件，而是一套流水线。

Becomes:

> 组件串成了一条流水线。

When the pivot carries the real claim, keep that half alone. When both halves
carry separate facts, split them. Never keep the symmetric frame just because
it sounds balanced.

## 3. Disclaimers in the deliverable / 正文里的免责说明

"本文不讨论 X"、"我们不会在本文中处理 X"、"请注意，本文不保证 Y" turn the
deliverable into a defense transcript. A drafting instruction leaked into the
artifact: "do not mention X" became "we do not address X".

The fix is not a softer disclaimer. X is either in the document or it is
absent.

> 本文不讨论实现细节。

Becomes: nothing. If implementation detail matters, write it. If it does not,
the sentence was never needed.

> 本文不保证复现性。

Becomes: 「复现步骤见附录 B」 — or delete the sentence if there is no appendix.

One exception is real: a limit the reader would otherwise assume away. Then
state it as a property of the thing, not as a disclaimer about the writing:
「复现需要 RTX 4090」, not 「本文不保证复现性」.

A document that needs many of these sentences is a document whose scope was
never settled. Fix the scope, not the sentences.

## 4. Word preference table / 用词表

The table lives in `scripts/word_rules.py` and is authoritative.

- A rule with a replacement names the preferred term: 脊背 → 后背/背部,
  深入骨髓 → 些许/轻微, 乐了 → 笑了笑, 降维打击 → 大获全胜, 亚空间 → 混沌.
- A rule marked avoid names a word that must not appear. Rewrite the clause as
  concrete action, state, or detail instead of hunting for a synonym. The
  avoided groups cover body and pain imagery, emotion and intensity words,
  religious and ritual vocabulary, mechanical and clinical vocabulary, stock
  scenic props (石子、石头、湖面、涟漪), calqued English frames (冒充、
  假冒、当做、当作、当成), technical calques (洗成、塞进、吸到、凑足、
  偷偷、悄悄、静默+修改动词、有预算的、留出数据/留出集), and emotional
  calques that name a body sensation or a therapy-frame verb instead of the
  feeling (烧心、接住情绪、情绪被接住).
- Every avoid-word is reported wherever it appears, including in a domain term
  where it happens to be correct (燃烧效率, 机械结构, 精密加工, 静默安装).
  The scanner does not know the document's domain; the reviewer does. Do not
  add per-word exception lists to the table.
- The scene requirement behind the table: plain Chinese prose, verbs doing the
  work, scenes built rather than events narrated, no exaggerated extreme
  rhetoric, and characters shown through action, speech, and expression.

### Calqued frames / 直译框架词

冒充、假冒、当做、当作、当成 are English frames carried over: masquerade as,
treat as, pass off as. They arrive in Chinese already framed as an
explanatory gesture toward the reader, and they name an equivalence the
source may not have asserted.

> 这被当作一条规则。

Rewrite by stating the fact directly: 「这条规则适用于所有请求」.

> 把错误当做失败来处理。

The treat-as frame still reads as a deliberate equivalence. State the branch
instead: 「错误一律按失败处理」.

Every hit is reported, including the ones that turn out to be correct in
context. The scanner does not judge which; the reviewer decides.

Do not swap in another stock word of the same register. 猛地 does not become
忽然; it becomes the action itself.

### Technical calques / 技术黑话

Calqued English verbs and AI-generated jargon read as machine translation,
not as Chinese technical writing. The fix is the same as for the calqued
frames above: state the fact with a plain verb.

> 把预测结果洗成观测来源。

The clause names a conversion the source may not have asserted. State the
provenance directly: 「把预测结果的来源记为观测」.

> 将所有候选吸到同一条边界。

Rewrite with the actual relationship: 「所有候选对齐到同一条边界」.

> 把恢复操作写成有预算的诊断策略。

Budget is a property of the operation, not its adjective: 「诊断操作的
预算约束」 or 「恢复操作设预算上限」.

> 用留出集做独立验证。

held-out has no authoritative Chinese translation (§5). The calque
留出数据/留出集 is reported wherever it appears; the rendering is the
original term: 「held-out 集」.

## 5. Translation terminology / 译文用词

Translated technical terms must follow the PRT (信息化部) standard or the
terminology the relevant authority publishes. When a term has no such
authoritative translation, or the domain has a settled conventional rendering,
use that rendering. Only when neither exists, keep the original term.

Order of preference:

1. PRT / 信息化部 standard translation, or the translation published by the
   relevant authority.
2. The conventional rendering inside the domain, as used by practitioners.
3. The original term, untranslated.

A literal translation that no standard and no practitioner uses is a defect:
flag it, then replace it with the authoritative or conventional form. Never
invent a translation for a term that already has one.

Worked examples:

- threshold has an authoritative rendering 阈值. The older literal 门限
  is reported by the word table and replaced with 阈值.
- held-out has no authoritative translation and no settled conventional
  rendering. It stays held-out. The literal calque 留出数据/留出集 is
  reported wherever it appears; do not let it stand.

## 6. Character portrayal / 人物塑造

Each character needs a distinct temperament and habits. Show them through
action, speech, and expression rather than through an adjective assigned by
the narrator. A character described as 果断 is not portrayed; a character who
answers before the question is finished is.

## 7. Verdict and exceptions

These rules are house defaults, not absolute bans. Genre still governs:

- Technical, status, specification, and reference text keep normative force
  where the document owns the decision and violating it has a consequence.
- Safety, security, privacy, legal, and compliance text keeps prohibitions.
- Quotation and cited sources keep the source's own wording.
- A negative statement about what the system or method cannot establish is a
  property of the object, not a ban on the reader:
  「两个视图的最优匹配不能保证第三个视图一致」 states a validity
  boundary of the method; it stays negative. The prohibition scanner still
  reports it — the reviewer confirms it is a fact about the object before
  keeping it.

The scanner reports candidates. The reviewer decides, using the scene rules in
`REWRITING_GUIDE.md`.

### Do not build exception lists

An exception table is itself a form of over-defense. A list of "safe" words or
"safe" prohibition contexts looks thorough, and it quietly moves the decision
from the person who understands the document into a lookup table that cannot.

The scanner therefore reports every hit, including the ones that are correct in
context. The reviewer's job is to judge, and judgement is not a table.

Source: [HERO-Anti-OverDefense](https://github.com/wanshuiyin/HERO-Anti-OverDefense)
(MIT), family R — "rubrics": judgement replaced by machinery. The same
reference's family O — scaffolding built for a future nobody asked for — is why
this file ships rules rather than a rule engine.
