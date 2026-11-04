"""Make full-frame, hash-bound inspection sheets from two completed browser reports.

Previews only. A coordinator must actually inspect them before recording visual
acceptance; this utility never approves a model or modifies an exported canvas.
"""
import argparse,json,re
from pathlib import Path
from PIL import Image,ImageDraw
from run import ROOT,read,save,digest

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--report',action='append',required=True);a=p.parse_args();out=(ROOT/a.out).resolve();assert out.is_relative_to(ROOT/'docs/astra-city/government-import')and not out.exists()and len(a.report)==2
 groups={};reports=[]
 for name in a.report:
  path=(ROOT/name).resolve();assert path.is_relative_to(ROOT/'docs/astra-city/government-import');r=read(path);assert r['passed']and not r['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
  # Retained schema is mandatory even for an explicitly empty set.
  for v in r['views']+r['retainedNativeOwnViews']:
   if'file'not in v:continue
   assert v['width']in [390,1280]and v['time']in ['15:00','22:00']and re.fullmatch(r'landsd/[0-9]+:0',v['uid'])
   image=(path.parent/v['file']).resolve();assert image.is_relative_to(path.parent)and image.suffix=='.png'
   panel=dict(uid=v['uid'],width=v['width'],time=v['time'],path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()));groups.setdefault(v['uid'],[]).append(panel)
 assert groups;out.mkdir();rows=[]
 for uid,panels in sorted(groups.items()):
  assert len(panels)==4 and {(r['width'],r['time'])for r in panels}=={(w,t)for w in [390,1280]for t in ['15:00','22:00']}
  panels.sort(key=lambda r:(-r['width'],r['time']));sheet=Image.new('RGB',(1280,948),'white');draw=ImageDraw.Draw(sheet)
  for i,r in enumerate(panels):
   x=i%2*640;y=i//2*474;im=Image.open(ROOT/r['path']).convert('RGB');im.thumbnail((640,450));draw.text((x+2,y+3),f"{uid} {r['width']} {r['time']}",fill='black');sheet.paste(im,(x+(640-im.width)//2,y+24))
  dest=out/(uid.replace('/','-').replace(':','-')+'.jpg');sheet.save(dest,quality=95);rows.append(dict(path=str(dest.relative_to(ROOT)),sha256=digest(dest.read_bytes()),panels=panels))
 save(out/'panel-bindings.json',dict(reports=reports,rows=rows,exportedSourceImagesModified=False,fullFramesPreserved=True,visualAcceptance=False,imageInspectionRequired=True))
 print(dict(sheets=len(rows),exports=sum(len(r['panels'])for r in rows),visualAcceptance=False),flush=True)
if __name__=='__main__':main()
