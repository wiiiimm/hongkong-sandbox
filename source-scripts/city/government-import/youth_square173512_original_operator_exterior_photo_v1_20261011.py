"""Bounded primary exterior-photo acquisition from exact captured operator HTML property."""
from pathlib import Path
import datetime,json,re,requests,io
from PIL import Image
from run import ROOT,read,save,digest
BASE=ROOT/'docs/astra-city/government-import/government-xl-youth-square173512-official-floor-map-html-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import/government-xl-youth-square173512-original-operator-exterior-photo-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();DOC.mkdir()
 p=BASE/'original-reader1.html';assert p.read_bytes()==(BASE/'original-reader2.html').read_bytes()
 m=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',p.read_text());assert m
 data=json.loads(m.group(1));url=data['props']['pageProps']['pageContent']['design_concept_image_url']
 assert url=='https://www.youthsquare.hk/youth_square/abouts/homes/1/about_us_design_concept_image_2.jpg'
 readings=[];raws=[]
 for i in [1,2]:
  r=requests.get(url,timeout=(15,45));raw=r.content;assert len(raw)<=8*1024*1024
  meta=dict(url=url,finalURL=r.url,status=r.status_code,sha256=digest(raw),bytes=len(raw),fetchedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),headers={k:r.headers.get(k)for k in ['Content-Type','ETag','Last-Modified','Date']})
  save(DOC/f'reader{i}.json',meta);raws.append(raw);readings.append(meta);assert r.status_code==200 and r.url==url
 assert raws[0]==raws[1]
 for k in ['ETag','Last-Modified']:assert readings[0]['headers'][k]==readings[1]['headers'][k]
 im=Image.open(io.BytesIO(raws[0]));assert im.format=='JPEG';out=DOC/'original-operator-exterior-design-photo.jpg';out.write_bytes(raws[0])
 save(DOC/'acquisition.json',dict(sourceOnly=True,actualReaders=readings,bothReaderBytesEqual=True,originalImage=ref(out),width=im.width,height=im.height,unwarpedOriginal=True,sourceUIDOrElevationProven=False,identityAccepted=False,currentAcceptance=False,sourceHTMLJSONPointer='/props/pageProps/pageContent/design_concept_image_url',evidenceRefs=[ref(Path(__file__)),ref(p),ref(BASE/'original-reader2.html'),ref(BASE/'acquisition.json')]))
 print(json.dumps(dict(image=ref(out),width=im.width,height=im.height)),flush=True)
if __name__=='__main__':main()
