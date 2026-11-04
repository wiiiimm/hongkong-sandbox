"""Bounded LCSD/HKPL/LegCo documents only; no project imports or model work."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
ALLOW = ('Date','ETag','Last-Modified','Content-Type','Content-Length','Content-Disposition')
SOURCES = (
 ('pool-245RS-government-works-2009.pdf','https://www.legco.gov.hk/yr08-09/english/fc/pwsc/papers/p09-36e.pdf'),
 ('park-lcsd-permit-site-2020.pdf','https://www.lcsd.gov.hk/ls/tender/en/list/forms/LCLSQLRKSSPLCKP2020_EN.pdf'),
 ('sports-centre-lcsd.html','https://www.lcsd.gov.hk/clpss/en/webApp/Facility/Details.do?fid=666'),
 ('swimming-pool-lcsd.html','https://www.lcsd.gov.hk/clpss/en/webApp/Swimming.do?swpId=8'),
 ('pool-completion-lcsd-2012-13.html','https://www.lcsd.gov.hk/dept/annualrpt/2012-13/en/leisure/leisure02.html'),
 ('library-ground-floor-hkpl.html','https://www.hkpl.gov.hk/en/about-us/HKCL/floor-plan/Ground.html'),
 ('library-first-floor-hkpl.html','https://www.hkpl.gov.hk/en/about-us/hkcl/floor-plan/first.html'),
 ('library-ground-floor-original.jpg','https://www.hkpl.gov.hk/en/common/images/about-us/HKCL/gf_fp.jpg'),
 ('library-first-floor-original.JPG','https://www.hkpl.gov.hk/en/common/images/about-us/HKCL/floorplan1f.JPG'),
)

def main():
 out=HERE/'primary-documents';out.mkdir(exist_ok=False);rows=[]
 for filename,url in SOURCES:
  row={'filename':filename,'requestURL':url,'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (bounded primary-document research)'}),timeout=60) as response:
    raw=response.read(32*1024*1024+1);assert len(raw)<=32*1024*1024
    row.update(status=response.status,finalURL=response.geturl(),provenanceHeaders={k:response.headers[k] for k in ALLOW if k in response.headers})
   with (out/filename).open('xb') as stream:stream.write(raw)
   row.update(saved=True,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  except Exception as error:
   row.update(saved=False,errorType=type(error).__name__,error=str(error))
   if isinstance(error,urllib.error.HTTPError):row.update(status=error.code,finalURL=error.geturl(),provenanceHeaders={k:error.headers[k] for k in ALLOW if k in error.headers})
  rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 with (HERE/'retrieval.json').open('x',encoding='utf-8') as stream:json.dump({'headerAllowlist':ALLOW,'sources':rows,'noModelProcessing':True,'noDBOrReservations':True},stream,ensure_ascii=False,indent=2);stream.write('\n')

if __name__=='__main__':main()
