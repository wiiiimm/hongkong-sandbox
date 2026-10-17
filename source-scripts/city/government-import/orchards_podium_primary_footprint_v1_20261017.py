"""Compare exact original podium projection with its current authoritative GIS record."""
from pathlib import Path
import requests,numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-orchards-podium-current-checks-v1-20261017';BATCH='government-xl-orchards-podium-primary-footprint-v1-20261017';DOC=BASE/BATCH
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 row=read(PRIOR/'selection.json.gz')['rows'][0];b=row['source']['building'];params=dict(f='json',where="BuildingCSUID='"+b['buildingCSUID']+"'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000')
 response=requests.get(URL,params=params,timeout=60);response.raise_for_status();data=response.json();assert not data.get('error')and not data.get('exceededTransferLimit')and len(data['features'])==1
 feature=data['features'][0];a=feature['attributes'];assert a['BuildingCSUID']==b['buildingCSUID']and a['BuildingID']==b['buildingId']and a['BuildingBlockType']==b['structureType'];assert data['spatialReference'].get('latestWkid',data['spatialReference'].get('wkid'))==2326
 DOC.mkdir();(DOC/'provider.json').write_bytes(response.content);save(DOC/'request.json',dict(url=URL,method='GET',parameters=params,status=response.status_code,sha256=digest(response.content)))
 rings=[[(x-834500,816500-y)for x,y in ring]for ring in feature['geometry']['rings']];primary=Polygon(rings[0],rings[1:]);current=Polygon(b['rings'][0],b['rings'][1:]);assert primary.is_valid and current.is_valid
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));summary=dict(uid=b['uid'],providerObjectId=a['OBJECTID'],viewerObjectId=b['objectId'],primaryAreaM2=primary.area,currentAreaM2=current.area,primaryCurrentSymmetricDifferenceM2=primary.symmetric_difference(current).area,originalProjectionCoveragePrimary=projection.intersection(primary).area/primary.area,originalProjectionCoverageCurrent=projection.intersection(current).area/current.area,fullAcceptance=False)
 save(DOC/'comparison.json',summary)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',ROOT/row['candidate']['path'],HERE/'exact_packed_world_geometry_20261009.py']
 out=module('orchards_primary_footprint_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-original-podium-authoritative-current-footprint-comparison-v1',refs,dict(uids=[b['uid']],summary=summary,fullAcceptance=False,nextStep='Use primary footprint comparison to choose exact source identity reconciliation; do not relax coverage or modify runtime from this diagnostic.'));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
