"""Completed King Cheung identity and ground evidence declaration only.
Exact inherited Beverly v4 aliases/leaves/typed pointers are unchanged.
All new source/current numerical references recurse; no future pair acceptance.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-beverly-k-p-fresh70279-held-revisit-additive-scope-v4-20261011/declared-scope.json';DOC=B/'government-xl-king-cheung-completed-identity-ground-additive-scope-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
 audit[str((B/'government-xl-beverly-fresh-source-held-revisit-root-closure-v4-20261011/root-closed-scope.json').relative_to(ROOT))]=ref(B/'government-xl-beverly-fresh-source-held-revisit-root-closure-v4-20261011/root-closed-scope.json')
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
 folders=['government-xl-king-cheung-95691-authentic-tin-source-context-v1-20261011', 'government-xl-king-cheung-95691-canopy-complete-current-ground-diagnostic-v1-20261011', 'government-xl-king-cheung-95691-canopy-current-grade-cause-v1-20261011', 'government-xl-king-cheung-95691-complete-ancillary-proposal-v1-20261011', 'government-xl-king-cheung-95691-complete-low-parts-contacts-v1-20261011', 'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011', 'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011', 'government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011', 'government-xl-king-cheung-95691-current-original-identity-input-v1-20261011', 'government-xl-king-cheung-95691-current-original-identity-v1-20261011', 'government-xl-king-cheung-95691-dc-exact-site-plan-primary-packet-v1-20261011', 'government-xl-king-cheung-95691-ha-estate-loader-primary-packet-v1-20261011', 'government-xl-king-cheung-95691-ha-exact-owner-data-v1-20261011', 'government-xl-king-cheung-95691-ha-owner-bfa-plan-photo-packet-v1-20261011', 'government-xl-king-cheung-95691-ha-primary-packet-v1-20261011', 'government-xl-king-cheung-95691-primary-actual-pdf-source-context-exports-v2-20261011', 'government-xl-king-cheung-95691-primary-relations-v1-20261011', 'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011']
 expected=['government-xl-king-cheung-95691-canopy-current-grade-cause-v1-20261011','government-xl-king-cheung-95691-authentic-tin-source-context-v1-20261011','government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011']
 assert all(f in folders for f in expected)
 assert not any('authentic-versus-drawn' in f or 'canopy-post-role' in f or 'complete18742-current' in f for f in folders)
 for folder in folders:
  r=read(B/folder/'result.json');assert not r.get('physicalAccepted',False)and not r.get('installationApproved',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-king-cheung-95691-http-runtime-preflight-attempt-v1-20261011','government-xl-king-cheung-95691-identity-to-physical-handoff-v1-20261011']:
  base=B/folder;assert base.exists()
  for p in base.rglob('*'):
   if p.is_file():initial.add(str(p.relative_to(ROOT)))
 initial.add(str(Path(__file__).relative_to(ROOT)))
 # Source code and actual tests become explicit only when pinned by a completed receipt.
 for folder in folders:
  for r in read(B/folder/'result.json')['evidenceRefs']:
   p=ROOT/r['path']
   if p.is_file()and p.suffix in ['.py','.mjs','.js']:initial.add(str(p.relative_to(ROOT)))
 for rel in sorted(initial):add(ROOT/rel)
 for r in prior['referenceVersions']:bind(r['path'],r['sha256'],'exact inherited Beverly v4 referenceVersions')
 for r in prior['exactReferencedTrackedInputs']:bind(r['path'],r['sha256'],'exact inherited Beverly v4 tracked cache')
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
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,priorV3CurrentManifestHistoricalOnly=prior['priorV3CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/95691:0'],completedEvidenceBatches=folders,modelReviewWrites=0,newlyInstalled=0,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Completed King Cheung original18742 evidence only: stable named source, unique Housing Authority owner/photo architectural ancillary104 interpretation and full18638 ordinary identity extent, complete raw original two extent reasons retained; fresh all4world actual source/current ground, all104 raw finite/rim failures and exact grade/cap cause, authentic original3SW11B100731facets420relevant untouched context. No grounding/import/runtime acceptance, no building or terrain changes. Ongoing open-post and source-TIN comparison excluded. Exact inherited registry contracts unchanged, every new numeric/current reference recursive. Current capture becomes historical if live changes.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
