"""Observed primary images and two document pages only; never model exports."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request
import fitz

HERE=Path(__file__).resolve().parent
ALLOW=('Date','ETag','Last-Modified','Content-Type','Content-Length','Content-Disposition')
OBSERVED=(
 ('sports-centre-official-photo1.jpg','sports-centre-lcsd.html','https://www.lcsd.gov.hk/file_upload_clpss/leisure_facilities/en/common/images/photo/facilities/SSP/lckpsc_01.jpg'),
 ('pool-official-photo.jpg','swimming-pool-lcsd.html','https://www.lcsd.gov.hk/en/beach/common/graphics/SP/small/Lai%20Chi%20Kok%20Park%20SP.jpg'),
)
def main():
 out=HERE/'primary-observed-images';out.mkdir(exist_ok=False);rows=[]
 for name,html,url in OBSERVED:
  assert url in (HERE/'primary-documents'/html).read_text()
  row={'filename':name,'requestURL':url,'observedIn':html,'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:
    raw=response.read(4*1024*1024+1);assert len(raw)<=4*1024*1024
    row.update(status=response.status,finalURL=response.geturl(),provenanceHeaders={k:response.headers[k] for k in ALLOW if k in response.headers})
   with (out/name).open('xb') as stream:stream.write(raw)
   row.update(saved=True,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  except Exception as error:row.update(saved=False,errorType=type(error).__name__,error=str(error))
  rows.append(row)
 with (HERE/'observed-images-retrieval.json').open('x') as stream:json.dump({'sources':rows,'headerAllowlist':ALLOW},stream,indent=2);stream.write('\n')
 pages=HERE/'primary-document-pages';pages.mkdir(exist_ok=False)
 raw=HERE/'primary-documents/park-lcsd-permit-site-2020.pdf';doc=fitz.open(raw);exports=[]
 for i in (102,103):
  page=doc[i];pix=page.get_pixmap(matrix=fitz.Matrix(2400/max(page.rect.width,page.rect.height),2400/max(page.rect.width,page.rect.height)),alpha=False)
  png=pages/f'park-lcsd-permit-physical-page-{i+1:03d}-2400px.png';pix.save(png)
  exports.append({'sourceSHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'physicalPageOneBased':i+1,'sourcePageCount':len(doc),'png':str(png.relative_to(HERE)),'width':pix.width,'height':pix.height,'sha256':hashlib.sha256(png.read_bytes()).hexdigest()})
 doc.close()
 with (HERE/'primary-document-page-lineage.json').open('x') as stream:json.dump({'renderer':'PyMuPDF','version':fitz.VersionBind,'documentOnlyNotModelExports':True,'pages':exports},stream,indent=2);stream.write('\n')
 print(json.dumps({'observedImageResults':rows,'documentPages':exports}))
if __name__=='__main__':main()
