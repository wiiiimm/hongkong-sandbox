"""Additive source-only checkpoint: three final paths plus negative visual hosts.

Preserve v1 and inherit exactly its reviewed metadata boundaries/aliases; no new
numerical leaves, live/current approval or source geometry changes.
"""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-hoi-source-checkpoint-scope-v2';DOC=BASE/BATCH
OLD=BASE/'xl-terrain-recovery-20261011-langham-hoi-source-checkpoint-scope-v1/declared-scope.json'
ADDITIONS=('xl-terrain-recovery-20261011-langham-three-remaining-four-stream-exposed-paths-v1','xl-terrain-recovery-20261011-langham-remaining14-new-visual-hosts-four-stream-diagnostic-v1')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD);assert old['sourceOnly']is True and old['newMetadataLeaves']is False
 paths=set(old['closedExplicitPaths']);paths.update((str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))));receipts=list(old['completedFencedSourceReceipts'])
 for batch in ADDITIONS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  bound={x['path']:x for x in r['evidenceRefs']};diag=folder/'diagnostic.json.gz';assert bound[str(diag.relative_to(ROOT))]==ref(diag)
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file());paths.add(str((HERE/(batch+'.py')).relative_to(ROOT)))
  receipts.append(dict(batch=batch,receipt=ref(folder/'result.json'),jobId=r['jobId']))
 DOC.mkdir();readme=DOC/'README.md';readme.write_text('''# Additive Langham / Hoi Shing source-only checkpoint\n\nThe original v1 checkpoint remains immutable. This slice adds two completed source diagnoses, installing zero models and granting no current, native, visual or structural acceptance. All source geometry and existing numerical limits are unchanged. The captured source/runtime/ground baseline remains historical `cb79525c…`; subsequent map publications require independent fresh current binding before any promotion.\n\nThe final three native963→owned entry paths (owned bodies33,787,788) now pass complete bounded exposed paths in all four representations. Path lengths are48,36,40, and each upper interface has positive line dimension. Genuine grade witnesses, strictly exposed first edges and previous complete facets are reused only after exact Neon-fenced artifact membership, identical full source/world/ground bytes and unchanged helper versions. Actual shared edges and upper contacts are independently reconstructed; additional Float32 facets use the unchanged full finite proof. Combined with the four earlier alternatives, all seven entry routes have four-stream bounded exposure evidence. This supplies no whole native-body reapproval; 2,859 whole-native clearance negatives remain preserved.\n\nAll14 remaining complete details were tested against all five newly associated conditional visual host bodies, in all four representations. Complete 3D bounds independently exclude every host within the existing0.1m mounting band: the smallest exact distance lower bound is over14.93m. Thus these hosts do not recover the14 details. No partial boundary or interior association is credited, and their previous failed865-host census and one-point-only result remain explicit.\n\nLangham body565 retains its literal exact-negative interface separately from the conditional original→literal affine association. The76 opening-panel and five end-patch proposals still require independently grounded host and typed visual-role acceptance. Hoi Shing retains its nine real upward-burial holds. Root owns independent closure review, Git and any future publication. No new metadata/source/numeric leaves or pointer exceptions are introduced.\n''');paths.add(str(readme.relative_to(ROOT)))
 leaves=old['metadataLeafPaths'];assert not any(('langham'in p or'hoi-shing'in p)and p in leaves for p in paths)
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],historicalManifestAliases=old['historicalManifestAliases'],metadataLeafPaths=leaves,metadataLeafJsonPointers=old['metadataLeafJsonPointers'],completedFencedSourceReceipts=receipts,inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorScope=ref(OLD),additiveCompletedSlices=list(ADDITIONS),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,sourceGeometryChanges=0,sourceOnly=True,currentAcceptance=False,stageAndLiveExcluded=True,newlyInstalled=0)
 assert out['metadataLeafPaths']==old['metadataLeafPaths']and out['metadataLeafJsonPointers']==old['metadataLeafJsonPointers']and out['historicalManifestAliases']==old['historicalManifestAliases']
 save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),fencedSourceReceipts=len(receipts),newMetadataLeaves=False),flush=True)
if __name__=='__main__':main()
