"""Freeze staged terrain/model candidates and their complete neighbouring source scope."""
import json,sys,uuid
from pathlib import Path
import shapely
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import/government-200-20260911';DOC=BASE/'resolution';LOCAL=HERE/'local/government-198-resolution-20260911'
source=read(DOC/'selection.json.gz');resolution=read(DOC/'source-resolution.json');patches=resolution['patches'];ids={uid for p in patches for uid in p['uids']}
selected=[r for r in source['rows'] if r['uid'] in ids]
save(DOC/'terrain-candidates.json',[{'path':p['path'],'sha256':p['sha256']} for p in patches]);save(DOC/'candidate-selection.json.gz',{**source,'rows':selected})
cat=read(HERE/'local/government-200-20260911/candidates/catalogue.json');cat['models']=[r['candidate']['entry'] for r in selected];cat['counts']['packedModels']=len(selected)
for r in selected:
    e=r['candidate']['entry'];raw=(HERE/'local/government-200-20260911/candidates'/e['asset']).read_bytes();assert digest(raw)==e['sha256'];p=LOCAL/'candidates'/e['asset'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
save(LOCAL/'candidates/catalogue.json',cat);save(LOCAL/'candidates/catalogue-index.json',{'models':len(selected),'catalogues':['catalogue.json']});save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in selected})
manifest=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
tree=shapely.STRtree([box(*p['bounds']) for p in patches]);neighbours=[];hashes={}
for tile in manifest['tiles']:
    path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
    for b in json.loads(raw)['buildings']:
        rings=b['rings'];poly=Polygon(rings[0],rings[1:])
        hits=tree.query(poly,predicate='intersects')
        if not len(hits):continue
        neighbours.append({'building':b,'patchIndexes':[int(i) for i in hits],'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))});touched=True
    if touched:hashes[str(path.relative_to(ROOT))]=digest(raw)
save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'patches':patches,'candidateIds':sorted(ids)})
resources={'building:'+r['uid'] for r in source['rows']}|{('building:' if r['building']['uid'].startswith('landsd/') else 'source-form:')+r['building']['uid'] for r in neighbours};assert len(resources)<=1000
assert not (LOCAL/'reservation.json').exists(),'Reservation receipt already exists; resume its owned work'
claim=reservations.claim('codex-government-resolution-'+str(uuid.uuid4()),sorted(resources),ttl=3600,batch='government-198-resolution-20260911');assert claim['ok'],'Source/terrain neighbour ownership conflict'
save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
print(json.dumps({'stagedModels':len(selected),'patches':len(patches),'neighbourForms':len(neighbours),'reservedResources':len(resources)}))
