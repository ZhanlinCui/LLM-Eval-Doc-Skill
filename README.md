<p align="center">
  <img src="assets/readme-cover.jpg" alt="模型评测文档 — 从证据到决策" width="100%" />
</p>

<h1 align="center">模型评测文档</h1>

<p align="center"><strong>让评测结果支持模型选型、版本升级与上线决策。</strong></p>
<p align="center">A decision-oriented evaluation skill for LLMs, classifiers, RAG and agents.</p>

<p align="center">
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-194B4C?style=flat-square" />
  <img alt="Evidence first" src="https://img.shields.io/badge/Evidence-First-194B4C?style=flat-square" />
  <img alt="Python standard library" src="https://img.shields.io/badge/Python-Standard_Library-194B4C?style=flat-square" />
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#使用示例">使用示例</a> ·
  <a href="#方法与边界">方法与边界</a> ·
  <a href="SKILL.md">Skill 指令</a> ·
  <a href="references/sources.md">方法来源</a>
</p>

---

一份好的评测文档，应当说明：模型适合什么任务、相对基线有什么收益、付出什么代价、在哪些条件下不能采用，以及别人如何验证这些结论。

**Model Evaluation Doc** 将这条证据链做成可复用的 Codex Skill：从业务验收标准出发，设计实验、核对证据、分析失败，最后给出有适用范围和采用条件的建议。

```text
业务决定 → 代表性任务 → 评分与实验协议 → 可追溯证据 → 有边界的建议
```

## 能帮你完成什么

| 你已有的材料 | Skill 的工作 | 主要交付 |
|---|---|---|
| 任务说明、候选模型或上线目标 | 设计评测 | 执行方案、指标与评分规则、数据计划、结果表头 |
| 汇总结果、逐条日志或实验产物 | 撰写报告 | 决策摘要、结果与切片、失败分析、证据账本、复现入口 |
| 一份已有评测文档 | 审阅与修订 | 按决策影响排序的问题、修订内容、补测优先级 |

可直接使用现有模板和日志。没有实测数据时交付方案；只有汇总数据时保留其来源并标记核验限制。

## 快速开始

### 1. 安装

将整个仓库克隆为一个 Skill 文件夹：

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/ZhanlinCui/LLM-Eval-Doc-Skill.git \
  "$HOME/.agents/skills/model-evaluation-doc"
```

上述用户级目录采用 [Codex 官方本地 Skill 说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。项目级使用时，也可将完整 Skill 文件夹放入项目的 `.agents/skills/`。若当前环境使用其他发现目录，请以该环境的设置为准。

Codex 会检测 Skill 变化；若选择器中未显示，可重启 Codex。完整目录应包含根目录的 `SKILL.md` 及其 `references/`、`scripts/` 等资源。

### 2. 调用

在 Codex 中输入：

```text
使用 $model-evaluation-doc，判断模型 A 能否替换当前模型 B。
任务是中文客服工单分类。我会提供任务说明和已有实验材料。
请生成支持选型决策的评测文档，核验关键指标，并标明证据缺口和采用条件。
```

优先提供三类信息：**要做什么决定、真实任务是什么、已有何种证据**。已有的 Prompt、配置、数据版本和原始日志可以一并附上；材料不足时，Skill 会用明确的假设推进方案，并指出影响结论的缺口。

### 3. 更新

```bash
git -C "$HOME/.agents/skills/model-evaluation-doc" pull --ff-only
```

## 使用示例

### 从零设计评测

```text
使用 $model-evaluation-doc。
我们计划用新模型处理中文客服工单，目前没有实验数据。
目标是在控制高风险误分的前提下降低处理成本。
请先产出可执行方案，建议验收标准时注明依据和待确认项。
```

### 将已有数据变成报告

```text
使用 $model-evaluation-doc。
请读取我提供的模型配置、逐条运行记录和评分文件，评估候选能否替换基线。
复算关键指标，分开质量、风险、成本与延迟，给出配对比较的适用方法，
并将推荐依赖的结论定位到原始证据。
```

### 审阅已有结论

```text
使用 $model-evaluation-doc 审阅这份 Agent 评测报告。
重点检查尝试预算是否一致、是否验证真实任务终态、裁判是否有效，
以及统计证据是否足以支撑上线建议。保留原结构并直接修改。
```

### 检查决策模型的稳定性

```text
使用 $model-evaluation-doc。
我们发现选项顺序变化时输出字母会变化。
请设计语义等价扰动测试，区分正确性、重复调用稳定性和决策翻转，
明确语义标签映射、统计单位及分母。
```

## 方法与边界

### 证据强度决定结论强度

| 证据状态 | 文档如何处理 |
|---|---|
| 已核验 | 给出定位、计算口径与核验范围 |
| 已报告，未复核 | 保留用户或外部汇总，披露缺少的原始材料 |
| 待验证假设 | 将解释、预测或建议与观察事实分开，说明验证方式 |
| 缺失 | 说明缺口会影响什么判断，以及优先补什么 |

关键主张通过 `claim_id` 连接到数据范围、配置、分母、计算与证据位置。完整结构见 [报告骨架](references/report-template.md)。

### 按任务加载专项规则

| 对象 | 重点检查 |
|---|---|
| 分类与概率决策 | 逐类表现、混淆、高风险错误、阈值、概率校准 |
| 语义等价扰动 | 标签映射、决策翻转、组内一致性、变体依赖 |
| 开放生成与 RAG | 正确性、完整性、检索覆盖、证据忠实性、引用支持 |
| Agent 与工具系统 | 真实终态、工具与权限、恢复、副作用、尝试预算 |

详见 [评测方法](references/methodology.md) 与 [专项模块](references/task-modules.md)。

### 结论需要通过六项检查

**能决策 · 能追溯 · 能复跑 · 能质疑 · 能行动 · 能维护**

Skill 会区分模型、系统和产品层级；保留超时、失败和重试的成本；处理重复运行与变体的依赖；将风险硬门槛与平均质量、成本收益分开。没有充分证据时，建议可以是继续保留基线或完成指定补测。

本仓库提供评测文档工作流和可选的数据核验工具。实际实验仍依赖用户提供的数据、模型调用环境及授权；文档完成不等于实验完成，离线通过不自动证明线上收益。Word、PDF 等排版导出取决于运行环境可用的文档能力。

## 可选：证据检查脚本

已有明确二元成功条件、且需要对账时，可将现有日志映射为 [证据交换格式](references/evidence-contract.md)，再运行：

```bash
python3 scripts/audit_evidence.py /path/to/evidence.json --out /path/to/audit.json
```

脚本仅依赖 Python 3 标准库，检查计划/实际覆盖、重复记录、成功率分母、未知成本和基础汇总。`/path/to/…` 为使用者自己的文件路径。

| 退出码 | 含义 |
|---|---|
| `0` | 已实现的检查项未发现问题 |
| `1` | 存在需要解决或披露的缺口 |
| `2` | 输入无效或文件读写失败 |

脚本不验证原始记录真实性、引用内容、裁判正确性或统计独立性，也不生成置信区间或上线认证。

## 仓库导航

```text
.
├── SKILL.md                         # 入口与决策工作流
├── agents/openai.yaml               # 名称、描述与默认调用提示
├── references/
│   ├── methodology.md               # 数据、协议、评分与统计判断
│   ├── task-modules.md              # 分类、扰动、RAG、Agent 专项
│   ├── report-template.md           # 自适应报告骨架
│   ├── evidence-contract.md         # 可选证据格式与脚本口径
│   └── sources.md                   # 原始方法来源与使用边界
├── scripts/audit_evidence.py         # 确定性证据对账
├── tests/test_audit_evidence.py      # 脚本回归测试
├── evals/scenarios.json              # 8 个行为回归场景
└── assets/readme-cover.jpg           # README 封面
```

## 验证与维护

```bash
python3 -m unittest discover -s tests -v
```

当前 **21 项脚本测试已通过**，覆盖缺失运行、未知成本、重复记录、超时、未评分、非法数值和 CLI 输出等账目边界；Skill 结构校验已通过。

另提供 [8 个行为回归场景](evals/scenarios.json)，用于观察实际产出是否遵守证据和决策边界。**这些场景尚未完成独立模型测试**，不能与脚本测试混为一谈。

修改方法或指令后，用真实任务检查建议是否改变、证据是否可定位、未验证内容是否被明确标注；修改脚本后重跑上述测试。提交问题时附最小输入、预期行为与实际结果，业务样本请先脱敏。

## 方法来源

设计参考 OpenAI 评测实践、Anthropic Agent 评测经验、Stanford HELM、LLM-as-a-Judge 研究及 NIST 二项率区间资料。每类来源支持什么、不支持什么，见 [完整来源说明](references/sources.md)。

本 Skill 的决策约定、证据状态、报告结构与审阅分级是综合设计；实际业务结论必须由本次实验支持。

---

<p align="center"><strong>把“模型表现如何”写清楚，把“接下来怎么做”落到证据上。</strong></p>
