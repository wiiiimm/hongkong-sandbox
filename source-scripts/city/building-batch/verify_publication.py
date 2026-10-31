"""Verify the trial publication against the recorded baseline, including retained fallbacks."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/astra-city/building-batch/visual-trial'
def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
pub=read(DOC/'publication.json');assert pub['published']
for name,expected in pub['after'].items():assert sha(ROOT/name)==expected,name
baseline=json.loads(subprocess.check_output(['git','show',pub['beforeCommit']+':3d-viewer/city/data/manifest.json'],cwd=ROOT))
manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert manifest['counts']==baseline['counts'];assert manifest['tiles']==baseline['tiles'];assert manifest['terrainPatches']==baseline['terrainPatches']
assert manifest['officialModelCatalogues'][:len(baseline['officialModelCatalogues'])]==baseline['officialModelCatalogues']
changed=subprocess.check_output(['git','diff','--name-only',pub['beforeCommit'],'--','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines()
assert all(p=='3d-viewer/city/data/manifest.json' or p.startswith('3d-viewer/city/data/official-models/tourist-trial-') for p in changed),'Unrelated terrain/source data changed'
new={};seen=set()
for url in manifest['officialModelCatalogues']:
 c=read(ROOT/'3d-viewer'/url);assert len(c['models'])==c['counts']['packedModels']
 for model in c['models']:
  assert model['uid'] not in seen;seen.add(model['uid'])
  if '/tourist-trial-' in url:
   path=ROOT/'3d-viewer'/pathlib.Path(url).parent/model['asset'];assert sha(path)==model['sha256'];assert path.stat().st_size==model['bytes'];new[model['uid']]=model
work=ROOT/'source-scripts/city/building-batch/local/publication'
held={m['uid'] for m in read(work/'held.json')};assert not held.intersection(new)
found=set();embedded=0;forms=0
for tile in manifest['tiles']:
 for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
  forms+=1;embedded+=bool(b.get('modelGeometry'))
  if b['uid'] in new:
   m=new[b['uid']];assert not b.get('modelGeometry');assert b['objectId']==m['objectId'];assert b['buildingCSUID']==m['buildingCSUID'];assert b.get('baseHeightHKPD')==m['recordedBaseHeight'];assert b.get('topHeightHKPD')==m['recordedTopHeight'];found.add(b['uid'])
  if b['uid'] in held:assert not b.get('modelGeometry') and b['uid'] not in seen,'Held fallback replaced'
assert found==set(new);assert forms==manifest['counts']['buildings'];assert len(new)==read(work/'screening.json')['accepted']
r=dict(passed=True,newModels=len(new),heldFallbacks=len(held),forms=forms,progressiveModels=len(seen),embeddedModels=embedded,totalDetailedModels=embedded+len(seen),newCompressedBytes=sum(m['bytes'] for m in new.values()),terrainAndSourceTilesUnchanged=True,sourceIdentitiesAndElevationsPreserved=True,duplicateFree=True)
(DOC/'publication-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
