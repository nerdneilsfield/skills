"""Contracts, not word matching; only installed optional frameworks run."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'coding/python-data-analysis'

def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.mod = load('csv_audit', 'scripts/csv_contract_audit.py')
    def audit(self, text, **kwargs):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'input.csv'; p.write_text(text, encoding='utf-8')
            return self.mod.audit(p, **kwargs)
    def test_counts_no_value_disclosure(self):
        r=self.audit('id,value\nsecret,3\nsecret,NaN\n,\n', key=['id'], numeric=['value'])
        self.assertEqual(r['rows'], 3)
        self.assertEqual(r['duplicate_key_rows'], 1)
        self.assertEqual(r['missing_key_rows'], 1)
        self.assertEqual(r['numeric']['value']['nonfinite'], 1)
        self.assertNotIn('secret',json.dumps(r))
    def test_limits_fail_closed(self):
        for kw in [{'max_rows':1}, {'max_bytes':10}, {'max_columns':1}]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.audit('id,value\na,1\nb,2\n', **kw)
    def test_bad_schema_and_rows(self):
        for text in ['id,id\na,b\n','id,value\na,1,2\n','id,value\na\n','']:
            with self.subTest(text=text), self.assertRaises(ValueError): self.audit(text)
    def test_required_column(self):
        with self.assertRaises(ValueError): self.audit('id\na\n', key=['absent'])
    def test_non_numeric_and_empty(self):
        r=self.audit('x\nabc\n""\n', numeric=['x'])
        self.assertEqual(r['numeric']['x'], {'missing':1,'invalid':1,'nonfinite':0})
    def test_duplicate_and_oversized_selectors(self):
        for kwargs in [{'key':['id','id']}, {'numeric':['id','id']},
                       {'key':['id']*257}, {'key':['x'*257]}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.audit('id\na\n',**kwargs)
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'source'; src.write_text('id\na\n')
            link=Path(d)/'link';link.symlink_to(src)
            with self.assertRaises(ValueError): self.mod.audit(link)
    @unittest.skipUnless(hasattr(__import__('os'), 'mkfifo'), 'FIFO unavailable')
    def test_fifo_rejected_without_blocking(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fifo';os.mkfifo(p)
            r=subprocess.run([sys.executable,str(ROOT/'scripts/csv_contract_audit.py'),str(p)],
                             capture_output=True,text=True,timeout=3)
            self.assertEqual(r.returncode,2)
    def test_cli_invalid_no_raw_values(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'s.csv';p.write_text('id,id\nprivate,private\n')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/csv_contract_audit.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2)
            self.assertNotIn('private',r.stdout+r.stderr)

@unittest.skipUnless(importlib.util.find_spec('pandas'), 'pandas absent; no installation')
class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.mod=load('analysis_example','assets/analysis_example.py')
    def test_rates_and_accounting(self):
        events, groups=self.mod.fixture()
        summary, audit=self.mod.analyze(events,groups)
        a=summary.set_index('group').loc['A']
        self.assertEqual(int(a['eligible']),3)
        self.assertEqual(int(a['known']),2)
        self.assertAlmostEqual(float(a['known_success_rate']),.5)
        self.assertEqual(audit['unknown_outcomes'],1)
        self.assertEqual(audit['unmatched_rows'],0)
    def test_duplicate_dimensions_fail(self):
        import pandas as pd
        events, groups=self.mod.fixture()
        with self.assertRaises(ValueError): self.mod.analyze(events,pd.concat([groups,groups.iloc[:1]]))
    def test_null_keys_fail(self):
        events,groups=self.mod.fixture();events.loc[0,'subject_id']=None
        with self.assertRaises(ValueError): self.mod.analyze(events,groups)
    def test_unmatched_dimension_fail(self):
        events,groups=self.mod.fixture();groups=groups.iloc[:1]
        with self.assertRaises(ValueError): self.mod.analyze(events,groups)
    def test_duplicate_event_and_invalid_outcome_fail(self):
        events,groups=self.mod.fixture();events.loc[1,'event_id']=events.loc[0,'event_id']
        with self.assertRaises(ValueError): self.mod.analyze(events,groups)
        events,groups=self.mod.fixture();events.loc[0,'success']=4
        with self.assertRaises(ValueError): self.mod.analyze(events,groups)
    def test_all_unknown_and_empty(self):
        import pandas as pd
        events,groups=self.mod.fixture();events['success']=pd.array([None]*len(events),dtype='Int64')
        summary,_=self.mod.analyze(events,groups)
        self.assertTrue(summary['known_success_rate'].isna().all())
        self.assertEqual(int(summary['known'].sum()),0)
        summary,audit=self.mod.analyze(events.iloc[:0],groups)
        self.assertTrue(summary.empty)
        self.assertEqual(audit['input_rows'],0)
    @unittest.skipUnless(importlib.util.find_spec('matplotlib'), 'matplotlib absent; no renderer test')
    def test_real_headless_render(self):
        summary,_=self.mod.analyze(*self.mod.fixture())
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'summary.png';self.mod.render(summary,out)
            self.assertEqual(out.read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
            with self.assertRaises(FileExistsError): self.mod.render(summary,out)

if __name__=='__main__': unittest.main()
