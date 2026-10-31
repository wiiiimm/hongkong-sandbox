"""Record ROOT's accepted live exports after ROOT actually opens every image.

Never call automatically from an installer. The explicit flag attests completed
visual inspection; report checks cannot replace actually viewing the images.
This version requires an empty retained-native set, independently fenced by the
installation config/review. Nonempty cases need their full retained own-views.
"""
import argparse,os
from pathlib import Path
from run import ROOT,read,save,digest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--accept-exports-actually-viewed-by-root',action='store_true',required=True)
    p.add_argument('--observation',action='append',required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import'
    config=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert config.is_relative_to(base)
    cfg=read(config);assert cfg['retainedNativeUids']==[]
    installed=base/(cfg['prefix']+'-original-installed-'+cfg.get('installVersion','v1')+'-'+cfg['date'])
    assert installed.is_relative_to(base) and installed.exists()
    images=[]
    for w in [390,1280]:
        folder=installed/('viewport-'+str(w));report=read(folder/'live-browser.json');assert report['passed'] and not report['errors'] and report['retainedNativeOwnViews']==[]
        for v in [v for v in report['views'] if 'time' in v]:
            assert v['uid'] in cfg['sources'] and v['sourceSHA256']==cfg['sources'][v['uid']] and v['pick']==v['collision']==v['uid'] and v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
            path=(folder/v['file']).resolve();assert path.is_relative_to(folder)
            images.append(dict(uid=v['uid'],width=w,time=v['time'],path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    assert len(images)==len({i['path'] for i in images})==4*len(cfg['sources'])
    assert {(i['uid'],i['width'],i['time']) for i in images}=={(u,w,t) for u in cfg['sources'] for w in [390,1280] for t in ['15:00','22:00']}
    producer=Path(__file__).resolve()
    save(installed/'ROOT-LIVE-EXPORT-INSPECTION.json',dict(reviewer='ROOT',visualAcceptance=True,producer=dict(path=str(producer.relative_to(ROOT)),sha256=digest(producer.read_bytes())),imagesActuallyViewed=images,retainedImagesActuallyViewed=[],inspectionSheetsActuallyViewed=[],inspectionMethod='Every original individual exported canvas image opened by ROOT; no substitute contact-sheet claim.',observations=a.observation))
    print(dict(exportsActuallyViewed=len(images),visualAcceptance=True))

if __name__=='__main__':main()
