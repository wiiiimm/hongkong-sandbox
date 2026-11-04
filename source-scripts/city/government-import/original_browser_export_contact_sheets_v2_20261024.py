"""Make hash-bound full-frame inspection previews; never approve browser exports."""
import argparse,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from run import ROOT,read,save,digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--report',required=True);p.add_argument('--include-retained',action='store_true');p.add_argument('--output',required=True);p.add_argument('--width',type=int,choices=[390,1280],required=True);a=p.parse_args();reportpath=(ROOT/a.report).resolve();out=(ROOT/a.output).resolve();base=ROOT/'docs/astra-city/government-import';assert reportpath.is_relative_to(base)and out.is_relative_to(base);report=read(reportpath);assert report['passed']and not report['errors'];views=[dict(v,inspectionKind='new-source')for v in report['views']if 'time'in v];views += [dict(v,inspectionKind='retained-original')for v in report.get('retainedNativeOwnViews',[])] if a.include_retained else [];uids={v['uid']for v in views};assert len(views)==2*len(uids)and all(v['width']==a.width for v in views);out.mkdir(parents=True,exist_ok=True);records=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
    for time in ['15:00','22:00']:
        chosen=[v for v in views if v['time']==time];assert len(chosen)==len(uids);sheet=Image.new('RGB',(1920,480*math.ceil(len(chosen)/3)),'white');draw=ImageDraw.Draw(sheet);panels=[]
        for n,v in enumerate(chosen):
            path=(reportpath.parent/v['file']).resolve();assert path.is_relative_to(base);image=Image.open(path);original=image.size;image.thumbnail((640,450));x=n%3*640;y=n//3*480;sheet.paste(image,(x,y+30));draw.text((x+6,y+6),v['uid']+' '+str(a.width)+' '+time,fill='black',font=font);panels.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=v['uid'],inspectionKind=v['inspectionKind'],sourceSHA256=v['sourceSHA256'],time=time,originalDimensions=list(original),previewDimensions=list(image.size)))
        dest=out/(str(a.width)+'-'+time.replace(':','')+'.jpg');assert not dest.exists();sheet.save(dest,quality=94);records.append(dict(sheet=str(dest.relative_to(ROOT)),sha256=digest(dest.read_bytes()),panels=panels,inspectionDisplay='Aspect-preserving whole-frame previews, at most640x450. Original exports untouched; inspect original resolution if appearance is ambiguous.',visualAcceptance=False))
    save(out/(str(a.width)+'-panel-bindings.json'),dict(report=dict(path=str(reportpath.relative_to(ROOT)),sha256=digest(reportpath.read_bytes())),producer=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=digest(Path(__file__).read_bytes())),rows=records,visualAcceptance=False));print([r['sheet']for r in records],flush=True)

if __name__=='__main__':main()
