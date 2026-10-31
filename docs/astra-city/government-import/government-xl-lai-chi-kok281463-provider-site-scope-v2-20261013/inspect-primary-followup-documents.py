"""Read/render official document pages and retrieve the observed park map only."""
import datetime,hashlib,json
from pathlib import Path
import urllib.request
import fitz
HERE=Path(__file__).resolve().parent
def main():
 out=HERE/'primary-document-inspection';out.mkdir(exist_ok=False)
 url='https://www.lcsd.gov.hk/en/parks/lckp/common/graphics/lckp_parkmap.png'
 assert '/en/parks/lckp/common/graphics/lckp_parkmap.png' in (HERE/'primary-documents/park-map-page.html').read_text()
 receipt={'requestURL':url,'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:
   raw=response.read(8*1024*1024+1);assert len(raw)<=8*1024*1024
   receipt.update(status=response.status,finalURL=response.geturl(),provenanceHeaders={k:response.headers[k] for k in ('Date','ETag','Last-Modified','Content-Type','Content-Length','Content-Disposition') if k in response.headers})
  with (out/'lcsd-original-park-map.png').open('xb') as stream:stream.write(raw)
  receipt.update(saved=True,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 except Exception as error:receipt.update(saved=False,errorType=type(error).__name__,error=str(error))
 with (HERE/'park-map-retrieval.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
 rawpdf=HERE/'primary-documents/government-park-podium-garden-booklet.pdf'
 source_sha=hashlib.sha256(rawpdf.read_bytes()).hexdigest();doc=fitz.open(rawpdf);found=[]
 for i,page in enumerate(doc):
  text=page.get_text()
  if 'Lai Chi Kok Park' in text and ('Podium' in text or 'podium' in text):found.append(i)
 assert 1<=len(found)<=3
 pages=[]
 for i in found:
  page=doc[i];pix=page.get_pixmap(matrix=fitz.Matrix(2400/max(page.rect.width,page.rect.height),2400/max(page.rect.width,page.rect.height)),alpha=False)
  png=out/f'government-podium-garden-physical-page-{i+1:03d}-2400px.png';pix.save(png)
  textfile=out/f'government-podium-garden-physical-page-{i+1:03d}-text.txt'
  with textfile.open('x') as stream:stream.write(page.get_text())
  pages.append({'sourceSHA256':source_sha,'physicalPageOneBased':i+1,'totalSourcePages':len(doc),'png':str(png.relative_to(HERE)),'width':pix.width,'height':pix.height,'pngSHA256':hashlib.sha256(png.read_bytes()).hexdigest(),'text':str(textfile.relative_to(HERE)),'textSHA256':hashlib.sha256(textfile.read_bytes()).hexdigest()})
 doc.close()
 with (HERE/'primary-document-page-lineage.json').open('x') as stream:json.dump({'documentOnlyNoModelExports':True,'renderer':'PyMuPDF','version':fitz.VersionBind,'pages':pages},stream,indent=2);stream.write('\n')
 print(json.dumps({'map':receipt,'pages':pages}))
if __name__=='__main__':main()
