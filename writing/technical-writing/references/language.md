# Chinese, English, and mixed-language writing

先遵从项目既有语言和术语约定。没有约定时，使用以下默认规则；同一文档保持一致。

## Chinese technical writing

### Grammar is a correctness requirement

句子必须有可识别的语法主干，修饰关系和逻辑关系必须唯一。技术事实正确但句法无法可靠解析，仍是不合格文档。

写完每句后，去掉修饰语，检查能否立即识别“谁或什么—做什么—作用于什么—产生什么结果”。若主干不存在、成分残缺或可能有两种解析，重写；不要靠读者猜。

Bad:

> 针对高并发场景下对于请求处理能力的进一步优化。

Good:

> 调度器合并重复请求，以提高高并发场景下的吞吐量。

前一句只是名词短语，没有谓语，不能独立承担技术陈述。标题、表头和并列列表项可以使用短语，但同一列表应保持同类结构。

### Write natural, direct Chinese

使用具体主体、精确动词和自然语序。避免公文腔、翻译腔和 AI 式层层总结。

Bad:

> 本模块主要实现了对于设备相关状态信息的统一化获取功能，从而能够完成对异常情况的及时发现。

Good:

> 该模块读取设备状态，并在状态异常时报告错误。

删除没有新增含义的“首先需要指出的是”“值得注意的是”“从整体上来看”“综上所述”。若信息确实重要，直接陈述事实或风险。

### Do not hide the subject

中文可省略已明确的主语，但以下情况应补出 actor：

- 同段有多个系统、组件或角色；
- 动作责任影响实现或操作；
- 被动句无法判断谁触发状态变化；
- “其”“该”“对应的”可能指向多个对象。

Bad:

> 收到响应后写入缓存，然后通知客户端。

Good:

> 代理收到上游响应后，将响应写入缓存，再通知客户端读取结果。

同一句中不要无标记地更换主语。

Bad:

> 控制器读取温度后写入寄存器，并由主机每秒轮询一次。

Good:

> 控制器将温度写入寄存器。主机每秒轮询一次该寄存器。

`由` 后应接动作执行者，`被` 应表示真实的被动关系。若技术对象只是处于某种状态，直接陈述状态。

Bad:

> 请求被返回 `403` 状态码。

Good:

> 服务器为该请求返回 HTTP `403` 状态码。

### Keep modifiers attached to their targets

定语、状语和补语应紧邻其修饰对象。长定语链容易产生多个解析，应拆成独立句或先定义对象。

Bad:

> 系统读取用户上传的经过压缩和加密处理后的可用于恢复的配置文件。

Good:

> 用户上传用于恢复的配置文件。该文件已经压缩并加密。系统读取该文件后开始恢复。

正确使用“的、地、得”，但不机械添加：

- `的` 连接定语和名词：`校准后的传感器`。
- `地` 连接需要明确标出的状语和动词：`独立地验证两个通道`。固定或简短组合可写 `自动重试`、`快速启动`。
- `得` 引出程度或结果补语：`服务启动得更快`。

避免连续使用多个“的”。出现“对……的……的……”时，通常应拆句或改用动词。

### State logical relations exactly

连接词必须反映真实关系。不要把时间、条件、因果、转折和递进混为一谈。

- 条件：`如果 A，则 B`；有多条分支时逐条写明。
- 充分条件：`只要 A，就 B`。不能用它表达必要条件。
- 必要条件：`只有 A，才 B`。不能用它表达任选方案。
- 排他条件：`除非 A，否则 B`。
- 转折：`虽然 A，但是 B`；A 与 B 必须存在真实对照。
- 递进：`不仅 A，而且 B`；A 与 B 应为同类成分，B 的语义更进一步。
- 因果：明确原因和结果。不要用“从而”“因此”连接并无因果的两件事。

Bad:

> 当连接断开时，客户端重试三次，从而日志记录失败原因。

Good:

> 当连接断开时，客户端最多重试三次。三次重试均失败后，客户端将失败原因写入日志。

不要在同一句中堆叠“由于……因此……从而……进而……”，也不要用“同时”掩盖先后关系。

### Keep coordination parallel

`和`、`与`、`及`、`以及`、`并`、`或` 两侧应为同一语法层级和同一语义类别。列表项也应采用平行结构。

Bad:

> 工具支持采集、数据分析和可视化结果。

Good:

> 工具支持数据采集、数据分析和结果可视化。

Bad:

> 升级前，请备份数据库、检查磁盘空间，以及服务必须停止。

Good:

> 升级前，请备份数据库、检查磁盘空间并停止服务。

`或` 必须说明是任选、互斥还是条件分支。若选择会改变结果，分别写出条件。

### Make reference and scope unambiguous

代词、数量词、否定词和范围副词应紧邻其作用对象。

- `它`、`其`、`该项`、`前者`、`后者` 必须只有一个可能的先行词；否则重复名词。
- 区分 `不完全支持`（支持一部分）与 `完全不支持`（全部不支持）。
- `未检测到所有节点` 有歧义。按真实含义写成 `并非所有节点都已检测到` 或 `未检测到任何节点`。
- `仅`、`只`、`至少`、`至多`、`分别` 应放在被限定成分之前。
- 使用“分别”时，列出的对象和结果必须一一对应。

Bad:

> 网关将证书发送给代理，然后验证它。

Good:

> 网关将证书发送给代理。代理验证该证书。

### Prefer verbs over nominalized stacks

避免把动作全部改成“……的实现、……的进行、……的完成、……能力的提升”等名词结构。这类句子常缺 actor、时序和结果。

Bad:

> 通过对缓存策略的调整实现对于响应延迟的降低。

Good:

> 将缓存有效期从 30 s 增至 60 s 后，P95 响应延迟从 120 ms 降至 80 ms。

不要照搬英文名词串或被动结构。先恢复语义角色，再按中文语序重写。

Bad:

> 被用于设备状态获取的接口由控制器所提供。

Good:

> 控制器提供设备状态查询接口。

### Remove empty verbs and vague qualifiers

- `进行 + 动作名词`：通常改为动词，如“进行初始化”改为“初始化”。
- `实现 + 名词`：若只是执行动作，改为精确动词；若表示满足接口、算法或能力契约，可保留。
- `完成 + 动作`：若无完成态语义，删去；若需区分进行中与完成后状态，可保留。
- `相关`：列出实际对象；只有集合已被明确界定时使用。
- `对应`：仅用于真实映射关系，并写明两端对象。
- `适当`：给出范围、方法或责任角色。
- `必要时`：给出可判断的触发条件。

Bad:

> 必要时适当调整相关参数。

Good:

> 若丢包率超过 1%，将 `retry_count` 从 3 增至 5。

### Chinese punctuation and width

- 中文句子使用全角中文标点：`，。；：？！`。
- 中文说明性括号使用全角 `（ ）`。代码语法、函数调用、ASCII protocol text 和路径中的括号保持原样。
- 中文引文使用 `“ ”`；代码值、UI 标签和 identifier 不用引号代替格式。
- 不混用全角字母、全角数字或全角空格。代码块内保持原始 ASCII。
- 中文范围符号、波浪号和 dash 选择一种项目约定；避免同页混用 `-`、`~`、`～` 表示同一语义。

### Chinese, Latin text, and numbers

没有项目约定时，中文与独立的 Latin term 或阿拉伯数字之间留一个半角空格：

> 使用 CUDA kernel 处理 4 个 batch。

以下位置不插空格：identifier 内部、URL、路径、版本号、数字与 `%`/`°`、成对标点内侧。数字与 SI unit 之间留空格：`5 V`、`10 ms`。

不要把换行或不可见的全角空格当排版手段。

### Abbreviations and proper names

首次出现不熟悉缩写时，使用“中文名称（English name，ABBR）”或项目约定格式。缩写比全称更常见时，不必机械展开，如 API、CLI、CPU。

产品名、协议名和专有名词遵从权威拼写：PCIe、Wi-Fi、GitLab、Kubernetes。不要为“中文化”而改大小写或创造译名。

### Long Chinese sentences

一条句子同时包含多个条件、actor、动作和结果时，按因果或时序拆开。条件置前；多项属性用列表或表格。不要只靠顿号和分号无限延长句子。

以下任一情况通常应拆句：

- 主语在句中改变；
- 同时出现两组以上条件—结果关系；
- 一个代词存在多个先行词；
- 一个否定词可能覆盖不同成分；
- 并列项不是同一语法结构；
- 读到句末才能理解句首动作的条件。

分号只分隔关系紧密、结构平行的分句。分号不能修复成分残缺或逻辑混乱的句子。

## English technical writing

### Write complete, parseable sentences

Except in headings, labels, tables, and deliberately parallel list fragments, every sentence needs a subject and a finite verb. Match the verb to its subject, and do not join independent clauses with only a comma.

Bad:

> The controller responsible for polling all sensors and reporting failures.

Good:

> The controller polls all sensors and reports failures.

Prefer direct language, clear actors, present tense, and second person when addressing the reader. Use imperative verbs for procedures: `Connect the probe to TP3.`

### Attach modifiers clearly

Place modifiers next to what they modify. Avoid dangling introductory phrases and long noun stacks.

Bad:

> After configuring the server, the connection is tested automatically.

Good:

> After you configure the server, the client tests the connection automatically.

Bad:

> Configure the production request timeout retry policy.

Good:

> Configure the retry policy for request timeouts in production.

Place `only`, `not`, `at least`, and `up to` immediately before the words they limit.

### Keep coordination and references parallel

Coordinate equivalent grammatical forms. A list should not mix commands, noun phrases, and descriptive clauses unless the structure explicitly distinguishes them.

Bad:

> The tool validates signatures, schema checking, and can generate a report.

Good:

> The tool validates signatures, checks schemas, and generates a report.

Every pronoun must have one clear antecedent. Repeat the technical noun when `it`, `this`, `that`, `which`, or `they` could refer to multiple objects.

### Use active and passive voice deliberately

Prefer active voice when the actor matters. Use passive voice when the actor is unknown or unimportant, when the receiver is the topic, or when active voice is awkward: `The checksum is stored in the final four bytes.` Do not ban every passive sentence.

### Preserve grammatical signals for global English

- Include articles (`a`, `an`, `the`) where standard English requires them; dropping articles makes noun boundaries harder to parse and translate.
- Use standard subject–verb–object order unless another order is clearer.
- Keep `that` or `who` when omission could blur clause boundaries.
- Use one stable term for each concept. Do not rotate synonyms for variety.
- Keep conditions before instructions: `If secure boot is enabled, sign the image before flashing it.`
- Avoid idioms, slang, culture-specific references, ambiguous phrasal verbs, and claims such as `easy`, `simply`, or `obviously`.
- Use sentence case for headings unless the project requires otherwise.

Short sentences are not automatically clear. Preserve a complete cause, condition, or contrast when splitting would make the relationship implicit.

## Mixed Chinese and English

### Preserve identifiers

Keep these forms verbatim and format them as code when they are code entities:

- `torch.Tensor`、`cudaMalloc()`、`DeviceConfig`
- `--device`、`--dry-run`
- `CUDA_VISIBLE_DEVICES`、`PATH`
- `/etc/acme/config.yaml`、`C:\ProgramData\Acme`
- `CTRL_STATUS`、`RESET_N`
- `0x1F`、`bits [7:4]`

不要翻译 identifier，也不要把 option 写成“设备选项”。可补充普通中文名词：`--device` option、`torch.Tensor` 对象、`CTRL_STATUS` 寄存器。

### Embed established technical terms naturally

常见组合可直接嵌入中文：CUDA kernel、PCIe link、API endpoint、CLI option。若已有稳定中文术语且不损失识别性，可用中文；同一概念不要在中文译名与英文名之间反复切换。

### Units and hardware terms

- 写 `16-bit ADC` 或“16 位 ADC”，不要写 `16bit的ADC`。
- 写 `3.3 V rail` 或“3.3 V 电源轨”。
- register name、signal name 和 pin label 保持原文；首次出现可解释含义。
- SI unit symbol、hex value、bit range 和 protocol literal 不随中文标点或全角转换而改变。

### Punctuation around code

中文句子仍以中文标点结束，标点置于 inline code 外：

> 将 `timeout_ms` 设置为 `5000`，然后重启服务。

代码值内部的逗号、冒号、括号和引号保持原样：`range(0, 8)`、`{"mode":"safe"}`。

## Language check

- 同一概念是否只用一个术语？
- 每个正文句是否有完整、唯一的语法主干？
- 中文的主语、修饰对象、指代、并列关系、否定范围和条件关系是否唯一？
- 中文是否存在成分残缺、主语跳转、名词化堆叠、翻译腔、公文腔或不必要总结？
- 英文是否有完整主句、正确主谓一致、清楚的 modifier/antecedent 和平行结构？
- 英文是否直接、可翻译，且未机械禁用有用的被动语态？
- identifier、option、path、register 和 signal 是否逐字保留？
- 中文标点、半角字符、空格、数字和单位是否一致？
