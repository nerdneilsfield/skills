# Structure and document types

## Choose by reader need

文档类型是写作工具，不是强制 schema。先判断主要读者意图，再选择结构；一页可包含相邻类型，但不要让不同意图互相干扰。

- 学习并获得首次成功：tutorial / quick start
- 完成具体目标：how-to / deployment / procedure
- 理解概念、机制或取舍：concept / explanation / design spec
- 查询稳定事实：reference / API / CLI / hardware reference
- 定位并解决异常：troubleshooting
- 规定组件间契约：interface spec
- 安全、有效地使用产品：user manual
- 复现测量并判断合格：test-verification

README 通常是组合页，可同时包含 overview、quick start、configuration 和少量 reference。根据项目实际保留所需部分，不硬套单一类型。

## Document types

### Overview / README

**Need:** 快速判断项目是什么、是否适用、如何开始、去哪里查详情。

**Usually includes:** 目的和范围、关键能力与限制、最短可运行示例、安装或入口、配置摘要、后续链接。

**Writing:** 先给价值和适用边界，再给最短成功路径。README 中的 reference 只保留高频项，详细表格链接到专页。

**Common failure:** 用项目历史、目录树或内部架构占据开头；quick start 缺少版本、依赖或验证结果。

### Tutorial / quick start

**Need:** 在受控路径中学习，并取得可见结果。

**Usually includes:** 学习目标、前置条件、可用样例、连续步骤、每个阶段的可观察结果、下一步。

**Writing:** 选择一条可靠路径，减少分支；解释足以支持学习，但不在步骤中塞入完整 reference。

**Common failure:** 把 how-to 当 tutorial，只列命令而不建立理解；或提供太多可选路线，使初学者无法判断。

### How-to

**Need:** 已具备基础知识的读者完成一个真实目标。

**Usually includes:** 适用条件、prerequisites、步骤、预期结果、验证、必要的故障入口。

**Writing:** 标题使用动作 + 对象；直接进入目标和步骤。只解释会影响当前任务的原因。

**Common failure:** 按功能菜单罗列，而非按目标组织；把背景知识、所有参数和多个替代方案塞进主路径。

### Concept / explanation

**Need:** 理解某个概念是什么、为何如此、如何与其他部分关联。

**Usually includes:** 定义、上下文、机制、关系、约束、取舍、示例或图。

**Writing:** 用明确问题控制范围；解释因果和设计理由。需要操作时链接到 how-to，不把解释伪装成零散步骤。

**Common failure:** 只改写接口表；或无限扩展背景，读者仍不知道核心机制。

### Reference

**Need:** 快速查找稳定、完整、可比较的事实。

**Usually includes:** 对象定义、字段或参数、值域、默认值、约束、关系、兼容性、示例。

**Writing:** 采用可预测顺序和重复结构；表格用于固定属性，短节用于复杂语义。

**Common failure:** 写成长篇叙事；属性顺序不一致；省略默认值、单位、边界或异常行为。

### API reference

**Need:** 正确调用接口并处理结果。

**Usually includes:** 签名或 endpoint、鉴权、参数、类型、必填性、默认值、范围、请求/响应、返回值、异常或状态码、约束、幂等性或副作用、示例。

**Writing:** 名称和类型逐字匹配权威定义；明确缺省、`null`、空值和省略字段的区别。

**Common failure:** 只给成功示例；示例与签名不一致；未说明错误条件、分页、速率限制或版本边界。

### CLI reference

**Need:** 构造正确命令并预测输出与退出状态。

**Usually includes:** synopsis、arguments、options、类型或格式、默认值、环境变量、配置优先级、stdin/stdout/stderr、exit codes、示例。

**Writing:** 区分必选、可选、可重复和互斥项；占位符与字面量格式不同并有定义。

**Common failure:** 只复制 `--help`；不说明 option 组合、配置优先级、破坏性行为或退出码。

### Troubleshooting

**Need:** 根据症状恢复到正常状态。

**Usually includes:** 可搜索的症状或原始错误、适用范围、可能原因、低风险诊断、解决方法、验证、何时停止并升级。

**Writing:** 从症状出发，不从内部组件分类出发。先做无损检查；临时规避写作 workaround，永久处理写作 resolution。

**Common failure:** 只有“重试”“检查配置”；危险诊断没有风险说明；原因与解决方法无法对应。

### Deployment guide

**Need:** 在目标环境部署、升级、回滚并验证系统。

**Usually includes:** 支持矩阵、容量和权限、依赖、配置、部署步骤、密钥处理、健康检查、升级/回滚、故障入口。

**Writing:** 环境和版本先于命令；明确不可逆步骤、停机影响和回滚前提。

**Common failure:** 只覆盖首次安装；未说明数据迁移、兼容性、回滚限制或验证标准。

### Design spec

**Need:** 让评审者理解并判断拟议设计能否满足目标和约束。

**Usually includes:** 背景、目标与非目标、需求、架构、组件、接口、数据流或状态、关键决策、约束、风险、验证和待决项。

**Writing:** 区分事实、决策、假设和备选方案。图与正文使用同一名称；验证项对应需求。

**Common failure:** 只有方案描述，没有目标、边界、失败模式或验证；把未决定事项写成既定事实。

### Interface spec

**Need:** 让接口两侧独立实现且能够互操作。

**Usually includes:** 边界和角色、协议或信号、数据格式、方向、单位、时序、状态机、错误处理、兼容性、安全和验证。

**Writing:** 使用规范性用语区分要求与说明；为每个字段或信号给出唯一含义。

**Common failure:** 只画框图；未定义时序、所有权、字节序、重试、超时、复位态或保留位。

### Hardware reference

**Need:** 正确连接、配置和集成器件或板卡。

**Usually includes:** pinout、绝对最大额定值与推荐工作条件、电气参数、时序、接口、register map、复位值、bit fields、封装和机械信息。

**Writing:** 明确条件、单位、min/typ/max、测量基准、active-high/low、读写属性、保留位行为和时序关系。

**Common failure:** 混淆 absolute maximum 与 operating condition；图表和 register table 数值不一致；省略电平、容差或测试条件。

### User manual

**Need:** 在产品生命周期内安全、有效地安装、操作、维护和处置产品。

**Usually includes:** 预期用途和限制、产品识别、安全、运输/存储、安装、启动、正常操作、异常处理、维护、技术数据和处置。

**Writing:** 按用户任务与生命周期组织；风险信息出现在相关动作之前。不同角色的任务和权限要分清。

**Common failure:** 只描述控件，不说明目标；安全信息集中在开头后便不再关联危险步骤；维护周期和合格标准缺失。

### Test-verification

这是正式文档类型，不并入普通 procedure。

**Need:** 复现测试或测量，并依据明确标准判断通过或失败。

**Usually includes:** purpose、被测对象和版本、environment/setup、设备和校准状态、preconditions、inputs、procedure、measurement、expected result、tolerance、pass/fail criteria、记录项和异常处理。

**Writing:** 每个判据可测量；区分 expected、observed 和 derived values；给出单位、精度、采样条件和数据处理方法。

**Common failure:** 只写“确认功能正常”；测试步骤无法复现；没有容差、判定规则、环境或设备精度。

## Heading and page structure

- 页面标题反映主要目的。英文任务标题用 base-form verb 开头；概念标题用名词短语。中文任务标题用明确动词，如“配置双机热备”。
- 默认使用 sentence case；产品名、API 和专有名词保留权威大小写。
- 标题层级连续，不用粗体段落冒充标题。
- 标题应独立可理解，避免“概述”“其他”“相关信息”等无对象标题。
- 页面很短时减少层级；层级过深时拆页或重组，不继续堆 `#####`。

