"""Bind official original community component and measure full composite spatial limits."""
from pathlib import Path
import requests,numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-community-primary-scope-v1-20261017';DOC=BASE/BATCH
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists();refs=[Path(__file__)];rows=[];proofs={};pins={}
 for name in ['government-xl-orchards-podium-current-checks-v1-20261017','government-xl-orchards-community-current-checks-v1-20261017']:
  d=BASE/name;receipt=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for e in receipt['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  rows.extend(read(d/'selection.json.gz')['rows']);proofs.update({r['uid']:r for r in read(d/'identity-proofs.json')['rows']});refs.extend([d/'result.json',d/'identity-proofs.json',d/'selection.json.gz'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 DOC.mkdir();records=[];meshes=[];targets=[];projections=[]
 for r in rows:
  b=r['source']['building'];params=dict(f='json',where="BuildingCSUID='"+b['buildingCSUID']+"'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000');response=requests.get(URL,params=params,timeout=60);response.raise_for_status();data=response.json();assert not data.get('error')and not data.get('exceededTransferLimit')and len(data['features'])==1
  assert data['spatialReference'].get('latestWkid',data['spatialReference'].get('wkid'))==2326
  feature=data['features'][0];a=feature['attributes'];assert a['BuildingCSUID']==b['buildingCSUID']and a['BuildingID']==b['buildingId']and a['BuildingBlockType']==b['structureType']
  name=b['uid'].split('/')[1];(DOC/(name+'-provider.json')).write_bytes(response.content);save(DOC/(name+'-request.json'),dict(url=URL,parameters=params,status=response.status_code,sha256=digest(response.content)))
  rings=[[(x-834500,816500-y)for x,y in ring]for ring in feature['geometry']['rings']];official=Polygon(rings[0],rings[1:]);target=Polygon(b['rings'][0],b['rings'][1:]);assert official.is_valid and target.is_valid;assert official.hausdorff_distance(target)<.002
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];tri=decode_original_world_triangles(raw);assert digest(tri.astype('<f8').tobytes())==proofs[b['uid']]['worldTrianglesSHA256'];meshes.append(tri);targets.append(target);projections.append(shapely.union_all(shapely.polygons(tri[:,:,[0,2]])));refs.append(ROOT/r['candidate']['path']);records.append(dict(uid=b['uid'],officialAttributes=a,currentForm=b,primarySymmetricDifferenceM2=official.symmetric_difference(target).area,primaryHausdorffDistanceM=official.hausdorff_distance(target)))
 alltri=np.concatenate(meshes);lo,hi=alltri.min((0,1)),alltri.max((0,1));final=module('orchards_composite_scope_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);source=shapely.union_all(projections);target=shapely.union_all(targets);uids={r['uid']for r in rows};parents={r['source']['building'].get('parent')for r in rows};others=shapely.union_all([g for b,g,t in forms if b['uid']not in uids and b.get('parent')not in parents]);excess=source.difference(target)
 measures=dict(targetCoveredBySourceProjection=source.intersection(target).area/target.area,sourceExcessMaximumDistanceFromTargetM=float(shapely.distance(shapely.points(alltri[:,:,[0,2]].reshape(-1,2)),target).max()),sourceExcessCoveredByUnrelatedFormsM2=excess.intersection(others).area,podiumCoverageExcludingCommunityFootprint=projections[0].intersection(targets[0].difference(targets[1])).area/targets[0].difference(targets[1]).area)
 refs.extend(ROOT/'3d-viewer'/t for b,g,t in forms);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']);save(DOC/'scope.json',dict(records=records,rawIndividualIdentity=proofs,measures=measures,identityApproved=False,qualification='Different map parents retained explicitly. Official records and actual source coverage support component attribution research, not a waiver of strict support, placement or runtime gates.'))
 out=module('orchards_community_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-community-podium-primary-spatial-scope-v1',list(set(refs)),dict(uids=sorted(uids),measures=measures,fullAcceptance=False));print(dict(jobId=out['jobId'],measures=measures),flush=True)
if __name__=='__main__':main()
