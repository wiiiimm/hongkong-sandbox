"""Compose unedited actual browser exports for efficient visual inspection; no review credit."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--browser',required=True);a=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;source=base/a.browser
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.browser])and not out.exists()
    receipt,pins=authenticate(source);assert receipt['allBrowserDiagnosticsPassed']
    refs=[Path(__file__),source/'result.json'];sheets=[];images=[]
    for width in [1280,390]:
        reportpath=source/str(width)/'staged-browser.json';assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))];refs.append(reportpath);report=read(reportpath);assert report['passed']and not report['errors']
        for kind,items in [('source',report['views']),('retained',report['retainedNativeOwnViews'])]:
            views=[r for r in items if r.get('file')]
            for offset in range(0,len(views),4):
                group=views[offset:offset+4];loaded=[];records=[]
                for row in group:
                    p=source/str(width)/row['file'];sha=digest(p.read_bytes());assert sha==pins[str(p.relative_to(ROOT))];refs.append(p)
                    with Image.open(p)as image:loaded.append(image.convert('RGB'))
                    record=dict(path=str(p.relative_to(ROOT)),sha256=sha,uid=row['uid'],time=row['time'],width=width,kind=kind);records.append(record);images.append(record)
                cellw=max(i.width for i in loaded);cellh=max(i.height for i in loaded)+32;canvas=Image.new('RGB',(cellw*2,cellh*2),'white');draw=ImageDraw.Draw(canvas)
                for i,(im,r)in enumerate(zip(loaded,records)):
                    x=(i%2)*cellw;y=(i//2)*cellh;draw.text((x+5,y+7),r['uid']+' | '+str(width)+' | '+r['time']+' | '+r['sha256'][:12],fill='black');canvas.paste(im,(x,y+32))
                path=out/(str(width)+'-'+kind+'-'+str(offset//4+1)+'.png');path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path)
                sheets.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),sourceImages=records,scale=1,cropped=False))
    assert len(images)==len({r['path']for r in images})
    result=dict(uids=receipt['uids'],browserBatch=a.browser,images=images,sheets=sheets,sourceImageCount=len(images),contactSheetCount=len(sheets),imagesActuallyReviewed=False,visualAcceptance=False,installationApproved=False,publication=False,aiCalls=0,qualification='Pixel-preserving1x contact sheets of actual authenticated exported PNGs, with added labels and empty padding only. Every source export remains unchanged. Composition grants no visual or modelling approval.')
    save(out/'summary.json',result)
    module('browser_contact_sheets_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unaltered-browser-export-contact-sheets-for-root-inspection',list(dict.fromkeys(refs)),result)
    print(dict(images=len(images),sheets=len(sheets)),flush=True)


if __name__=='__main__':main()
