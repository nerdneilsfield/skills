import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'coding/python/assets/record-contract/records.py'

class PythonContractExample(unittest.TestCase):
    def load(self):
        self.assertTrue(SOURCE.is_file(), 'record contract example missing')
        spec=importlib.util.spec_from_file_location('record_contract_example',SOURCE)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

    def test_owned_validated_units_and_source_mutation(self):
        m=self.load();source=[{'id':'p1','xyz':[1000,2000,3000]}]
        prepared=m.prepare_records(source,'mm');source[0]['xyz'][0]=9
        self.assertEqual(prepared,(('p1',(1.0,2.0,3.0)),))

    def test_invalid_tail_does_not_publish_partial_batch(self):
        m=self.load();published=m.prepare_records([{'id':'p1','xyz':[1,2,3]}],'m')
        with self.assertRaises(ValueError):
            candidate=m.prepare_records([{'id':'new','xyz':[1,2,3]},{'id':'bad','xyz':[1,float('nan'),3]}],'m')
            published=candidate
        self.assertEqual(published[0][0],'p1')

    def test_boundary_errors_and_empty(self):
        m=self.load();self.assertEqual(m.prepare_records([],'m'),())
        for rows,unit in [([{'id':'x','xyz':[True,2,3]}],'m'),([{'id':'x','xyz':[1,2]}],'m'),([{'id':'x','xyz':[1,2,3]}]*2,'m'),([{'id':'x','xyz':[1,2,3]}],'unknown'),([{'id':'x','xyz':[10**400,2,3]}],'m')]:
            with self.subTest(rows=rows,unit=unit),self.assertRaises(ValueError):m.prepare_records(rows,unit)

if __name__=='__main__':unittest.main()
