"""Verify exact publisher-qualified five-original metadata/assets privately."""
import argparse,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';FIXTURE=P+'five-qualified-stage-v1-20261101';BATCH=P+'five-qualified-stage-lifecycle-v1-20261101'
APPROVAL_KEYS={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','placementReview','aiGeometryModelling','sourceEvidenceInterpretationUsedAI'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,p):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    summary=take(FIXTURE,BASE/FIXTURE/'summary.json');assert summary['canonicalFullPublisherDryRunPassed']and summary['qualifiedExactStage'];resources=sorted(set(summary['leaseResources'])|{'server:127.0.0.1:4177'})
    if not a.owned:
        assert not local.exists();claim=reservations.claim('prosperous-qualified-lifecycle-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);stage=HERE/'accepted'/FIXTURE;cat=take(FIXTURE,stage/'catalogue.json');cfg=take(FIXTURE,stage/'live-browser-config.json');plan=take(FIXTURE,stage/'plan.json');dry=take(FIXTURE,BASE/FIXTURE/'publisher-dry-run/publication-plan.json')
    assert set(plan)=={'areas','topLevelTerrainPatches'}and len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    prior=P+'five-private-preview-v4-20261101';oldpath=HERE/'local'/(P+'five-private-preview-v2-20261101')/'atomic/catalogue.json';old=take(prior,oldpath);assert len(cat['models'])==len(old['models'])==5
    assert {k:v for k,v in cat.items()if k!='models'}=={k:v for k,v in old.items()if k!='models'}
    for before,after in zip(old['models'],cat['models']):
        assert {k:v for k,v in before.items()if k not in APPROVAL_KEYS}=={k:v for k,v in after.items()if k not in APPROVAL_KEYS}
        assert all(after[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
        p=stage/after['asset'];assert digest(p.read_bytes())==after['sha256'];refs.append(p)
    # Canonical publisher emits the same complete catalogue object; no tile overlays.
    pub=module('prosperous_qualified_encoding',HERE.parent/'island-detail-integration/publish.py');destination=plan['areas'][0]['destination'];assert digest(pub.encoded(cat))==dry['after']['3d-viewer/'+destination]
    assert not plan.get('illustrativeFoundations')and not cfg.get('privateSourceBoundTileOverlays')
    cfg.update(stage=str(stage.relative_to(ROOT))+'/',catalogueURL=destination,terrain=plan['topLevelTerrainPatches'],diagnosticOnly=True,publication=False,qualifiedExactStage=True);save(local/'config.json',cfg);refs.append(local/'config.json')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();refs.append(manifest)
    tool=HERE/'model_atomic_lifecycle_browser_v4_20261101.mjs';closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';refs.extend([tool,closure,HERE.parent/'island-detail-integration/publish.py']);out.mkdir();cp=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with(out/'browser.log').open('w')as log:result=subprocess.run(['node',str(tool),str((local/'config.json').relative_to(ROOT)),str((out/'browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        report=read(out/'browser/report.json');assert result.returncode==0 and report['passed']and not report['pageErrors']and len(report['cases'])==6
        expected={(1280,None)}|{(390,m['uid'])for m in cat['models']};assert {(r['width'],r['failedUid'])for r in report['cases']}==expected
        for r in report['cases']:
            assert r['baseOnlyRestoredCompleteGroup']and r['completeGroupEvicted']and not r['audit']['violations']
            if r['failedUid']:assert r['failureKeptAllBasics']
            assert {m['uid']:m['sha256']for m in r['sources']}==summary['sourceSHA256ByUid']
        assert manifest.read_bytes()==before and reservations.owns(lease);subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(cp);refs.extend(ROOT/p for p in read(cp)['inputHashes'])
        result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],browserPassed=True,cases=6,expectedCases=6,qualifiedExactStage=True,exactCanonicalCatalogueEncodingVerified=True,sourceMetadataDiffLimitedToApprovalKeys=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Actual6case desktop/mobile atomic lifecycle on exact qualified catalogue object, unchanged source assets/pose/support/activation metadata, and exact publisher terrain. Only approval/evidence fields differ from the prior6case tested catalogue. Canonical publisher catalogue bytes verified against dry-run SHA. No tile overlays or public writes. Fenced original-source snapshot/publication and actual installed HTTP/readback remain required.')
        save(out/'summary.json',result);module('prosperous_qualified_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-qualified-five-original-private-atomic-lifecycle',list(dict.fromkeys(refs)),result)
    finally:server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':main()
