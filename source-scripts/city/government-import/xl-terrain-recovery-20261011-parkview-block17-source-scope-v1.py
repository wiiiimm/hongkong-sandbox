"""Block17 initial source scope matching root's exact tracked-input cache contract."""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';DOC=B/'xl-terrain-recovery-20261011-parkview-block17-source-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();rolepath=B/'xl-terrain-recovery-20261011-parkview-block17-current-role-v1';assert read(rolepath/'result.json')['currentTypedPhysicalAccepted']is True;role=read(rolepath/'typed-role.json.gz');assert role['currentManifest']['sha256']=='ba6399c629e6c8876125a339cc80e0a03974080449cf156438c9fe6c346901f3';priorpath=B/'xl-terrain-recovery-20261011-parkview-block6-installed-scope-v1/declared-scope.json';prior=read(priorpath);aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);assert not prior['metadataLeafJsonPointers'];archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set();paths=set();queue=[];hashes={};versions={};cached={};unknown=[];audit={};seen=set()
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
 # Every actual Block17 artifact is initial even if previously committed. Neither
 # predecessor audit inventory nor unrelated previously committed lineage is initial.
 for d in B.glob('*parkview-block17*'):
  if d.is_dir()and 'source-scope'not in d.name and 'stage'not in d.name and 'installed'not in d.name:
   for p in d.rglob('*'):
    if p.is_file():initial_add(p)
 for patterns in ['*parkview_block17*','*parkview-block17*','complete_original_lower_opening_mounts*.py','test_complete_original_lower_opening_mounts*.py','test_exact_original_segment_surface_contact_band*.py']:
  for p in HERE.glob(patterns):
   if p.is_file():initial_add(p)
 for d in (HERE/'local').glob('*parkview-block17*'):
  if d.is_dir()and 'stage'not in d.name:
   for p in d.rglob('*'):
    if p.is_file():initial_add(p)
 for p in [Path(__file__),HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs',HERE/'candidate_native_support_witness_v1_20261010.mjs',HERE.parent/'landmark-preflight/browser-runtime.mjs']:initial_add(p)
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
 current=role['currentManifest'];assert ref(ROOT/current['path'])==current;assert not any('block17'in p for p in leaves)
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),trackedCacheContract='Root contract: exact referenced tracked file hash verified; recurse only if explicitly initial. Full new Block17 source/numerical/current artifacts are explicitly initial even tracked.',historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=[],auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),auditDeclarationsNotCandidateNumericInputs=True,unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,currentManifest=current,newMetadataLeaves=False,newHistoricalAliases=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0,fullNumericalSourceClosureRequired=True,newBlock17StageOutputsAndLiveWritesExcluded=True,explicitInitialPaths=sorted(initial),elapsedSeconds=time.monotonic()-start,qualification='Full Block17 raw failures/four streams/whole source and ground/body/contact/eligible face path/cap/v2-v3 opening kernels/tests/current identity/23foreign/six native/runtime inputs recurse. Reused committed Block11 data/kernels/proof inputs use the root existing exact tracked-input contract and receive no new whole-native approval. Prior Block6 declared/closed audit inventories are hash-bound separately, never source proofs. Inherited exact aliases/metadata contracts unchanged; root independent verification and stage/live guards remain mandatory.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),exactTrackedDependencies=len(cached),versions=len(versions),elapsedSeconds=out['elapsedSeconds'],unboundCount=len(unknown),firstUnbound=unknown[:5])),flush=True)
if __name__=='__main__':main()
