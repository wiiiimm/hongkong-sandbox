import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from retained_basic_support import encoded, validate_retained_basic_support, stage_retained_basic_support


class RetainedBasicSupportTests(unittest.TestCase):
    def setUp(self):
        self.form = {'uid': 'podium', 'buildingCSUID': 'P1', 'base': 4.3, 'height': 13, 'rings': [[[0, 0], [1, 0], [0, 1]]]}
        self.dependency = dict(uid='tower', sourceSHA256='a' * 64, supportUid='podium', supportCSUID='P1',
                               dependencyMode='retained-current-basic-podium', currentBasicForm=self.form,
                               currentBasicFormSHA256=hashlib.sha256(encoded(self.form).encode()).hexdigest(),
                               completeIndexedBasicGeometrySHA256='b' * 64,
                               mustRemainBasicAndUnsuppressed=True, futureReplacementRequiresDependentRevalidation=True)
        self.model = dict(uid='tower', sha256='a' * 64, retainedBasicSupportDependencies=[self.dependency])

    def verify(self, models=None, forms=None):
        return validate_retained_basic_support(models or [self.model], {'podium': self.form} if forms is None else forms)

    def test_exact_retained_support_passes(self):
        self.assertEqual(self.verify()[0]['supportUid'], 'podium')

    def test_json_integer_float_representation_keeps_exact_values(self):
        form = copy.deepcopy(self.form)
        form['height'] = 13.0
        self.assertEqual(len(self.verify(forms={'podium': form})), 1)

    def test_future_native_import_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'enhanced'):
            self.verify([self.model, dict(uid='podium')])

    def test_other_model_cannot_suppress_support(self):
        with self.assertRaisesRegex(AssertionError, 'suppressed'):
            self.verify([self.model, dict(uid='other', suppressesBuildingUids=['podium'])])

    def test_support_edit_or_missing_form_rejected(self):
        for forms in [{}, {'podium': {**self.form, 'height': 14}}, {'podium': {**self.form, 'modelGeometry': {'mesh': True}}}]:
            with self.subTest(forms=forms), self.assertRaises(AssertionError):
                self.verify(forms=forms)

    def test_changed_source_cannot_inherit_dependency(self):
        with self.assertRaisesRegex(AssertionError, 'source changed'):
            self.verify([{**self.model, 'sha256': 'c' * 64}])

    def test_invalid_or_disabled_binding_rejected(self):
        for key, value in [('uid', 'other'), ('currentBasicFormSHA256', '0' * 64), ('completeIndexedBasicGeometrySHA256', ''), ('mustRemainBasicAndUnsuppressed', False), ('futureReplacementRequiresDependentRevalidation', False)]:
            model = copy.deepcopy(self.model)
            model['retainedBasicSupportDependencies'][0][key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                self.verify([model])

    def test_effective_plan_edits_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = dict(officialModelCatalogues=['cat.json'], tiles=[dict(url='tile.json')])
            cat = root / '3d-viewer/cat.json'
            tile = root / '3d-viewer/tile.json'
            cat.parent.mkdir()
            cat.write_text(json.dumps(dict(models=[self.model])))
            tile.write_text(json.dumps(dict(buildings=[self.form])))
            def load(path): return json.loads(path.read_bytes())
            report = {}
            stage_retained_basic_support(root, manifest, {}, report, load)
            self.assertEqual(len(report['retainedBasicSupportChecks']), 1)
            with self.assertRaisesRegex(AssertionError, 'form changed'):
                stage_retained_basic_support(root, manifest, {tile: json.dumps(dict(buildings=[{**self.form, 'base': 0}])).encode()}, {}, load)
            with self.assertRaisesRegex(AssertionError, 'enhanced'):
                stage_retained_basic_support(root, manifest, {cat: json.dumps(dict(models=[self.model, dict(uid='podium')])).encode()}, {}, load)


if __name__ == '__main__': unittest.main()
