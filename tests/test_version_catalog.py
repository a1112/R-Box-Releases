import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('version_catalog',ROOT/'version_catalog.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'release-history.json').read_text(encoding='utf-8'))
    def test_checked_in_history(self):
        result=module.validate(self.data)
        self.assertEqual(result,{'applications':17,'application_releases':18,'catalog_releases':1,'unresolved_sources':['r-labelimg']})
    def test_does_not_mutate(self):
        before=copy.deepcopy(self.data)
        module.validate(self.data)
        self.assertEqual(before,self.data)
    def test_duplicate_identity_rejected(self):
        self.data['applications'].append(copy.deepcopy(self.data['applications'][0]))
        with self.assertRaises(ValueError):module.validate(self.data)
    def test_duplicate_release_rejected(self):
        a=self.data['applications'][0];a['releases'].append(copy.deepcopy(a['releases'][0]))
        with self.assertRaises(ValueError):module.validate(self.data)
    def test_tag_mismatch_rejected(self):
        self.data['applications'][0]['releases'][0]['tag']='r-other-v0.1.0'
        with self.assertRaises(ValueError):module.validate(self.data)
    def test_source_required(self):
        self.data['applications'][0]['releases'][0]['source_commits']=['main']
        with self.assertRaises(ValueError):module.validate(self.data)
    def test_unresolved_mapping_not_invented(self):
        a=next(a for a in self.data['applications'] if a['identity']=='r-labelimg')
        a['source_repository']='a1112/labelImg';a['source_mapping']='verified'
        with self.assertRaises(ValueError):module.validate(self.data)
    def test_channel_and_asset_isolation(self):
        for field,value in [('prerelease',False),('artifact_names',['r-other-0.1.0.zip']),('version','01.0.0')]:
            with self.subTest(field=field):
                data=copy.deepcopy(self.data);data['applications'][0]['releases'][0][field]=value
                with self.assertRaises(ValueError):module.validate(data)
    def test_catalog_not_application(self):
        self.data['catalog_release']['versioned_application']=True
        with self.assertRaises(ValueError):module.validate(self.data)

if __name__=='__main__':unittest.main()
