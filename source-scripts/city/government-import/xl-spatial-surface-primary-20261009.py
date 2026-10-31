"""Capture primary source documents for original bridge/canopy-role investigation."""
import urllib.request,urllib.parse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from run import ROOT,save
DOC=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009/primary'
rows=[('youthsquare-footbridge-original-plan.pdf','https://www.legco.gov.hk/yr18-19/english/fc/pwsc/papers/pwsc20190111pwsc-71-1-e.pdf'),('kai-tak-cruise-terminal-archsd-transcript.pdf','https://www.archsd.gov.hk/media/exhibition/kai-tak-cruise-terminal-building/kaitakcruiseterminalbuilding.pdf'),('youth-square-official.html','https://www.youthsquare.hk/zh-CN/about_us?floor_id=2&floor_item_id=8'),('kai-tak-cruise-terminal-archsd.html','https://www.archsd.gov.hk/en/exhibition/kai-tak-cruise-terminal-building.html')]
rows += [('kai-tak-cruise-terminal-pedestrian-map.pdf','https://www.kaitakcruiseterminal.com.hk/downloads/ktct-pedestrian-map.pdf'),('kai-tak-cruise-terminal-operator-floorplans.pdf','https://www.kaitakcruiseterminal.com.hk/downloads/ktct-mice-presentation-18-jan-2019-final.pdf')]
rows += [(name,'https://www.archsd.gov.hk/media/exhibition/kai-tak-cruise-terminal-building/'+urllib.parse.quote(name)) for name in ['330x330_HKReport_14_Exterior.jpg','330x330_o_CTB-255.jpg','330x330_o_DSC_3755.jpg','330x330_window 2.jpg']]
for name,url in rows:
 p=DOC/name;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():continue
 
 try:r=urllib.request.urlopen(url,timeout=30)
 except Exception as e:save(p.with_suffix(p.suffix+'.failure.json'),{'url':url,'failure':str(e),'obtained':False});print(name,'unavailable',flush=True);continue
 body=r.read();p.write_bytes(body);save(p.with_suffix(p.suffix+'.request.json'),{'url':url,'finalURL':r.geturl(),'retrievedAt':datetime.now(timezone.utc).isoformat(),'status':r.status,'headers':dict(r.headers),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'qualification':'Original unmodified primary document, source interpretation only, not geometric tracing or placement fitting.'});print(name,len(body),flush=True)
