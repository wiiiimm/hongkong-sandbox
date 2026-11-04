"""Archive primary MTR context privately; never approve geometry from a project page."""
from pathlib import Path
import urllib.request
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-southside-primary-mtr-context-v1-20261028';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
SOURCES=[('project.html','https://www.mtr.com.hk/en/corporate/properties/sil_wongchukhang.html',2*1024**2),('station-index.html','https://www.mtr.com.hk/en/corporate/operations/station_sil_wch.html',2*1024**2),('la-marina-primary-photo.jpg','https://www.mtr.com.hk/en/corporate/images/properties/wch_la_marina2.jpg',8*1024**2),('station-protection-plan.pdf','https://www.mtr.com.hk/archive/corporate/en/operations/SIL_RPAP/MTR_AP_608_2.pdf',16*1024**2)]
def main():
 assert not DOC.exists()and not LOCAL.exists();rows=[];refs=[Path(__file__)]
 for name,url,limit in SOURCES:
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90)as response:
    raw=response.read(limit+1);assert len(raw)<=limit;final=response.url;headers={k:v for k,v in response.headers.items()if k.lower()in ['etag','last-modified','content-type','content-length']}
   if name.endswith('.pdf'):assert raw.startswith(b'%PDF')
   if name.endswith('.jpg'):assert raw.startswith(b'\xff\xd8')
   p=LOCAL/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);refs.append(p);rows.append(dict(url=url,finalURL=final,asset=dict(path=str(p.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw)),headers=headers))
  except Exception as error:rows.append(dict(url=url,errorType=type(error).__name__,httpStatus=getattr(error,'code',None)))
 result=dict(uids=['landsd/311761:0','landsd/311762:0','landsd/315025:0','landsd/300867:0'],primarySources=rows,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Primary MTR project, station and illustration context only. No survey/map registration, dated protection-plan currency claim, exported-image inspection or geometric identity/placement approval. Raw copyrighted files kept in local references; failed acquisitions remain explicit.')
 save(DOC/'summary.json',result);module('southside_primary_mtr_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'primary-mtr-context-acquisition-no-model-approval',refs,result);print([(r['url'],r.get('httpStatus'),r.get('asset',{}).get('bytes'))for r in rows],flush=True)
if __name__=='__main__':main()
