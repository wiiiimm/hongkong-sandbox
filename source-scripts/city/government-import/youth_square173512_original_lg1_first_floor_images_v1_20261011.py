"""Two exact English operator floor images, derived from captured original site module."""
from pathlib import Path
import datetime,json,re,requests,io
from PIL import Image
from run import ROOT,read,save,digest
BASE=ROOT/'docs/astra-city/government-import/government-xl-youth-square173512-official-floor-map-html-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import/government-xl-youth-square173512-original-lg1-first-floor-images-v1-20261011'
def ref(p): return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();DOC.mkdir()
 module=BASE/'original-floor-map-module-reader1.js';text=module.read_text();metadata=read(BASE/'floor-map-module-acquisition.json')
 assert metadata['bothReaderBytesEqual'] and metadata['actualReaders'][0]['sha256']==ref(module)['sha256']
 assert (BASE/'original-floor-map-module-reader2.js').read_bytes()==module.read_bytes()
 assert '"/floormap/desktop/floor_map_".concat(Z.floormap_img_name).concat(x,".png")'in text
 records=[]
 for id,name,stem in [(5,'LG1/F','lg1'),(6,'1/F','1f')]:
  assert f'id:{id},floor_id:2,name:"{name}",floormap_img_name:"{stem}"'in text
  url=f'https://www.youthsquare.hk/floormap/desktop/floor_map_{stem}.png';data=[];readings=[]
  for n in [1,2]:
   r=requests.get(url,timeout=(15,45));raw=r.content;assert len(raw)<=8*1024*1024
   m=dict(url=url,finalURL=r.url,status=r.status_code,bytes=len(raw),sha256=digest(raw),headers={k:r.headers.get(k)for k in ['Content-Type','ETag','Last-Modified','Date']},fetchedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
   save(DOC/(stem+f'.reader{n}.json'),m);data.append(raw);readings.append(m)
   assert r.status_code==200 and r.url==url
  assert data[0]==data[1]
  for k in ['ETag','Last-Modified']:assert readings[0]['headers'][k]==readings[1]['headers'][k]
  p=DOC/(f'original-operator-floor-map-{stem}.png');p.write_bytes(data[0]);im=Image.open(io.BytesIO(data[0]));assert im.format=='PNG';size=im.size
  records.append(dict(floorName=name,originalImage=ref(p),width=size[0],height=size[1],actualReaders=readings,bothReaderBytesEqual=True,unwarpedOriginal=True))
 save(DOC/'acquisition.json',dict(sourceOnly=True,completeExactImageCount=2,originalFloorImages=records,sourceUIDOrElevationProven=False,identityAccepted=False,currentAcceptance=False,referenceOnlyNotPreciseMeasurement=True,qualification='Original operator English LG1/F and1/F maps; exact URL stems derived from original captured site module. No image fitting/warp/scale or government-source ownership/elevation/support inferred.',evidenceRefs=[ref(Path(__file__)),ref(BASE/'original-reader1.html'),ref(BASE/'original-reader2.html'),ref(BASE/'acquisition.json'),ref(module),ref(BASE/'original-floor-map-module-reader2.js'),ref(BASE/'floor-map-module-acquisition.json')]))
 print(json.dumps(records),flush=True)
if __name__=='__main__':main()
