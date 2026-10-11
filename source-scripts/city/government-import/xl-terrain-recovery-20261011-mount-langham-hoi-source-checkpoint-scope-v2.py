"""Additive completed source/current diagnostics; inherited closure unchanged.

No numerical/source/current/native/kernel metadata exemptions are introduced.
The current pair role must be frozen and independently reviewed before this
declaration can exist. Stage/live publication evidence closes separately.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-langham-hoi-source-checkpoint-scope-v2';DOC=BASE/BATCH
OLD=BASE/'xl-terrain-recovery-20261011-mount-langham-hoi-source-checkpoint-scope-v1/declared-scope.json'
ADDITIONS=(
 'xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1',
 'xl-terrain-recovery-20261011-mount-verdant-34-complete-backing-patches-context-v1',
 'xl-terrain-recovery-20261011-mount-verdant-three-long-original-backing-facets-v1',
 'xl-terrain-recovery-20261011-mount-verdant-207-four-stream-complete-back-associations-v1',
 'xl-terrain-recovery-20261011-mount-verdant-tower-backing-display-crops-v1',
 'xl-terrain-recovery-20261011-mount-verdant-tower-authentic-four-stream-finite-v1',
 'xl-terrain-recovery-20261011-mount-verdant-three-strips-ordinary-rim-source-diagnostic-v1',
 'xl-terrain-recovery-20261011-mount-verdant-three-open-bottom-four-stream-roof-perimeters-v1',
 'xl-terrain-recovery-20261011-mount-verdant-podium-four-stream-authentic-grade-cap-v1',
 'xl-terrain-recovery-20261011-mount-verdant-four-stream-restricted-source-contacts-v1',
 'xl-terrain-recovery-20261011-mount-verdant-204-four-stream-named-back-visual-proposals-v1',
 'government-xl-terrain-recovery-mount-verdant-two-original-current-probe-v2-20261011',
 'xl-terrain-recovery-20261011-mount-verdant-pair-current-inputs-v1',
 'government-xl-terrain-recovery-mount-verdant-pair-authentic-current-v1-20261011',
 'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v2',
 'xl-terrain-recovery-20261011-mount-verdant-pair-current-four-stream-finite-grade-v1',
 'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v9',
 'xl-terrain-recovery-20261011-mount-verdant-pair-complete-current-role-v1',
 'xl-terrain-recovery-20261011-hoi-shing-whole-authentic-tin-derived-step-candidate-v1',
 'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1',
 'government-xl-hoi-shing-unresolved-original-body-topology-v1-20261011')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD);assert old['sourceOnly'] and not old['newMetadataLeaves'];paths=set(old['closedExplicitPaths']);paths.update([str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]);receipts=list(old['completedFencedSourceReceipts'])
 for batch in ADDITIONS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for p in r['evidenceRefs']:assert (ROOT/p['path']).is_file(),p['path'];paths.add(p['path'])
  paths.update(str(p.relative_to(ROOT)) for p in folder.rglob('*') if p.is_file());receipts.append(dict(batch=batch,receipt=ref(folder/'result.json'),jobId=r['jobId']))
 for name in ['xl-terrain-recovery-20261011-mount-verdant-pair-composition-code-validation-v1']:
  paths.update(str(p.relative_to(ROOT)) for p in (BASE/name).rglob('*') if p.is_file())
 extra=['mount_verdant_204_original_complete_back_visual_proposals_v1_20261011.py','mount_verdant_204_exact_original_back_visual_proposal_membership_v1_20261011.json','test_mount_verdant_204_original_complete_back_visual_proposals_v1_20261011.py','mount_verdant_current_pair_role_composition_v1_20261011.py','test_mount_verdant_current_pair_role_composition_v1_20261011.py','exact_original_tin_shared_vertex_lowering_diagnostic_v1_20261011.py','test_exact_original_tin_shared_vertex_lowering_diagnostic_v1_20261011.py']
 paths.update(str((HERE/n).relative_to(ROOT)) for n in extra)
 DOC.mkdir();archive=DOC/'historical-current-manifest.json';original=BASE/'government-xl-terrain-recovery-mount-verdant-pair-authentic-current-v1-20261011/historical-current-manifest.json';archive.write_bytes(original.read_bytes());assert digest(archive.read_bytes())=='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e';paths.add(str(archive.relative_to(ROOT)))
 aliases=list(old['historicalManifestAliases']);aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(archive.read_bytes()),archive=ref(archive)))
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=old['metadataLeafPaths'],metadataLeafJsonPointers=old['metadataLeafJsonPointers'],completedFencedSourceReceipts=receipts,inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorScope=ref(OLD),additiveCompletedSlices=list(ADDITIONS),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,oneNewByteExactHistoricalGlobalManifestAlias=ref(archive),sourceGeometryChanges=0,sourceAndCandidateDiagnosticsOnly=True,currentAcceptanceRequiresSeparateStagedAndLiveProof=True,stageAndLiveExcluded=True,newlyInstalled=0)
 assert out['metadataLeafPaths']==old['metadataLeafPaths'] and out['metadataLeafJsonPointers']==old['metadataLeafJsonPointers'];save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),completedFencedReceipts=len(receipts),newNumericLeaves=False),flush=True)
if __name__=='__main__':main()
