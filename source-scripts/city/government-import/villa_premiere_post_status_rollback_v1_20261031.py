"""Verify a fully checked installation rolled back only after final status output."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD='government-xl-villa-premiere89917-five-original-installed-v1-20261031';BATCH='government-xl-villa-premiere89917-post-status-rollback-readback-v1-20261031'

def verify():
    folder=BASE/OLD;failure=read(folder/'failure-recovery.json');history=read(folder/'historical-input-context.json');final=read(folder/'result.json');acceptance=read(folder/'installed-acceptance.json')
    assert failure==dict(allPublicDestinationsRestored=True,currentPointerRestoredNotDerivedCredit=True,derivedInstalledReviewHistoryRetained=True,error="BrokenPipeError(32, 'Broken pipe')",rollbackErrors=[])
    assert final['snapshotId']==acceptance['snapshotId']and final['sourceSHA256ByUid']==acceptance['sourceSHA256ByUid']and len(final['sourceSHA256ByUid'])==5
    assert final['fullXLCurrentCounts']==dict(total=521,installedVerified=411,remaining=110)
    expected={r['originalPath']:r['originalSHA256']for r in history['mutableCurrentByteSnapshots']};assert len(expected)==len(history['mutableCurrentByteSnapshots']);states=[]
    for r in history['mutableCurrentByteSnapshots']:
        b=r['savedHistoricalBytes'];p=(ROOT/b['path']).resolve();assert p.is_relative_to(ROOT)and digest(p.read_bytes())==b['sha256']==r['originalSHA256']
    for name in history['allMutableDestinations']:
        p=(ROOT/name).resolve();assert p.is_relative_to(ROOT);actual=digest(p.read_bytes())if p.exists()else None;assert actual==expected.get(name),name;states.append(dict(path=name,restoredSHA256=actual))
    pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']==history['preInstallSnapshot']and pointer['snapshotId']!=final['snapshotId']
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert not any('villa-premiere89917-qualified-stage'in url for url in manifest['officialModelCatalogues'])
    live=read(folder/'live-http/report.json');review=read(folder/'ROOT-LIVE-EXPORT-OBSERVATIONS.json');assert live['passed']and live['liveInstalledHTTP']and not live['catalogueAndTerrainSubstitution']and len(live['cases'])==6 and not live['pageErrors']
    assert review['liveExportsAccepted']and review['reviewer']=='Codex ROOT'and review['sourceGeometryChanges']==0
    for b in [review['browserReport'],*review['imagesActuallyInspected']]:assert digest((ROOT/b['path']).read_bytes())==b['sha256']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(final['jobId'],)).fetchone()==('complete',final)
        for uid,sha in final['sourceSHA256ByUid'].items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(final['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    return dict(uids=sorted(final['sourceSHA256ByUid']),sourceSHA256ByUid=final['sourceSHA256ByUid'],historicalCompletedJobId=final['jobId'],historicalDerivedSnapshotId=final['snapshotId'],currentSnapshotId=pointer['snapshotId'],allMutableDestinationsByteRestored=True,verifiedRestoredStates=states,liveCasesPassedBeforePostStatusFailure=6,rootActuallyReviewedLiveExports=True,installationCurrentlyPresent=False,newInstallationCredit=0,reason='Closed output pipe caused only the final status print to fail AFTER successful job/ledger/count/readback completion. Existing broad transaction exception handler then restored every public destination and active pointer. Historical installed ledger remains explicit and inactive; a distinct fenced recovery attempt is required. No source corruption, geometry edits, hidden model failure or duplicate current installation credit.',installationApproved=False,publication=False,sourceGeometryChanges=0)

def main():
    result=verify();out=BASE/BATCH;assert not out.exists();save(out/'summary.json',result);folder=BASE/OLD;refs=[Path(__file__),*[folder/n for n in ['failure-recovery.json','historical-input-context.json','result.json','installed-acceptance.json','live-http/report.json','ROOT-LIVE-EXPORT-OBSERVATIONS.json']]]
    refs.extend(ROOT/r['savedHistoricalBytes']['path']for r in read(folder/'historical-input-context.json')['mutableCurrentByteSnapshots'])
    module('villa_post_status_rollback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-live-checks-post-status-output-rollback-current-state',refs,result)

if __name__=='__main__':main()
