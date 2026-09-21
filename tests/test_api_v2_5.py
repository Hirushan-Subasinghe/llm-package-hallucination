import csv
import hashlib
import json
import os
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect_api_batch
import collect_api_run
import create_api_manifest
import create_experiment_freeze_v2_5
import render_api_prompts

CONFIG = ROOT / 'config/api_model_set_1.3.0.json'
MANIFEST = ROOT / 'manifests/api_final_v2.5.0_manifest.csv'
STATE = ROOT / 'data/final/api_batch_state_v2.5.0.json'


class V25Tests(unittest.TestCase):
    def test_config_only_changes_ceiling_and_version_metadata(self):
        old = json.loads((ROOT / 'config/api_model_set_1.2.0.json').read_text())
        new = collect_api_run.load_config(CONFIG)
        self.assertEqual(new['model_set_version'], 'api-model-set-1.3.0')
        self.assertEqual(new['candidate_common_parameters']['max_output_tokens'], 16000)
        self.assertEqual(old['candidate_common_parameters']['max_output_tokens'], 12000)
        normalized = json.loads(json.dumps(new))
        normalized['model_set_version'] = old['model_set_version']
        normalized['frozen_at_utc'] = old['frozen_at_utc']
        normalized['candidate_common_parameters']['max_output_tokens'] = 12000
        self.assertEqual(normalized, old)
        self.assertEqual(new['batch_pacing']['minimum_seconds_between_openrouter_requests'], 0)
        self.assertEqual(new['batch_pacing']['minimum_seconds_between_groq_requests'], 0)
        for model in new['models']:
            with patch.dict(os.environ, {model['api_key_environment_variable']: 'test-only'}):
                _, _, body = collect_api_run.build_request(new, model, b'prompt')
            request = json.loads(body)
            self.assertEqual(request[model['output_token_parameter']], 16000)
            self.assertEqual(request['messages'], [{'role': 'user', 'content': 'prompt'}])
            self.assertEqual(request['tool_choice'], 'none')
            self.assertNotIn('tools', request)
            self.assertNotIn('seed', request)
            if model['api_provider'] == 'OpenRouter':
                self.assertEqual(request['provider']['order'], [model['openrouter_routing']['underlying_provider_slug']])
                self.assertFalse(request['provider']['allow_fallbacks'])

    def test_prompt_bytes_and_manifest(self):
        template = ROOT / 'prompts/prompt_template_v2.5.0.md'
        previous = ROOT / 'prompts/prompt_template_v2.4.0.md'
        self.assertEqual(template.read_bytes(), previous.read_bytes())
        self.assertEqual(hashlib.sha256(template.read_bytes()).hexdigest(), '8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528')
        expected = render_api_prompts.expected_rendered(template)
        self.assertEqual(len(expected), 30)
        for task_id, value in expected.items():
            self.assertEqual((ROOT / f'data/generated_prompts/v2.5.0/{task_id}.txt').read_bytes(), value)
            self.assertEqual((ROOT / f'data/generated_prompts/v2.4.0/{task_id}.txt').read_bytes(), value)
        rows = collect_api_batch.ordered_rows(MANIFEST)
        self.assertEqual(len(rows), 360)
        self.assertEqual(Counter(r['model_condition_id'] for r in rows), {m: 90 for m in ('M1','M2','M3','M4')})
        self.assertEqual(Counter(r['run_repetition'] for r in rows), {r: 120 for r in ('R01','R02','R03')})
        self.assertEqual(Counter(r['category'] for r in rows), {c: 60 for c in ('AUTH-FED','DATA-ADV','DIST-OBS','DOC-BINARY','ENT-INT','PKI-CRYPTO')})
        self.assertTrue(all(r['collection_status'] == 'pending' and r['run_id'].startswith('API-v2.5-') for r in rows))
        state = json.loads(STATE.read_text())
        self.assertEqual(state['events'], [])
        self.assertEqual(state['provider_next_allowed_at_epoch'], {})
        self.assertEqual(state['manifest_sha256'], hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
        self.assertEqual(list((ROOT / 'data/final/raw').glob('API-v2.5-*')), [])
        generated = create_api_manifest.make_rows(collect_api_run.load_config(CONFIG), create_api_manifest.load_frozen_tasks(), ROOT / 'data/generated_prompts/v2.5.0', 'API-v2.5')
        self.assertEqual(MANIFEST.read_bytes(), create_api_manifest.csv_bytes(generated))

    def test_dry_run_and_preserved_statuses(self):
        config = collect_api_run.load_config(CONFIG)
        rows = collect_api_batch.ordered_rows(MANIFEST)
        result = collect_api_batch.run_batch(config, rows, manifest_hash=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), state_path=STATE, dry_run=True, continue_after_failed=True)
        self.assertEqual(result, {'next_run_id': 'API-v2.5-AUTH-FED-01-M1-R01', 'collection_order': 1, 'api_provider': 'OpenRouter', 'wait_seconds': 0.0})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for row, status in zip(rows, ('completed', 'truncated', 'failed')):
                d = root / row['run_id']
                d.mkdir()
                (d / 'metadata.json').write_text(json.dumps({'collection_status': status}))
            result = collect_api_batch.run_batch(config, rows[:4], manifest_hash='test', state_path=root / 'state.json', raw_root=root, dry_run=True, continue_after_failed=True)
            self.assertEqual(result['collection_order'], 4)
            self.assertFalse((root / 'state.json').exists())
            blocked = collect_api_batch.run_batch(config, rows[:4], manifest_hash='test', state_path=root / 'state.json', raw_root=root, dry_run=True, continue_after_failed=False)
            self.assertEqual(blocked['existing_status'], 'failed')

    def test_freeze_record_is_reproducible(self):
        record = json.loads((ROOT / 'config/experiment_freeze_v2.5.0.json').read_text())
        self.assertEqual(record['sampling_parameters']['max_output_tokens'], 16000)
        self.assertEqual(record['failure_policy']['continue_after_preserved_failure'], True)
        expected = create_experiment_freeze_v2_5.build_record()
        expected['freeze_record_created_at_utc'] = record['freeze_record_created_at_utc']
        self.assertEqual(record, expected)
        self.assertEqual((ROOT / 'docs/experiment_freeze_v2.5.0.md').read_text(), create_experiment_freeze_v2_5.markdown(record))

if __name__ == '__main__':
    unittest.main()
