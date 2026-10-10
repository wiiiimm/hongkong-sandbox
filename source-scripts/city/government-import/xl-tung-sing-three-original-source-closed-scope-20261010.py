"""Immutable closed source/numeric Tung Sing scope; stage/live kept separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-tung-sing-three-original-source-closed-scope-20261010';DOC=BASE/BATCH;ROLE=BASE/'government-xl-tung-sing-three-original-current-complete-typed-role-v5-20261010'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();r=read(ROLE/'result.json');typed=read(ROLE/'typed-role.json.gz');assert typed['currentTypedPhysicalAccepted'] and typed['reasons']==[]
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 paths={ROOT/x['path'] for x in r['evidenceRefs']};paths.add(Path(__file__))
 for d in BASE.iterdir():
  if ('tung-sing' in d.name or 'lei-tung' in d.name) and '20261010' in d.name and not any(x in d.name for x in ['typed-stage','installed','source-closed-scope']):paths.update(p for p in d.rglob('*') if p.is_file())
 for p in HERE.iterdir():
  if p.is_file() and any(x in p.name for x in ['tung-sing','tung_sing','lei-tung','lei_tung']) and '20261010' in p.name and not any(x in p.name for x in ['typed-stage','live-install','source-closed-scope']):paths.add(p)
 for folder in ['government-xl-tung-sing-three-original-current-anchor-v2-20261010','government-xl-tung-sing-three-original-current-tower-footing-v2-20261010']:
  paths.update(p for p in (BASE/folder).rglob('*') if p.is_file())
 prior=read(BASE/'xl-terrain-recovery-20261010-festival-source-closed-scope-v1/closed-scope.json');aliases=list(prior['historicalManifestAliases']);leaf=set(prior['metadataLeafPaths']);current=ROOT/'3d-viewer/city/data/manifest.json';raw=current.read_bytes();assert digest(raw)==typed['currentManifest']['sha256'];DOC.mkdir();archive=DOC/'acceptance-manifest.json';archive.write_bytes(raw);paths.add(archive);aliases.append({'originalPath':'3d-viewer/city/data/manifest.json','sha256':digest(raw),'archive':ref(archive)});manifest=read(archive);leaf.add(str(archive.relative_to(ROOT)));leaf.update('3d-viewer/'+u for u in manifest['officialModelCatalogues']);leaf.update('3d-viewer/'+x['url'] for x in manifest['terrainPatches'])
 names=sorted(str(p.relative_to(ROOT)) for p in paths);save(DOC/'closed-scope.json',{'closedPaths':names,'closedExplicitPaths':names,'presentFileBindings':[ref(ROOT/p) for p in names],'historicalManifestAliases':aliases,'metadataLeafPaths':sorted(leaf),'metadataLeafJsonPointers':prior.get('metadataLeafJsonPointers',[]),'currentRoleNeon':r['jobId'],'sourceGeometryChanges':0,'terrainProposalGeometryChanged':True,'stageAndLiveExcluded':True,'qualification':'Complete12751 original and literal-rendered facets,387 source components,385 rooted ordinary parts and two bounded visual sleeves. Both source and independent literal-rendered P0/T361 strict footings,37 certified source/actual wall paths, all33 current foreign basics,4 retained natives and6614 catalogue complete bounds preserve independent physical checks. The original building geometry/poses/attributes are unchanged; the flat92211-facet terrain proposal intentionally changes authenticated terrain/transition/residual, includes14 source-disjoint literal parent facets, and remains below100k. Raw failed attempts retained. No browser/publication/installed credit.'});print({'paths':len(names),'currentRoleNeon':r['jobId']},flush=True)
if __name__=='__main__':main()
