"""Follow the captured HA loader's three same-owner JSON routes.

Select the unique named estate from owner region data, not an obsolete locator
query id or a default HTML shell. No appendage geometry/ownership/grade credit.
"""
import importlib.util,json
from pathlib import Path
from urllib.parse import urlsplit
import requests
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
LOADER=BASE/'government-xl-king-cheung-95691-ha-estate-loader-primary-packet-v1-20261011'
BATCH='government-xl-king-cheung-95691-ha-exact-owner-data-v1-20261011';DOC=BASE/BATCH
HOST='https://www.housingauthority.gov.hk';PREFIX='/json/property-location'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in [INPUT/'result.json',LOADER/'result.json']:
   receipt=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 loader=(LOADER/'raw/load-estate-locator-detail.js').read_text()
 assert '"/json/property-location"'in loader and '"/estate-locator-access.json"'in loader and 'inJsonInterPath + inAccessJsonPath + dist + ".json"'in loader
 row=read(INPUT/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/95691:0'
 DOC.mkdir(parents=True);records=[];session=requests.Session();session.headers['User-Agent']='Mozilla/5.0 HongKongSandbox source-provenance research'
 def fetch(name,path):
  assert path.startswith(PREFIX+'/')and '..'not in path and urlsplit(path).query==''and urlsplit(path).netloc==''and path.endswith('.json')
  url=HOST+path;record=dict(requestedURL=url,sourceOwner='Hong Kong Housing Authority',sourceRole='Exact observed owner loader routing JSON, no geometric acceptance')
  try:
   response=session.get(url,timeout=40);assert urlsplit(response.url).hostname=='www.housingauthority.gov.hk'
   p=DOC/'raw'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(response.content)
   record.update(finalURL=response.url,status=response.status_code,responseHeaders=dict(response.headers),body=ref(p),downloadSucceeded=response.status_code==200)
   data=response.json()if response.status_code==200 else None
  except (requests.RequestException,ValueError)as error:record.update(downloadSucceeded=False,error=str(error));data=None
  records.append(record);save(DOC/'raw-retrieval-progress.json',dict(uids=[row['uid']],records=records));return data
 access=fetch('estate-locator-access.json',PREFIX+'/estate-locator-access.json');estate=None;route=None
 if access is not None:
  assert isinstance(access,list);found=[r for r in access if str(r['id'])=='1'];assert len(found)==1;route=found[0]
  regions=fetch('owner-prh-region.json',PREFIX+route['region'])
  if regions is not None:
   matches=[]
   for region in regions['regionArray']:
    for district in region['district']:
     for candidate in district['estates']:
      text=json.dumps(candidate,ensure_ascii=False)
      if '祥龍圍'in text or 'Cheung Lung Wai'in text:matches.append((district['id'],candidate))
   assert len(matches)==1,'Named owner estate must be unique, never use default last district'
   district_id,named=matches[0];assert str(district_id).isalnum()and str(named['aplySysId']).isdigit()
   details=fetch('owner-named-district-estates.json',PREFIX+route['estate']+str(district_id)+'.json')
   if details is not None:
    selected=[r for r in details if str(r['aplySysId'])==str(named['aplySysId'])];assert len(selected)==1
    estate=selected[0];assert '祥龍圍'in json.dumps(estate,ensure_ascii=False)or 'Cheung Lung Wai'in json.dumps(estate,ensure_ascii=False)
    save(DOC/'named-owner-record.json',dict(uniqueNamedEstate=estate,regionNamedEstate=named,districtId=district_id,ownerLocatorURL=HOST+'/tc/global-elements/estate-locator/detail.html?id='+str(named['aplySysId'])+'&propertyType=1',old2778LocatorNotAssumedEquivalent=True))
 save(DOC/'primary-packet.json',dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],records=records,uniqueNamedOwnerRecordFound=estate is not None,ownerDataRoute=route,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourceAppendageOwnershipAccepted=False,surveyedRegistrationClaimed=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False))
 refs=[Path(__file__),INPUT/'result.json',INPUT/'selection.json.gz',LOADER/'result.json',LOADER/'raw/load-estate-locator-detail.js']
 s=importlib.util.spec_from_file_location('king_cheung_named_ha_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'raw-unique-named-owner-estate-json-route-no-appendage-ownership-or-grade-credit',refs,dict(uids=[row['uid']],downloadedSources=sum(r['downloadSucceeded']for r in records),uniqueNamedOwnerRecordFound=estate is not None,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(uniqueNamedOwnerRecordFound=estate is not None,namedOwnerRecord=estate),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
