#!/usr/bin/env python3
"""Audit a v1 binary-outcome evidence manifest; no network or third-party deps."""
import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def number_or_null(value):
    return value is None or (
        type(value) in (int, float) and math.isfinite(value) and value >= 0
    )


def indexed(items, key):
    require(isinstance(items, list) and bool(items), f'{key}: expected nonempty list')
    result = {}
    for item in items:
        require(isinstance(item, dict), f'{key}: expected objects')
        ident = item.get(key)
        require(nonempty(ident), f'{key}: expected nonempty ID')
        require(ident not in result, f'{key}: duplicate ID {ident}')
        result[ident] = item
    return result


def p95(values):
    return sorted(values)[math.ceil(0.95 * len(values)) - 1] if values else None


def audit(data):
    require(isinstance(data, dict), 'root must be an object')
    require(data.get('schema_version') == '1', 'schema_version must be string 1')
    for field in ('evaluation_id', 'dataset_ref', 'currency'):
        require(nonempty(data.get(field)), f'{field}: required nonempty string')
    cases = indexed(data.get('cases'), 'case_id')
    configs = indexed(data.get('configs'), 'config_id')
    for case in cases.values():
        require(nonempty(case.get('group_id')), 'case group_id is required')
    for config in configs.values():
        for field in ('model_version', 'config_ref'):
            require(nonempty(config.get(field)), f'config {field} is required')
        trials = config.get('trials_per_case')
        require(type(trials) is int and trials > 0, 'trials_per_case must be positive int')
    records = data.get('records')
    require(isinstance(records, list), 'records must be a list (may be empty)')
    seen = set()
    by_config = {ident: [] for ident in configs}
    findings = []
    statuses = {'completed', 'timeout', 'api_error', 'tool_error', 'cancelled'}
    for index, record in enumerate(records):
        prefix = f'record[{index}]'
        require(isinstance(record, dict), f'{prefix}: expected object')
        cid, case_id, trial = (record.get(k) for k in ('config_id', 'case_id', 'trial_id'))
        require(isinstance(cid, str) and cid in configs, f'{prefix}: unknown config_id')
        require(isinstance(case_id, str) and case_id in cases, f'{prefix}: unknown case_id')
        require(type(trial) is int and 1 <= trial <= configs[cid]['trials_per_case'],
                f'{prefix}: trial_id out of planned range')
        key = (cid, case_id, trial)
        require(key not in seen, f'{prefix}: duplicate config/case/trial {key}')
        seen.add(key)
        status = record.get('status')
        require(isinstance(status, str) and status in statuses, f'{prefix}: invalid status')
        require('success' in record, f'{prefix}: success is required (null if ungraded)')
        success = record['success']
        require(success is None or type(success) is bool, f'{prefix}: success must be boolean/null')
        require(status == 'completed' or success is False,
                f'{prefix}: non-completed trial must have success=false')
        for field in ('cost', 'latency_ms'):
            require(field in record and number_or_null(record[field]),
                    f'{prefix}: {field} must be finite nonnegative number/null')
        for field in ('output_ref', 'grade_ref'):
            ref = record.get(field)
            require(ref is None or nonempty(ref), f'{prefix}: invalid {field}')
            if status == 'completed' and success is not None and ref is None:
                findings.append(f'{prefix}: scored completed trial lacks {field}')
        by_config[cid].append(record)

    summaries = {}
    groups = {case['group_id'] for case in cases.values()}
    for cid, config in configs.items():
        rows = by_config[cid]
        expected = len(cases) * config['trials_per_case']
        missing = expected - len(rows)
        ungraded = sum(row['success'] is None for row in rows)
        successes = sum(row['success'] is True for row in rows)
        absent_cost = sum(row['cost'] is None for row in rows)
        durations = [row['latency_ms'] for row in rows if row['latency_ms'] is not None]
        known_cost = sum(row['cost'] for row in rows if row['cost'] is not None)
        require(math.isfinite(known_cost), f'{cid}: aggregate cost exceeds finite numeric range')
        complete = missing == 0 and ungraded == 0
        cost_complete = missing == 0 and absent_cost == 0
        for count, message in (
            (missing, 'planned runs missing'), (ungraded, 'runs ungraded'),
            (absent_cost, 'recorded costs unknown'),
            (len(rows) - len(durations), 'recorded durations unknown'),
        ):
            if count:
                findings.append(f'{cid}: {count} {message}')
        if not successes:
            findings.append(f'{cid}: no confirmed success; cost_per_success is undefined')
        observed_cases = {row['case_id'] for row in rows}
        summaries[cid] = {
            'planned_tasks': len(cases), 'planned_groups': len(groups),
            'observed_tasks': len(observed_cases),
            'observed_groups': len({cases[ident]['group_id'] for ident in observed_cases}),
            'trials_per_case': config['trials_per_case'],
            'planned_runs': expected, 'recorded_runs': len(rows),
            'missing_runs': missing, 'ungraded_runs': ungraded,
            'status_counts': dict(sorted(Counter(row['status'] for row in rows).items())),
            'confirmed_successes': successes,
            'confirmed_success_fraction_of_scheduled': successes / expected,
            'success_rate_e2e': successes / expected if complete else None,
            'known_cost_sum': known_cost,
            'total_cost': known_cost if cost_complete else None,
            'cost_per_success': known_cost / successes if complete and cost_complete and successes else None,
            'observed_duration_count': len(durations),
            'observed_duration_p95_ms': p95(durations),
        }
    if len({c['trials_per_case'] for c in configs.values()}) > 1:
        findings.append('configs use unequal trial budgets; do not infer equal-budget superiority')
    return {
        'audit_status': 'findings' if findings else 'clean',
        'evaluation_id': data['evaluation_id'], 'currency': data['currency'],
        'findings': findings, 'summaries': summaries,
        'limitations': [
            'References, record truth, grader correctness and group independence are not verified.',
            'Descriptive counts only; no confidence intervals, weighted slices or deployment approval.',
            'Observed durations include censored timeout durations; P95 uses nearest rank.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.input.read_text(encoding='utf-8')))
        code = 1 if result['findings'] else 0
    except (OSError, ValueError, OverflowError, RecursionError) as exc:
        result = {'audit_status': 'invalid', 'errors': [str(exc)]}
        code = 2
    output = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.out:
        try:
            args.out.write_text(output, encoding='utf-8')
        except OSError as exc:
            print(f'Unable to write audit: {exc}', file=sys.stderr)
            return 2
    else:
        sys.stdout.write(output)
    return code


if __name__ == '__main__':
    sys.exit(main())
