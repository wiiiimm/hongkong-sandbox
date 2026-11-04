"""Disable procedural facade windows on the Tian Tan Buddha; no geometry changes or AI."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
UID='landsd/241332:0'
STAGED=HERE/'accepted/government-xxl-tian-tan-20260912/catalogue.json'
LIVE=ROOT/'3d-viewer/city/data/official-models/government-xxl-tian-tan-20260912/catalogue.json'
DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/third-pass/tian-tan/material'
def read(path):return json.loads(Path(path).read_text())
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,separators=(',',':'),sort_keys=True)+'\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return str(path.relative_to(ROOT))
def main():
 before={rel(p):digest(p) for p in (STAGED,LIVE)}
 for path in (STAGED,LIVE):
  catalogue=read(path);models=[m for m in catalogue['models'] if m['uid']==UID];assert len(models)==1
  model=models[0];assert model['label']=='Tian Tan Buddha Statue' and model['sha256']=='d369abcc4b6c02da3722ec2372e5cdf00eb075026709408b91d07c206a93238a'
  model['proceduralWindows']=False;save(path,catalogue)
 live=read(LIVE);model=next(m for m in live['models'] if m['uid']==UID);assert model['proceduralWindows'] is False
 config=read(HERE/'accepted/government-xxl-tian-tan-20260912/browser-config.json');config.update(doc=rel(DOC)+'/',browserUids=[UID],failureTestUids=[UID]);save(DOC/'browser-config.json',config)
 save(DOC/'correction.json',{'policy':'opaque-landmark-material-correction-v1','uid':UID,'cause':'The shared facade shader was drawing procedural windows over the statue.','proceduralWindows':False,'sourceMaterialsRetained':True,'sourceSHA256':model['sha256'],'catalogueBeforeSHA256':before,'catalogueAfterSHA256':{rel(p):digest(p) for p in (STAGED,LIVE)},'aiCalls':0,'geometryChanges':0})
 print(json.dumps({'updated':UID,'proceduralWindows':False,'aiCalls':0,'geometryChanges':0}))
if __name__=='__main__':main()
