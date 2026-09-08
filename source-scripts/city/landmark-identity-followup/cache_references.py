"""Retain bounded primary identity evidence, never geometry or credentials."""
from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request
HERE=Path(__file__).resolve().parent;OUT=HERE/'reference-cache';OUT.mkdir(exist_ok=True)
URLS={'china-resources':'https://www.skyscrapercenter.com/building/china-resources-building/2422','cullinan-i':'https://www.skyscrapercenter.com/hong-kong/the-cullinan-i/675/','cullinan-ii':'https://www.skyscrapercenter.com/building/the-cullinan-ii/676','oakhill':'https://www.skyscrapercenter.com/building/the-oakhill/11844','nina-factsheet':'https://www.ninahotelgroup.com/media/iy4ffnai/240315-tww-fact-sheet-en.pdf'}
def one(item):
 name,url=item;p=OUT/(name+('.pdf' if url.endswith('.pdf') else '.html'))
 try:
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:data=r.read(8_000_001)
   assert len(data)<=8_000_000;p.write_bytes(data)
  return {'id':name,'url':url,'path':str(p.relative_to(HERE.parents[2])),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
 except Exception as e:return {'id':name,'url':url,'error':type(e).__name__}
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(one,URLS.items()));(HERE/'reference-cache-manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
