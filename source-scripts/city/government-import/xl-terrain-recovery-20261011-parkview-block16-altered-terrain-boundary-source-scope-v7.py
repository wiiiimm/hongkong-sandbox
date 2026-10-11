"""Block16 separately versioned rejected proposal and canonical frontier scope matching root's exact tracked-input cache contract."""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';DOC=B/'xl-terrain-recovery-20261011-parkview-block16-altered-terrain-boundary-source-scope-v7'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();priorpath=B/'xl-terrain-recovery-20261011-parkview-block16-two-parent-facet-proposal-frontier-partial3D-locus-atomic-boundary-scope-v6/declared-scope.json';prior=read(priorpath);assert prior['declaredReferencesClosed']is True;current=prior['currentManifest'];assert current['sha256']=='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285';aliases=list(prior['historicalManifestAliases']);leaves=set(prior['metadataLeafPaths']);assert not prior['metadataLeafJsonPointers'];manifestArchive=HERE/'local/government-xl-parkview-block16-current-manifest-archive-20261011/manifest-post17-4a6756.json';assert digest(manifestArchive.read_bytes())==current['sha256'];archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set();paths=set();queue=[];hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};seen=set()
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
 def refs(v,origin):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:bind(v['path'],v['sha256'],origin)
   for k,x in v.items():
    if k in ['inputHashes','hashes','neighbourTileHashes','currentTileHashes','nativeCatalogueInputHashes','sourceInputHashes']and isinstance(x,dict):
     for p,h in x.items():
      if isinstance(p,str)and isinstance(h,str)and len(h)==64:bind(p,h,origin)
    else:refs(x,origin)
  elif isinstance(v,list):
   for x in v:refs(x,origin)
 # All actual new immutable altered-terrain diagnostics/methods are explicit.
 folders=['government-xl-parkview-block16-fixed-boundary-two-parent-vertex-feasibility-v1-20261011','government-xl-parkview-block16-causal-negative-corner-vertex-star-inventory-v1-20261011','government-xl-parkview-block16-partial-edge-vertex-star-boundary-inventory-v1-20261011','government-xl-parkview-block16-altered-terrain-boundary-obstruction-checkpoint-v1-20261011']
 for folder in folders:
  assert read(B/folder/'result.json')['currentAcceptance']is False
  for p in (B/folder).rglob('*'):
   if p.is_file():initial_add(p)
 for p in (B/'government-xl-parkview-block16-fixed-boundary-internal-vertex-height-feasibility-method-v1-20261011').rglob('*'):
  if p.is_file():initial_add(p)
 for n in ['parkview_block16_fixed_boundary_two_parent_vertex_feasibility_v1_20261011.py','parkview_block16_causal_negative_corner_vertex_star_inventory_v1_20261011.py','parkview_block16_partial_edge_vertex_star_boundary_inventory_v1_20261011.py','parkview_block16_altered_terrain_boundary_obstruction_checkpoint_v1_20261011.py']:
  initial_add(HERE/n)
 initial_add(Path(__file__))
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
 assert ref(manifestArchive)['sha256']==current['sha256'];assert not any('block16'in p for p in leaves)
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),trackedCacheContract='Root contract: exact referenced tracked file hash verified; recurse only if explicitly initial. Full new Block16 source/numerical/current artifacts are explicitly initial even tracked.',historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=[],auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),auditDeclarationsNotCandidateNumericInputs=True,unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,currentManifest=current,newMetadataLeaves=False,newHistoricalAliases=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0,fullNumericalSourceClosureRequired=True,localTerrainProposalWritten=False,solverInvoked=False,meshCreated=False,newBlock16StageOutputsAndLiveWritesExcluded=True,explicitInitialPaths=sorted(initial),elapsedSeconds=time.monotonic()-start,qualification='Actual immutable fixed-boundary two-parent infeasibility, causal negative-corner stars with unique primary grades, full actual94794/284382 partial-edge and corner incidence, exact obstruction/next-input Neon checkpoint. Every new numerical producer/result/method and declared library/test dependency recursively closes; previously independently reviewed committed v6/fd96 proofs remain exact tracked-cache dependencies. No unexecuted solver/candidate outcome, new alias/leaf, geometry/terrain edit, support waiver or global infeasibility claim. Prior audit inventories are separately exact metadata, never numeric inputs.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),exactTrackedDependencies=len(cached),versions=len(versions),elapsedSeconds=out['elapsedSeconds'],unboundCount=len(unknown),firstUnbound=unknown[:5])),flush=True)
if __name__=='__main__':main()
