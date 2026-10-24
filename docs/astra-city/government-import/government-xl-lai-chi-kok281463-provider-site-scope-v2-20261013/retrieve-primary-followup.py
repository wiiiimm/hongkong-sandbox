"""Bounded official park records only; no model buffers or project imports."""
import datetime,hashlib,json
from pathlib import Path
import urllib.error,urllib.request
HERE=Path(__file__).resolve().parent
HEADERS=('Date','ETag','Last-Modified','Content-Type','Content-Length','Content-Disposition')
SOURCES=(
 ('park-introduction.html','https://www.lcsd.gov.hk/en/parks/lckp/intro.html'),
 ('park-outdoor-facilities.html','https://www.lcsd.gov.hk/en/parks/lckp/facilities/outdoor.html'),
 ('park-map-page.html','https://www.lcsd.gov.hk/en/parks/lckp/layout.html'),
 ('government-park-podium-garden-booklet.pdf','https://www.greening.gov.hk/filemanager/greening/en/content_94/Kln2_180912.pdf'),
)
def main():
 out=HERE/'primary-documents';out.mkdir(exist_ok=False);rows=[]
 for name,url in SOURCES:
  row={'filename':name,'requestURL':url,'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:
    raw=response.read(32*1024*1024+1);assert len(raw)<=32*1024*1024
    row.update(status=response.status,finalURL=response.geturl(),provenanceHeaders={k:response.headers[k] for k in HEADERS if k in response.headers})
   with (out/name).open('xb') as stream:stream.write(raw)
   row.update(saved=True,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  except Exception as error:
   row.update(saved=False,errorType=type(error).__name__,error=str(error))
   if isinstance(error,urllib.error.HTTPError):row.update(status=error.code,provenanceHeaders={k:error.headers[k] for k in HEADERS if k in error.headers})
  rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 with (HERE/'retrieval.json').open('x') as stream:json.dump({'sources':rows,'headerAllowlist':HEADERS},stream,indent=2);stream.write('\n')
if __name__=='__main__':main()
