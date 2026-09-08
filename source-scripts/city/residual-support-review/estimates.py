"""Recalculate only unsurveyed open-sided base estimates after the bounded terrain refinement."""
import json,pathlib,sys,hashlib,uuid
from shapely.geometry import Polygon
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import terrain_patches as t
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();uids={'landsd/109723:0','landsd/311673:0'};sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
receipt=pathlib.Path('/tmp/astra-residual-estimates-lease.json')
if receipt.exists():assert reservations.owns(read(receipt))
else:
 r=reservations.claim('residual-estimates-'+str(uuid.uuid4()),['building:'+u for u in sorted(uids)],batch='HKS-214-residual-estimated-bases');assert r['ok'],r;receipt.write_text(json.dumps(r['reservation'],default=str))
path=HERE/'terrain-patches/support-native-111608-0.json';patch=read(path);sampler=t.fine.DemSampler(patch,rendered=True);mf=read(ROOT/'3d-viewer/city/data/manifest.json');rows=[]
for tile in mf['tiles']:
 for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
  if b['uid']not in uids:continue
  assert b['baseHeightHKPD']is None and b['topHeightHKPD']is None and b['heightSource']=='estimated' and b['baseSource']=='terrain-estimated';extent=sampler.extrema(Polygon(b['rings'][0],b['rings'][1:]));assert extent['max']-extent['min']<b['height']-1.8
  rows.append({'uid':b['uid'],'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'baseSource':b['baseSource'],'previousBase':b['base'],'height':b['height'],'base':extent['min'],'terrain':extent,'sourceFieldsPreserved':{'baseHeightHKPD':None,'topHeightHKPD':None},'policy':'Unsurveyed 3m canopy retains its estimated height. Base uses the exact minimum of the source footprint intersected with final terrain triangles, preventing floating posts. This remains an explicit estimate, not a survey.'})
assert len(rows)==2;out={'issue':'HKS-214','parentSha256':patch['meta']['parentSha256'],'refinementSha256':sha(path),'terrainSource':str(path.relative_to(ROOT)),'buildings':rows,'published':False};(HERE/'estimated-bases.json').write_text(json.dumps(out,indent=2)+'\n');(DOC/'estimated-bases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
