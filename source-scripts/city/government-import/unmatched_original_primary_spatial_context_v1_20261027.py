"""Fresh official metadata around exact unmatched original XL source keys.

Spatial candidates are investigation context, never identity or skip approval.
"""
import argparse,gzip,json,sys
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','inventory']:p.add_argument('--'+k,required=True)
 p.add_argument('--source-key',action='append',required=True);a=p.parse_args()
 assert a.batch.startswith('government-xl-')and'/'not in a.batch and len(a.source_key)==len(set(a.source_key))<=8
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
 _,pins=authenticate(base/a.inventory);ip=base/a.inventory/'summary.json';assert digest(ip.read_bytes())==pins[str(ip.relative_to(ROOT))]
 rows=[r for r in read(ip)['rows']if r['sourceKey']in a.source_key];assert {r['sourceKey']for r in rows}==set(a.source_key)and all(r.get('uid')is None and not r['currentInstalled']for r in rows)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))]
 refs=[Path(__file__),base/a.inventory/'result.json',ip,manifest,HERE.parent/'landsd-territory/source.py'];results=[];out.mkdir()
 def query(name,parameters):
  raw,receipt=request(URL,dict(f='json',outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID',**parameters),json_expected=False)
  decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
  path=out/(name+'.json');path.write_bytes(decoded);refs.append(path);rp=out/(name+'-request.json');save(rp,dict(**receipt,decodedSHA256=digest(decoded)));refs.append(rp)
  data=read(path);assert not data.get('error')and not data.get('exceededTransferLimit');return data['features']
 for row in rows:
  key,model_id=row['sourceKey'].split('/');assert model_id[1:11].isdigit()
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT 1 FROM astra_modelling.native_stage_members WHERE run_id=%s AND cache_key=%s',(NATIVE_RUN,key)).fetchone()
   result_sha,model=db.execute("SELECT r.result_sha,m FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m WHERE r.cache_key=%s AND m->>'modelId'=%s",(key,model_id)).fetchone()
  assert result_sha==row['nativeResultSHA256']and model['asset']['sha256']==row['indexedSourceSHA256']
  assert model['state']=='source-match-held'and not model['matching']['viewerMatches']and not model['matching']['officialMatches']
  source_path=out/(model_id+'-native-record.json');save(source_path,dict(cacheKey=key,resultSHA256=result_sha,model=model));refs.append(source_path)
  geo=model_id[1:11];exact=query(model_id+'-exact-georef',dict(where="GeoRefNo='"+geo+"'"))
  low,high=model['worldBounds'];envelope=dict(xmin=low[0]+834500-5,xmax=high[0]+834500+5,ymin=816500-high[2]-5,ymax=816500-low[2]+5,spatialReference=dict(wkid=2326))
  spatial=query(model_id+'-spatial',dict(where='1=1',geometry=json.dumps(envelope),geometryType='esriGeometryEnvelope',inSR='2326',spatialRel='esriSpatialRelIntersects'))
  point=shapely.Point(800000+int(geo[:5]),800000+int(geo[5:]));box=shapely.box(low[0]+834500,816500-high[2],high[0]+834500,816500-low[2]);candidates=[]
  for feature in spatial:
   attributes=feature['attributes'];shape=shapely.GeometryCollection();valid=True
   try:
    for ring in feature['geometry']['rings']:shape=shape.symmetric_difference(shapely.Polygon(ring))
    valid=shape.is_valid
   except shapely.errors.GEOSException:valid=False
   candidates.append(dict(attributes=attributes,primaryGeometryValid=valid,containsNominalSourceGeoRefPoint=bool(shape.covers(point))if valid else None,sourceBoundingBoxOverlapM2=float(shape.intersection(box).area)if valid else None,identityAccepted=False))
  results.append(dict(sourceKey=row['sourceKey'],uid=None,modelId=model_id,sourceSHA256=row['indexedSourceSHA256'],worldBounds=model['worldBounds'],exactGeoRefRecords=len(exact),exactActiveGeoRefRecords=sum(f['attributes'].get('Status')=='Active'for f in exact),spatialRecords=len(spatial),spatialCandidates=candidates,candidateIdentityAccepted=False,installationApproved=False,permanentRejection=False))
  print(dict(modelId=model_id,exactRecords=len(exact),spatialRecords=len(spatial),nominalPointCandidates=sum(c['containsNominalSourceGeoRefPoint']is True for c in candidates)),flush=True)
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 result=dict(uids=[],sourceKeys=a.source_key,rows=results,fixedUnmatchedSourceKeysRetained=True,sourceGeometryChanges=0,candidateIdentityAccepted=False,installationApproved=False,publication=False,permanentRejection=False,qualification='Exact pinned native records and fixed unmatched source keys retained. Fresh official exact-GeoRef and whole original-bounds+5m envelope queries are complete. Bounding-box overlap and nominal-point membership are routing context only; no automatic reassignment, corruption finding, historical/current equivalence, skip credit or installation approval.')
 save(out/'summary.json',result);module('unmatched_primary_spatial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-unmatched-original-primary-spatial-investigation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
