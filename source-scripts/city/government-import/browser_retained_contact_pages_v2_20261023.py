"""Paginate exact successful retained exports for readable ROOT inspection."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw
from run import ROOT,read,save,digest

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--browser',required=True);p.add_argument('--out',required=True);p.add_argument('--width',type=int,choices=[1280,390],required=True);p.add_argument('--mode',choices=['staged','live'],required=True)
 a=p.parse_args();assert all(n.startswith('government-xl-')and '/'not in n for n in [a.browser,a.out])
 base=ROOT/'docs/astra-city/government-import';folder=base/a.browser/(str(a.width)if a.mode=='staged'else'viewport-'+str(a.width));rp=folder/(a.mode+'-browser.json');report=read(rp);assert report['passed']and not report['errors']
 rows=sorted(report['retainedNativeOwnViews'],key=lambda r:(r['uid'],r['time']));assert rows and len({(r['uid'],r['time'])for r in rows})==len(rows)
 assert all(r['active']and r['visible']and r['fullyFramed']and not r['fallbackFaces']for r in rows)
 out=base/a.out;out.mkdir(parents=True,exist_ok=True);pages=[]
 cw,ch=(640,475)if a.width==1280 else(390,930)
 for offset in range(0,len(rows),12):
  canvas=Image.new('RGB',(cw*3,ch*4),'white');draw=ImageDraw.Draw(canvas);inputs=[]
  for i,r in enumerate(rows[offset:offset+12]):
   source=folder/r['file'];im=Image.open(source).convert('RGB');im.thumbnail((cw,ch-25));x=(i%3)*cw;y=(i//3)*ch;canvas.paste(im,(x+(cw-im.width)//2,y+25));draw.text((x+8,y+5),r['uid']+' '+r['time'],fill='black');inputs.append(dict(path=str(source.relative_to(ROOT)),sha256=digest(source.read_bytes())))
  path=out/f'{a.mode}-retained-{a.width}-page-{offset//12+1}.png';assert not path.exists();canvas.save(path);page=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),inputs=inputs);pages.append(page)
  save(out/f'{a.mode}-retained-{a.width}-page-{offset//12+1}-binding.json',dict(report=dict(path=str(rp.relative_to(ROOT)),sha256=digest(rp.read_bytes())),inputs=inputs,output={k:v for k,v in page.items()if k!='inputs'},qualification='Display-only page of up to12 exact hash-bound native exports; originals unmodified.'))
 assert all(digest((ROOT/q['path']).read_bytes())==q['sha256']for page in pages for q in page['inputs'])
 save(out/f'{a.mode}-retained-{a.width}-pages.json',dict(report=dict(path=str(rp.relative_to(ROOT)),sha256=digest(rp.read_bytes())),pages=pages,sourceImagesUnmodified=True,visualAcceptance=False,qualification='Display-only paginated contact sheets; exact original exports remain untouched/hash-bound. Page creation does not grant visual acceptance.'))
 print(dict(pages=len(pages),exports=len(rows)),flush=True)
if __name__=='__main__':main()
