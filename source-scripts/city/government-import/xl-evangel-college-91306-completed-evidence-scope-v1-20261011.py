"""Completed-only Evangel evidence declaration; no candidate acceptance.
Exact Elements root-verified aliases/metadata contracts are inherited unchanged.
Every new source/current numerical record remains recursively bound.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-elements-installed-root-closure-v1-20261011/root-closed-scope.json';DOC=B/'government-xl-evangel-college-91306-completed-evidence-scope-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['independentlyVerified']and prior['installedVerified'];aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set();paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
 inherited=prior['inheritedMetadataScope'];assert ref(ROOT/inherited['path'])==inherited;audit[inherited['path']]=inherited
 def hashed(p):
  if p not in hashes:hashes[p]=digest(p.read_bytes())if p.is_file()else None
  return hashes[p]
 def is_audit(p):return p.name in ['declared-scope.json','closed-scope.json','root-closed-scope.json']
 def add(p):
  p=Path(p);rel=str(p.relative_to(ROOT));assert p.is_file(),rel
  if is_audit(p):audit[rel]=ref(p);return
  if rel in tracked and rel not in initial:cached[rel]=ref(p);return
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
  if boundary:assert hashed(ROOT/origin)==boundary['documentSHA256']and digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())==boundary['boundary']['canonicalSHA256'];return
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:bind(v['path'],v['sha256'],origin)
   for k,x in v.items():
    if k in ['inputHashes','hashes','neighbourTileHashes','currentTileHashes','nativeCatalogueInputHashes','sourceInputHashes']and isinstance(x,dict):
     for p,h in x.items():
      if isinstance(p,str)and isinstance(h,str)and len(h)==64:bind(p,h,origin)
    else:refs(x,origin,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
  elif isinstance(v,list):
   for i,x in enumerate(v):refs(x,origin,pointer+'/'+str(i))
 folders=['government-xl-evangel-college-91306-authentic-four-body-grade-paths-v1-20261011', 'government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011', 'government-xl-evangel-college-91306-authentic-tin-complete-source-comparison-v2-20261011', 'government-xl-evangel-college-91306-authentic-tin-current-physical-v2-20261011', 'government-xl-evangel-college-91306-authentic-tin-source-context-v1-20261011', 'government-xl-evangel-college-91306-complete13960-current-finite-diagnostic-v1-20261011', 'government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011', 'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011', 'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011', 'government-xl-evangel-college-91306-current-original-identity-input-v1-20261011', 'government-xl-evangel-college-91306-current-wing-extension-identity-v1-20261011', 'government-xl-evangel-college-91306-observed-owner-packet-verification-v1-20261011', 'government-xl-evangel-college-91306-original-wing-extension-proposal-v1-20261011', 'government-xl-evangel-college-91306-post-elements-current-complete-identity-diagnostic-v2-20261011', 'government-xl-evangel-college-91306-post-elements-current-wing-extension-identity-v2-20261011', 'government-xl-evangel-college-91306-primary-relations-v1-20261011', 'government-xl-evangel-college-91306-unchanged-current-ordinary-physical-v1-20261011', 'government-xl-evangel-college-91306-untouched-original-recovery-v1-20261011', 'government-xl-complete-native-actual-position-evangel-post-elements-delta-v1-20261011']
 for folder in folders:
  r=read(B/folder/'result.json');assert not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-evangel-college-91306-authentic-tin-current-physical-v1-failure-archive-20261011','government-xl-evangel-college-91306-authentic-tin-current-physical-v1-20261011','government-xl-evangel-college-91306-official-campus-packet-v1-20261011','government-xl-evangel-college-91306-complete-source-extent-context-v1-20261011','government-xl-evangel-college-91306-western-original-patches-context-v1-20261011']:
  for component in [B/folder,HERE/'local'/folder]:
   if component.exists():
    for p in component.rglob('*'):
     if p.is_file()and p.name!='reservation.json':initial.add(str(p.relative_to(ROOT)))
 for n in ['xl-evangel-college-91306-authentic-tin-current-physical-v1-20261011.py','test_exact_cell_replay_with_original_routed_callable_20261011.py',Path(__file__).name]:initial.add(str((HERE/n).relative_to(ROOT)))
 # Source code and actual tests become explicit only when pinned by a completed receipt.
 for folder in folders:
  for r in read(B/folder/'result.json')['evidenceRefs']:
   p=ROOT/r['path']
   if p.is_file()and p.suffix in ['.py','.mjs','.js']:initial.add(str(p.relative_to(ROOT)))
 for rel in sorted(initial):add(ROOT/rel)
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaves:continue
  if p.name.endswith(('.json','.json.gz')):refs(read(p),rel)
  if p.suffix=='.py':
   for n in ast.walk(ast.parse(p.read_text())):
    names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[a.name for a in n.names]if isinstance(n,ast.Import)else[]
    for name in names:
     q=HERE/(name.split('.')[0]+'.py')
     if q.exists():add(q)
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges='Changed terrain diagnostic proposals preserved, never installed',newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,inheritedRootMetadataContract=ref(PRIOR),historicalManifestSourceArchivesRemainExact=True,explicitUIDs=['landsd/91306:0'],completedEvidenceBatches=folders,modelReviewWrites=0,newlyInstalled=0,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Completed Evangel evidence only: complete unchanged13960 source and named136 wing identity; genuine four-world226 body interfaces and33zero-area retained/uncredited; old/current/authentic fullfacet negatives, authentic source TIN and four-body107wall paths/617grade contacts; fresh post-Elements strict raw/typed identity, complete17actor input, physical-v2 raw downward/root/neighbour guards, v1 recursion failure and exact all6645 actual current native composition. No future retention candidate, current typed physical/stage/import acceptance. Exact Elements root-verified aliases/leaves/pointers inherited unchanged; every new source/current numerical record recursive.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
