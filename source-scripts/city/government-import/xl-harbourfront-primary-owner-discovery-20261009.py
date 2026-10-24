"""Capture primary owner material for exact Two Harbourfront source-role review."""
import sys,json,re,importlib.util
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
BATCH='government-xl-two-harbourfront-primary-owner-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
URLS={'owner-property-page':'https://www.ckah.com/hong-kong-properties/leasing/156','owner-virtual-tour-index':'https://www.harbourfront.hk/','owner-main-photo':'https://www.ckah.com/sites/default/files/styles/height_auto/public/2023-10/The%20Harbourfront_cropped_20231009.jpg?itok=3jolUOFD'}
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);rows=[]
 for name,url in URLS.items():
  raw,receipt=request(url,json_expected=False);suffix='.jpg' if name.endswith('photo') else '.html';p=DOC/(name+suffix);p.write_bytes(raw);save(DOC/(name+'.request.json'),receipt);links=[]
  if suffix=='.html':
   text=raw.decode(errors='replace');links=re.findall(r'(?:src|href)\s*=\s*[\"\']([^\"\']+)',text)
  rows.append({'name':name,'url':url,'path':str(p.relative_to(ROOT)),'sha256':digest(raw),'bytes':len(raw),'links':links});print({'name':name,'bytes':len(raw),'links':links[:70]},flush=True)
 save(DOC/'primary-owner-discovery.json',{'uid':'landsd/118230:0','rows':rows,'sourceGeometryChanges':0,'identityAccepted':False,'qualification':'Owner explicitly links the virtual tour; captures provide primary property context, not yet registered low-wall function/ownership proof.'})
if __name__=='__main__':main()
