"""Raw official HA/DBC sources for one named estate; historical plans are context.
No inferred surveyed placement, ownership, source-extension or support credit.
"""
import importlib.util,json,time
from pathlib import Path
import requests
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
BATCH='government-xl-king-cheung-95691-ha-owner-bfa-plan-photo-packet-v1-20261011';DOC=BASE/BATCH
OWNER=BASE/'government-xl-king-cheung-95691-ha-exact-owner-data-v1-20261011'
OWNER_RECORD=read(OWNER/'named-owner-record.json')['uniqueNamedEstate']
assert OWNER_RECORD['aplySysId']=='1418347800065'and OWNER_RECORD['name']['en']=='Cheung Lung Wai Estate'and 'King Cheung House'in OWNER_RECORD['blockName']['en']
assert '/en/common/pdf/global-elements/estate-locator/cheunglungwaiestate-barrier-free-en.pdf'in OWNER_RECORD['furtherInfo']['en']
assert OWNER_RECORD['image']=='/common/image/global-elements/estate-locator/prh/CLW.jpg'
SOURCES=[('owner-barrier-free-access-en.pdf','https://www.housingauthority.gov.hk/en/common/pdf/global-elements/estate-locator/cheunglungwaiestate-barrier-free-en.pdf','Owner-linked exact named-estate accessible-facilities plan; cartographic context only, no surveyed registration/source appendage ownership or ground claim'),
 ('owner-estate-CLW.jpg','https://www.housingauthority.gov.hk/common/image/global-elements/estate-locator/prh/CLW.jpg','Owner-linked exact named-estate photo; image context only, no source-component role or georeferencing assumed')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');owner_receipt=read(OWNER/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(owner_receipt['jobId'],)).fetchone()==('complete',owner_receipt)
 row=read(INPUT/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/95691:0';DOC.mkdir(parents=True);records=[];session=requests.Session();session.headers['User-Agent']='Mozilla/5.0 HongKongSandbox source-provenance research'
 for name,url,role in SOURCES:
  record=dict(requestedURL=url,sourceRole=role,sourceOwner='Hong Kong Housing Authority'if 'housingauthority.gov.hk'in url else 'North District Council',dateCaveat='Historical/current publication context only, no surveyed geometric or physical credit')
  try:
   r=session.get(url,timeout=40);path=DOC/'raw'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(r.content)
   record.update(finalURL=r.url,status=r.status_code,responseHeaders=dict(r.headers),body=ref(path),bodyBytes=len(r.content),returnedContentType=r.headers.get('content-type'),downloadSucceeded=r.status_code==200)
  except requests.RequestException as e:record.update(downloadSucceeded=False,error=str(e))
  records.append(record);save(DOC/'raw-retrieval-progress.json',dict(uid=row['uid'],records=records));print(json.dumps(dict(source=name,success=record['downloadSucceeded'],status=record.get('status'))),flush=True)
 save(DOC/'primary-packet.json',dict(uids=[row['uid']],currentNamedSource=row['source']['building'],sourceSHA256=row['sourceSHA256'],records=records,primaryURLs=[r['requestedURL']for r in records],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,surveyedRegistrationClaimed=False,sourceAppendageOwnershipAccepted=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False))
 refs=[Path(__file__),INPUT/'result.json',INPUT/'selection.json.gz',OWNER/'result.json',OWNER/'named-owner-record.json',OWNER/'raw/owner-named-district-estates.json']
 s=importlib.util.spec_from_file_location('king_cheung_raw_ha_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'raw-authoritative-owner-and-district-historical-source-packet-no-identity-physical-credit',refs,dict(uids=[row['uid']],downloadedSources=sum(r['downloadSucceeded']for r in records),currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
