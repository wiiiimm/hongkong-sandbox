"""Pixel-preserving QA sheets for immutable images from a still-running browser.

Never fabricates a successful software report or grants review/acceptance.
The final reviewer must bind these exact image hashes to the completed report.
"""
import argparse,hashlib,json,time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.resolve().relative_to(ROOT))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--width',type=int,choices=[390,1280],required=True)
    ap.add_argument('--limit',type=int,default=32);ap.add_argument('--exclude-review',type=Path,action='append',default=[])
    a=ap.parse_args();assert 1<=a.limit<=64 and a.source.resolve().is_relative_to(ROOT/'docs/astra-city/government-import') and a.out.resolve().is_relative_to(ROOT/'docs/astra-city/government-import') and not a.out.exists()
    seen={}
    for review_path in a.exclude_review:
        review=json.loads(review_path.read_text());assert review['reviewer']=='ROOT'and review['allListedExportsActuallyInspected']is True
        for r in review['images']:
            p=(ROOT/r['path']).resolve();assert p.is_relative_to(ROOT)and sha(p)==r['sha256']
            assert r['path']not in seen or seen[r['path']]==r['sha256'];seen[r['path']]=r['sha256']
    files=[];recent=[]
    for p in sorted(a.source.glob('*.png')):
        key=rel(p)
        if key in seen:assert sha(p)==seen[key];continue
        if p.stat().st_mtime>time.time()-5:recent.append(key);continue
        if len(files)<a.limit:files.append(p)
    assert files,'No new stable image exports to review'
    a.out.mkdir(parents=True);rows=[];sheets=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12 if a.width==390 else 18)
    for start in range(0,len(files),4):
        group=files[start:start+4];sheet=Image.new('RGB',(2*a.width,1848),'#20252e');draw=ImageDraw.Draw(sheet)
        for n,p in enumerate(group):
            before=sha(p)
            with Image.open(p)as original:
                assert original.size==(a.width,900);image=original.convert('RGB')
            x,y=n%2*a.width,n//2*924;sheet.paste(image,(x,y+24));draw.text((x+8,y+1),p.name,font=font,fill='white')
            extrema=image.getextrema();assert sha(p)==before
            rows.append(dict(path=rel(p),sha256=before,width=a.width,height=900,sheet=start//4+1,flatSceneWarning=not any(hi-lo>20 for lo,hi in extrema)))
        dest=a.out/('sheet-'+str(start//4+1).zfill(2)+'.png');sheet.save(dest);sheets.append(dict(path=rel(dest),sha256=sha(dest),sourcePaths=[rel(p)for p in group]))
    manifest=dict(partialEvidenceOnly=True,softwareChecksComplete=False,publication=False,reviewPending=True,sourceDirectory=rel(a.source),originalPixelsResized=False,originalImages=rows,sheets=sheets,recentImagesDeferred=recent)
    (a.out/'partial-contact-sheets.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(images=len(rows),sheets=len(sheets),partialEvidenceOnly=True,softwareChecksComplete=False,flatWarnings=sum(r['flatSceneWarning']for r in rows))))
if __name__=='__main__':main()
