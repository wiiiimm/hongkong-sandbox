"""Explicit process-local HKDI route with authenticated component evidence.

Other sources continue to use the unchanged generic installed-parent contract.
This adapter never changes installed parent flags, source geometry or thresholds.
"""
from pathlib import Path
import hkdi88343_installed_parent_contract_v1_20261101 as contract
from china_ferry_current_foundations_v1_20261020 import authenticate
from run import ROOT, HERE, read, digest
BASE = ROOT / 'docs/astra-city/government-import'
PARENT_REVIEW = BASE / 'government-xl-hkdi22089-component-identity-review-v1-20261101'
REVIEW_FILE = PARENT_REVIEW / 'ROOT-COMPONENT-IDENTITY-REVIEW.json'

def review_and_refs():
    receipt, pins = authenticate(PARENT_REVIEW)
    assert digest(REVIEW_FILE.read_bytes()) == pins[str(REVIEW_FILE.relative_to(ROOT))]
    for name, sha in pins.items():
        assert digest((ROOT / name).read_bytes()) == sha, name
    return read(REVIEW_FILE), [Path(__file__), HERE / 'hkdi88343_installed_parent_contract_v1_20261101.py', PARENT_REVIEW / 'result.json', *[ROOT / p for p in pins]]

def configure():
    import installed_support_model_only_qualified_stage_v1_20261027 as stage
    assert stage.CONFIG['prefix'] == 'government-xl-hkdi88343-reviewed-current-original'
    assert stage.SOURCES == {contract.UID: contract.SHA} and stage.SUPPORTS == {contract.UID: contract.PARENT}
    assert stage.CONFIG['parentComponentIdentityReview'] == str(REVIEW_FILE.relative_to(ROOT))
    review, refs = review_and_refs()
    assert review['currentManifestSHA256'] == digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes())
    physical = read(BASE / stage.CONFIG['physical'] / 'ROOT-PHYSICAL-REVIEW.json')
    assert physical['parentComponentIdentityReview'] == stage.ref(REVIEW_FILE)
    def verify(models, sources, supports, original, current):
        fresh, _ = review_and_refs()
        assert fresh == review
        return contract.verify_metadata(models, sources, supports, original, current, fresh)
    stage.metadata_contract = verify
    # The contacts receipt covers a larger source cohort. Preserve every row for
    # this exact source, including any unexpected neighbour, for generic checks.
    def native(scope, contacts, current):
        assert len(scope['uids']) == len(set(scope['uids'])) and contract.UID in scope['uids']
        selected = {**scope, 'uids': [contract.UID], 'rows': [r for r in scope['rows'] if r['uid'] == contract.UID]}
        native_rows = {**contacts, 'rows': [r for r in contacts['rows'] if r['uid'] == contract.UID]}
        return stage.native_contract(selected, native_rows, current, stage.SOURCES, stage.SUPPORTS,
            set(stage.CONFIG['retainedNativeUids']), stage.CONFIG['currentNativeActors'], physical)
    stage.verify_native_scope = native
    original_module = stage.module
    def module(name, path):
        loaded = original_module(name, path)
        if Path(path).name == 'xl-popcorn-source-investigations-checkpoints-20261009.py':
            freeze = loaded.freeze
            def bound_freeze(batch, recipe, paths, result):
                _, current_refs = review_and_refs()
                return freeze(batch, recipe, list(dict.fromkeys([*paths, *current_refs,
                    HERE / 'hkdi88343_qualified_stage_v1_20261101.py'])),
                    {**result, 'exactParentComponentIdentityRoute': stage.ref(Path(__file__))})
            loaded.freeze = bound_freeze
        return loaded
    stage.module = module
    return stage
