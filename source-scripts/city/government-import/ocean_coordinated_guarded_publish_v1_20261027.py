"""Lease-fenced publisher for the exact reviewed four-original atomic assembly.

No general guard is weakened: source support/group, old entries and exact nested
terrain are checked by the separate positive contract before canonical publish.
"""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import ocean_coordinated_qualified_stage_v2_20261027 as stage
from original_coordinated_retained_contract_v1_20261027 import verify_metadata,verify_retained_entries,verify_native_interfaces
from original_nested_coordinated_publisher_v1_20261027 import publisher
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=stage.CONFIG['prefix']+'-original-installed-v1-'+stage.CONFIG['date']
BROWSER=BASE/stage.CONFIG['browser'];REVIEW=BASE/stage.CONFIG['physical']

def check(q):assert stage.ref(ROOT/q['path'])==q,q['path']

def assert_publication_idle():
    assert stage.read(stage.DOC/'qualification.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')

def evidence():
    pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [stage.DOC,stage.SOURCE,BROWSER,REVIEW]:
            result=stage.read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
            for q in result['evidenceRefs']:
                assert q['path'] not in pins or pins[q['path']]==q;pins[q['path']]=q
    for q in pins.values():check(q)
    q=stage.read(stage.DOC/'qualification.json')
    assert all(q[k] for k in ['privateStageQualified','originalSourceReviewAccepted','identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
    assert q['sourceSHA256ByUid']==stage.SOURCES and not q['publication']
    assert_publication_idle()
    assert len(q['imagesActuallyViewed'])==16 and len(q['retainedImagesActuallyViewed'])==108 and len(q['supplementalImagesActuallyViewed'])==24
    for field in ['imagesActuallyViewed','retainedImagesActuallyViewed','supplementalImagesActuallyViewed']:
        for image in q[field]:check(image)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';current={}
    for url in stage.read(manifest)['officialModelCatalogues']:
        for m in stage.read(ROOT/'3d-viewer'/url)['models']:assert m['uid'] not in current;current[m['uid']]=m
    assert verify_retained_entries(current,q['retainedNativeEntries'],stage.SOURCES,stage.CONFIG['currentNativeActors'])
    scope=stage.read(BASE/stage.CONFIG['modelScope']/'summary.json');contacts=stage.read(BASE/stage.CONFIG['nativeContacts']/'summary.json')
    assert verify_native_interfaces(q,scope,contacts,current,stage.SOURCES)
    selection=stage.read(BASE/stage.CONFIG['runtime']/'selection.json.gz');original={r['uid']:r['candidate']['entry'] for r in selection['rows']}
    models=stage.read(stage.STAGE/'catalogue.json')['models']
    assert verify_metadata(models,stage.SOURCES,stage.CONFIG['supportByUid'],original,stage.CONFIG['groundOwnerUids'])
    for m in models:
        assert all(m[k] is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
        assert m['sourceIdentityReview']==stage.ref(stage.SOURCE/'ROOT-SOURCE-REVIEW.json')
        assert m['sourceFunctionalApplicability']==stage.ref(stage.DOC/'qualification.json')
        check(dict(path=str((stage.STAGE/m['asset']).relative_to(ROOT)),sha256=stage.SOURCES[m['uid']]))
    plan=stage.read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    assert not plan.get('catalogueReplacements') and not plan['areas'][0].get('estimates')
    entry=plan['topLevelTerrainPatches'][0];patch=stage.read(BASE/stage.CONFIG['patch']/'summary.json')
    replaced=patch['replacedNativeTerrain'][0]
    assert entry['replaces']=={k:replaced[k] for k in ['url','sha256','retainedUids']}
    assert entry['sha256']==patch['candidate']['sha256'];check(dict(path=entry['source'],sha256=entry['sha256']))
    old=ROOT/'3d-viewer'/replaced['url'];candidate=ROOT/patch['candidate']['path']
    _,retention=publisher('ocean_guard_contract_validation',old,candidate,stage.CONFIG['groundOwnerUids'],stage.SOURCES,patch)
    assert retention==q['retention']
    check(entry['nativeReview']);decision=stage.read(ROOT/entry['nativeReview']['path'])
    assert decision['retention']==retention and decision['replacementSHA256']==entry['sha256']
    check(decision['fullMeshCheck']);rows=stage.read(ROOT/decision['fullMeshCheck']['path'])['rows']
    assert {r['uid'] for r in rows}==set(stage.CONFIG['retainedNativeUids'])
    assert all(r['passed'] and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in rows)
    return set(q['leaseResources'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json'
    keys=evidence();lease=json.loads(Path(a.receipt).read_text())
    @contextmanager
    def guard():
        with connect() as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            live=reservations._current(db,lease);assert live and keys<=set(live['resources'])
            assert_publication_idle();yield
    with guard():pass
    patch=stage.read(BASE/stage.CONFIG['patch']/'summary.json');old=ROOT/'3d-viewer'/patch['replacedNativeTerrain'][0]['url'];candidate=ROOT/patch['candidate']['path']
    pub,_=publisher('ocean_guarded_original_nested_publisher',old,candidate,stage.CONFIG['groundOwnerUids'],stage.SOURCES,patch)
    pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
    sys.argv=['publish.py',a.plan]+(['--apply'] if a.apply else[]);pub.main()

if __name__=='__main__':main()
