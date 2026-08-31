# Review mode

review 只指出问题和修改方向，不默认重写全文。先验证技术语义、可执行性和安全，再看结构与语言。

## Severity

### Critical

可能导致错误实现、人员风险、设备或数据损坏、严重安全暴露，或高影响误操作。

Examples:

- 电气参数把 absolute maximum 写成正常工作值。
- 删除命令的作用域描述错误，可能删除其他 tenant 数据。
- register bit 定义与示例相反，可能关闭保护功能。
- 安全警告位于危险步骤之后，或规避动作本身错误。

### Major

技术信息缺失或矛盾，导致文档难以正确使用、实现或复现；包括明显歧义、不可复现步骤、参数定义不完整、术语冲突或严重结构问题。

Examples:

- API parameter 缺少单位、范围或默认值。
- procedure 未写 prerequisite，普通用户没有权限完成第 3 步。
- test-verification 只有“结果正常”，没有 pass/fail criteria。
- interface spec 未定义 endianness、timeout 或 error recovery。
- 句子存在两种合理语法解析，且不同解析会改变 actor、条件、范围或技术结论。

### Minor

不改变核心技术结果，但降低扫描、可读性或一致性；包括格式、措辞、标点、中英混排和局部结构问题。

Examples:

- 同一 option 有时用 code style，有时用引号。
- 标题大小写不一致。
- 中文与英文间距混乱，但 identifier 本身正确。
- 局部语病或句式不平行，但不会改变技术含义或操作结果。

严重程度取决于实际上下文。不要因为某类问题通常严重，就忽略本次文档的受众、产品风险和传播范围。

## Review order

1. **Technical facts:** 名称、签名、参数、数值、单位、范围、默认值、版本、register、signal、错误和示例是否一致。
2. **Safety and damage:** 风险、后果、规避、位置、备份、权限和不可逆操作是否完整。
3. **Task completion:** prerequisite、条件、步骤顺序、expected result 和 verification 是否足以执行。
4. **Document type:** 结构是否符合读者意图；reference 是否可查，explanation 是否解释因果，test 是否可判定。
5. **Clarity and terminology:** actor、代词、术语、条件和限制是否明确。
6. **Language and format:** 标题、列表、表格、代码格式、标点、空格和 accessibility。

## Report findings

每条 finding 包含：

- severity；
- 精确位置或可识别原文；
- 问题是什么；
- 为什么会影响读者或实现；
- 修改方向，而非整段代写。

Example:

> **Major — “Set the timeout to 30.”** 缺少单位，API 同时接受秒和毫秒字段，读者可能配置成错误值。写明参数名、单位、允许范围和默认值。

相同根因在多处出现时合并报告，并列出代表位置。不要把一个术语问题拆成十条。

## Do not invent findings

- 没有证据时，不把可能的产品行为写成缺陷。
- 风格偏好不应升级为 Major。
- 用户明确采用项目约定时，不用其他 style guide 强行覆盖。
- 不为凑数量报告无影响差异。
- 未发现问题时，直接说明“未发现需要报告的问题”，并简述已检查范围。

## Review output

先按 `Critical`、`Major`、`Minor` 排列 findings。若无 findings，停止；不要附带全文重写。用户另行要求改写时，再切换到 `rewrite` mode，并保留技术事实清单。
