"""DRAFT bounded official map capture; schematic context, no measured registration."""
from pathlib import Path
import urllib.request,hashlib,json,time
import fitz
from PIL import Image
from run import ROOT,save
DOC=ROOT/'docs/astra-city/government-import/government-xl-polyu-sports305582-official-campus-map-context-v1-20261012'
SOURCES=[('current-campus-map','https://www.polyu.edu.hk/campus-map/pdf/CampusMap.pdf'),('older-official-campus-map','https://www.polyu.edu.hk/engl/event/up_load/general/IRCCH/3rd%20IRCCH%20Symposium/Accomodation/CampusMap.pdf')]
MAX_BYTES=8*1024*1024
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def fetch(url):
 request=urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox source-context/1.0'})
 with urllib.request.urlopen(request,timeout=30)as response:
  raw=response.read(MAX_BYTES+1);assert len(raw)<=MAX_BYTES and response.status==200 and raw.startswith(b'%PDF-');return raw,dict(status=response.status,finalURL=response.geturl(),headers=dict(response.headers.items()))
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);rows=[]
 for name,url in SOURCES:
  a=b=None
  try:
   a,h1=fetch(url);p=DOC/(name+'.pdf');p.write_bytes(a);save(DOC/(name+'-first-read.json'),dict(url=url,reader='independent-urlopen-response-1',body=ref(p),http=h1))
   b,h2=fetch(url);assert a==b,'Independent official response bodies differ';assert h1['finalURL']==h2['finalURL'];etag1=h1['headers'].get('ETag');etag2=h2['headers'].get('ETag');assert etag1==etag2,'Official ETag changed during capture'
   with fitz.open(stream=a,filetype='pdf')as document:
    assert document.page_count==1;page=document[0];pix=page.get_pixmap(matrix=fitz.Matrix(200/72,200/72),alpha=False);png=DOC/(name+'-page1-200dpi.png');pix.save(png)
    with Image.open(png)as image:assert image.size==(pix.width,pix.height);dimensions=[image.width,image.height]
    rows.append(dict(name=name,url=url,body=ref(p),bytes=len(a),reader1=h1,reader2=h2,independentReadBodiesIdentical=True,metadata=document.metadata,originalPageSizePoints=[page.rect.width,page.rect.height],export=dict(**ref(png),dimensions=dimensions,dpi=200,unwarpedFullPage=True),dateInference=None,schematicNotMetricRegistration=True))
  except Exception as error:
   failure=dict(name=name,url=url,errorType=type(error).__name__,error=str(error),firstBodyCaptured=a is not None,secondBodyCaptured=b is not None,noAuthoritativeAbsenceClaim=True,noTLSBypass=True);save(DOC/(name+'-failure.json'),failure);rows.append(failure)
 save(DOC/'context.json',dict(sourceOnly=True,noModelGeometryChanges=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,noSourceUIDOrSourceHeightClaim=True,sourceInputs=[ref(Path(__file__))],rows=rows,qualification='Two official schematic campus maps only. Full unwarped pages, no pixel fit/warp or metric height/UID/ownership/engineered joint claim. Each actual fetch/export or failure preserved; one failed response never proves source absence. Temporal metadata is literal, not assumed as-built source epoch.'))
 print(json.dumps(dict(rows=rows,identityAccepted=False)),flush=True)
if __name__=='__main__':main()
