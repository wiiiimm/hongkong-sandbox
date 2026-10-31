"""Verify exact rollback baseline after the known inactive review-snapshot collision."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-villa-premiere89917-';BATCH=P+'distinct-retry-baseline-v1-20261031'

def verify():
    v1=BASE/(P+'five-original-installed-v1-20261031');v2=BASE/(P+'five-original-installed-v2-20261031');final=read(v1/'result.json');failure=read(v2/'failure-recovery.json')
    assert failure==dict(allPublicDestinationsRestored=True,currentPointerRestoredNotDerivedCredit=True,derivedInstalledReviewHistoryRetained=False,error="AssertionError('publisher-apply failed; see saved log')",rollbackErrors=[])
    assert read(v1/'failure-recovery.json')['error']=="BrokenPipeError(32, 'Broken pipe')"
    assert read(v1/'acceptance.json')==read(v2/'acceptance.json'),'Collision diagnosis no longer matches exact attempts'
    states=[]
    for folder in [v1,v2]:
        history=read(folder/'historical-input-context.json');expected={r['originalPath']:r['originalSHA256']for r in history['mutableCurrentByteSnapshots']}
        for r in history['mutableCurrentByteSnapshots']:
            b=r['savedHistoricalBytes'];assert digest((ROOT/b['path']).read_bytes())==b['sha256']==r['originalSHA256']
        for name in history['allMutableDestinations']:
            p=(ROOT/name).resolve();assert p.is_relative_to(ROOT);actual=digest(p.read_bytes())if p.exists()else None;assert actual==expected.get(name),name;states.append(dict(attempt=folder.name,path=name,restoredSHA256=actual))
    pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']=='a78b572ebeaac3a6'and pointer['snapshotId']!=final['snapshotId']
    assert not any('villa-premiere89917-qualified-stage'in u for u in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'])
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(final['jobId'],)).fetchone()==('complete',final)
        for uid,sha in final['sourceSHA256ByUid'].items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(final['snapshotId'],uid)).fetchone()==('approved-for-integration',sha)
    return dict(uids=sorted(final['sourceSHA256ByUid']),sourceSHA256ByUid=final['sourceSHA256ByUid'],currentSnapshotId=pointer['snapshotId'],inactiveCollidingSnapshotId=final['snapshotId'],bothAttemptsByteRestored=True,identicalAttemptAcceptanceCausedSnapshotCollision=True,verifiedRestoredStates=states,newAttemptMustBindTransactionBatch=True,installationCurrentlyPresent=False,newInstallationCredit=0,sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='V1 succeeded then rolled back on final stdout BrokenPipe. V2 restored the same baseline, but identical acceptance payload reused inactive snapshot5507 and changed its five rows back to approved before publisher preflight. Current active pointer and all public bytes remain baseline. Preserve both histories; the next fenced attempt must bind its unique transaction batch into acceptance/snapshot identity, leaving old5507 untouched. No source/model corruption or current installed credit.')

def main():
    result=verify();out=BASE/BATCH;assert not out.exists();save(out/'summary.json',result);refs=[Path(__file__)]
    for version in [1,2]:
        folder=BASE/(P+'five-original-installed-v'+str(version)+'-20261031');refs.extend(folder/n for n in ['acceptance.json','failure-recovery.json','historical-input-context.json']);refs.extend(ROOT/r['savedHistoricalBytes']['path']for r in read(folder/'historical-input-context.json')['mutableCurrentByteSnapshots'])
    refs.append(BASE/(P+'five-original-installed-v1-20261031')/'result.json');module('villa_distinct_retry_baseline_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-rolled-back-baseline-and-inactive-snapshot-retry-collision',refs,result)

if __name__=='__main__':main()
