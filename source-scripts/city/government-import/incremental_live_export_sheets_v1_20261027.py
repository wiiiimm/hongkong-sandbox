"""Compose a completed viewport while the other runs; authenticate both at finish.

PNG pixels are copied at 1x with labels and padding only. Partial composition
and final authenticated composition grant no visual or installation approval.
"""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def prepare(source,out,width):
    partial=out/('width-'+str(width)+'.json');assert not partial.exists()
    folder=source/('viewport-'+str(width));reportpath=folder/'live-browser.json';report=read(reportpath)
    assert report['passed'] and not report['errors'];images=[];sheets=[]
    for kind,items in [('source',report['views']),('retained',report['retainedNativeOwnViews'])]:
        views=[v for v in items if v.get('file')]
        for offset in range(0,len(views),4):
            group=views[offset:offset+4];loaded=[];records=[]
            for v in group:
                p=(folder/v['file']).resolve();assert p.is_relative_to(folder.resolve())
                with Image.open(p) as im:loaded.append(im.convert('RGB'))
                records.append(dict(**ref(p),uid=v['uid'],time=v['time'],width=width,kind=kind))
            cellw=max(im.width for im in loaded);cellh=max(im.height for im in loaded)+32
            canvas=Image.new('RGB',(cellw*2,cellh*2),'white');draw=ImageDraw.Draw(canvas)
            for i,(im,row) in enumerate(zip(loaded,records)):
                x=(i%2)*cellw;y=(i//2)*cellh
                draw.text((x+5,y+7),row['uid']+' | '+str(width)+' | '+row['time']+' | '+row['sha256'][:12],fill='black')
                canvas.paste(im,(x,y+32))
            path=out/(str(width)+'-'+kind+'-'+str(offset//4+1)+'.png');assert not path.exists()
            path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path)
            sheets.append(dict(**ref(path),sourceImages=records,scale=1,cropped=False));images+=records
    save(partial,dict(browserBatch=source.name,mode='live',width=width,browserReport=ref(reportpath),images=images,sheets=sheets,imagesActuallyReviewed=False,visualAcceptance=False,installationApproved=False,publication=False,authenticationPending=True))
    print(dict(width=width,images=len(images),sheets=len(sheets),authenticationPending=True),flush=True)

def finalize(source,out):
    assert not (out/'summary.json').exists();receipt,pins=authenticate(source)
    assert receipt['publication'] and receipt['installedUids'] and receipt['completeCurrentCatalogueModels']>0
    images=[];sheets=[];refs=[Path(__file__),source/'result.json']
    for width in [1280,390]:
        partial=out/('width-'+str(width)+'.json');r=read(partial)
        assert r['browserBatch']==source.name and r['mode']=='live' and r['width']==width
        report=r['browserReport'];assert digest((ROOT/report['path']).read_bytes())==pins[report['path']]==report['sha256']
        refs.extend([partial,ROOT/report['path']]);part_images=[]
        browser=read(ROOT/report['path']);assert browser['passed'] and not browser['errors']
        expected=[]
        for kind,items in [('source',browser['views']),('retained',browser['retainedNativeOwnViews'])]:
            for v in items:
                if not v.get('file'):continue
                path=(ROOT/report['path']).parent/v['file']
                expected.append(dict(**ref(path),uid=v['uid'],time=v['time'],width=width,kind=kind))
        assert r['images']==expected
        for sheet in r['sheets']:
            assert sheet['scale']==1 and sheet['cropped'] is False
            assert ref(ROOT/sheet['path'])=={k:sheet[k] for k in ['path','sha256']}
            originals=[]
            for row in sheet['sourceImages']:
                assert row['width']==width and digest((ROOT/row['path']).read_bytes())==pins[row['path']]==row['sha256']
                refs.append(ROOT/row['path']);part_images.append(row)
                with Image.open(ROOT/row['path']) as im:
                    if 'A' in im.getbands():assert im.getchannel('A').getextrema()==(255,255)
                    originals.append(im.convert('RGB'))
            cellw=max(im.width for im in originals);cellh=max(im.height for im in originals)+32
            with Image.open(ROOT/sheet['path']) as canvas:
                assert canvas.size==(2*cellw,2*cellh)
                for i,im in enumerate(originals):
                    x=(i%2)*cellw;y=(i//2)*cellh+32
                    assert canvas.crop((x,y,x+im.width,y+im.height)).convert('RGB').tobytes()==im.tobytes(),'Export pixels changed during composition'
        assert part_images==r['images'];images+=r['images'];sheets+=r['sheets']
    assert len(images)==len({r['path'] for r in images})
    summary=dict(uids=receipt['installedUids'],browserBatch=source.name,mode='live',images=images,sheets=sheets,sourceImageCount=len(images),contactSheetCount=len(sheets),imagesActuallyReviewed=False,visualAcceptance=False,installationApproved=False,publication=False,aiCalls=0,qualification='Unscaled uncropped pixel copies from completed live viewport reports, fully authenticated against final installed receipt. Earlier viewport composition grants no approval; ROOT inspection remains separate.')
    save(out/'summary.json',summary)
    module('incremental_live_sheet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'authenticated-incremental-live-export-contact-sheets-v1',list(dict.fromkeys(refs)),summary)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--batch',required=True);ap.add_argument('--browser',required=True);ap.add_argument('--width',type=int,choices=[390,1280]);a=ap.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.browser])
    base=ROOT/'docs/astra-city/government-import';source=base/a.browser;out=base/a.batch
    if a.width:prepare(source,out,a.width)
    else:finalize(source,out)

if __name__=='__main__':main()
