"""Exact-source Fu Ying publication under existing reservations and transaction guard."""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import fuying_five_member_qualified_stage_v1_20261029 as stage
from fuying_five_member_terrain_stage_v1_20261029 import publication_adapter
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=stage.PREFIX+'five-member-original-installed-v1-20261029'
BROWSER=BASE/stage.BROWSER;REVIEW=BASE/stage.REVIEW

def check(ref):assert stage.ref(ROOT/ref['path'])==ref,ref['path']
def evidence():
    from china_ferry_current_foundations_v1_20261020 import authenticate
    cache={}
    def take(batch,path):
        if batch not in cache:cache[batch]=authenticate(BASE/batch)[1]
        assert stage.ref(path)['sha256']==cache[batch][str(path.relative_to(ROOT))];return stage.read(path)
    q=take(stage.DOC.name,stage.DOC/'qualification.json')
    assert q['privateStageQualified']and q['originalSourceReviewAccepted']and q['visualAcceptance']and q['physicalAcceptance']
    assert q['sourceSHA256ByUid']==stage.SOURCES
    assert q['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
    review=take(stage.REVIEW,REVIEW/'ROOT-SOURCE-PHYSICAL-VISUAL-REVIEW.json');assert all(review[k]for k in ['identityAccepted','physicalAcceptance','visualAcceptance','completeNeighbourInterpretationAccepted'])
    assert review['sourceSHA256ByUid']==stage.SOURCES and review['sourceGeometryChanges']==review['sourcePoseChanges']==0
    approved=take(stage.DOC.name,stage.STAGE/'catalogue.json');original=take(stage.BROWSER,stage.PREVIOUS/'catalogue.json');stripped=copy.deepcopy(approved)
    assert len(approved['models'])==len(original['models'])==1
    for model,old in zip(stripped['models'],original['models']):
        for key in stage.PUBLIC_FIELDS:
            if key in old:model[key]=old[key]
            else:model.pop(key,None)
    assert stripped==original,'Rendering metadata changed after actual private preview'
    for m in approved['models']:
        assert m['uid']in stage.SOURCES and m['sha256']==stage.SOURCES[m['uid']]
        assert all(m[k]is True for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        check(dict(path=str((stage.STAGE/m['asset']).relative_to(ROOT)),sha256=m['sha256']))
        assert not any(m.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids'])
    assert len(q['imagesActuallyViewed'])==40 and len(q['browserReports'])==2
    for image in q['imagesActuallyViewed']:check(image)
    for report in q['browserReports']:
        check(report);r=take(stage.BROWSER,ROOT/report['path']);assert r['passed']and not r['errors']
        views=[v for v in r['views']if 'time'in v];assert len(views)==2 and len(r['retainedNativeOwnViews'])==18
        for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['sourceSHA256']==stage.SOURCES[v['uid']]and v['pick']==v['collision']==v['uid']
    plan=take(stage.DOC.name,stage.STAGE/'plan.json');assert len(plan['areas'])==1 and len(plan['topLevelTerrainPatches'])==5
    assert plan['fuYingWholeNativeTerrainReplacement']['proof']==review['wholeParentContract']
    for entry in plan['topLevelTerrainPatches']:check(dict(path=entry['source'],sha256=entry['sha256']))
    assert not any(a.get('estimates')for a in plan['areas'])
    return set(q['leaseResources'])
def assert_publication_idle():assert stage.read(stage.DOC/'qualification.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
def main():
    p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('--receipt',required=True);p.add_argument('--phase',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json'
    keys=evidence();lease=json.loads(Path(a.receipt).read_text())
    @contextmanager
    def guard():
        with connect()as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
    with guard():pass
    pub=stage.module('fuying_five_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
    with publication_adapter(pub):
        sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
