"""Add completed Hoi source-only diagnostics without any closure exemption.

All old numerical references/aliases and metadata boundaries stay. Complete
source math must have a fenced final receipt before this declaration exists.
No current, host, role, terrain deployment or installation acceptance.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-source-checkpoint-scope-v3';DOC=BASE/BATCH
OLD=BASE/'xl-terrain-recovery-20261011-mount-langham-hoi-source-checkpoint-scope-v2/declared-scope.json'
ADDITIONS=(
 'xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-checkpoint-v2',
 'xl-terrain-recovery-20261011-hoi-shing-eleven-open-wall-roof-loops-context-v1',
 'xl-terrain-recovery-20261011-hoi-shing-eleven-open-wall-upper-underside-band-v1',
 'xl-terrain-recovery-20261011-hoi-shing-derived-ground-complete-original-finite-v1',
 'xl-terrain-recovery-20261011-hoi-shing-three-face-original-patch-host-context-v1')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD);assert not old['newMetadataLeaves']and old['stageAndLiveExcluded'];paths=set(old['closedExplicitPaths']);paths.update([str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]);receipts=list(old['completedFencedSourceReceipts'])
 for batch in ADDITIONS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert not r.get('installationApproved',False)and not r.get('newlyInstalled',0)
  for p in r['evidenceRefs']:assert (ROOT/p['path']).is_file(),p['path'];paths.add(p['path'])
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file());receipts.append(dict(batch=batch,receipt=ref(folder/'result.json'),jobId=r['jobId']))
 # Failed v1 receipt preserves already-complete 207-face math and raw error.
 failed=BASE/'xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-v1'
 paths.update(str(p.relative_to(ROOT))for p in failed.rglob('*')if p.is_file())
 extra=['xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-v1.py','exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py']
 paths.update(str((HERE/n).relative_to(ROOT))for n in extra)
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],historicalManifestAliases=old['historicalManifestAliases'],metadataLeafPaths=old['metadataLeafPaths'],metadataLeafJsonPointers=old['metadataLeafJsonPointers'],completedFencedSourceReceipts=receipts,inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorScope=ref(OLD),additiveCompletedSlices=list(ADDITIONS),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,sourceGeometryChanges=0,sourceOnly=True,hostQualification=False,roleAssigned=False,currentAcceptance=False,terrainDeployment=False,structuralRootOrBridgeCredit=False,newlyInstalled=0)
 assert out['metadataLeafPaths']==old['metadataLeafPaths']and out['metadataLeafJsonPointers']==old['metadataLeafJsonPointers'];save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),completedFencedReceipts=len(receipts),newNumericLeaves=False),flush=True)
if __name__=='__main__':main()
