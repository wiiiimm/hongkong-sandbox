"""Read-only actual publisher terrain staging with exact nested-parent proofs."""
from pathlib import Path
import copy
import traceback
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from three_member_native_boundary_v1_20261027 import private_validator as three_validator
from nested_retained_parent_publisher_validation_v1_20261029 import private_validator

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-academy69025-canonical-terrain-staging-probe-v1-20261029'
BROWSER='government-xl-academy69025-nested-private-preview-v2-20261029'


def main():
    out=BASE/BATCH
    assert not out.exists()
    receipt,pins=authenticate(BASE/BROWSER)
    cfgpath=HERE/'local'/BROWSER/'browser-config-390.json'
    assert digest(cfgpath.read_bytes())==pins[str(cfgpath.relative_to(ROOT))]
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes())==pins[str(manifestpath.relative_to(ROOT))]
    original=read(manifestpath); successor=copy.deepcopy(original)
    terrain=copy.deepcopy(read(cfgpath)['terrain'])
    assert len(terrain)==1
    entry=terrain[0]
    candidate=ROOT/entry['source']
    assert digest(candidate.read_bytes())==entry['sha256']==pins[str(candidate.relative_to(ROOT))]
    before=manifestpath.read_bytes()
    edits,report={},{}
    pub=module('academy_canonical_terrain_probe',HERE.parent/'island-detail-integration/publish.py')
    out.mkdir()
    result=dict(uids=['landsd/69025:0'],publication=False,installationApproved=False,
                physicalAcceptance=False,sourceGeometryChanges=0,publicFilesWritten=0)
    try:
        with three_validator(),private_validator(pub):
            pub.stage_top_level_terrain(dict(topLevelTerrainPatches=terrain),original,successor,edits,report)
        assert len(edits)==1 and len(successor['terrainPatches'])==len(original['terrainPatches'])
        assert entry['replaces']['url']not in {r['url']for r in successor['terrainPatches']}
        assert manifestpath.read_bytes()==before
        result.update(passed=True,stagedAssetCount=len(edits),terrainManifestCountPreserved=True)
        save(out/'publication-terrain-report.json',report)
    except Exception as error:
        result.update(passed=False,reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(message=str(error),traceback=traceback.format_exc()))
    assert manifestpath.read_bytes()==before
    save(out/'summary.json',result)
    refs=[Path(__file__),BASE/BROWSER/'result.json',cfgpath,manifestpath,candidate,
          HERE/'nested_retained_parent_publisher_validation_v1_20261029.py',
          HERE/'test_nested_retained_parent_publisher_validation_v1_20261029.py',
          HERE/'disjoint_nested_append_contract_v1_20261029.py',
          HERE/'nested_terrain_patch_validation_v1_20261027.py',
          HERE/'nested_native_terrain_validation_v1_20261027.py',
          HERE/'nested_coordinated_native_boundary_v1_20261027.py',
          HERE/'nested_coordinated_parent_contract_v1_20261027.py',
          HERE.parent/'island-detail-integration/publish.py']
    for name in ['native_terrain_validation.py','coordinated_native_boundary.py']:
        refs.append(HERE.parent/'island-detail-integration'/name)
    for path,pin in pub.PINNED_INPUTS.items():
        p=Path(path)
        assert digest(p.read_bytes())==pin
        refs.append(p)
    module('academy_canonical_probe_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'read-only-canonical-publisher-exact-nested-parent-replacement',list(dict.fromkeys(refs)),result)
    print({k:result[k]for k in result if k not in ['uids']},flush=True)


if __name__=='__main__':main()
