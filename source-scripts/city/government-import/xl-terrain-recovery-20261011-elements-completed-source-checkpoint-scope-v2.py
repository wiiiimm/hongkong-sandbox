"""Add only completed Elements diagnostics to the sealed source checkpoint.

Every numerical dependency remains recursive. Inherited metadata boundaries
and historical aliases are byte-preserved; there are no new source/ground
leaves. This is not a current, authored-role, native or installation approval.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements-completed-source-checkpoint-scope-v2';DOC=BASE/BATCH
OLD=BASE/'xl-terrain-recovery-20261011-elements-completed-source-checkpoint-scope-v1/declared-scope.json'
ADDITIONS=(
 'xl-terrain-recovery-20261011-elements132-complete-unit-mount-patches-v1',
 'xl-terrain-recovery-20261011-elements31-complete-lateral-patches-and39-disposition-v1')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD)
 assert old['sourceOnly']and not old['currentAcceptance']and not old['newMetadataLeaves']and not old['newMetadataPointerContract']
 paths=set(old['closedExplicitPaths']);paths.update([str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]);receipts=list(old['completedFencedSourceReceipts'])
 for batch in ADDITIONS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert not r.get('newlyInstalled',0)and not r.get('installationApproved',False)
  for binding in r['evidenceRefs']:
   p=ROOT/binding['path'];assert p.is_file()and ref(p)==binding;paths.add(binding['path'])
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
  local=HERE/'local'/batch
  if local.exists():paths.update(str(p.relative_to(ROOT))for p in local.rglob('*')if p.is_file())
  receipts.append(dict(batch=batch,receipt=ref(folder/'result.json'),jobId=r['jobId']))
 paths.update(str((HERE/n).relative_to(ROOT))for n in ['exact_closed_ground_aabb_pruning_v1_20261011.py','test_exact_closed_ground_aabb_pruning_v1_20261011.py'])
 archive=BASE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1/historical-current-manifest.json'
 aliases=list(old['historicalManifestAliases']);alias=dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(archive.read_bytes()),archive=ref(archive))
 if alias not in aliases:aliases.append(alias)
 assert archive.is_file();paths.add(str(archive.relative_to(ROOT)))
 paths.add(str((DOC/'declared-scope.json').relative_to(ROOT)))
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)if p!=str((DOC/'declared-scope.json').relative_to(ROOT))],historicalManifestAliases=aliases,metadataLeafPaths=old['metadataLeafPaths'],metadataLeafJsonPointers=old['metadataLeafJsonPointers'],completedFencedSourceReceipts=receipts,inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorScope=ref(OLD),additiveCompletedElementsSlices=list(ADDITIONS),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,sourceGeometryChanges=0,terrainChanges=0,stageAndLiveExcluded=True,sourceOnly=True,hostQualification=False,authoredRoleAccepted=False,currentAcceptance=False,nativeReacceptance=False,structuralRootOrBridgeCredit=False,newlyInstalled=0)
 assert out['metadataLeafPaths']==old['metadataLeafPaths']and out['metadataLeafJsonPointers']==old['metadataLeafJsonPointers'];save(DOC/'declared-scope.json',out)
 print(dict(paths=len(paths),completedFencedReceipts=len(receipts),newNumericLeaves=False,currentAcceptance=False),flush=True)
if __name__=='__main__':main()
