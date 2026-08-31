# Sources read

实际访问日期：2026-08-31。以下记录只说明本 skill 从公开资料吸收的规则，不作学术式逐条引用。

## Public style guides and information models

- [Google Developer Documentation Style Guide](https://developers.google.com/style)：阅读 About、Highlights、Voice and tone、Procedures、Headings and titles、Lists、Code in text、UI elements and interaction、Units of measurement、Write accessible documentation、Word list。主要吸收：主动语态与第二人称、条件先于动作、procedure 的动作/结果顺序、sentence-case 标题、平行列表、代码与 UI 格式、单位和范围、global audience 与 accessibility。该 guide 明确允许为清晰性偏离规则，因此本 skill 不把一般风格置于技术正确性之上。
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)：阅读 brand voice、word choice、grammar/verbs、procedures and instructions、UI interaction、capitalization、global communications/writing tips。主要吸收：直接且可扫描的表达、present tense、imperative procedure、稳定术语、input-neutral UI verbs、sentence-style capitalization、短而标准的句法及可翻译性。
- [IBM Style / Technical Content Standards](https://www.ibm.com/docs/en/technical-content?topic=standards-style) 与 [Content Quality](https://www.ibm.com/docs/en/technical-content?topic=standards-content-quality)：主要吸收：accuracy、completeness、clarity、consistency、retrievability、global audience、主动/被动语态的适用条件、平行结构、一致 highlighting 和可复用表达。
- [GitLab Documentation Style Guide](https://docs.gitlab.com/development/documentation/styleguide/) 与 [Documentation topic types](https://docs.gitlab.com/development/documentation/topic_types/)：阅读 task、concept、reference、troubleshooting。主要吸收：面向用户任务而非实现过程、prerequisites、可搜索故障症状、CLI/code formatting、简洁直接且利于 localization 的写法。
- [Kubernetes Documentation Style Guide](https://kubernetes.io/docs/contribute/style/style-guide/)、[Documentation Content Guide](https://kubernetes.io/docs/contribute/style/content-guide/) 与 [Page content types](https://kubernetes.io/docs/contribute/style/page-content-types/)：主要吸收：present tense、active voice、直接表达、API/code name 处理、命令与输出分离、Markdown heading 结构及 task/concept/reference 页面边界。
- [Diátaxis](https://diataxis.fr/)：阅读 Tutorials、How-to guides、Reference、Explanation 及 map。主要吸收：学习、目标、查询和理解是不同读者意图，需采用不同写法。本 skill 不强制所有文档机械四分，README、user manual、design spec 等可保留适合自身目的的组合结构。
- [OASIS DITA Technical Content](https://dita-lang.org/dita-techcomm/archspec/technicalcontent/dita-technicalcontent-informationtypes)：阅读 concept、general task、reference 和 information typing。主要吸收：concept 回答“是什么”、task 回答“如何做”、reference 支持查询；task 由前置/上下文、步骤、结果和 troubleshooting 等部分构成。不采用 XML schema 或 DTD 作为本 skill 的结构。
- [ASD-STE100 Simplified Technical English, Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) 与 [official FAQ](https://www.asd-ste100.org/STE_faq.html)：主要吸收：controlled terminology、one word/one meaning、程序使用直接 imperative、降低句法歧义，以及 Warning/Caution 需表达风险。未机械采用航空词典、句长限制或领域专用规则。

## Standards and official previews

- [ISO/IEC/IEEE 26514:2022](https://www.iso.org/standard/77451.html) 及 [ISO Online Browsing Platform preview](https://www.iso.org/obp/ui/#iso:std:iso-iec-ieee:26514:ed-1:v1:en)：公开摘要、目录和预览显示其覆盖受众/任务分析、information quality，以及软件用户信息的 structure、content、format、conceptual/instructional/reference/troubleshooting、API 和 localization。skill 由此强化读者需求、信息质量、API reference 与生命周期适用性；未根据未公开条文补造要求。
- [IEC/IEEE 82079-1:2019](https://webstore.iec.ch/en/publication/29075) 及 [ISO Online Browsing Platform contents](https://www.iso.org/obp/ui/#iso:std:iec-ieee:82079:-1:ed-2:v1:en,fr)：公开摘要与目录覆盖各种产品的 information for use、原则、管理过程、内容、结构、媒介和专业能力。skill 由此强化产品生命周期、procedure、安全信息及设备/数据风险；未声称复现完整标准。
- [GB/T 32424-2015 官方记录](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=46E7B46987557413B4AFDC53F1BD6D8A)：官方页面确认该标准为《系统与软件工程 用户文档的设计者和开发者要求》，采用国际标准且因版权不公开全文。仅结合其公开范围和 ISO/IEC 26514 的可访问资料理解用户文档的过程、结构和内容，不猜具体条文。
- [GB/T 9969-2008 官方记录](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=A948ABC041945DF531BADF590044C971)：官方页面确认其为现行《工业产品使用说明书 总则》。公开元数据有限；skill 对工业产品说明、安全、生命周期和 procedure 的具体规则主要依据 IEC/IEEE 82079-1 的公开资料，不把标题推断成条文。
- [GB/T 8567-2006 官方记录](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=84C42B6277D2714B7176B10C6E6B1A44)：官方页面确认其为现行《计算机软件文档编制规范》。未从不可访问内容推断模板或强制章节；本 skill 仅保留 design spec、interface spec、test-verification 等实际工程文档类型，并按读者用途裁剪结构。

