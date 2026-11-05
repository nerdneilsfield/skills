# Agent skills 行为评测报告 · 第二轮

生成时间：2026-11-05。全部数据在 `/tmp/behavior-eval`，脚本在 `harness/`，
结果在 `results/round2/`，原始记录在 `runs/` 与 `runs/round2/`。

- 快照 commit：`f6acaf93ad113e57fc46b88a4d5d42d37bd15076`（`results/round2/snapshot_commit.txt`）
- 模型：`claude-sonnet-5-5`，传输 `direct`（Anthropic 订阅直连，未走本地代理）
- 运行数：**97**（trigger 21 + partB_na 8 + difficulty 60 + nafill 8），与预期一致
- 完成标记：`results/round2/DONE`，`finished=2026-11-05T13:07:14`
- 本轮**未**合并第一轮的 24 个代理运行；第一轮结论只在第 D 节作对比引用

本轮不覆盖 `REPORT.md`（第一轮报告），两者独立。

---

## 0. 结论摘要

- **counterweight 触发**：改描述后仍然不可靠。三个"应当触发"的简短改代码请求里，
  `safety-path-traversal` 0/3、`explicit-no-plan` 0/3，`pushed-against-rules` 2/3。
  三个负对照 0/3，无误触发。描述里已写"however small or terse"，模型仍不加载。
  判定：**触发层是主要缺陷，且改描述没有修好**。
- **deai**：新增 3 个更难用例（n=5）。with 79/85 vs without 80/85，Fisher p=1.0，
  token **+18.8%**、时间 +18%。判定：**无差别，且更贵**。与第一轮（+46%）方向一致。
- **qi-read-paper**：新增 3 个更难用例（n=5）。with 71/75 vs without 67/75，Fisher p=0.37，
  token **+8.4%**、时间 +22%。差异全部来自 `qirp-latency-evidence-gap` 的 3 个断言
  （with 优），但 Fisher 不显著；另有 2 个断言 without 更优。判定：**无显著差别，代价为正**。
- **补跑（NA 填充）**：`bug_fixed`、`coverage_gate_met`、`no_invented_facts`、
  `no_invented_params` 四个断言本轮全部可测，NA 计数 **0**。其中
  `coverage_gate_met` 两臂同样失败（无区分度），`bug_fixed` 两臂同样通过。

**n=5 能支持什么**：能给出每个断言的两臂通过次数与 Fisher 精确检验；能区分
"两臂稳定同结果"和"单次波动"；本轮所有 30 个 with_skill 运行都确认加载了 skill，
所以差异不是"没加载"造成的。
**n=5 不能支持什么**：不能给通过率的置信区间；Fisher 在 5 vs 5 的样本上只能排除
极端差异（例如 5/5 vs 0/5，p≈0.008），中间地带（5/5 vs 3/5）p=0.44，什么都说明不了；
不能区分"skill 有效但方差大"和"skill 无效"。

---

## A. 触发测试（描述改动后）

每个用例 3 次，共 21 次运行。`loaded` 由 transcript 里的 `Skill` 工具调用判定，
不是由文本猜测。全部 21 次运行里插件均正确注册为 `evalplug:counterweight`。

| 用例 | expected_trigger | loaded | 判定 |
|---|---|---|---|
| `trigger-safety-path-traversal` | True | **0/3** | 不合理 |
| `trigger-explicit-no-plan` | True | **0/3** | 不合理 |
| `trigger-pushed-against-rules` | True | 2/3 | 可接受 |
| `trigger-exploration-not-authorized` | False | 0/3 | 正确 |
| `trigger-neg-explain-code` | False | 0/3 | 正确 |
| `trigger-neg-review-only` | False | 0/3 | 正确 |
| `trigger-neg-prose` | False | 0/3 | 正确 |

逐次记录：`safety-path-traversal` [F,F,F]；`explicit-no-plan` [F,F,F]；
`pushed-against-rules` [T,T,F]；四个负对照全部 [F,F,F]。

### A.1 对"没加载是否合理"的逐例判断

负对照（4 个）都正确：`exploration-not-authorized` 是提问（"How would we add
multi-region support?"），`neg-explain-code` 是解释现有代码，`neg-review-only`
明说"Don't change anything"，`neg-prose` 是改文风。这些都不该加载，0/3 是满分，
说明当前描述没有制造误触发。

三个正例要分开看。

`pushed-against-rules` 2/3，可以接受。这条请求长、并且明确要求"跳过 retry 和 backoff"，
正好落在描述里"when that request would otherwise grow a ... retry, cache, fallback"上。

`explicit-no-plan`（"Add a --quiet flag to the export command. Do not write a plan."）
0/3 **不合理**。这是最短的一句改代码请求，描述里专门写了"however small or terse"
和"including when the user says skip the plan"，两条都命中，模型仍然不加载。
`trigger-safety-path-traversal`（"Join an uploaded filename to the upload directory."）
0/3 **同样不合理**，它是最典型的"fix a bug"请求。

诊断实验（**不计入 97 次**）把原因锁在"请求太短"而不是环境上：

| 实验 | 变更 | 结果 |
|---|---|---|
| `diag-noagents` | 去掉工作区里的 `AGENTS.md` | 0/3 加载，仍走 Read/Edit |
| `diag3` | 同一句短请求，重复 4 次 | 0/4 加载，token 稳定在 78–79k |
| `diag2` | 同一任务 + 一句 workflow 提示 | **1/1 加载**，出现 `Skill` 调用 |

`diag2` 证明插件和 skill 本身可加载；`diag3` 证明短请求下模型稳定不加载，不是随机。
`AGENTS.md` 的 YAGNI 内容不是原因（去掉后依旧 0/3）。

一个重要的补充事实：`safety-path-traversal` 的 t1 和 t3 **没加载 skill，但把
path traversal 修对了**（`src/store.py` 加了 `resolve()` + `is_relative_to` 检查），
t2 只跑了 `ls -la` 没改代码。也就是说，这条用例上 skill 没被加载，任务照样完成——
这不是 skill 的功劳，但也不是失败。

---

## B. 补跑：第一轮的 NA 断言

第一轮有 4 个断言因为缺 venv 而不可测（各 4 次 NA）。本轮建好
`/tmp/behavior-eval/venv`（Python 3.13.15，pytest 9.2.0，coverage 7.17.2），
`cw_checks.py` 的 `py()` 改走 `EVAL_PYTHON`，`_has()` 改为真实 `import` 探测。
四个断言现在全部可测，**NA 计数 0**。

| 断言 | 用例 | 臂 | 运行数 | 通过 | NA |
|---|---|---|---|---|---|
| `bug_fixed` | `earned-regression-in-repo` | yagni | 2 | 2/2 | 0 |
| `bug_fixed` | `earned-regression-in-repo` | counterweight | 2 | 2/2 | 0 |
| `coverage_gate_met` | `ci-gate-conflict` | yagni | 2 | **0/2** | 0 |
| `coverage_gate_met` | `ci-gate-conflict` | counterweight | 2 | **0/2** | 0 |
| `no_invented_facts` | `deai-boundary-heavily-cited-academic` | with_skill | 2 | 2/2 | 0 |
| `no_invented_facts` | `deai-boundary-heavily-cited-academic` | without_skill | 2 | 1/2 | 0 |
| `no_invented_params` | `qirp-reproduction-assessment` | with_skill | 2 | 1/2* | 0 |
| `no_invented_params` | `qirp-reproduction-assessment` | without_skill | 2 | 2/2 | 0 |

（`*` 为修复后结果，见第 D 节；按运行当时的结果是 0/2，两次都因为把"§6.1 / §6.2 / §6.4"
当成了凭空编造的数字。）

逐条说明：

- `bug_fixed`（`earned-regression-in-repo`）：两臂都是 pytest rc=0，且新增回归测试落在
  `tests/test_scheduler.py`（仓库内），没有只在 scratch 里写测试。两臂无差异。
- `coverage_gate_met`（`ci-gate-conflict`）：两臂 4 次运行全部 coverage=50% < 门槛，
  同样失败。lint 两臂都修好、测试数量两臂都没超标。**这个断言在四个运行里零区分度**，
  它证明的是"任务本身的门槛比两个臂都高"，不是 skill 的问题。
- `no_invented_facts`：with 2/2，without 1/2（t2 出现 `unexplained_numbers=['1']`，
  是原文 "top 1% of queries" 里的 1 被误读，属于残留误报类别，见 D 节）。
- `no_invented_params`：见 D 节的评分器修复。

NA 清零是这一节唯一的硬结论：**第一轮那 4 个 NA 不是"skill 无差别"，是当时测不了。**

---

## C. 新增 deai / qi-read-paper 用例（n=5，两臂各 5 次，共 60 次）

**加载情况**：6 个用例 × 5 次 with_skill 运行，全部 5/5 加载了 skill（由 `tools.json`
里的 `Skill` 调用核实）。因此**没有运行因为"skill 未加载"被排除**。这与第一轮不同，
第一轮存在 with_skill 臂没加载 skill 的运行。

### C.1 逐用例总分（每行 = 5 次运行各自通过的断言数）

| 用例 | 断言数 | with_skill | without_skill | 两臂合计 | Fisher |
|---|---|---|---|---|---|
| `deai-latex-cited-section` | 6 | [6,5,6,6,6] = 29/30 | [6,6,6,6,6] = 30/30 | 59/60 | p=1.0 |
| `deai-long-template-doc` | 6 | [5,5,5,5,5] = 25/30 | [5,5,5,5,5] = 25/30 | 50/60 | p=1.0 |
| `deai-quote-and-hedge-mix` | 5 | [5,5,5,5,5] = 25/25 | [5,5,5,5,5] = 25/25 | 50/50 | p=1.0 |
| `qirp-figure-contradicts-claim` | 4 | [4,4,4,3,3] = 18/20 | [4,4,4,4,4] = 20/20 | 38/40 | p=0.49 |
| `qirp-latency-evidence-gap` | 5 | [5,5,5,5,5] = 25/25 | [4,5,5,5,2] = 21/25 | 46/50 | p=0.11 |
| `qirp-reproduction-blockers` | 6 | [6,6,5,5,6] = 28/30 | [6,5,6,3,6] = 26/30 | 54/60 | p=0.67 |

汇总：deai 三项 with 79/85 vs without 80/85（p=1.0）；qi-read-paper 三项
with 71/75 vs without 67/75（p=0.37）。**没有任何一项达到 p<0.05。**

### C.2 逐断言（两臂各 5 次，通过次数）

`deai-latex-cited-section`（with / without）：

| 断言 | with | without | 方向 |
|---|---|---|---|
| `latex_refs_intact` | 5/5 | 5/5 | both-pass |
| `no_invented_numbers` | 5/5 | 5/5 | both-pass |
| `no_strength_softening` | 5/5 | 5/5 | both-pass |
| `output_written_to_file` | 5/5 | 5/5 | both-pass |
| `protected_span_survival` | 5/5 | 5/5 | both-pass |
| `template_openers_gone` | 4/5 | 5/5 | without 优 |

`deai-long-template-doc`：

| 断言 | with | without | 方向 |
|---|---|---|---|
| `closing_section_removed` | **0/5** | **0/5** | both-fail |
| `cross_paragraph_skeleton_broken` | 5/5 | 5/5 | both-pass |
| `no_invented_numbers` | 5/5 | 5/5 | both-pass |
| `output_written_to_file` | 5/5 | 5/5 | both-pass |
| `protected_span_survival` | 5/5 | 5/5 | both-pass |
| `span_count_preserved` | 5/5 | 5/5 | both-pass |

`deai-quote-and-hedge-mix`：5 个断言（`empty_intensifiers_reduced`、
`no_false_decision`、`no_new_numbers`、`output_written_to_file`、
`protected_span_survival`）**全部 5/5 vs 5/5**，两臂完全一致。

`qirp-figure-contradicts-claim`：

| 断言 | with | without | 方向 |
|---|---|---|---|
| `no_unqualified_overclaim` | 5/5 | 5/5 | both-pass |
| `states_main_numbers` | 5/5 | 5/5 | both-pass |
| `stops_after_round_one` | 4/5 | 5/5 | without 优 |
| `surfaces_subset_conflict` | 4/5 | 5/5 | without 优 |

`qirp-latency-evidence-gap`：

| 断言 | with | without | 方向 |
|---|---|---|---|
| `cites_locations` | 5/5 | 3/5 | with 优（p=0.44） |
| `confounded_candidate_count` | 5/5 | 4/5 | with 优 |
| `no_ab_measured` | 5/5 | 5/5 | both-pass |
| `no_reproduction_claim` | 5/5 | 5/5 | both-pass |
| `replay_not_ab` | 5/5 | 4/5 | with 优 |

`qirp-reproduction-blockers`：

| 断言 | with | without | 方向 |
|---|---|---|---|
| `cites_locations` | 5/5 | 4/5 | with 优 |
| `no_false_reproduction` | 4/5 | 5/5 | without 优 |
| `no_invented_params` | 4/5 | 4/5 | 平分 |
| `states_arrival_process_missing` | 5/5 | 4/5 | with 优 |
| `states_weights_unpublished` | 5/5 | 5/5 | both-pass |
| `weighs_columns_differently` | 5/5 | 4/5 | with 优 |

**both-pass 断言**（两臂各 5/5，本轮不区分）：deai 14 个、qi-read-paper 5 个。
**both-fail 断言**：`deai-long-template-doc` 的 `closing_section_removed`，两臂 0/5。
这条断言当前难度下两臂都过不了，是断言/fixture 的问题，不是 skill 的结论。

### C.3 token 与耗时（每臂 5 次的均值）

| 用例 | with tok | without tok | Δtok | with 耗时 | without 耗时 | Δtime |
|---|---|---|---|---|---|---|
| `deai-latex-cited-section` | 69377 | 61606 | +12.6% | 15.2s | 14.3s | +6% |
| `deai-long-template-doc` | 83189 | 63453 | **+31.1%** | 22.1s | 15.4s | +44% |
| `deai-quote-and-hedge-mix` | 66416 | 59342 | +11.9% | 10.2s | 8.6s | +19% |
| `qirp-figure-contradicts-claim` | 48866 | 45460 | +7.5% | 34.0s | 28.2s | +21% |
| `qirp-latency-evidence-gap` | 76410 | 71902 | +6.3% | 43.8s | 32.9s | +33% |
| `qirp-reproduction-blockers` | 75106 | 67544 | +11.2% | 33.7s | 28.1s | +20% |

分 skill：**deai +18.8% token / +18% 时间；qi-read-paper +8.4% token / +22% 时间。**
所有 60 次运行都是首次尝试通过（`attempts=1`），没有重试、没有 `run_failed`、
没有 `is_error`。

### C.4 统计检验说明

Fisher 用两臂的断言级通过/失败计数（非配对，各臂独立运行）。逐用例 p 值见 C.1。
唯一接近显著的是 `qirp-latency-evidence-gap`（p=0.11），它由 without 臂 t5 单次
崩到 2/5 贡献，方向不稳。用符号检验看"哪些断言 with 优/without 优"：
with 优 8 个断言、without 优 4 个、平分 1 个，n=12，双尾 p≈0.39。**没有任何角度能
把本轮判成"有增益"。**

---

## D. 与第一轮的差异；评分器改动及改动时机

### D.1 结论层面的差异

| 项 | 第一轮 | 第二轮 | 说明 |
|---|---|---|---|
| deai token 代价 | +46% | +18.8% | 用例换了（本轮是新 fixture），不能直接比 |
| qi token 代价 | +30% | +8.4% | 同上 |
| deai/qi 是否区分 | 无差别 / 无差别偏负 | 无显著差别 | 方向一致 |
| counterweight 触发率 | 69%（4 个用例 0/2） | 3 个正例 2/3、0/3、0/3 | 描述改了，`pushed-against-rules` 从 0/2 → 2/3 |
| Part B NA | 4 个断言各 4 次 NA | 0 NA | venv 补齐 |
| with_skill 未加载 | 存在 | 30/30 全加载 | 本轮 deai/qi 结果不受"没加载"污染 |

**counterweight 描述改动没有修好短请求触发。** 第一轮 4 个用例 0/2，第二轮其中
`pushed-against-rules` 升到 2/3，另外两个仍是 0/3。描述已经从"before implementation"
扩写到"Run before any request to change code, however small or terse"，模型行为没跟上。

### D.2 评分器/harness 改动清单（按时机）

**改动发生在任何第二轮结果产生之前（预注册，不计入事后调整）：**

1. `check_no_new_numbers` 改为同时判 `answer_blob + file_blob`（原来只判文件），
   并新增 `unexplained_numbers()` 带推导识别（`4×12000×6≈288KB`、`1/ln2≈1.44`、
   `400万`↔`3.9×10⁶`），`numeric_tokens()` 展开科学计数法。目的是修第一轮
   `no_invented_facts` / `no_invented_params` 的 NA 与漏判。
2. 新增检查 `no_markers`、`latex_intact`、`answer_slop_reduced`，扩展 `CHECKS`。
3. `run_eval.run_failed()`：空回答或 0 token 判为运行失败，重试一次。
4. 新 fixture 与用例在**跑之前**写好，断言在**跑之前**固定：
   `fixtures/deai/{long-template-doc.md,latex-cited.tex,quote-mix.md}`、
   `fixtures/papers/MERIDIAN.md`、`evals/deai_round2.json`、
   `evals/qi-read-paper_round2.json`、`evals/counterweight_trigger.json`。

**改动发生在看到第二轮结果之后（事后修复，必须披露）：**

5. **`TEXT_SUFFIXES`（`.tex` 缺失）**——`harness/run_part_a.py` 原来只把
   `.md/.txt/.py` 当可评分文本。`deai-latex-cited-section` 的产出是 `.tex`，
   于是 `latex_intact` 判的是空 blob、`template_openers_gone` 全部返回 NA。
   修复：把 `.tex/.typ/.rst/.json/.yaml/.yml` 加入列表。影响 **19 个判定**
   （deai-latex 两臂全部 `latex_refs_intact` 由 False→True、`template_openers_gone`
   由 NA→真值）。这是 harness 缺陷，不是放宽门槛：`.tex` 文件确实存在，
   检查只是看不到它；真正的丢引用仍会失败。
6. **`SECTION_REF`（章节号误报）**——`unexplained_numbers()` 把 `§6.2`、`Section 6.2`、
   `第 6.2 节`、`Table 1` 当成"凭空编造的数字"。修复：比较前先剥掉章节/图表编号。
   影响 **4 个判定**（`deai-quote-and-hedge-mix/with_skill/t4`、
   `qirp-reproduction-blockers` with t2/t3 与 without t3、`qirp-reproduction-assessment`
   with t1）。两个臂都因此变好，不是单方面救 with_skill。
   反向验证：`2.9%`、`512 KB`、`288 KB`、`48 小时`、`1.44 倍` 仍被判为未解释。

两处事后改动都由 `harness/regrade_round2.py` 从保留的 `workspace_after` 重算，
原始结果文件 `partA_difficulty.json` / `partA_nafill.json` 未被覆盖，
修正后写入 `*.regraded.json`，两份并存。报告里 C 节和 B 节引用的是修正后的数字。

**残留的已知误报类别**（本轮未改，避免继续向"让结果好看"方向调）：
`no_new_numbers` 会把 `top 1% of queries` 里的 `1`、`decays to 0` 里的 `0`
当作未解释数字。`deai-boundary/without_skill/t2` 和
`qirp-reproduction-assessment/with_skill/t2` 各因此扣 1 个断言。
把这类也修掉会进一步改变 qi 的对比，所以留在原处并在此声明。

---

## E. 结论分级

按第一轮的定义：**明显增益 / 无差别 / 有害或太贵**。

| skill | 判定 | 依据 |
|---|---|---|
| **counterweight** | **触发层不可用（有害或太贵）** | 3 个正例触发 2/3、0/3、0/3；短请求下模型稳定不加载，而描述已明说覆盖短请求 |
| **deai** | **无差别，且更贵** | 79/85 vs 80/85，p=1.0；token +18.8%、时间 +18% |
| **qi-read-paper** | **无显著差别，代价为正** | 71/75 vs 67/75，p=0.37；token +8.4%、时间 +22%；符号检验 p≈0.39 |

对 counterweight 需要说清楚：本轮只测了触发，没有重测"加载之后是否有增益"。
第一轮的结论是"相对一行 YAGNI 无收益且更贵"，本轮没有推翻它；本轮新增的证据是
**改描述没有提高触发率**，所以"先修触发"这个方向本身也需要重新评估——
如果模型在短请求上稳定不加载，那么 skill 对最常见的改代码请求就是空操作。

### 本轮能支持什么

- 能支持：counterweight 在简短改代码请求上触发失败，且改描述没有修好（0/3，且
  4 次重复诊断仍 0/4，`diag2` 证明可加载）。
- 能支持：deai / qi-read-paper 在 6 个新用例上两臂无统计显著差异，且 with 臂 token
  与时间都更高。
- 能支持：第一轮 4 个 NA 断言现在可测，NA 归零；`coverage_gate_met` 两臂同样失败，
  该断言无区分度。
- 能支持：本轮 30 个 with_skill 运行全部真实加载了 skill，deai/qi 的对比没有被
  "没加载"污染。
- 能支持：harness 有两处会系统性歪曲结果的结构性缺陷（`.tex` 不评分、章节号当数字），
  已定位并给出反向验证。

### 本轮不能支持什么

- 不能给任何通过率的置信区间；n=5 的 Fisher 只能排除 5/5 vs 0/5 这种极端差异。
- 不能断言 deai / qi-read-paper "无用"——只能说不显著。both-pass 的 19 个断言说明
  当前难度下这些断言不区分，不说明 skill 无用。
- 不能比较 deai / qi 的 token 代价与第一轮（+46%/+30%），因为用例不同。
- 不能说明 counterweight 加载之后有没有增益；本轮没测加载后的效果。
- 不能排除评分器残留误报（`no_new_numbers` 对 `1`/`0` 的误判）对 qi 对比的干扰。

---

## 附录：数据出处

| 内容 | 文件 |
|---|---|
| 快照 commit | `results/round2/snapshot_commit.txt` |
| 触发测试（21） | `results/round2/trigger.json` |
| 补跑 NA（8） | `results/round2/partB_na.json`、`results/round2/partA_nafill.json` |
| 难度用例（60） | `results/round2/partA_difficulty.json` |
| 修正后判定 | `results/round2/partA_difficulty.regraded.json`、`partA_nafill.regraded.json` |
| 运行日志 | `results/round2/run.log` |
| 完成标记 | `results/round2/DONE` |
| 重算脚本 | `harness/regrade_round2.py` |
| 逐运行记录 | `runs/<case>/<arm>-t<n>/{transcript,tools,grading}.json` |

诊断实验（`runs/diag-noagents`、`runs/diag2`、`runs/diag3`，共 8 次）
**不计入 97 次正式运行**，仅用于第 A 节的归因。
