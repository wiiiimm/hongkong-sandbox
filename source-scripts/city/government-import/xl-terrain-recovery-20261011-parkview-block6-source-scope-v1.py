"""Explicit recursive Block6 numerical/source scope; inherit only exact aliases."""
import ast,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';DOC=B/'xl-terrain-recovery-20261011-parkview-block6-source-scope-v1';P=B/'government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();priorpath=B/'xl-terrain-recovery-20261011-parkview-block11-installed-scope-v1/declared-scope.json';prior=read(priorpath);aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];assert not pointers;assert not any('block6'in p for p in leaves);archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};paths=set();queue=[];versions=[];unknown=[];hash_cache={}
 def hashed(p):
  p=Path(p)
  if p not in hash_cache:hash_cache[p]=digest(p.read_bytes())if p.is_file()else None
  return hash_cache[p]
 def add(p):
  p=Path(p);assert p.is_file(),str(p);rel=str(p.relative_to(ROOT))
  if rel not in paths:paths.add(rel);queue.append(p)
 def bind(path,h,origin):
  p=Path(path)if Path(path).is_absolute()else ROOT/path
  if not p.exists()and path.startswith('city/'):p=ROOT/'3d-viewer'/path
  rel=str(p.relative_to(ROOT));actual=hashed(p)
  if actual!=h:
   p=archive.get((rel,h))
   if p is None:unknown.append(dict(path=rel,sha256=h,origin=origin));return
  assert hashed(p)==h;versions.append(dict(path=rel,sha256=h));add(p)
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
 typed=B/'xl-terrain-recovery-20261011-parkview-block6-current-role-v1'
 assert read(typed/'typed-role.json.gz')['currentTypedPhysicalAccepted']and (typed/'result.json').is_file()
 add(priorpath);add(Path(__file__))
 for d in B.glob('*parkview-block6*'):
  if d.is_dir()and d!=DOC and 'stage'not in d.name and 'installed'not in d.name:
   for p in d.rglob('*'):
    if p.is_file():add(p)
 for p in HERE.glob('*parkview_block6*'):
  if p.is_file():add(p)
 for p in HERE.glob('*parkview-block6*'):
  if p.is_file():add(p)
 for d in (HERE/'local').glob('*parkview-block6*'):
  if d.is_dir()and 'stage'not in d.name:
   for p in d.rglob('*'):
    if p.is_file():add(p)
 # Exact mounted-opening body/kernel adverse tests remain numerical dependencies.
 for stem in ['complete_original_lower_opening_mounts','test_complete_original_lower_opening_mounts','test_exact_original_segment_surface_contact_band']:
  for p in HERE.glob(stem+'*.py'):add(p)
 for p in [HERE/'xl-terrain-recovery-20261011-parkview-block11-authentic-current-stage-v1.py',HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs',B/'government-xl-parkview-block11-unchanged-installed-v1-20261011/result.json']:add(p)
 seen=set()
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaves:continue
  if p.name.endswith('.json')or p.name.endswith('.json.gz'):refs(read(p),rel)
  if p.suffix=='.py':
   for n in ast.walk(ast.parse(p.read_text())):
    modules=([n.module]if isinstance(n,ast.ImportFrom)and n.module else[a.name for a in n.names]if isinstance(n,ast.Import)else[])
    for m in modules:
     q=HERE/(m.split('.')[0]+'.py')
     if q.exists():add(q)
 current=read(P/'current-raw-outcome.json')['currentManifest'];assert ref(ROOT/current['path'])==current
 save(DOC/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted({(r['path'],r['sha256']):r for r in versions}.values(),key=lambda x:(x['path'],x['sha256'])),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,currentManifest=current,inheritedScope=ref(priorpath),newMetadataLeaves=False,newHistoricalAliases=False,fullNumericalSourceClosureRequired=True,newBlock6StageOutputsAndLiveWritesExcluded=True,draftStageScriptIncluded=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,qualification='Complete Block6 immutable raw failures/whole-source graph/finite/current literal and explicit F32 arrays/actual drawn ground/cap/eligible-face path/opening v2-v3 guards and adverse tests plus all current identity, native, source and runtime modules. Existing exact aliases and metadata boundaries inherited unchanged from reviewed Block11 installed scope. No Block6 numerical/current/role data is a metadata leaf. Root independent closure remains mandatory.'))
 print(json.dumps(dict(paths=len(paths),versions=len(versions),unbound=unknown[:12],unboundCount=len(unknown),stageNotExecuted=True)),flush=True)
if __name__=='__main__':main()
