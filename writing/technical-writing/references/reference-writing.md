# Reference writing

reference 面向查询，不面向连续阅读。读者应能快速定位对象、比较属性、确认边界，并直接用于实现或操作。

## Use a predictable record

同类对象使用同一字段顺序。缺少信息时明确写“未定义”“不适用”或“待确认”；不要通过省略让读者猜测。

一个 reference entry 通常按需包含：

- name and purpose
- signature、syntax、address 或 identifier
- type、direction、required/optional
- default、range、unit、enum values
- preconditions and constraints
- behavior、side effects、timing
- returns、output、errors
- compatibility、version、deprecation
- example

不是每项都适用于所有对象。只删除不适用项，不删除读者完成调用、配置、接线或实现所需的项。

## Tables versus sections

表格适合比较固定、短小的属性；复杂行为、条件、异常和示例用小节。

Bad: 在一个表格单元格中塞入三段条件、两个代码块和异常说明。

Good: 参数表给出名称、类型、必填性和摘要；复杂约束在参数名小节中展开。

表格必须有清楚列名、单位和上下文。不要用颜色、空白或列位置承载唯一含义。

## API reference

- 签名、endpoint、HTTP method、字段和类型逐字匹配权威定义。
- 区分 omitted、`null`、empty string、empty collection 和 zero。
- 每个参数写明 required/optional、default、range/format、unit、重复性和互斥关系。
- 说明鉴权、权限、幂等性、副作用、分页、速率限制和版本条件（若适用）。
- returns 不只写类型；说明关键字段及何时为空。
- errors 按触发条件描述，不只列代码。
- 至少有一个与正文一致的现实示例；复杂接口应覆盖常见失败或边界。

Bad:

> `timeout`: 请求超时时间。

Good:

> `timeout_ms` (`integer`, optional): 客户端等待响应的最长时间，单位为 ms。范围为 100–60000；默认值为 5000。值为 0 时禁用客户端超时，但服务器的 60 s 上限仍然生效。

## CLI reference

syntax 中明确：

- 字面量、占位符、必选项和可选项；
- option 是否可重复、是否互斥、是否接受多个值；
- 短 option 与长 option 的等价关系；
- 参数解析终止符 `--` 的行为（若支持）；
- 配置文件、环境变量与 CLI option 的优先级；
- stdout、stderr、exit code 和破坏性副作用。

示例不应代替完整 option 定义。不要把 shell prompt 放进可复制命令。

## Interface spec

接口两侧应能据此独立实现。至少明确：

- 角色、所有权和方向；
- 数据或信号定义、编码、字节序、对齐和单位；
- 时序、超时、重试、流控和状态转换；
- 初始化、复位和异常恢复；
- 兼容性、版本协商和保留值；
- 安全边界、认证或电气保护（适用时）；
- 可验证的 conforming behavior。

规范性用语要稳定。若使用 MUST/SHOULD/MAY，先说明其含义或沿用项目规定；不要在同一要求中混用“必须”“应”“建议”而不区分强度。

## Hardware reference

### Pinout

为每个引脚给出编号、名称、方向、类型、电平域、复位/未上电状态和说明。标明 `NC`、reserved、open-drain、active-low 等特殊语义。连接器视图必须说明观察方向。

### Electrical parameters

- 将 absolute maximum ratings 与 recommended operating conditions 分开。
- 参数表给出 symbol、condition、min/typ/max、unit。
- `typ` 不是保证边界；缺失的 min/max 不得自行补齐。
- 明确温度、电压、负载、频率和测量点等测试条件。

### Timing

时序图和表使用同一 signal name 与 parameter symbol。说明 reference edge、阈值、setup/hold、周期、占空比、jitter 及其适用条件。

### Register map

为每个寄存器给出 address/offset、width、access、reset value 和简述。为每个 field 给出 bits、name、access、reset、allowed values 和行为。

明确以下特殊行为：read-to-clear、write-one-to-clear (`W1C`)、self-clearing、latch、reserved bits、未实现地址及并发访问限制。不要建议写入保留位；若必须保留原值，明确 read-modify-write 规则。

## Cross-check reference content

- 签名、表格、示例和正文使用同一名称与数值。
- 枚举值、bit fields 和范围无遗漏、重叠或越界。
- 默认值与 reset value 不混用。
- 单位、进制、字节序、方向和视图基准明确。
- 所有错误、特殊值和保留行为都能定位到触发条件。

