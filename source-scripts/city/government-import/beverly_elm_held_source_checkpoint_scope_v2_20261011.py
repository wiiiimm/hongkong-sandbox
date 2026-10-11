"""Beverly/Elm complete source-only diagnostics and separate K/Pheld source ledger scope matching root's exact tracked-input cache contract."""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-beverly-elm-held-source-checkpoint-scope-v2-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();priorpath=B/'xl-terrain-recovery-20261011-parkview-block16-two-parent-facet-proposal-frontier-partial3D-locus-atomic-boundary-scope-v6/declared-scope.json';prior=read(priorpath);assert prior['declaredReferencesClosed']is True;current=read(B/'government-xl-beverly-podium233218-complete-current-ground-capture-v1-20261011/capture-scope.json')['currentManifest'];assert current['sha256']=='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e';resolutionPath=B/'government-xl-beverly-elm-exact-reference-resolution-v3-20261011/resolution.json';resolution=read(resolutionPath);assert resolution['resolutionComplete']is True;aliases=list(prior['historicalManifestAliases'])+resolution['historicalManifestAliases'];pointers=resolution['metadataLeafJsonPointers'];pointermap={(r['path'],r['boundary']['pointer']):r for r in pointers};leaves=set(prior['metadataLeafPaths']);assert not prior['metadataLeafJsonPointers'];archiveFolder=HERE/'local/government-xl-beverly-elm-held-source-byte-archives-v1-20261011';archiveFolder.mkdir(parents=True,exist_ok=True);newAliases=[]
 frozenV1Path=B/'government-xl-beverly-elm-held-source-checkpoint-scope-v1-20261011/declared-scope.json';frozenV1=read(frozenV1Path)
 for alias in frozenV1['newExactByteAliasRefs']:
  dest=ROOT/alias['archive']['path'];assert ref(dest)==alias['archive'];assert digest(dest.read_bytes())==alias['sha256'];newAliases.append(alias);aliases.append(alias)
 assert len(newAliases)==2 and {a['originalPath']for a in newAliases}=={'3d-viewer/city/data/manifest.json','docs/astra-city/model-integration-20260909/current-source-review.json'}
 assert read(archiveFolder/'main-source-review-pointer-8d35b6.json')['snapshotId']=='8d35b6f1d6f6bcdc'
 manifestArchive=archiveFolder/'manifest-b61c0bc.json';assert digest(manifestArchive.read_bytes())==current['sha256'];archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set();paths=set();queue=[];hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};seen=set()
 def hashed(p):
  if p not in hashes:hashes[p]=digest(p.read_bytes())if p.is_file()else None
  return hashes[p]
 def is_audit(p):return p.name in ['declared-scope.json','closed-scope.json','root-closed-scope.json']
 def initial_add(p):
  p=Path(p);assert p.is_file(),str(p);rel=str(p.relative_to(ROOT))
  if is_audit(p):audit[rel]=ref(p);return
  initial.add(rel)
 def add(p):
  p=Path(p);rel=str(p.relative_to(ROOT));assert p.is_file(),rel
  if is_audit(p):audit[rel]=ref(p);return
  if rel in tracked and rel not in initial:
   cached[rel]=dict(path=rel,sha256=hashed(p));return
  if rel not in paths:paths.add(rel);queue.append(p)
 def bind(path,h,origin):
  p=Path(path)if Path(path).is_absolute()else ROOT/path
  if not p.exists()and path.startswith('city/'):p=ROOT/'3d-viewer'/path
  rel=str(p.relative_to(ROOT))
  if hashed(p)!=h:
   p=archive.get((rel,h))
   if p is None:unknown.append(dict(path=rel,sha256=h,origin=origin));return
  assert hashed(p)==h;versions[(rel,h)]=dict(path=rel,sha256=h);add(p)
 def refs(v,origin,pointer=''):
  boundary=pointermap.get((origin,pointer))
  if boundary:
   assert digest((ROOT/origin).read_bytes())==boundary['documentSHA256'];assert digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())==boundary['boundary']['canonicalSHA256'];return
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:bind(v['path'],v['sha256'],origin)
   for k,x in v.items():
    if k in ['inputHashes','hashes','neighbourTileHashes','currentTileHashes','nativeCatalogueInputHashes','sourceInputHashes']and isinstance(x,dict):
     for p,h in x.items():
      if isinstance(p,str)and isinstance(h,str)and len(h)==64:bind(p,h,origin)
    else:refs(x,origin,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
  elif isinstance(v,list):
   for i,x in enumerate(v):refs(x,origin,pointer+'/'+str(i))
 # All actual new source/current/failed evidence and raw exports are explicit, including metadata-only registry snapshots read by source matching.
 folders=['government-xl-fixed295-simple-source-support-nomination-census-v1-20261011', 'government-xl-beverly-hill-k-original-carrier-bounded-grade-route-diagnostic-v1-20261011', 'government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011', 'government-xl-beverly-elm-complete-current-support-ground-capture-v1-20261011', 'government-xl-beverly-elm-complete-current-support-ground-capture-v2-20261011', 'government-xl-beverly-hill-k-current-carrier-four-stream-bounded-grade-route-diagnostic-v3-20261011', 'government-xl-elm-tree-original-podium-complete-current-finite-ground-diagnostic-v1-20261011', 'government-xl-beverly-hill-k-complete-current-carrier-strict-clearance-grade-exclusion-v1-20261011', 'government-xl-beverly-hill-k-j-original-podium233218-provenance-complete-contact-v1-20261011', 'government-xl-beverly-hill-k-j-original-podium233218-provenance-complete-contact-v2-20261011', 'government-xl-beverly-podium233218-complete-current-ground-capture-v1-20261011', 'government-xl-beverly-podium233218-complete-current-finite-ground-diagnostic-v1-20261011', 'government-xl-beverly-podium233218-foreign70279-identity-attribution-v1-20261011', 'government-xl-beverly-podium233218-70279-original-registry-farpoint-attribution-v1-20261011', 'government-xl-beverly-70279-primary-directory-absence-checkpoint-v1-20261011', 'government-xl-beverly-k-p-separate-held-source-review-plan-v1-20261011', 'government-xl-elm-tree-b-podium-frozen-source-identity-context-v1-20261011']
 for folder in folders:
  assert read(B/folder/'result.json').get('currentAcceptance',False)is False
  for root in [B/folder,HERE/'local'/folder]:
   for p in root.rglob('*'):
    if p.is_file():initial_add(p)
 for folder in ['government-xl-beverly-podium233218-complete-current-ground-capture-method-v1-20261011','government-xl-beverly-podium233218-foreign70279-identity-attribution-method-v1-20261011']:
  for p in (B/folder).rglob('*'):
   if p.is_file():initial_add(p)
 for p in archiveFolder.rglob('*'):
  if p.is_file():initial_add(p)
 numericalCode=set()
 for folder in folders:
  for r in read(B/folder/'result.json').get('evidenceRefs',[]):
   q=ROOT/r['path']
   if q.parent==HERE and q.suffix in ['.py','.mjs']and(q.name.startswith('beverly_')or q.name.startswith('elm_tree_')or q.name.startswith('xl_fixed295_'))and not q.name.startswith('beverly_garden_'):numericalCode.add(q)
 for p in sorted(numericalCode):initial_add(p)
 initial_add(ROOT/'source-scripts/city/model-review-ledger/ledger.py')
 initial_add(Path(__file__));initial_add(HERE/'beverly_elm_scope_exact_reference_resolver_v2_20261011.py');initial_add(HERE/'beverly_elm_scope_remaining_actual_manifest_archive_v3_20261011.py');initial_add(resolutionPath)
 for a in resolution['historicalManifestAliases']:initial_add(ROOT/a['archive']['path'])
 audit[str(priorpath.relative_to(ROOT))]=ref(priorpath)
 for rel in sorted(initial):add(ROOT/rel)
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaves:continue
  if p.name.endswith('.json')or p.name.endswith('.json.gz'):refs(read(p),rel)
  if p.suffix=='.py':
   for n in ast.walk(ast.parse(p.read_text())):
    names=([n.module]if isinstance(n,ast.ImportFrom)and n.module else[a.name for a in n.names]if isinstance(n,ast.Import)else[])
    for name in names:
     q=HERE/(name.split('.')[0]+'.py')
     if q.exists():add(q)
 assert ref(manifestArchive)['sha256']==current['sha256'];assert not(initial&leaves)
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),trackedCacheContract='Root contract: exact referenced tracked file hash verified; recurse only if explicitly initial. Full new Beverly/Elm source/numerical/current/held-ledger artifacts are explicitly initial even tracked.',historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),auditDeclarationsNotCandidateNumericInputs=True,unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,currentManifest=current,newMetadataLeaves=False,newMetadataPointerContract=True,exactHistoricalResolution=ref(resolutionPath),newHistoricalAliases=True,newExactByteAliasRefs=newAliases,currentAcceptance=False,installationApproved=False,newlyInstalled=0,fullNumericalSourceClosureRequired=True,localTerrainProposalWritten=False,solverInvoked=False,meshCreated=False,sourceOnly=True,separateHeldSnapshotId='1ef9e76176f13d45',mainPointerAndInstalledJUnchangedInHistoricalHeldLedgerBeforeAfterOnly=True,allCompletedSourceJobsIncluded=folders,noStageOrLiveOutputs=True,explicitInitialPaths=sorted(initial),elapsedSeconds=time.monotonic()-start,qualification='Actual full source/census/contact and actual complete drawn-ground captures, full four-stream finite/grade/foreign intersection proofs and all raw v1 source-identity/module-closure failures retained. Original70279 bounded complete native/primary directory inventory and exact PMAINbody farpoint attribution; durable separate exactlyK/Pheld ledger snapshot, no main/J change. Elm source fixed spatial fields only; no authenticTIN candidate, stage, source edits, native reapproval or installation. Every new actual numerical/source/current/ledger producer/result/method/test dependency explicit; prior committed root-reviewed tracked-cache dependencies exact hash only. Prior declarations are qualified audit metadata, not all prior candidate inputs. Exact historical Git blob aliases plus actual b61manifest/main8d35pointer copies; narrowly reviewed registry unused preparedFiles pointers only; no synthetic versions or new metadata leaves')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),exactTrackedDependencies=len(cached),versions=len(versions),elapsedSeconds=out['elapsedSeconds'],unboundCount=len(unknown),firstUnbound=unknown[:5])),flush=True)
if __name__=='__main__':main()
