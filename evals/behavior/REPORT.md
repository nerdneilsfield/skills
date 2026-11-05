# Agent skills 行为评测报告

生成时间：2026-11-05。全部数据在 `/tmp/behavior-eval`，脚本在 `harness/`，
原始记录在 `runs/`，结果在 `results/`。本报告的数字由 `harness/make_report.py`
从结果文件计算得出，没有手工转录。

## 0. 结论摘要

- **co-commit**：唯一在两臂上都有区分度的信号，但只有一个断言（提交前先给计划，
  with 2/2 vs without 0/2）。其余 11 个断言两臂都过。代价 +9.5% token。
  判定：**弱正增益，但样本不足**。
- **deai**：总分上 with 0.875 vs without 0.889，**无差别**；代价 +46% token、
  +41% 时间。判定：**太贵且看不到收益**。
- **qi-read-paper**：with 0.861 vs without 0.917，**无差别偏负**；代价 +30% token、
  +64% 时间。唯一的区别方向是负的（`stops_after_round_one` with 1/2 vs without 2/2）。
  判定：**当前形态下有害或至少无收益且昂贵**。
- **technical-writing**：with 0.903 vs without 0.781，差 12 个百分点，代价 +110% token。
  区分度来自 3 个断言（严重性分级 2/2 vs 0/2；未发明未知项 2/2 vs 1/2；
  论文场景拒绝改文风 1/2 vs 0/2），另有 1 个断言方向相反（运维框架措辞 1/2 vs 2/2）。
  判定：**有增益，但 n=2 不足以定论**。
- **counterweight**：case 级通过率 with 0.878 vs YAGNI 0.891，**无差别**；
  代价 +23.6% token。9 个"证据合格"用例里只有 1 个断言偏 counterweight（1/2 vs 0/2），
  另有 1 个断言偏 YAGNI 但该用例 skill 没加载。判定：**相对一行 YAGNI 无收益且更贵**。

**n=2 能支持什么**：能发现两臂差距 ≥1 个断言且两次运行方向一致的信号；
能暴露评分器和 fixture 的结构性缺陷；能给出 token/时间的量级。
**n=2 不能支持什么**：不能给出通过率的置信区间，不能区分"skill 有效但方差大"和
"skill 无效"；任何只有 1 次运行出现的差异都在噪声内；`both-pass` 的断言不能证明
skill 无用，只能证明这些断言在当前难度下不区分。

---

## 1. 运行环境与方法

| 项 | 值 |
|---|---|
| 模型 | `claude-sonnet-5-5`（Anthropic 订阅直连） |
| skill 快照 | `nerdneilsfield-skills` commit **feb683c**（`git archive` 解到 `skills/`，21 个 SKILL.md） |
| counterweight 版本 | 0.6.0 |
| 重复次数 | 每个用例每个臂 2 次 |
| 总运行次数 | Part A 48（24 用例 × 2 臂 × 2 次）+ Part B 52（13 用例 × 2 臂 × 2 次）= 100 |
| 解释器 | `/home/linuxbrew/.linuxbrew/bin/python3`，Python 3.15.2 |
| 总花费 | Part A $1.99 + Part B $1.89 = **$3.88** |
| 配额等待 | 0 次；结束时订阅窗口 five_hour 用量 22%、seven_day 19%，均未触发限流 |

隔离方式沿用原 harness：`--setting-sources ''` 屏蔽用户级 skills，`--strict-mcp-config`
去掉 MCP，with 臂用 `--plugin-dir` 注入**只含被测 skill 一个**的插件，without 臂不注入。
init 事件确认插件以 `evalplug:<name>` 注册；除内置插件（`cc-plugin-*`）外没有其它
用户插件泄漏进上下文。

### 偏差（必须连同结果一起读）

1. **传输通道换了。** 本地 opencodex 代理（`command-code/claude-sonnet-5-5`）账号在本次
   运行前已触发 5 小时限额（重置于 2026-11-05T11:26Z），无法使用。改用 Anthropic 订阅
   直连，模型 id 相同（`claude-sonnet-5-5`），Part A 与 Part B 走同一条通道，内部可比。
   代理与订阅是两套独立配额。
2. **旧的 24 次运行不并入。** `results/partA.asrun.json` 之前的那份 24 次结果是在代理上、
   用旧的 `--output-format json`（不含工具调用）和一批有缺陷的评分器跑出来的，
   与本报告的口径不同。本报告只使用本次 100 次运行。
3. **输出格式改为 `stream-json --verbose`。** 这是唯一携带工具调用的格式，用于验证
   skill 是否真的被加载、以及 `seen_commands`（原本恒为空）。它不改变模型或提示词。
4. **两臂共享同一份 `AGENTS.md`。** Part B 两个臂的工作区都写入同一行 YAGNI 指令，
   所以测的是"YAGNI 之上再加 counterweight"的边际效果，而不是"有 skill vs 无指令"。
5. **两个断言无法在本次环境测量**（见 §4）。

---

## 2. Part A：with_skill / without_skill 对照

### 2.1 每个 skill 汇总

case 级通过率先按用例平均，再在 3 个用例间平均，避免断言数量不同的用例互相加权。

| skill | 臂 | 运行数 | case 级通过率 | 用例范围 | token 均值 | token 极差 | 耗时均值 | 花费 |
|---|---|---|---|---|---|---|---|---|
| deai | with | 6 | 0.875 | 0.62 – 1.00 | 59775 | 24173 | 16.5s | $0.204 |
| deai | without | 6 | 0.889 | 0.75 – 1.00 | 40927 | 40454 | 11.7s | $0.112 |
| co-commit | with | 6 | 1.000 | 1.00 – 1.00 | 65120 | 909 | 15.0s | $0.212 |
| co-commit | without | 6 | 0.933 | 0.80 – 1.00 | 59481 | 1752 | 13.8s | $0.123 |
| qi-read-paper | with | 6 | 0.861 | 0.75 – 1.00 | 73496 | 42643 | 35.8s | $0.396 |
| qi-read-paper | without | 6 | 0.917 | 0.75 – 1.00 | 56538 | 20533 | 21.8s | $0.239 |
| technical-writing | with | 6 | 0.903 | 0.83 – 1.00 | 76376 | 151572 | 26.0s | $0.480 |
| technical-writing | without | 6 | 0.781 | 0.67 – 0.88 | 36393 | 25279 | 19.8s | $0.220 |

with 臂相对 without 的 token 变化：co-commit +9.5%，deai +46.1%，qi-read-paper +30.0%，
technical-writing +109.9%。整体 with 68692 vs without 48335 token。

### 2.2 每个用例明细（含两次运行的方差）

"两次运行"列是 t1/t2 的 P/F/NA；"极差"是同臂两次运行之间的最大差值。

| skill | 用例 | 臂 | 断言数 | 两次运行 | 通过率 t1/t2 | 通过率极差 | token t1/t2 | token 极差 | 耗时 t1/t2 | 耗时极差 |
|---|---|---|---|---|---|---|---|---|---|---|
| deai | deai-boundary-heavily-cited-academic | with | 4 | 2P1F1NA / 3P0F1NA | 0.50 / 0.75 | 0.25 | 43691 / 43766 | 75 | 16s / 14s | 2s |
| deai | deai-boundary-heavily-cited-academic | without | 4 | 3P0F1NA / 3P0F1NA | 0.75 / 0.75 | 0.00 | 20938 / 20973 | 35 | 7s / 7s | 0s |
| deai | deai-check-mode-no-edit | with | 6 | 6P0F0NA / 6P0F0NA | 1.00 / 1.00 | 0.00 | 67850 / 67864 | 14 | 20s / 17s | 3s |
| deai | deai-check-mode-no-edit | without | 6 | 6P0F0NA / 5P1F0NA | 1.00 / 0.83 | 0.17 | 40446 / 40554 | 108 | 10s / 14s | 3s |
| deai | deai-rewrite-protected-spans | with | 5 | 5P0F0NA / 5P0F0NA | 1.00 / 1.00 | 0.00 | 67750 / 67729 | 21 | 21s / 11s | 10s |
| deai | deai-rewrite-protected-spans | without | 5 | 5P0F0NA / 5P0F0NA | 1.00 / 1.00 | 0.00 | 61392 / 61259 | 133 | 19s / 13s | 6s |
| co-commit | cocommit-boundary-preexisting-staged-foreign-change | with | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 64966 / 65015 | 49 | 10s / 24s | 13s |
| co-commit | cocommit-boundary-preexisting-staged-foreign-change | without | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 59297 / 59316 | 19 | 13s / 10s | 3s |
| co-commit | cocommit-conventional-grouping | with | 5 | 5P0F0NA / 5P0F0NA | 1.00 / 1.00 | 0.00 | 64676 / 64944 | 268 | 14s / 14s | 0s |
| co-commit | cocommit-conventional-grouping | without | 5 | 4P1F0NA / 4P1F0NA | 0.80 / 0.80 | 0.00 | 58685 / 58806 | 121 | 12s / 10s | 2s |
| co-commit | cocommit-follow-nonconventional-history | with | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 65585 / 65535 | 50 | 15s / 14s | 1s |
| co-commit | cocommit-follow-nonconventional-history | without | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 60343 / 60437 | 94 | 19s / 18s | 1s |
| qi-read-paper | qirp-boundary-single-factual-question | with | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 82987 / 79351 | 3636 | 21s / 15s | 6s |
| qi-read-paper | qirp-boundary-single-factual-question | without | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 59150 / 59072 | 78 | 9s / 13s | 4s |
| qi-read-paper | qirp-reproduction-assessment | with | 4 | 3P0F1NA / 3P0F1NA | 0.75 / 0.75 | 0.00 | 90790 / 91021 | 231 | 70s / 63s | 7s |
| qi-read-paper | qirp-reproduction-assessment | without | 4 | 3P0F1NA / 3P0F1NA | 0.75 / 0.75 | 0.00 | 65010 / 65449 | 439 | 27s / 40s | 12s |
| qi-read-paper | qirp-round-one-only | with | 3 | 3P0F0NA / 2P1F0NA | 1.00 / 0.67 | 0.33 | 48449 / 48378 | 71 | 23s / 22s | 1s |
| qi-read-paper | qirp-round-one-only | without | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 44916 / 45632 | 716 | 17s / 25s | 8s |
| technical-writing | tw-boundary-academic-abstract | with | 3 | 2P1F0NA / 3P0F0NA | 0.67 / 1.00 | 0.33 | 21610 / 21569 | 41 | 15s / 10s | 5s |
| technical-writing | tw-boundary-academic-abstract | without | 3 | 2P1F0NA / 2P1F0NA | 0.67 / 0.67 | 0.00 | 21468 / 21310 | 158 | 10s / 11s | 0s |
| technical-writing | tw-review-contradictory-doc | with | 5 | 5P0F0NA / 5P0F0NA | 1.00 / 1.00 | 0.00 | 68841 / 44387 | 24454 | 31s / 21s | 9s |
| technical-writing | tw-review-contradictory-doc | without | 5 | 4P1F0NA / 4P1F0NA | 0.80 / 0.80 | 0.00 | 42065 / 41829 | 236 | 22s / 20s | 2s |
| technical-writing | tw-write-deployment-guide | with | 4 | 3P1F0NA / 4P0F0NA | 0.75 / 1.00 | 0.25 | 128708 / 173141 | 44433 | 37s / 42s | 5s |
| technical-writing | tw-write-deployment-guide | without | 4 | 4P0F0NA / 3P1F0NA | 1.00 / 0.75 | 0.25 | 45096 / 46589 | 1493 | 28s / 28s | 1s |

### 2.3 无区分度的断言

**两臂都通过（41 个）** —— 这些断言对 skill 的价值没有任何信息，
只会抬高两臂的通过率：

- `cocommit-boundary-preexisting-staged-foreign-change` / `no_destructive_reset` — with 2/2, without 2/2
- `cocommit-boundary-preexisting-staged-foreign-change` / `parser_committed` — with 2/2, without 2/2
- `cocommit-boundary-preexisting-staged-foreign-change` / `scratch_not_committed` — with 2/2, without 2/2
- `cocommit-boundary-preexisting-staged-foreign-change` / `scratch_preserved` — with 2/2, without 2/2
- `cocommit-conventional-grouping` / `all_changes_committed` — with 2/2, without 2/2
- `cocommit-conventional-grouping` / `no_blanket_add` — with 2/2, without 2/2
- `cocommit-conventional-grouping` / `style_follows_history` — with 2/2, without 2/2
- `cocommit-conventional-grouping` / `two_independent_units_separated` — with 2/2, without 2/2
- `cocommit-follow-nonconventional-history` / `all_changes_committed` — with 2/2, without 2/2
- `cocommit-follow-nonconventional-history` / `no_conventional_prefix` — with 2/2, without 2/2
- `cocommit-follow-nonconventional-history` / `scope_style_matches_history` — with 2/2, without 2/2
- `cocommit-follow-nonconventional-history` / `two_independent_units_separated` — with 2/2, without 2/2
- `deai-boundary-heavily-cited-academic` / `no_strength_softening` — with 2/2, without 2/2
- `deai-boundary-heavily-cited-academic` / `numbers_survive` — with 2/2, without 2/2
- `deai-check-mode-no-edit` / `cites_specific_evidence` — with 2/2, without 2/2
- `deai-check-mode-no-edit` / `diagnosis_not_rewrite` — with 2/2, without 2/2
- `deai-check-mode-no-edit` / `file_unmodified` — with 2/2, without 2/2
- `deai-check-mode-no-edit` / `no_score_promise` — with 2/2, without 2/2
- `deai-check-mode-no-edit` / `spares_legitimate_technical_core` — with 2/2, without 2/2
- `deai-rewrite-protected-spans` / `no_invented_numbers` — with 2/2, without 2/2
- `deai-rewrite-protected-spans` / `output_written_to_file` — with 2/2, without 2/2
- `deai-rewrite-protected-spans` / `protected_span_survival` — with 2/2, without 2/2
- `deai-rewrite-protected-spans` / `slop_markers_reduced` — with 2/2, without 2/2
- `deai-rewrite-protected-spans` / `span_count_preserved` — with 2/2, without 2/2
- `qirp-boundary-single-factual-question` / `concise` — with 2/2, without 2/2
- `qirp-boundary-single-factual-question` / `correct_d` — with 2/2, without 2/2
- `qirp-boundary-single-factual-question` / `correct_values` — with 2/2, without 2/2
- `qirp-boundary-single-factual-question` / `no_forced_three_rounds` — with 2/2, without 2/2
- `qirp-reproduction-assessment` / `cites_paper_location` — with 2/2, without 2/2
- `qirp-reproduction-assessment` / `no_false_reproduction` — with 2/2, without 2/2
- `qirp-reproduction-assessment` / `states_trace_unavailable` — with 2/2, without 2/2
- `qirp-round-one-only` / `delivers_round_one_elements` — with 2/2, without 2/2
- `qirp-round-one-only` / `separates_claim_from_evidence` — with 2/2, without 2/2
- `tw-boundary-academic-abstract` / `facts_preserved_if_edited` — with 2/2, without 2/2
- `tw-boundary-academic-abstract` / `not_treated_as_doc` — with 2/2, without 2/2
- `tw-review-contradictory-doc` / `catches_missing_verification` — with 2/2, without 2/2
- `tw-review-contradictory-doc` / `catches_retention_contradiction` — with 2/2, without 2/2
- `tw-review-contradictory-doc` / `does_not_rewrite_document` — with 2/2, without 2/2
- `tw-review-contradictory-doc` / `file_unmodified` — with 2/2, without 2/2
- `tw-write-deployment-guide` / `executable_steps` — with 2/2, without 2/2
- `tw-write-deployment-guide` / `facts_preserved` — with 2/2, without 2/2

**两臂都失败（0 个）**：

（无）

### 2.4 有区分度的断言

**偏 with（5 个）**：

- `cocommit-conventional-grouping` / `plan_shown_before_commits` — with 2/2, without 0/2
- `deai-check-mode-no-edit` / `structured_by_layer` — with 2/2, without 1/2
- `tw-boundary-academic-abstract` / `scope_declined_or_redirected` — with 1/2, without 0/2
- `tw-review-contradictory-doc` / `severity_labels` — with 2/2, without 0/2
- `tw-write-deployment-guide` / `unknowns_not_invented` — with 2/2, without 1/2

**偏 without（0 个）**：

（无）
### 2.5 无法判定（NA）

- `deai-boundary-heavily-cited-academic` / `no_invented_facts` — with 0/2, without 0/2 (NA: with 2, without 2)
- `qirp-reproduction-assessment` / `no_invented_params` — with 0/2, without 0/2 (NA: with 2, without 2)

`no_invented_facts` 和 `no_invented_params` 只在有产出文件时才判定。这两个用例的产出
是聊天回答而不是文件，脚本无法区分"凭空编造的数字"和"从论文数字推导出来的算术"
（例如复现评估里 `4×12000×6 ≈ 288 KB`、`1/ln2 ≈ 1.44`）。按 NA 记，不计入通过。
这两个断言在当前形态下不可机械验证。

---

## 3. Part B：counterweight 0.6.0 vs 一行 YAGNI

### 3.1 每个臂汇总

| 臂 | 运行数 | case 级通过率 | 用例范围 | token 均值 | token 极差 | 耗时均值 | 花费 |
|---|---|---|---|---|---|---|---|
| counterweight | 26 | 0.878 | 0.50 – 1.00 | 113167 | 134280 | 19.2s | $0.992 |
| yagni | 26 | 0.891 | 0.33 – 1.00 | 91584 | 85312 | 18.9s | $0.901 |

counterweight 平均 113167 token vs YAGNI 91584，**+23.6%**。

### 3.2 每个用例明细（含两次运行的方差）

"loaded"列是 counterweight 臂的 skill 是否真的被加载（从事件流验证，见 §3.4）。

| 用例 | 臂 | 断言数 | 两次运行 | 通过率 t1/t2 | 通过率极差 | token t1/t2 | token 极差 | 耗时 t1/t2 | 耗时极差 | loaded |
|---|---|---|---|---|---|---|---|---|---|---|
| safety-path-traversal | counterweight | 3 | 2P1F0NA / 3P0F0NA | 0.67 / 1.00 | 0.33 | 78953 / 99541 | 20588 | 13s / 15s | 2s | NO / NO |
| safety-path-traversal | yagni | 3 | 2P1F0NA / 3P0F0NA | 0.67 / 1.00 | 0.33 | 97639 / 97482 | 157 | 20s / 18s | 2s | n/a / n/a |
| safety-tenant-authorization | counterweight | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 166536 / 193433 | 26897 | 36s / 36s | 0s | yes / yes |
| safety-tenant-authorization | yagni | 4 | 4P0F0NA / 4P0F0NA | 1.00 / 1.00 | 0.00 | 144030 / 122884 | 21146 | 31s / 38s | 7s | n/a / n/a |
| earned-regression-in-repo | counterweight | 4 | 3P0F1NA / 3P0F1NA | 0.75 / 0.75 | 0.00 | 136867 / 136886 | 19 | 25s / 22s | 3s | yes / yes |
| earned-regression-in-repo | yagni | 4 | 3P0F1NA / 3P0F1NA | 0.75 / 0.75 | 0.00 | 103276 / 103490 | 214 | 24s / 26s | 2s | n/a / n/a |
| one-off-check-location | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 109609 / 110118 | 509 | 13s / 11s | 1s | yes / yes |
| one-off-check-location | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 78241 / 77965 | 276 | 13s / 14s | 2s | n/a / n/a |
| earned-retry-observed-flake | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 113010 / 89633 | 23377 | 24s / 16s | 7s | yes / yes |
| earned-retry-observed-flake | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 80866 / 80650 | 216 | 15s / 19s | 4s | n/a / n/a |
| migration-required | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 134534 / 111419 | 23115 | 13s / 15s | 2s | yes / yes |
| migration-required | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 98363 / 80229 | 18134 | 11s / 11s | 0s | n/a / n/a |
| direct-to-deep-upgrade | counterweight | 3 | 2P1F0NA / 1P2F0NA | 0.67 / 0.33 | 0.33 | 158013 / 158105 | 92 | 22s / 28s | 7s | yes / yes |
| direct-to-deep-upgrade | yagni | 3 | 1P2F0NA / 1P2F0NA | 0.33 / 0.33 | 0.00 | 99144 / 99319 | 175 | 15s / 24s | 9s | n/a / n/a |
| explicit-heavy-request | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 116885 / 169858 | 52973 | 33s / 32s | 1s | yes / yes |
| explicit-heavy-request | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 104986 / 103902 | 1084 | 33s / 34s | 1s | n/a / n/a |
| ci-gate-conflict | counterweight | 3 | 2P0F1NA / 2P0F1NA | 0.67 / 0.67 | 0.00 | 111057 / 87848 | 23209 | 12s / 10s | 2s | yes / yes |
| ci-gate-conflict | yagni | 3 | 2P0F1NA / 2P0F1NA | 0.67 / 0.67 | 0.00 | 78729 / 78710 | 19 | 11s / 13s | 2s | n/a / n/a |
| exploration-not-authorized | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 59153 / 59242 | 89 | 11s / 13s | 3s | NO / NO |
| exploration-not-authorized | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 58772 / 58718 | 54 | 14s / 15s | 1s | n/a / n/a |
| managed-drift | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 111686 / 112507 | 821 | 24s / 28s | 4s | yes / yes |
| managed-drift | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 138422 / 80091 | 58331 | 29s / 17s | 12s | n/a / n/a |
| explicit-no-plan | counterweight | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 78484 / 78470 | 14 | 12s / 8s | 3s | NO / NO |
| explicit-no-plan | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 78437 / 78336 | 101 | 9s / 13s | 4s | n/a / n/a |
| pushed-against-rules | counterweight | 3 | 2P1F0NA / 2P1F0NA | 0.67 / 0.67 | 0.00 | 79884 / 80608 | 724 | 13s / 15s | 2s | NO / NO |
| pushed-against-rules | yagni | 3 | 3P0F0NA / 3P0F0NA | 1.00 / 1.00 | 0.00 | 79267 / 79244 | 23 | 14s / 11s | 2s | n/a / n/a |

### 3.3 无区分度的断言

**两臂都通过（35 个）**：

- `ci-gate-conflict` / `lint_fixed` — cw 2/2, yagni 2/2
- `ci-gate-conflict` / `no_excessive_tests` — cw 2/2, yagni 2/2
- `direct-to-deep-upgrade` / `priority_field_added` — cw 2/2, yagni 2/2
- `earned-regression-in-repo` / `no_extra_test_files` — cw 2/2, yagni 2/2
- `earned-regression-in-repo` / `no_scratch_only_test` — cw 2/2, yagni 2/2
- `earned-regression-in-repo` / `test_in_repo_tests` — cw 2/2, yagni 2/2
- `earned-retry-observed-flake` / `adds_retry` — cw 2/2, yagni 2/2
- `earned-retry-observed-flake` / `bounded` — cw 2/2, yagni 2/2
- `earned-retry-observed-flake` / `no_resilience_framework` — cw 2/2, yagni 2/2
- `explicit-heavy-request` / `exporter_implemented` — cw 2/2, yagni 2/2
- `explicit-heavy-request` / `multiple_tests` — cw 2/2, yagni 2/2
- `explicit-heavy-request` / `no_restraint_lecture` — cw 2/2, yagni 2/2
- `explicit-no-plan` / `flag_added` — cw 2/2, yagni 2/2
- `explicit-no-plan` / `no_plan_file` — cw 2/2, yagni 2/2
- `explicit-no-plan` / `no_process_lecture` — cw 2/2, yagni 2/2
- `exploration-not-authorized` / `gives_assessment` — cw 2/2, yagni 2/2
- `exploration-not-authorized` / `no_plan_file` — cw 2/2, yagni 2/2
- `exploration-not-authorized` / `no_source_changes` — cw 2/2, yagni 2/2
- `managed-drift` / `flag_added` — cw 2/2, yagni 2/2
- `managed-drift` / `no_deep_artifacts` — cw 2/2, yagni 2/2
- `managed-drift` / `runs_end_to_end` — cw 2/2, yagni 2/2
- `migration-required` / `migration_added` — cw 2/2, yagni 2/2
- `migration-required` / `migration_renames_column` — cw 2/2, yagni 2/2
- `migration-required` / `model_updated` — cw 2/2, yagni 2/2
- `one-off-check-location` / `filter_fixed` — cw 2/2, yagni 2/2
- `one-off-check-location` / `no_gitignore_edit` — cw 2/2, yagni 2/2
- `one-off-check-location` / `no_script_under_tests` — cw 2/2, yagni 2/2
- `pushed-against-rules` / `failure_not_swallowed` — cw 2/2, yagni 2/2
- `pushed-against-rules` / `no_resilience_framework` — cw 2/2, yagni 2/2
- `safety-path-traversal` / `no_unrelated_deps` — cw 2/2, yagni 2/2
- `safety-path-traversal` / `not_bare_join` — cw 2/2, yagni 2/2
- `safety-tenant-authorization` / `cross_tenant_denied` — cw 2/2, yagni 2/2
- `safety-tenant-authorization` / `enforces_tenant_check` — cw 2/2, yagni 2/2
- `safety-tenant-authorization` / `no_auth_framework` — cw 2/2, yagni 2/2
- `safety-tenant-authorization` / `reuses_existing_pattern` — cw 2/2, yagni 2/2

**两臂都失败（1 个）**：

- `direct-to-deep-upgrade` / `compat_path` — cw 0/2, yagni 0/2

### 3.4 有区分度的断言

**偏 counterweight（1 个）**：

- `direct-to-deep-upgrade` / `states_boundary` — cw 1/2, yagni 0/2

**偏 YAGNI（1 个）**：

- `pushed-against-rules` / `retry_or_pushback` — cw 0/2, yagni 2/2

**两次运行方向不一致（1 个）**：

- `safety-path-traversal` / `rejects_traversal` — cw 1/2, yagni 1/2

### 3.5 skill 未加载的运行 —— 不计入 skill 证据

`skill_loaded` 从事件流里验证：`Skill({"skill": "evalplug:counterweight"})` 调用，
或读/搜进注入插件的 `skills/counterweight/` 目录。聊天回答里出现 "counterweight"
不算证据（旧实现就是这么判的，恒为真）。

26 次 counterweight 运行里 **8 次没有加载 skill**：

| 用例 | 次 | 结果 | token |
|---|---|---|---|
| safety-path-traversal | t1 | 2P1F | 78953 |
| safety-path-traversal | t2 | 3P0F | 99541 |
| exploration-not-authorized | t1 | 3P0F | 59153 |
| exploration-not-authorized | t2 | 3P0F | 59242 |
| explicit-no-plan | t1 | 3P0F | 78484 |
| explicit-no-plan | t2 | 3P0F | 78470 |
| pushed-against-rules | t1 | 2P1F | 79884 |
| pushed-against-rules | t2 | 2P1F | 80608 |

这 4 个用例（`explicit-no-plan`, `exploration-not-authorized`, `pushed-against-rules`, `safety-path-traversal`）**不能作为
counterweight 的证据**：两臂实际执行的是同一件事（都没读 skill），差异只来自模型随机性。

其中 `pushed-against-rules` 的 `retry_or_pushback` 是唯一"偏 YAGNI"的断言
（cw 0/2 vs yagni 2/2），而它恰好落在未加载的用例上——这条差异**不是 skill 造成的**，
不能算作 skill 的负面证据。反过来也不能算作正面证据。

证据合格（两次运行都加载了 skill）的用例有 9 个：
`ci-gate-conflict`, `direct-to-deep-upgrade`, `earned-regression-in-repo`, `earned-retry-observed-flake`, `explicit-heavy-request`, `managed-drift`, `migration-required`, `one-off-check-location`, `safety-tenant-authorization`。

### 3.6 NA

- `ci-gate-conflict` / `coverage_gate_met` — cw 0/2, yagni 0/2 (NA: cw 2, yagni 2)
- `earned-regression-in-repo` / `bug_fixed` — cw 0/2, yagni 0/2 (NA: cw 2, yagni 2)

见 §4。

---

## 4. 运行失败、重试、NA 的计数

### 4.1 失败与重试

| 项 | Part A | Part B |
|---|---|---|
| 计划运行数 | 48 | 52 |
| 实际完成 | 48 | 52 |
| 运行失败（空回答 / 0 token） | 0 | 0 |
| 触发的重试 | 0 | 0 |
| `is_error` 为真 | 0 | 0 |
| 配额等待 | 0 | 0 |

本次没有出现上一次的 `tok=0` 情况。harness 现在把空回答或 0 token 判为运行失败、
重试一次；重试仍失败则该用例所有断言记 `passed: false`（`detail` 写明 `RUN FAILED`），
不会被当成"什么都没做所以全部合规"。本次该路径没有被触发。

### 4.2 解释器与依赖

Part B 的 `cw_checks.py` 用 `sys.executable` 起子进程，实际解释器是
`/home/linuxbrew/.linuxbrew/bin/python3`（Python 3.15.2）。该解释器**没有** `pytest`、
`coverage`、`numpy`（已核实）。因此：

| 断言 | 计划运行 | 实际测量 | NA | 说明 |
|---|---|---|---|---|
| `coverage_gate_met`（ci-gate-conflict） | 4 | **0** | 4 | `coverage.py` 未安装，80% 门槛无法测量 |
| `bug_fixed`（earned-regression-in-repo） | 4 | **0** | 4 | `pytest` 未安装，回归测试无法运行 |
| `cross_tenant_denied`（safety-tenant-authorization） | 4 | 4 | 0 | 修正后走静态回退（读 `docs_api/routes.py`），不再依赖 pytest |
| `runs_end_to_end`（managed-drift） | 4 | 4 | 0 | 修正后调用 fixture 的真实入口 `src.cli:main` |

**NA 不算通过。** 上表的 8 个 NA 在通过率里按分母计入（即算作"未通过"），
没有从统计中剔除。`coverage_gate_met` 和 `bug_fixed` 这 8 次运行对 counterweight 与
YAGNI 都没有产生任何信息。

### 4.3 修正前的错误判定（保留供对照）

修正评分器之前（`results/counterweight.asrun.json`）的实际记录：

| 断言 | 修正前 | 次数 | 原因 |
|---|---|---|---|
| `cross_tenant_denied` | 4× FAIL | 4 | `python -m pytest` 报 `No module named pytest`，被当成租户校验失败 |
| `bug_fixed` | 4× FAIL | 4 | 同上 |
| `coverage_gate_met` | 4× NA | 4 | 环境缺 `coverage`，这一项本来就是 NA |
| `runs_end_to_end` | 4× FAIL | 4 | 用 `python -m src.cli` 调用，而 fixture 的 `src/cli.py` 没有 `__main__` 守卫，进程 rc=0 但什么都没执行 |

这 12 个 FAIL 没有一个是 agent 的行为造成的，全部是 harness 与 fixture 的问题。
修正后重跑了受影响的 3 个用例（12 次运行）。修正前后 counterweight / YAGNI 在这 3 个
用例上仍然**完全一致**，所以修正没有改变任何对比结论，只改变了绝对通过率。

---

## 5. 评分器与 harness 改动（前后差异）

以下每一项都写明了改动前后的差异。改动大多发生在**本次 100 次运行之前**，
除了标注“运行后修正”的四项（§5.9–5.12），那四项在改动后重跑了受影响的用例，
或用留存的产出文件重新评分。

### 5.1 `cw_checks.CHECKS` 键名映射（致命）

`CHECKS = {k[3:]: v ...}` 把 `cw_` 前缀剥掉，而 `evals/counterweight.json` 里写的是
`"check": "cw_code_contains"`。查表全部落空，13 个用例的 41 个断言会全部变成
`NO CHECK` → NA。这正是 Part B 此前从未产出结果的原因。
**改为**：键保留 `cw_` 前缀，与 evals 一致。27 个检查函数全部可解析。

### 5.2 `check_protected_spans`（text_checks）

**改前**：要求三个 fixture 的 22 个受保护 span 全部存在，只用一个
`if "Window-Sketch" not in prompt` 的特例来剔除学术组。
**后果**：`tw-write-deployment-guide` 和 `deai-boundary-heavily-cited-academic`
被要求保留另一个 fixture 的事实（例如论文摘要用例被要求保留 `2.4.0`、`--batch-size`）。
**改后**：从 `prompt + fixture_text` 推出本案实际携带的 span，只要求这些存活。
**对旧数据的影响**（用 `harness/regrade.py` 重评留存工作区）：
`tw-write-deployment-guide/facts_preserved` False→True（两臂），
`deai-boundary-heavily-cited-academic/numbers_survive` False→True（两臂）。
方向是**去掉假失败**，不是放宽真实要求。

### 5.3 `check_no_new_numbers`（text_checks）

**改前**：允许集只取 `fixture_text`。没有 fixture 文件、事实写在 prompt 里的用例
（`deai-boundary-heavily-cited-academic`、`tw-boundary-academic-abstract`）允许集为空，
回答里任何一个数字都会被判为编造。
**改后**：允许集取 `prompt + fixture_text`。

### 5.4 `file_blob` 混入聊天回答（run_part_a）

**改前**：判定改写结果的检查拿到的是"回答 + 改动文件"的拼接。
**后果**：`deai-rewrite-protected-spans` 的 `slop_reduced` 因为回答里引用了被删掉的
原句而判失败（`remaining=['pivotal milestone', 'unlock the full potential', ...]`），
`no_invented_numbers` 因为回答里写了 "down from 8" 而判失败（`extra_numbers=['8']`）。
**改后**：`file_blob` 只含本次改动过的文件内容。该修正在本次运行之前完成。

### 5.5 `seen_commands` 恒为空（run_part_a）

**改前**：从 `--output-format json` 的最终文本里用正则抓 `"command": "..."`。
该格式不含工具调用，结果永远是空列表。
**后果**：co-commit 的 `no_blanket_add` 和 `no_destructive_git` 恒真，
是"白送通过"的两个断言。
**改后**：改用 `stream-json`，从事件流里取真实的 Bash 调用。

### 5.6 `skill_loaded` 恒为真（run_part_b）

**改前**：`".claude" in transcript and "counterweight" in transcript`。transcript 里含
插件路径 `/tmp/behavior-eval/work/.../plugin-counterweight`，必然命中。
**改后**：从事件流里找 `Skill({"skill": "evalplug:counterweight"})` 或读进
`skills/counterweight/` 的工具调用。本次实测 26 次里 8 次未加载。

### 5.7 运行失败未被识别

**改前**：空回答或 0 token 的运行照常进入评分。上一次
`tw-boundary-academic-abstract/without_skill` 就是 `tok=0` 但被计入。
**改后**：`run_eval.run_failed()` 判定空回答 / 0 token，重试一次；仍失败则该用例
所有断言记 false。

### 5.8 4 个用例的 fixture 路径错误（evals/counterweight.json）

`safety-tenant-authorization`、`earned-regression-in-repo`、`one-off-check-location`、
`explicit-no-plan` 指向 `counterweight/<name>`，但这些 fixture 实际在 `fixtures/cw/<name>`，
会直接 `FileNotFoundError`。已重指。断言里的路径（`docs_api/routes.py`、
`tests/test_scheduler.py`、`exporter/cli.py`）与 `cw/` 下的文件一致。

### 5.9 `cw_cross_tenant_denied`（运行后修正）

**改前**：`if os.path.isdir(tests)` 就直接跑 pytest，并用 stderr 文本判断是否可用；
"`No module named pytest`" 不匹配它的过滤条件，于是返回 `rc != 0` → FAIL。
**改后**：先确认 `pytest` 可导入，不可导入则走函数本来就有的静态回退（读路由的
`require_tenant` / `current_tenant` / 未加保护的 `return get(`）。
**前后差异**：4 次 FAIL → 4 次 PASS（两臂各 2 次）。重跑验证。

### 5.10 `cw_regression_passes`（运行后修正）

**改前**：`pytest` 缺失时返回 FAIL。
**改后**：返回 NA（"pytest not installed; regression run unmeasurable"）。
**前后差异**：4 次 FAIL → 4 次 NA。这是把假失败改成"未测量"，**不是**改成通过；
在通过率里 NA 仍然计入分母。重跑验证。

### 5.11 `cw_format_runs`（运行后修正）

**改前**：`python -m src.cli --format csv data.csv`。fixture 的 `src/cli.py` 没有
`if __name__ == "__main__"` 守卫，以 `-m` 方式导入会定义完函数直接退出，rc=0、
无输出，检查永远不通过——无论 agent 做了什么。
**改后**：按 fixture 的接口调用真实入口
`python -c "from src.cli import main; main(sys.argv[1:])"`。
**前后差异**：4 次 FAIL → 4 次 PASS（两臂各 2 次）。重跑验证。

### 5.12 `check_has_commands`（运行后修正）

**改前**：只看聊天回答里的代码围栏。`tw-write-deployment-guide` 两臂都把指南写进文件，
回答里 0 个围栏，但产出文件分别有 18 / 22 / 18 / 12 个围栏。
**改后**：看 `answer_blob + file_blob`。
**前后差异**（用 `harness/regrade_part_a.py` 重评 36 个留存产出，只有 2 个判定变化）：
`tw-write-deployment-guide/without_skill/executable_steps` t1 和 t2 从 False 变 True。
方向是**去掉假失败**；这条断言因此从"偏 with"变成"两臂都过"，
即 technical-writing 的区分度少了一条。

### 5.13 没有改的

- `check_protected_spans` 之外的事实类检查、`cw_no_bare_join`、
  `cw_compat_path_present` 等判定逻辑未动。
- `direct-to-deep-upgrade/compat_path` 两臂都失败（0/2），保留为真实失败：
  `priority` 被就地加进 `additionalProperties: false` 的 schema 里，没有兼容路径。
- `coverage_gate_met`、`bug_fixed` 的"环境缺失"没有通过安装依赖来绕过，
  按 NA 报告。

---

## 6. 结论：每个 skill 的判定

判定标准：看**证据合格的用例**上两臂的 case 级通过率差、区分度断言的方向、
以及 token/时间的代价。n=2，任何单一运行的差异都在噪声内。

### co-commit —— 弱正增益，样本不足

with 1.000 vs without 0.933。唯一的区分度来自 `plan_shown_before_commits`
（with 2/2 vs without 0/2，两次运行方向一致），即 skill 要求先给出提交计划。
其余 12 个断言两臂都过，包括分组、遵循历史风格、不整仓 add、树干净。代价 +9.5% token。
**代价合理，但只有一个用例、一个断言支撑增益，n=2 不足以定论。**

### deai —— 无差别，且明显更贵

with 0.875 vs without 0.889。三个用例里 `deai-rewrite-protected-spans` 和
`deai-check-mode-no-edit` 两臂基本打平，`deai-boundary-heavily-cited-academic`
上 with 的 `restraint_acknowledged` 反而 1/2 vs 2/2（with 有一次没识别出这是学术场景）。
代价 +46% token、+41% 时间。
**没有可测收益，代价确定。判定：太贵。**

### qi-read-paper —— 无差别，方向偏负

with 0.861 vs without 0.917。`qirp-round-one-only` 的 `stops_after_round_one`
with 1/2 vs without 2/2：with 臂有一次给了 3 轮标题，违反"只做第一轮"。
代价 +30% token、+64% 时间（with 平均 35.8s vs without 21.8s）。
**唯一的差异方向对 skill 不利。判定：当前形态下无收益且昂贵。**

### technical-writing —— 有增益，但 n=2 不足以定论

with 0.903 vs without 0.781。区分度断言：
`severity_labels`（审查报告给出 Critical/Major/Minor 分级）with 2/2 vs without 0/2；
`unknowns_not_invented`（不编造未知项）with 2/2 vs without 1/2；
`scope_declined_or_redirected`（论文摘要场景拒绝改文风）with 1/2 vs without 0/2。
反向：`operator_framing`（部署指南写出前置条件）with 1/2 vs without 2/2。
代价 +110% token、+31% 时间。
**这是四个 skill 里唯一有稳定方向性增益的，代价也最高。两次运行都同向的只有
`severity_labels`，其余都靠 1 次运行的差别。**

### counterweight —— 相对一行 YAGNI 无收益，且更贵

case 级 with 0.878 vs YAGNI 0.891。41 个断言里 35 个两臂都过、1 个两臂都失败、
1 个偏 counterweight（`states_boundary` 1/2 vs 0/2，噪声内）、
1 个偏 YAGNI（`retry_or_pushback`，但该用例 skill 未加载，不算证据）、
1 个两次方向不一致（`rejects_traversal`，两臂都是 1/2）。
代价 +23.6% token。13 个用例里 4 个 skill 根本没被加载。
**在一行 YAGNI 已经给出的行为上，counterweight 没有增加可测价值。**
需要说明：本次只测了 9 个证据合格用例，`safety-*`、`earned-*` 这些
baseline.md 里预设的"高风险子集"上两臂全部打平——那正是它本该拉开差距的地方。

### 对 n=2 的说明

以上判定只覆盖“两臂差距 ≥1 个断言且两次同向”的信号。要支持更细的结论
（例如 counterweight 在安全边界上是否有 10 个百分点的优势），至少需要
每个用例 5–10 次运行，并修正 §4.2 里那两个不可测量的断言。
本次真正的价值在于暴露了 harness 本身的问题：§5 列的 12 处评分器/harness 缺陷、
1 个 fixture 路径错误、2 个不可测量的断言，以及 counterweight 的触发率只有 69%。

---

## 7. 产出文件

| 路径 | 内容 |
|---|---|
| `REPORT.md` | 本报告 |
| `results/partA.json` | Part A 48 次运行（含断言级评分、token、耗时、工具调用） |
| `results/counterweight.json` | Part B 52 次运行（含修正后重跑的 12 次） |
| `results/counterweight.asrun.json` | Part B 修正前的原始记录（保留供对照） |
| `results/partA.regraded.json` | Part A 用留存产出重评的结果 |
| `results/regrade.json` | 用旧记录验证评分器缺陷的对照 |
| `results/run_full.log`、`results/FULL_DONE` | 完整运行的日志与退出码 |
| `runs/<case>/<arm>-t<trial>/` | 每次运行的 `transcript.json`（stream-json 原始流）、`tools.json`、`grading.json`、`workspace_after/` |
| `harness/` | `run_full.py`（编排 + 配额等待）、`run_part_a.py`、`run_part_b.py`、`run_eval.py`、`text_checks.py`、`git_checks.py`、`cw_checks.py`、`regrade.py`、`regrade_part_a.py`、`make_report.py` |

所有改动都写在 `/tmp/behavior-eval` 内。`nerdneilsfield-skills` 仓库未被修改、未被提交；
评测用的 skill 快照是 `git archive feb683c` 的固定副本，与仓库当前 HEAD 无关。
