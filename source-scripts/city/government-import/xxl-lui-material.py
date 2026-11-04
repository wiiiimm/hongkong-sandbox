"""Disable procedural facade windows on Lui Seng Chun; no geometry changes or AI."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
UID='landsd/160070:0'
STAGED=HERE/'accepted/government-xxl-lui-20260912/catalogue.json'
LIVE=ROOT/'3d-viewer/city/data/official-models/government-xxl-lui-20260912/catalogue.json'
DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/lui-install/material'
def read(path):return json.loads(Path(path).read_text())
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,separators=(',',':'),sort_keys=True)+'\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return str(path.relative_to(ROOT))
def main():
 before={rel(p):digest(p) for p in (STAGED,LIVE)}
 for path in (STAGED,LIVE):
  catalogue=read(path);models=[m for m in catalogue['models'] if m['uid']==UID];assert len(models)==1
  model=models[0];assert model['label']=='Hong Kong Baptist University School of Chinese Medicine - Lui Seng Chun' and model['sha256']=='24e5dc36fd94705b3dadeb4f51eb1f344145dc6020cda85951fd5741f3a72fdd'
  model['proceduralWindows']=False;save(path,catalogue)
 model=next(m for m in read(LIVE)['models'] if m['uid']==UID);assert model['proceduralWindows'] is False
 config=read(HERE/'accepted/government-xxl-lui-20260912/browser-config.json');config.update(doc=rel(DOC)+'/',browserUids=[UID],failureTestUids=[UID]);save(DOC/'browser-config.json',config)
 save(DOC/'correction.json',{'policy':'source-surface-material-correction-v1','uid':UID,'cause':'The generic procedural facade shader placed window shades across architectural surfaces that do not correspond to windows.','proceduralWindows':False,'sourceMaterialsRetained':True,'sourceSHA256':model['sha256'],'catalogueBeforeSHA256':before,'catalogueAfterSHA256':{rel(p):digest(p) for p in (STAGED,LIVE)},'aiCalls':0,'geometryChanges':0})
 print(json.dumps({'updated':UID,'proceduralWindows':False,'aiCalls':0,'geometryChanges':0}))
if __name__=='__main__':main()
