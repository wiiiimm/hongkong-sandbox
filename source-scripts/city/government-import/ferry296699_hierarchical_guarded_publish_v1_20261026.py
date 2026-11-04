"""Fenced publication for the exact non-effect hierarchical original assembly."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import ferry296699_hierarchical_qualified_stage_v1_20261026 as stage
from run import connect,reservations,dict_row
from hierarchical_unaffected_diagnostic_contract_v2_20261026 import verify_context
from hierarchical_original_catalogue_review_v1_20261026 import verify_catalogue_review
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=stage.PREFIX+'ferry-hierarchical-original-installed-v1-20261026'
BROWSER=BASE/stage.BROWSER;REVIEW=stage.DOC

def check(q):assert stage.ref(ROOT/q['path'])==q,q['path']

def evidence():
    pins={};names=[stage.BATCH,stage.BROWSER,stage.ROLE,stage.PREFIX+'ferry-changed-actor-scope-v1-20261026',stage.PREFIX+'ferry-group-form-checks-v1-20261026',stage.PREFIX+'ferry-source-scope-v1-20261026']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for name in names:
            r=stage.read(BASE/name/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            check(stage.ref(BASE/name/'result.json'))
            for q in r['evidenceRefs']:
                assert q['path']not in pins or pins[q['path']]==q
                pins[q['path']]=q
    for q in pins.values():check(q)
    q=stage.read(stage.DOC/'qualification.json');assert all(q[k]for k in ['privateStageQualified','originalSourceReviewAccepted','visualAcceptance','identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted'])
    assert q['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')and q['sourceSHA256ByUid']==stage.SOURCES
    assert q['retainedSourcesReapproved']is False and q['supportByUid']=={} and q['retainedBasicSupportDependencies']==q['retainedCurrentBasicSupportUids']==[]
    images=q['imagesActuallyViewed'];assert len(images)==4 and {(i['uid'],i['width'],i['time'])for i in images}=={(u,w,t)for u in stage.SOURCES for w in [390,1280]for t in ['15:00','22:00']}
    for i in images:
        assert set(i)=={'path','sha256','uid','width','time'};check({k:i[k]for k in ['path','sha256']})
    for ref in q['browserReports']:
        check(ref);r=stage.read(ROOT/ref['path']);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2 and r['retainedNativeOwnViews']==[]
        for v in views:
            assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]
            expected=str(((ROOT/ref['path']).parent/v['file']).relative_to(ROOT));i=next(i for i in images if i['path']==expected);assert (i['uid'],i['width'],i['time'])==(v['uid'],v['width'],v['time'])
        assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==stage.SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
        if any(v['width']==390 for v in views):
            failures=[v for v in r['views']if v.get('phase')=='failed-download'];assert {v['uid']for v in failures}==set(stage.SOURCES)and len(failures)==1 and all(v['fallbackRetained']for v in failures)
    plan=stage.read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    assert set(plan)=={'areas','topLevelTerrainPatches'} and set(plan['areas'][0])=={'area','catalogue','destination'}
    before=stage.read(stage.PREVIOUS/'browser-config-390.json');cfg=stage.read(stage.STAGE/'live-browser-config.json')
    assert cfg['additionalRetainedUids']==before['additionalRetainedUids']==[]
    assert cfg['viewerURL']==before['viewerURL']=='http://127.0.0.1:4177/city.html'
    new=plan['topLevelTerrainPatches'][0];old=before['terrain'][0];assert new['sha256']==old['sha256']and new['resolution']==old['resolution']and new['replaces']==old['replaces']==q['exactTerrainReplacement']
    check(dict(path=new['source'],sha256=new['sha256']));check(dict(path=old['source'],sha256=old['sha256']))
    prior=ROOT/'3d-viewer'/new['replaces']['url'];check(dict(path=str(prior.relative_to(ROOT)),sha256=new['replaces']['sha256']))
    proof=stage.read(BASE/(stage.PREFIX+'ferry-changed-actor-scope-v1-20261026')/'summary.json');forms=stage.read(BASE/(stage.PREFIX+'ferry-group-form-checks-v1-20261026')/'summary.json');scope=stage.read(BASE/(stage.PREFIX+'ferry-source-scope-v1-20261026')/'summary.json')
    assert verify_context(stage.read(prior),stage.read(ROOT/new['source']),stage.TERRAIN_OWNERS,new['replaces'],proof,forms,scope)==q['hierarchicalRetention']
    check(new['hierarchicalNativeReview']);decision=stage.read(ROOT/new['hierarchicalNativeReview']['path'])
    assert decision['status']=='approved-for-integration'and decision['method']=='exact-whole-source-terrain-non-effect'and decision['replacementSHA256']==new['sha256']and decision['supersededSHA256']==new['replaces']['sha256']
    assert decision['retainedUids']==new['replaces']['retainedUids']and decision['affectedNativeUids']==decision['affectedRegisteredBasicSupportUids']==[] and decision['existingModelsReapproved']is False
    check(decision['wholeInstalledActorProof'])
    assert verify_catalogue_review(stage.read(stage.PREVIOUS/'catalogue.json'),stage.read(stage.STAGE/'catalogue.json'))
    assert {m['uid']:m['sha256']for m in stage.read(stage.STAGE/'catalogue.json')['models']}==stage.SOURCES
    return set(q['leaseResources'])

def assert_publication_idle():assert stage.read(stage.DOC/'qualification.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
    @contextmanager
    def guard():
        with connect()as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
    with guard():pass
    pub=stage.module('hierarchical_original_guarded_canonical_publish',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()

if __name__=='__main__':main()
