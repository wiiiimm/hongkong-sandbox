"""Completed-only additive Twin proof scope; no new metadata exemptions.

The running/draft1120 binder, current acceptance, stage/live and Git are excluded.
All six newly completed receipts retain full numerical/source/module/image refs.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-twin-regency-completed-source-checkpoint-scope-v2';DOC=BASE/BATCH
OLD=BASE/'government-xl-twin-regency-completed-source-root-closure-v1-20261011/root-closed-scope.json'
JOBS=(
 'xl-terrain-recovery-20261011-twin-regency-pair-current-four-stream-finite-grade-v1',
 'xl-terrain-recovery-20261011-twin-regency-whole-terrain-domain-current6645-native-census-v1',
 'xl-terrain-recovery-20261011-twin-regency-bounded-four-stream-current-podium-paths-v1',
 'xl-terrain-recovery-20261011-twin-regency293-four-stream-qualified-host-association-v1',
 'xl-terrain-recovery-20261011-twin155-named-complete-boundary-visual-proposals-v1',
 'xl-terrain-recovery-20261011-twin138-named-original-source-placement-proposals-v1')
EXTRA_FOLDERS=(
 'xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v2',
 'xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v3',
 'xl-terrain-recovery-20261011-twin-regency-f32-negative-representative-source-context-v1',
 'xl-terrain-recovery-20261011-twin155-source-proposal-validation-v1',
 'xl-terrain-recovery-20261011-twin138-source-placement-validation-v1',
 'xl-terrain-recovery-20261011-twin138-whole-original-placement-context-v1')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD);assert old['independentlyVerified']is True
 paths=set(old['paths']);paths.update([str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]);receipts=[]
 for batch in JOBS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert r.get('newlyInstalled',0)==0 and r.get('currentAcceptance',False)is False and not r.get('installationApproved',False)
  for q in r['evidenceRefs']:
   p=ROOT/q['path'];assert p.is_file()and ref(p)==q;paths.add(q['path'])
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
  local=HERE/'local'/batch
  if local.exists():paths.update(str(p.relative_to(ROOT))for p in local.rglob('*')if p.is_file())
  receipts.append(dict(batch=batch,receipt=ref(folder/'result.json'),jobId=r['jobId']))
 for batch in EXTRA_FOLDERS:
  folder=BASE/batch;assert folder.is_dir();paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
 for n in ['xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v2.py','xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v3.py','xl-terrain-recovery-20261011-twin-regency-f32-negative-representative-source-context-v1.py','xl-terrain-recovery-20261011-twin138-whole-original-placement-context-v1.py']:
  paths.add(str((HERE/n).relative_to(ROOT)))
 declaration=str((DOC/'declared-scope.json').relative_to(ROOT));paths.add(declaration)
 assert not any('twin_regency1120_'in p or 'twin-regency1120-'in p for p in paths),'Uncompleted binder is excluded'
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)if p!=declaration],historicalManifestAliases=old['historicalManifestAliases'],metadataLeafPaths=old['metadataLeafPaths'],metadataLeafJsonPointers=old['metadataLeafJsonPointers'],inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorRootScope=ref(OLD),completedFencedSourceReceipts=receipts,additiveCompletedTwinSlices=list(JOBS),sourceContextsValidationAndFailedWriterHistory=list(EXTRA_FOLDERS),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,stageAndLiveExcluded=True,sourceOnly=True,currentAcceptance=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,newlyInstalled=0)
 assert out['metadataLeafPaths']==old['metadataLeafPaths']and out['metadataLeafJsonPointers']==old['metadataLeafJsonPointers']and out['historicalManifestAliases']==old['historicalManifestAliases']
 save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),completedNewReceipts=len(receipts),newMetadataExemptions=False,newlyInstalled=0),flush=True)
if __name__=='__main__':main()
