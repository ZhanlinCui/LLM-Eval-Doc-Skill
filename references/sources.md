# 方法来源与使用边界

核对日期：2026-10-21。以下是方法参考，不是业务结果或强制合规要求。决策约定、证据状态、模板与审阅分级是本 skill 的综合设计，不能说成这些机构共同制定的标准。

1. [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)：任务特定评测、目标/数据/指标/比较与迭代、人工校准。只引用方法，不依赖 Evals 平台、SDK 或裁判型号，产品状态另查。
2. [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：区分任务、trial、轨迹与终态，组合评分，至少一次成功与持续成功，能力与回归评测。文章示例样本数不是通用验收要求。
3. [Stanford CRFM — Holistic Evaluation of Language Models](https://crfm.stanford.edu/2022/11/17/helm.html)：多场景、多指标、统一条件和覆盖缺口。排行榜不能直接替代业务选型。
4. [Zheng et al. — Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)：位置、冗长与自偏好等限制。特定实验一致率不能移植为新任务裁判可靠度。
5. [Anthropic — Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/research/infrastructure-noise)：运行资源和限制方式能混杂比较；控制并记录环境，不完全归因给模型。
6. [NIST/SEMATECH — Confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) 与 [Exact binomial confidence limits](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm)：二项率区间。依赖性、配对和代表性需另外处理，不能直接套独立二项区间。

报告把支持具体方法/事实的链接放在论断附近；实测结果引用本次产物。不批量添加无关来源，不把来源效果数字搬进用户实验表。
