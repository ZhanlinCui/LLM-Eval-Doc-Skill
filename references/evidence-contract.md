# 可选的证据交换格式

已有日志不必迁移。仅当结构化核验有价值时，将日志映射为此 JSON，并保留原文件、映射规则与版本。脚本只检查结构和账目，不证明记录真实或引用存在。

## 输入约定（v1）

```json
{
  "schema_version": "1",
  "evaluation_id": "demo-only",
  "dataset_ref": "datasets/test-v1.json",
  "currency": "USD",
  "cases": [
    {"case_id": "task-1", "group_id": "independent-group-1"}
  ],
  "configs": [
    {"config_id": "baseline", "model_version": "exact-version", "config_ref": "configs/baseline.json", "trials_per_case": 1}
  ],
  "records": [
    {"config_id": "baseline", "case_id": "task-1", "trial_id": 1,
     "status": "completed", "success": true,
     "latency_ms": 1200, "cost": 0.01,
     "output_ref": "outputs/task-1.json", "grade_ref": "grades/task-1.json"}
  ]
}
```

以上只是格式示例，不是业务结果。数组和记录可有其他字段（slice、source、expected_result、rubric_ref、trace_ref、timestamps 等），脚本不会评价这些字段。

- cases/configs 非空，ID 唯一。每个 config 预期执行所有 case，每题 trial_id 为 `1..trials_per_case`。若协议有不同测试范围，拆为不同评测清单，不把未安排的测试标作缺失。
- group_id 是重采样/依赖组，例如同用户、同会话或原题变体；真正独立任务可各用独立组。脚本只数不同 ID，不能验证独立性。
- `config_ref` 指向实际 Prompt、工具、参数和环境配置；`model_version` 保留原始精确值，未知则如实写明，不能自行补快照。
- `status` 为 `completed / timeout / api_error / tool_error / cancelled`。它描述整个 trial 的结束状态，不是其中一次内部调用；已恢复的 API 错误记在轨迹，trial 正常结束用 completed。
- `completed` 的 `success` 是业务成功条件的布尔判定；尚未评分为 null。其他结束状态 success 必须 false。正确拒答可为 completed + true；答案错误可为 completed + false。
- `cost` 为 trial 所有内部调用、重试及协议选定成本范围的合计，统一币种；未知写 null，不写 0。若汇率转换需额外保存原币种、汇率/日期及成本范围。每成功任务成本只在覆盖、评分、成本完整且至少一个成功时计算。
- `latency_ms` 为请求开始至结束的已观察耗时，未知为 null。超时耗时不是假如继续运行的完成时间。
- `output_ref`、`grade_ref` 为可定位字符串或 null；脚本对已评分 completed 记录检查是否填写，但不打开引用。操作失败的错误日志宜另外加 error_ref。
- 不要为适配脚本把连续分数、未知终态或工具成功码强制转为业务 true。只适用于已有明确二元成功定义的任务；其他指标保留在原始表中单独分析。

## 运行

```bash
python3 /path/to/model-evaluation-doc/scripts/audit_evidence.py /path/to/evidence.json --out /path/to/audit.json
```

只依赖 Python 3 标准库，不调用外部 API。退出码：0 为未发现已实现检查项的问题；1 为存在须解决/披露的缺口；2 为输入无效。输出 JSON 的 findings 与 summaries 可用于报告附录，**不能直接当验收证书**。

主要汇总口径：

- `success_rate_e2e`：覆盖且评分完整时，成功数/计划运行数；否则 null。
- `confirmed_success_fraction_of_scheduled`：已确认成功/计划运行数，不等同最终成功率。
- `missing_runs`、`ungraded_runs`、任务/组/运行数分别给出。
- `cost_per_success`：完整成本总和/成功数。没有成功、记录不完整或评分不完整时为 null，同时看 findings 与计数。
- `observed_duration_p95_ms`：全部已记录耗时的 nearest-rank P95，含超时的截断耗时；附样本数，不冒充“成功任务完成延迟 P95”。

不同 trials_per_case 会触发比较预算提示。脚本不生成置信区间、不估计 pass@k、不推断因果、不核查引用内容。权重、切片、裁判校准和统计推断仍按方法文档完成。

## 维护时验证

修改脚本后运行 `python3 -m unittest discover -s /path/to/model-evaluation-doc/tests -v`。修改评测方法或主指令时，可用 [行为回归场景](../evals/scenarios.json) 检查实际产出；该文件是测试设计，不代表这些行为已被独立验证。不要在普通报告任务中自动运行维护测试。
