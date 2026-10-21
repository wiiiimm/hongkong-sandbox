"""Exact provider/form/source identity evidence for four Parkview originals; no approval."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-four-identity-evidence-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
def take(name,file):
 _,ps=authenticate(BASE/name);p=BASE/name/file;assert digest(p.read_bytes())==ps[str(p.relative_to(ROOT))];refs.extend([BASE/name/'result.json',p]);pins.update(ps);return read(p)
selection=take('government-xl-parkview-12-15-shared-runtime-v1-20261021','selection.json.gz');contexts={}
for n in ['government-xl-parkview-13-14-primary-context-v1-20261021','government-xl-parkview-12-15-primary-context-v1-20261021']:
 for r in take(n,'context.json.gz')['rows']:assert r['uid']not in contexts;contexts[r['uid']]=r
mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==selection['manifestSHA256'];manifest=read(mp);refs.append(mp);entries=[r for r in selection['rows']if r['uid']in contexts];assert len(entries)==4
wanted={r['candidate']['entry']['buildingCSUID']for r in entries};census={u:[]for u in wanted}
for tile in manifest['tiles']:
 p=ROOT/'3d-viewer'/tile['url'];refs.append(p)
 for b in read(p)['buildings']:
  if b.get('buildingCSUID')in wanted:census[b['buildingCSUID']].append(b)
rows=[];projections={};footprints={}
for r in entries:
 uid=r['uid'];e=r['candidate']['entry'];b=r['source']['building'];ctx=contexts[uid];assert ctx['sourceSHA256']==r['sourceSHA256'];assert census[e['buildingCSUID']]==[b]
 f=ctx['provider']['features'];assert len(f)==1;a=f[0]['attributes'];assert a['Status']=='Active'and a['BuildingCSUID']==e['buildingCSUID']==b['buildingCSUID'];assert a['BuildingID']==b['buildingId'];assert a['GeoRefNo']==e['modelId'][1:11]==e['buildingCSUID'][:10];assert a['BaseHeight']==b['baseHeightHKPD']and a['TopHeight']==b['topHeightHKPD'];assert e['rootTranslation']==[-834500,0,816500]
 p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());assert len(tri)==r['triangles'];polys=shapely.polygons(tri[:,:,[0,2]]);proj=shapely.union_all(polys[shapely.area(polys)>1e-10]);shape=shapely.GeometryCollection()
 assert ctx['provider']['spatialReference']['latestWkid']==2326
 for ring in f[0]['geometry']['rings']:shape=shape.symmetric_difference(shapely.Polygon([(x-834500,816500-y)for x,y in ring]))
 assert shape.is_valid;projections[uid]=proj;footprints[uid]=shape
 rows.append(dict(uid=uid,modelId=e['modelId'],sourceSHA256=r['sourceSHA256'],csuid=e['buildingCSUID'],buildingId=b['buildingId'],uniqueCurrentForm=True,providerObjectId=a['OBJECTID'],storedObjectId=b['objectId'],name=a['BuildingNameEN'],occupationPermits=sorted({f['attributes']['OPNo']for f in ctx['opStructures']['features']if f['attributes'].get('OPNo')}),footprintCoverage=proj.intersection(shape).area/shape.area,sourceInsideFootprint=proj.intersection(shape).area/proj.area,sourceBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],officialWKT=shape.wkt,sourceWKT=proj.wkt))
allSource=shapely.union_all(list(projections.values()));allOfficial=shapely.union_all(list(footprints.values()));summary=dict(uids=sorted(contexts),combinedFootprintCoverage=allSource.intersection(allOfficial).area/allOfficial.area,combinedSourceInsideOfficial=allSource.intersection(allOfficial).area/allSource.area,sourcePairOverlaps=[dict(a=a,b=b,areaM2=projections[a].intersection(projections[b]).area)for a in sorted(projections)for b in sorted(projections)if a<b],identityApproved=False,installationApproved=False)
save(DOC/'evidence.json.gz',dict(rows=rows,**summary));save(DOC/'summary.json',summary)
assert digest(mp.read_bytes())==selection['manifestSHA256']
module('parkview_four_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-original-provider-current-form-identity-evidence',refs,summary);print(summary,flush=True)
