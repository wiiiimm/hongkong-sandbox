"""Fenced canonical publication of the exact qualified original assembly."""
import argparse
import copy
import sys
from contextlib import contextmanager
from pathlib import Path
from run import ROOT,HERE,read,digest,connect,reservations,dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_two_descriptor_terrain_dry_run_v2_20261103 import registered_two_descriptor_validators
from silvercord_lippo_two_descriptor_qualified_stage_v1_20261103 import BATCH as STAGE_BATCH,STAGE,BASE,SOURCE,PHYSICAL,BROWSER,ref
from original_supported_model_only_contract_v1_20261025 import REVIEW_FIELDS

BATCH='government-xl-silvercord-lippo-original-installed-v1-20261103'
DOC=BASE/STAGE_BATCH
PREVIOUS=HERE/'local'/BROWSER


def check(q):
    assert ref(ROOT/q['path']) == {k:q[k] for k in ['path','sha256']},q['path']


def evidence():
    pins={}
    batches=[STAGE_BATCH,SOURCE,PHYSICAL,BROWSER,'government-xl-silvercord-lippo-original-atomic-lifecycle-v2-20261103']
    for batch in batches:
        receipt,bound=authenticate(BASE/batch)
        for path,sha in bound.items():
            assert pins.setdefault(path,sha)==sha,'Conflicting current publication inputs'
        pins[str((BASE/batch/'result.json').relative_to(ROOT))]=digest((BASE/batch/'result.json').read_bytes())
    for path,sha in pins.items():check(dict(path=path,sha256=sha))
    q=read(DOC/'qualification.json');source=read(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json')
    assert q['privateStageQualified'] and q['originalSourceReviewAccepted'] and q['visualAcceptance']
    assert q['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')==source['currentManifest']
    assert q['sourceSHA256ByUid']==source['sourceSHA256ByUid'] and len(q['sourceSHA256ByUid'])==5
    assert source['identityAccepted'] and source['sourceSpecificPhysicalInterpretationAccepted'] and source['completeNeighbourInterpretationAccepted']
    assert source['fullTerrainForms']==5408 and source['fullTerrainNativeActors']==1228
    assert source['unchangedNativeTerrainEvidenceCount']==1227 and len(source['browserObservedRetainedUids'])==4
    assert len(source['imagesActuallyViewed'])==20 and len(source['retainedImagesActuallyViewed'])==16 and len(source['atomicImagesActuallyViewed'])==17
    cat=read(STAGE/'catalogue.json');before=read(PREVIOUS/'catalogue.json');stripped=copy.deepcopy(cat)
    assert {m['uid']:m['sha256'] for m in cat['models']}==q['sourceSHA256ByUid']
    assert len(cat['models'])==len(before['models'])==5
    for model,old in zip(stripped['models'],before['models']):
        for field in REVIEW_FIELDS:
            if field in old:model[field]=old[field]
            else:model.pop(field,None)
    assert stripped==before,'Published rendering metadata must equal the exact tested catalogue'
    plan=read(STAGE/'plan.json');cfg=read(PREVIOUS/'browser-config-390.json')
    assert len(plan['areas'])==1 and len(plan['topLevelTerrainPatches'])==len(cfg['terrain'])==2
    assert sum('replaces' in t for t in plan['topLevelTerrainPatches'])==1
    for new,old in zip(plan['topLevelTerrainPatches'],cfg['terrain']):
        assert new['sha256']==old['sha256'] and new['resolution']==old['resolution']
        assert new.get('replaces')==old.get('replaces')
        check(dict(path=new['source'],sha256=new['sha256']));check(dict(path=old['source'],sha256=old['sha256']))
    assert len(plan['dependencyReviews'])==1 and plan['dependencyReviews'][0]['visualApproval']==ref(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json')
    update=source['installedSupportUpdate'];path=ROOT/'3d-viewer'/update['url'];check(dict(path=str(path.relative_to(ROOT)),sha256=update['beforeSHA256']))
    from silvercord_lippo_private_six_part_browser_v4_20261103 import exact_owner_after
    assert exact_owner_after(read(path),read(ROOT/update['source']),update)
    assert not any(a.get('estimates') for a in plan['areas'])
    assert not (STAGE/'estimated-bases.json').exists()
    return set(q['leaseResources']),q,source,pins


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);parser.add_argument('--apply',action='store_true')
    args=parser.parse_args();keys,q,source,pins=evidence();lease=read(Path(args.receipt))
    @contextmanager
    def guard():
        with connect() as db:
            db.row_factory=dict_row
            db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            live=reservations._current(db,lease)
            assert live and keys<=set(live['resources'])
            assert ref(ROOT/'3d-viewer/city/data/manifest.json')==q['currentManifest']
            yield
    with guard():pass
    pub=module('silvercord_exact_two_descriptor_fenced_publisher',HERE.parent/'island-detail-integration/publish.py')
    for path,sha in pins.items():
        assert pub.PINNED_INPUTS.setdefault((ROOT/path).resolve(),sha)==sha
    pub.PUBLICATION_GUARD=guard
    pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/BATCH
    argv=sys.argv[:]
    try:
        sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))]+(['--apply'] if args.apply else [])
        with registered_two_descriptor_validators(pub):pub.main()
    finally:sys.argv=argv


if __name__=='__main__':main()
