"""Guarded publication of exact reviewed Tower 1/podium and source terrain."""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import yoho_seven_private_stage_v1_20261020 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH='government-xl-yoho-seven-original-installed-v1-20261020'
BROWSER=stage.BROWSER;REVIEW=BROWSER
stage.SOURCES=stage.read(stage.DOC/'qualification.json')['sourceSHA256ByUid']
def check(q):assert stage.ref(ROOT/q['path'])==q,q['path']
def evidence():
    pins={}
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [stage.DOC,BROWSER]:
            r=stage.read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            for q in r['evidenceRefs']:
                assert q['path']not in pins or pins[q['path']]==q; pins[q['path']]=q
    for q in pins.values():check(q)
    qualification=stage.read(stage.DOC/'qualification.json');assert qualification['privateStageQualified']
    assert qualification['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
    review=stage.read(BROWSER/'ROOT-IMAGE-REVIEW.json');report=dict(views=[],jointViews=[],errors=[],passed=True)
    for q in review['browserReports']:
        check(q);r=stage.read(ROOT/q['path']);assert r['passed']and not r['errors'];report['views'].extend(r['views']);report['jointViews'].extend(r['jointViews'])
    assert review['reviewer']=='Codex ROOT'and review['visualAcceptance']and len(review['imagesActuallyViewed'])==42
    assert review['currentManifest']==qualification['currentManifest']
    for q in review['imagesActuallyViewed']:check(q)
    views=[v for v in report['views']if 'time'in v]
    assert report['passed']and not report['errors']and len(views)==42 and len(report['jointViews'])==15
    for joint in report['jointViews']:
        expected=set(stage.SOURCES) if len(joint['models'])==7 else {joint['selectedUid'],'landsd/301636:0'}
        assert {m['uid']:m['sourceSHA256']for m in joint['models']}=={u:stage.SOURCES[u]for u in expected}
        assert all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
    for v in views:assert v['fullyFramed']and v['solidAppearance']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]
    assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(stage.SOURCES)
    plan=stage.read(stage.STAGE/'plan.json');assert set(plan)=={'areas','topLevelTerrainPatches'}and len(plan['areas'])==1 and len(plan['topLevelTerrainPatches'])==1
    approved=stage.read(stage.STAGE/'catalogue.json');original=stage.read(stage.PREVIOUS/'catalogue.json')
    assert {m['uid']:m['sha256']for m in approved['models']}==stage.SOURCES
    fields=['originalSourceKey','sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','sourceFunctionalApplicability','placementReview']
    stripped=copy.deepcopy(approved)
    for a,o in zip(stripped['models'],original['models']):
        for key in fields:
            if key in o:a[key]=o[key]
            else:a.pop(key,None)
    assert stripped==original,'Stage differs from browser-tested rendering metadata'
    oldTerrain=stage.read(stage.PREVIOUS/'browser-config.json')['terrain'];newTerrain=plan['topLevelTerrainPatches'];assert len(oldTerrain)==len(newTerrain)==1
    assert {k:v for k,v in oldTerrain[0].items() if k!='source'}=={k:v for k,v in newTerrain[0].items() if k!='source'}
    for e in oldTerrain+newTerrain:check(dict(path=e['source'],sha256=e['sha256']))

    return set(qualification['leaseResources'])
def assert_publication_idle():
    # The cross-process publication lock and exact current-map hash guard the map.
    assert stage.read(stage.DOC/'qualification.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json'
    keys=evidence();lease=json.loads(Path(a.receipt).read_text())
    @contextmanager
    def guard():
        with connect()as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease)
            assert live and keys<=set(live['resources']);assert_publication_idle();yield
    with guard():pass
    pub=stage.module('pacifica_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
    sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
