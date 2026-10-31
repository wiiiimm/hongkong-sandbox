"""Create labelled inspection aids; original live PNG exports remain untouched."""
from pathlib import Path
from PIL import Image,ImageDraw
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
BASE=ROOT/'docs/astra-city/government-import';INSTALL='government-xl-fuying181489-five-member-original-installed-v1-20261029';OUT=BASE/'government-xl-fuying181489-five-member-live-review-aids-v1-20261029'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not OUT.exists();receipt,pins=authenticate(BASE/INSTALL);assert receipt['newlyInstalled']==1
    sheets=[];images=[]
    for width in [390,1280]:
        folder=BASE/INSTALL/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed']and len(report['retainedNativeOwnViews'])==18
        for time in ['15:00','22:00']:
            views=sorted([v for v in report['retainedNativeOwnViews']if v['time']==time],key=lambda v:v['uid']);assert len(views)==9
            cell=(195,450)if width==390 else(512,360);canvas=Image.new('RGB',(3*cell[0],3*(cell[1]+24)),(245,245,245));draw=ImageDraw.Draw(canvas);cells=[]
            for i,v in enumerate(views):
                path=folder/v['file'];q=ref(path);assert q['sha256']==pins[q['path']]
                with Image.open(path)as original:
                    assert original.size==(width,900)
                    preview=original.convert('RGB');preview.thumbnail(cell,Image.Resampling.LANCZOS)
                    x=(i%3)*cell[0];y=(i//3)*(cell[1]+24);draw.text((x+4,y+4),v['uid']+' '+time,fill=(0,0,0));canvas.paste(preview,(x+(cell[0]-preview.width)//2,y+24))
                images.append(q);cells.append(dict(column=i%3,row=i//3,original=q))
            OUT.mkdir(parents=True,exist_ok=True);path=OUT/(str(width)+'-'+time.replace(':','')+'-retained-contact-sheet.png');canvas.save(path)
            sheets.append(dict(image=ref(path),width=width,time=time,cells=cells))
    assert len(images)==len({q['path']for q in images})==36
    save(OUT/'review-aids.json',dict(installationJobId=receipt['jobId'],originalsUntouched=True,sourcePNGsInspectedSeparately=True,sheets=sheets,qualification='Scaled labelled contact sheets for whole-model visibility/placement/terrain-regression inspection. No pixel-level facade or performance claim. Full native geometry/actor identity/framing/HTTP and terrain checks remain in the live reports. These aids do not constitute review until ROOT actually opens them.'))
    print(dict(contactSheets=4,retainedOriginalPNGs=36,output=str(OUT.relative_to(ROOT))))
if __name__=='__main__':main()
