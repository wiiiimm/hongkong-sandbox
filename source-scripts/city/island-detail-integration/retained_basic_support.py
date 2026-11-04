"""Keep an accepted original's exact basic support until a fresh review replaces it.

This guard grants no placement approval. It validates the effective post-plan
catalogues and forms, including already installed dependants, before publication.
"""
import hashlib
import json


def encoded(value):
    # Same canonical encoding as shared-modelling.jobs.encode.
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def validate_retained_basic_support(models, forms):
    by_uid = {model['uid']: model for model in models}
    assert len(by_uid) == len(models), 'Duplicate model UID in support scope'
    suppressed = {uid for model in models for uid in model.get('suppressesBuildingUids', [])}
    checked = []
    for model in models:
        for dependency in model.get('retainedBasicSupportDependencies', []):
            uid = dependency['supportUid']
            assert dependency['uid'] == model['uid'], 'Retained basic dependant changed'
            assert dependency['sourceSHA256'] == model['sha256'], 'Retained basic source changed'
            assert dependency['dependencyMode'] == 'retained-current-basic-podium'
            assert dependency['mustRemainBasicAndUnsuppressed'] is True
            assert dependency['futureReplacementRequiresDependentRevalidation'] is True
            assert uid != model['uid'] and uid not in by_uid, 'Retained basic support was enhanced: ' + uid
            assert uid not in suppressed, 'Retained basic support was suppressed: ' + uid
            assert uid in forms, 'Retained basic support is absent: ' + uid
            form = forms[uid]
            assert not form.get('modelGeometry'), 'Retained basic support has embedded geometry: ' + uid
            # JSON.stringify normalises 13.0 to 13. Verify the bound snapshot's
            # bytes and compare every current field numerically, without rounding.
            assert form == dependency['currentBasicForm'], 'Retained basic support form changed: ' + uid
            assert form['buildingCSUID'] == dependency['supportCSUID'], 'Retained basic support identity changed'
            assert hashlib.sha256(encoded(dependency['currentBasicForm']).encode()).hexdigest() == dependency['currentBasicFormSHA256'], 'Retained basic form digest changed'
            for key in ['currentBasicFormSHA256', 'completeIndexedBasicGeometrySHA256']:
                value = dependency[key]
                assert isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'Invalid retained support digest'
            checked.append({'uid': model['uid'], 'supportUid': uid, 'sourceSHA256': model['sha256'],
                            'completeIndexedBasicGeometrySHA256': dependency['completeIndexedBasicGeometrySHA256']})
    return checked


def stage_retained_basic_support(root, manifest, edits, report, load):
    def effective(path):
        return json.loads(edits[path]) if path in edits else load(path)
    models = [model for url in manifest.get('officialModelCatalogues', [])
              for model in effective(root / '3d-viewer' / url)['models']]
    wanted = {d['supportUid'] for m in models for d in m.get('retainedBasicSupportDependencies', [])}
    if not wanted:
        return
    forms = {}
    for tile in manifest['tiles']:
        for form in effective(root / '3d-viewer' / tile['url'])['buildings']:
            if form['uid'] in wanted:
                assert form['uid'] not in forms, 'Duplicate retained support form'
                forms[form['uid']] = form
    report['retainedBasicSupportChecks'] = validate_retained_basic_support(models, forms)
