"""Recover exact official component polygons for the two complete market halls.

Original request/context already recorded on 2026-10-08. Refuses to overwrite.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'source-scripts/city/government-import'))
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
from shapely.geometry import Polygon
sys.path.insert(0,str(HERE.parent/'mui-wo-buildings'))
from build import official_geometry,polys
source=ROOT/'docs/astra-city/government-import/government-xl-six-source-identity-review-20261008/review.json'
rows=[r for r in read(source)['rows'] if r['candidateForOfficialGroupVerification']]
forms={b['uid']:b for r in rows for b in r['groupForms']}
doc=ROOT/'docs/astra-city/government-import/government-xl-market-official-group-context-20261008'
assert not doc.exists()
ids=sorted({b['buildingCSUID'] for b in forms.values()})
raw,receipt=request(BASE+'/0/query',{'f':'json','where':'BuildingCSUID IN ('+','.join("'"+code+"'" for code in ids)+')','outFields':'*','returnGeometry':'true','outSR':'2326','returnTrueCurves':'false'})
payload=json.loads(raw);assert not payload.get('exceededTransferLimit')
save(doc/'official.json.gz',payload);save(doc/'request.json',receipt)
byid={f['attributes']['BuildingCSUID']:f for f in payload['features']};assert len(byid)==len(payload['features'])
manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
installed={m['uid']:m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
results=[]
for uid,b in forms.items():
 f=byid.get(b['buildingCSUID']); item={'uid':uid,'csuid':b['buildingCSUID'],'officialFound':bool(f),'alreadyInRuntimeCatalogue':uid in installed}
 if f:
  geom,repaired=official_geometry(f);ps=list(polys(geom));p=Polygon(b['rings'][0],b['rings'][1:]);matches=[v for v in ps if v.intersection(p).area>0]
  item.update(officialAttributes=f['attributes'],uniquePolygon=len(matches)==1)
  if len(matches)==1:item.update(hausdorffDistanceM=p.hausdorff_distance(matches[0]),officialRings=[list(map(list,v.coords)) for v in [matches[0].exterior,*matches[0].interiors]])
 results.append(item)
save(doc/'context.json',{'rows':results,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'reviewSHA256':digest(source.read_bytes()),'publication':False})
print(json.dumps(results,ensure_ascii=False))
