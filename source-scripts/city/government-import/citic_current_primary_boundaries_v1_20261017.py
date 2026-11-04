"""Retrieve current official identity/boundary evidence; no acceptance or geometry edits."""
from pathlib import Path
import requests,uuid
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-current-primary-boundaries-v1-20261017';DOC=BASE/BATCH
UIDS=['landsd/232579:0','landsd/278303:0','landsd/123871:0','landsd/234783:0','landsd/256427:0']
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());forms=[];refs=[Path(__file__),manifest]
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];found=[b for b in read(p)['buildings'] if b['uid'] in UIDS]
  if found:forms.extend(found);refs.append(p)
 assert len(forms)==len(UIDS);ids=sorted(b['buildingCSUID'] for b in forms)
 params=dict(f='json',where='BuildingCSUID IN ('+','.join("'"+x+"'" for x in ids)+')',outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
 claim=reservations.claim('citic-primary-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  response=requests.get(URL,params=params,timeout=60);response.raise_for_status();raw=response.content;data=response.json();assert not data.get('error') and not data.get('exceededTransferLimit');assert len(data['features'])==len(ids);assert sorted(f['attributes']['BuildingCSUID'] for f in data['features'])==ids
  assert digest(manifest.read_bytes())==msha;DOC.mkdir();(DOC/'provider-response.json').write_bytes(raw)
  save(DOC/'request.json',dict(method='GET',url=URL,parameters=params,decodedSHA256=digest(raw),responseStatus=response.status_code,contentType=response.headers.get('Content-Type')));save(DOC/'current-forms.json',dict(manifestSHA256=msha,forms=forms,tileHashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs[2:]}))
  rows=[]
  for b in forms:
   f=next(x for x in data['features'] if x['attributes']['BuildingCSUID']==b['buildingCSUID']);a=f['attributes']
   rows.append(dict(uid=b['uid'],buildingCSUID=b['buildingCSUID'],viewerObjectId=b['objectId'],providerObjectId=a.get('OBJECTID'),viewerBuildingId=b.get('buildingId'),providerBuildingId=a.get('BuildingID'),providerType=a.get('BuildingBlockType'),providerStatus=a.get('Status')))
  save(DOC/'summary.json',dict(rows=rows,installationApproved=False))
  result=module('citic_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'citic-five-current-primary-boundary-records-v1',refs,dict(uids=UIDS,rows=rows,newlyInstalled=0,installationApproved=False));print(dict(jobId=result['jobId'],rows=rows),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
