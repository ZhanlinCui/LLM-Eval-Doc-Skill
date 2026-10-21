"""Deterministic accounting tests; no model calls or external side effects."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_evidence.py'
SPEC = importlib.util.spec_from_file_location('audit_evidence', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    data = {
        'schema_version': '1', 'evaluation_id': 'synthetic-test',
        'dataset_ref': 'fixture-only', 'currency': 'USD',
        'cases': [{'case_id': 'a', 'group_id': 'same-source'},
                  {'case_id': 'b', 'group_id': 'same-source'}],
        'configs': [{'config_id': cid, 'model_version': 'fixture-version',
                     'config_ref': 'fixture-config', 'trials_per_case': 1}
                    for cid in ('baseline', 'candidate')],
        'records': [],
    }
    for cid, case, success, cost, latency in (
        ('baseline', 'a', True, 1.0, 100),
        ('baseline', 'b', False, 2.0, 200),
        ('candidate', 'a', True, 0.5, 50),
        ('candidate', 'b', True, 0.5, 100),
    ):
        data['records'].append({
            'config_id': cid, 'case_id': case, 'trial_id': 1,
            'status': 'completed', 'success': success,
            'cost': cost, 'latency_ms': latency,
            'output_ref': 'fixture-output', 'grade_ref': 'fixture-grade',
        })
    return data


class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def summary(self, cid='baseline'):
        return MODULE.audit(self.data)['summaries'][cid]

    def test_complete_accounting(self):
        result = MODULE.audit(self.data)
        self.assertEqual(result['audit_status'], 'clean')
        base = result['summaries']['baseline']
        self.assertEqual(base['success_rate_e2e'], 0.5)
        self.assertEqual(base['cost_per_success'], 3.0)
        self.assertEqual(base['observed_duration_p95_ms'], 200)

    def test_groups_are_not_runs(self):
        base = self.summary()
        self.assertEqual((base['planned_tasks'], base['planned_groups'], base['planned_runs']), (2, 1, 2))

    def test_timeout_stays_in_denominator_and_cost(self):
        self.data['records'][1]['status'] = 'timeout'
        base = self.summary()
        self.assertEqual(base['success_rate_e2e'], 0.5)
        self.assertEqual(base['cost_per_success'], 3.0)
        self.assertEqual(base['status_counts']['timeout'], 1)

    def test_missing_runs_do_not_become_known_failures(self):
        self.data['records'].pop(1)
        base = self.summary()
        self.assertIsNone(base['success_rate_e2e'])
        self.assertIsNone(base['total_cost'])
        self.assertIsNone(base['cost_per_success'])
        self.assertEqual(base['confirmed_success_fraction_of_scheduled'], 0.5)
        self.assertEqual(base['missing_runs'], 1)

    def test_ungraded_output_is_not_success(self):
        self.data['records'][1]['success'] = None
        base = self.summary()
        self.assertEqual(base['ungraded_runs'], 1)
        self.assertIsNone(base['success_rate_e2e'])
        self.assertIsNone(base['cost_per_success'])

    def test_unknown_cost_not_zero(self):
        self.data['records'][0]['cost'] = None
        base = self.summary()
        self.assertEqual(base['known_cost_sum'], 2.0)
        self.assertIsNone(base['total_cost'])
        self.assertIsNone(base['cost_per_success'])

    def test_no_success_cost_undefined(self):
        self.data['records'][0]['success'] = False
        base = self.summary()
        self.assertEqual(base['success_rate_e2e'], 0)
        self.assertIsNone(base['cost_per_success'])

    def test_zero_cost_is_valid(self):
        for record in self.data['records']:
            record['cost'] = 0
        self.assertEqual(self.summary()['cost_per_success'], 0)

    def test_missing_latency_has_coverage(self):
        self.data['records'][0]['latency_ms'] = None
        base = self.summary()
        self.assertEqual(base['observed_duration_count'], 1)
        self.assertTrue(MODULE.audit(self.data)['findings'])

    def test_duplicate_trial_rejected(self):
        self.data['records'].append(copy.deepcopy(self.data['records'][0]))
        with self.assertRaises(MODULE.Invalid):
            MODULE.audit(self.data)

    def test_duplicate_case_rejected(self):
        self.data['cases'].append(copy.deepcopy(self.data['cases'][0]))
        with self.assertRaises(MODULE.Invalid):
            MODULE.audit(self.data)

    def test_unknown_references_rejected(self):
        for field in ('case_id', 'config_id'):
            data = fixture()
            data['records'][0][field] = 'unknown'
            with self.subTest(field=field), self.assertRaises(MODULE.Invalid):
                MODULE.audit(data)

    def test_boolean_success_not_integer(self):
        self.data['records'][0]['success'] = 1
        with self.assertRaises(MODULE.Invalid):
            MODULE.audit(self.data)

    def test_operational_error_cannot_be_success(self):
        self.data['records'][0]['status'] = 'api_error'
        with self.assertRaises(MODULE.Invalid):
            MODULE.audit(self.data)

    def test_bad_numeric_values(self):
        for value in (-1, float('nan'), float('inf'), True, '1'):
            for field in ('cost', 'latency_ms'):
                data = fixture()
                data['records'][0][field] = value
                with self.subTest(value=value, field=field), self.assertRaises(MODULE.Invalid):
                    MODULE.audit(data)

    def test_aggregate_overflow_rejected(self):
        for record in self.data['records'][:2]:
            record['cost'] = 1e308
        with self.assertRaises(MODULE.Invalid):
            MODULE.audit(self.data)

    def test_trial_range_and_type(self):
        for trial in (0, 2, True, '1'):
            self.data['records'][0]['trial_id'] = trial
            with self.subTest(trial=trial), self.assertRaises(MODULE.Invalid):
                MODULE.audit(self.data)

    def test_unequal_budget_disclosed(self):
        self.data['configs'][1]['trials_per_case'] = 2
        result = MODULE.audit(self.data)
        self.assertTrue(any('unequal trial budgets' in f for f in result['findings']))
        self.assertIsNone(result['summaries']['candidate']['success_rate_e2e'])

    def test_empty_run_log_remains_incomplete(self):
        self.data['records'] = []
        base = self.summary()
        self.assertEqual(base['missing_runs'], 2)
        self.assertIsNone(base['success_rate_e2e'])
        self.assertIsNone(base['total_cost'])

    def test_missing_evidence_refs_disclosed(self):
        self.data['records'][0]['grade_ref'] = None
        self.assertTrue(any('grade_ref' in f for f in MODULE.audit(self.data)['findings']))

    def test_cli_exit_codes_and_json_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'input.json', Path(directory) / 'audit.json'
            for expected, data in ((0, fixture()), (1, {**fixture(), 'records': []}), (2, {})):
                source.write_text(json.dumps(data), encoding='utf-8')
                result = subprocess.run([sys.executable, str(SCRIPT), str(source), '--out', str(output)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertIn('audit_status', json.loads(output.read_text(encoding='utf-8')))


if __name__ == '__main__':
    unittest.main()
