<p align="center"><a href="README.md">简体中文</a> · <strong>English</strong></p>

<p align="center">
  <img src="assets/readme-cover-en.jpg" alt="Model Evaluation Doc — from evidence to decision" width="100%" />
</p>

<h1 align="center">Model Evaluation Doc</h1>

<p align="center"><strong>Turn evaluation evidence into model selection, upgrade and deployment decisions.</strong></p>
<p align="center">A decision-oriented evaluation skill for LLMs, classifiers, RAG and agents.</p>

<p align="center">
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-194B4C?style=flat-square" />
  <img alt="Evidence first" src="https://img.shields.io/badge/Evidence-First-194B4C?style=flat-square" />
  <img alt="Python standard library" src="https://img.shields.io/badge/Python-Standard_Library-194B4C?style=flat-square" />
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#usage-examples">Examples</a> ·
  <a href="#methods-and-limits">Methods and limits</a> ·
  <a href="SKILL.md">Skill instructions</a> ·
  <a href="references/sources.md">Sources</a>
</p>

---

A useful evaluation report explains which tasks a model can handle, how it compares with the baseline, what the gains cost, when it should not be adopted, and how others can verify the conclusions.

**Model Evaluation Doc** packages that evidence chain into a reusable Codex Skill. Start with business acceptance criteria, design the experiments, check the evidence, analyze failures, and produce recommendations with explicit conditions and limits.

```text
Business decision → Representative tasks → Scoring and protocol → Traceable evidence → Scoped recommendation
```

## What it helps you deliver

| Your starting point | What the skill does | Main deliverables |
|---|---|---|
| Task requirements, candidate models or deployment goals | Design an evaluation | Execution plan, metrics and rubrics, data plan, empty results tables |
| Aggregate results, per-run logs or experiment artifacts | Write a report | Decision summary, overall and slice results, failure analysis, evidence ledger, reproduction entry points |
| An existing evaluation report | Review and revise | Findings ranked by decision impact, edits, priorities for additional testing |

Use existing templates and logs. With no measured data, the skill produces a plan. With aggregate data alone, it preserves the source and marks the verification limits.

## Quick start

### 1. Install

Clone the entire repository as one skill folder:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/ZhanlinCui/LLM-Eval-Doc-Skill.git \
  "$HOME/.agents/skills/model-evaluation-doc"
```

This user-level location follows the [official Codex local skill documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills). For project-level use, place the complete skill folder under your project's `.agents/skills/` directory. If your environment uses another discovery location, follow that environment's configuration.

Codex detects skill changes automatically. If the skill does not appear in the selector, restart Codex. Keep the root `SKILL.md` together with its `references/`, `scripts/` and other resources.

### 2. Invoke

Enter this in Codex:

```text
Use $model-evaluation-doc to assess whether model A can replace our current model B.
The task is Chinese customer-support ticket classification. I will provide the task
requirements and existing experiment artifacts. Write the report in English.
Verify key metrics and identify evidence gaps and adoption conditions.
```

Start with three things: **the decision you need to make, the real workload, and the evidence you already have**. Include prompts, configurations, dataset versions and raw logs when available. With incomplete inputs, the skill proceeds with explicit assumptions and identifies gaps that affect the conclusion.

This README is available in English and Chinese. The core instructions and supporting method references are currently written in Chinese; the skill follows the user's requested output language, so you can ask for plans, reviews and reports in English.

### 3. Update

```bash
git -C "$HOME/.agents/skills/model-evaluation-doc" pull --ff-only
```

## Usage examples

### Design an evaluation from scratch

```text
Use $model-evaluation-doc. We plan to use a new model for customer-support ticket
classification, but have no experiment data yet. We want to reduce processing cost
while controlling high-risk misclassifications. Write an executable evaluation plan
in English. Mark proposed acceptance thresholds with their rationale and any items
that need confirmation.
```

### Turn existing data into a report

```text
Use $model-evaluation-doc. Read the model configurations, per-run records and grading
files I provide. Assess whether the candidate can replace the baseline. Recompute
key metrics, separate quality, risk, cost and latency, identify suitable methods for
paired comparisons, and trace the recommendation to its original evidence.
Write the report in English.
```

### Review an existing conclusion

```text
Use $model-evaluation-doc to review this agent evaluation report. Check whether
attempt budgets are comparable, actual task outcomes were verified, graders are
valid, and the statistical evidence supports the deployment recommendation.
Preserve the structure, make the edits directly, and write in English.
```

### Test decision stability

```text
Use $model-evaluation-doc. We observe different output letters when answer choices
are reordered. Design a semantics-preserving perturbation test. Separate correctness,
repeated-run stability and semantic decision flips. Define label mapping, the unit
of analysis and all denominators. Write the plan in English.
```

## Methods and limits

### Match the strength of the conclusion to the evidence

| Evidence status | How the report handles it |
|---|---|
| Verified within a stated scope | Provides evidence locations, calculation definitions and verification scope |
| Reported, not independently checked | Preserves user or external summaries and discloses missing raw artifacts |
| Hypothesis to test | Separates explanations, predictions and proposals from observations, with a way to test them |
| Missing | Explains which judgment the gap affects and what to collect first |

Key claims use `claim_id` to connect data scope, configuration, denominators, calculations and evidence locations. See the [report template](references/report-template.md) for the full structure.

### Load task-specific methods as needed

| Evaluation target | Main checks |
|---|---|
| Classification and probabilistic decisions | Per-class performance, confusion, high-risk errors, thresholds, probability calibration |
| Semantics-preserving perturbations | Semantic label mapping, decision flips, within-group consistency, dependence among variants |
| Open-ended generation and RAG | Correctness, completeness, retrieval coverage, faithfulness to evidence, citation support |
| Agents and tool-using systems | Actual final state, tools and permissions, recovery, side effects, attempt budgets |

See the [methodology guide](references/methodology.md) and [task-specific modules](references/task-modules.md).

### Check six properties before delivery

**Decision value · Traceability · Reproducibility · Scrutability · Actionability · Maintainability**

The skill distinguishes model, system and product evaluations; accounts for timeouts, failures and retries; handles dependence among repeated trials and variants; and keeps risk gates separate from average quality and cost gains. When evidence is insufficient, the recommendation may be to retain the baseline or complete specific additional tests.

This repository provides a documentation workflow and an optional data-auditing tool. Actual experiments depend on the user's data, model execution environment and authorization. A completed report does not mean an experiment has been run, and offline results do not automatically establish production benefits. Word or PDF export depends on the document capabilities available in the host environment.

## Optional evidence audit

When a task has a clearly defined binary success outcome and structured reconciliation is useful, map existing logs to the [evidence interchange format](references/evidence-contract.md), then run:

```bash
python3 scripts/audit_evidence.py /path/to/evidence.json --out /path/to/audit.json
```

The script uses only the Python 3 standard library. It checks planned versus recorded coverage, duplicate records, success-rate denominators, unknown costs and basic aggregates. Replace `/path/to/…` with your own file paths.

| Exit code | Meaning |
|---|---|
| `0` | No issues found by the implemented checks |
| `1` | Gaps need to be resolved or disclosed |
| `2` | Invalid input or a file read/write failure |

The script does not verify record truth, referenced content, grader correctness or statistical independence. It does not calculate confidence intervals or certify deployment readiness.

## Repository guide

```text
.
├── README.md                        # Chinese documentation
├── README.en.md                     # English documentation
├── SKILL.md                         # Entry point and decision workflow
├── agents/openai.yaml               # UI name, description and invocation prompt
├── references/
│   ├── methodology.md               # Data, protocols, grading and statistical judgment
│   ├── task-modules.md              # Classification, perturbations, RAG and agents
│   ├── report-template.md           # Adaptable report outline
│   ├── evidence-contract.md         # Optional evidence format and script definitions
│   └── sources.md                   # Primary sources and their limits
├── scripts/audit_evidence.py         # Deterministic evidence reconciliation
├── tests/test_audit_evidence.py      # Script regression tests
├── evals/scenarios.json              # Eight behavioral regression scenarios
└── assets/
    ├── readme-cover.jpg             # Chinese README cover
    └── readme-cover-en.jpg          # English README cover
```

## Validation and maintenance

```bash
python3 -m unittest discover -s tests -v
```

**All 21 script tests have passed.** They cover accounting edge cases including missing runs, unknown costs, duplicates, timeouts, ungraded outputs, invalid numbers and CLI output. The skill has also passed structural validation.

The repository includes [eight behavioral regression scenarios](evals/scenarios.json) for checking whether actual outputs respect evidence and decision boundaries. **These scenarios have not yet been independently tested with a model.** They are separate from the passing script tests.

After changing methods or instructions, use realistic tasks to check whether recommendations change appropriately, evidence remains traceable, and unverified claims are labeled. Rerun the tests after script changes. When reporting an issue, include a minimal input, expected behavior and actual result; remove sensitive information from business examples first.

## Method sources

The design draws on OpenAI evaluation guidance, Anthropic's agent evaluation experience, Stanford HELM, LLM-as-a-Judge research and NIST materials on binomial confidence intervals. See the [source notes](references/sources.md) for what each source supports and its limits.

The decision criteria workflow, evidence statuses, report structure and review priorities are a synthesis developed for this skill. Business conclusions must be supported by the current experiment.

---

<p align="center"><strong>Explain model performance clearly. Ground the next decision in evidence.</strong></p>
