"""Compose all exact live source/retained canvases into per-actor four-panel sheets.
No image rescaling, model processing, acceptance, publication or source changes.
"""
import argparse
from pathlib import Path
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont
from run import ROOT,read,save,digest

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    config=(ROOT/a.config).resolve();out=(ROOT/a.out).resolve();base=ROOT/'docs/astra-city/government-import';assert config.is_relative_to(base)and out.is_relative_to(base)and not out.exists()
    cfg=read(config);batch=cfg['prefix']+'-original-installed-'+cfg.get('installVersion','v1')+'-'+cfg['date'];installed=base/batch
    receipt=read(installed/'result.json');assert receipt['publication']and receipt['sourceSHA256ByUid']==cfg['sources'];expected=set(cfg['sources'])|set(cfg['retainedNativeUids']);groups=defaultdict(list);reports=[]
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    for w in [1280,390]:
        reportpath=installed/('viewport-'+str(w))/'live-browser.json';report=read(reportpath);assert report['passed']and not report['errors'];reports.append(ref(reportpath))
        values=[v for v in report['views']if'time'in v]+report['retainedNativeOwnViews'];assert len(values)==2*len(expected)and{v['uid']for v in values}==expected
        for v in values:
            path=reportpath.parent/v['file'];groups[v['uid']].append(dict(**ref(path),uid=v['uid'],width=w,time=v['time']))
    assert set(groups)==expected;out.mkdir();font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);rows=[]
    for uid,panels in sorted(groups.items()):
        assert len(panels)==4 and{(v['width'],v['time'])for v in panels}=={(w,t)for w in [1280,390]for t in ['15:00','22:00']}
        sheet=Image.new('RGB',(1670,1848),'#20252e');draw=ImageDraw.Draw(sheet)
        for panel in panels:
            image=Image.open(ROOT/panel['path']);assert image.size==(panel['width'],900)
            if image.mode=='RGBA':assert image.getchannel('A').getextrema()==(255,255)
            image=image.convert('RGB');x=0 if panel['width']==1280 else 1280;y=0 if panel['time']=='15:00' else 924
            draw.text((x+4,y+2),uid+' '+str(panel['width'])+' '+panel['time'],font=font,fill='white');sheet.paste(image,(x,y+24));panel['position']=[x,y+24]
        path=out/(uid.replace('/','-').replace(':','-')+'.png');sheet.save(path);rows.append(dict(**ref(path),uid=uid,panels=panels))
    bindings=dict(fullFramesPreserved=True,exportedSourceImagesModified=False,reports=reports,rows=rows,producer=ref(Path(__file__)),installationApproved=False,publication=False)
    save(out/'inspection-bindings.json',bindings);save(out/'inspection-config.json',{**cfg,'installedBatch':batch});print(dict(sourceAndRetainedExports=sum(len(r['panels'])for r in rows),sheets=len(rows)))
if __name__=='__main__':main()
