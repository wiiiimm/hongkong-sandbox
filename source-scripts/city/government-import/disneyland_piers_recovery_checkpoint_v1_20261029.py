"""Read back completed pier phases and preserve explicit unresolved obligations."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,connect,digest
from primrose_compound_foundation_v2_20261015 import module

BATCH='government-xl-disneyland-piers-recovery-checkpoint-v1-20261029'
INVENTORY='government-xl-after-lookout-current-inventory-v1-20261029'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists()
    paths=sorted(base.glob('government-xl-disneyland*-20261029/result.json'))+[base/INVENTORY/'result.json']
    paths=[p for p in paths if p.parent.name!=BATCH];receipts=[read(p)for p in paths];assert len({r['jobId']for r in receipts})==len(receipts)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        actual={key:(status,result)for key,status,result in db.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId']for r in receipts],))}
        assert all(actual[r['jobId']]==('complete',r)for r in receipts)
        active=db.execute("SELECT count(*) FROM astra_modelling.reservation_groups WHERE batch LIKE 'government-xl-disneyland%%20261029' AND released_at IS NULL AND lease_until>clock_timestamp()").fetchone()[0]
    assert active==0
    phases=[dict(batch=r['batch'],jobId=r['jobId'],localReceiptSHA256=digest(p.read_bytes()),neonCompleteAndIdentical=True)for p,r in zip(paths,receipts)]
    result=dict(uids=['landsd/75642:0','landsd/75643:0','landsd/74189:0'],installedFixedXL=400,exactCurrentSourceTerminalFixedXL=3,outstandingFixedXL=118,totalFixedXL=521,currentDetailedRuntimeActors=7015,newlyInstalled=0,phases=phases,activeOwnedReservations=0,aiGeometryModelling=False,optimisationStarted=False,sourceGeometryChanges=0,privateProposalsOnly=True,
      heldReasons=[dict(uid='landsd/75642:0',foundationPolicyPassed=True,buriedFaces=3,upwardBuriedFaces=0,remaining=['retained BASIC way/334029318:0 ground-gap regression','shared-cell composition with 75643 proposal','complete source/interface and browser/publication gates']),dict(uid='landsd/75643:0',foundationPolicyPassed=False,buriedFaces=2,upwardBuriedFaces=0,remaining=['authored lower-wall facets 32612/32613 exceed ordinary buried-area policy','retained BASIC way/334029318:0 identity/contact/ground-gap obligations','shared-cell composition with 75642 proposal','complete source/interface and browser/publication gates']),dict(uid='landsd/74189:0',xlCredit=False,remaining=['recovered unchanged original is a companion nomination only','zero conservative roof coverage of disputed BASIC footprint above 5m; do not suppress BASIC','fresh exact current-form routing and all physical gates if installation pursued'])],
      qualification='All completed phase receipts read back exactly from pinned Neon. Inactive feature scopes grant extent identity only, never physical/publication approval. Failed proposals remain failures. No duplicate suppression, government model edits, optimisation or new installed credit. Both NULL-UID fixed source keys remain in the 118 outstanding cohort.')
    save(doc/'summary.json',result)
    refs=[Path(__file__),*paths,ROOT/'3d-viewer/city/official-model-reviewed-original-feature-data.js']
    for name in ['astra-exact-parent-partition-final-tests-20261029.log','astra-disneyland-reviewed-feature-final-tests-20261029.log','astra-disneyland-feature-interface-final-tests-20261029.log']:
        p=Path('/tmp')/name;assert p.exists();dest=doc/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);refs.append(dest)
    module('pier_recovery_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'pier-recovery-held-obligations-and-completed-phase-neon-readback',refs,result)

if __name__=='__main__':main()
