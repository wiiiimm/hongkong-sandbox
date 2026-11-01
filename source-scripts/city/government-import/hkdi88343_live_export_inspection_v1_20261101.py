"""Bind eight actual ROOT-inspected live exports; never infer inspection."""
import argparse, os
from pathlib import Path
from run import ROOT, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from hkdi88343_installed_parent_contract_v1_20261101 import UID, PARENT, SHA, PSHA

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--observation',required=True);a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath)
    assert cfg['sources']=={UID:SHA} and cfg['retainedNativeUids']==[PARENT]
    folder=base/(cfg['prefix']+'-original-installed-v1-'+cfg['date']);receipt,pins=authenticate(folder)
    assert receipt['sourceSHA256ByUid']=={UID:SHA} and receipt['publication'] and receipt['newlyInstalled']==1
    observation=(ROOT/a.observation).resolve();assert observation.is_relative_to(base);seen=read(observation)
    assert seen['reviewer']=='Codex ROOT' and seen['allDeclaredExportsActuallyInspected'] is True and seen['limitations']
    images=[];retained=[]
    for width in [390,1280]:
        reportpath=folder/('viewport-'+str(width))/'live-browser.json';report=read(reportpath)
        assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))] and report['passed'] and not report['errors']
        for field,target,uid,sha in [('views',images,UID,SHA),('retainedNativeOwnViews',retained,PARENT,PSHA)]:
            rows=[v for v in report[field]if 'time'in v];assert len(rows)==2
            for v in rows:
                assert v['uid']==uid and v['sourceSHA256']==sha and v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces'] and not v['overflow']
                assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
                if uid==UID:assert v['pick']==v['collision']==UID and v['solidAppearance']
                path=reportpath.parent/v['file'];item=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=uid,width=width,time=v['time'])
                assert pins[item['path']]==item['sha256'];target.append(item)
    for field,rows in [('sourceImagesActuallyViewed',images),('retainedImagesActuallyViewed',retained)]:
        assert len(rows)==len(seen[field])==4 and {(r['path'],r['sha256'])for r in rows}=={(r['path'],r['sha256'])for r in seen[field]}
    target=folder/'ROOT-LIVE-EXPORT-INSPECTION.json';assert not target.exists()
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    save(target,dict(reviewer='ROOT',visualAcceptance=True,producer=ref(Path(__file__)),imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,
        inspectionSheetsActuallyViewed=[],inspectionMethod='All eight actual live PNG canvases opened directly',observations=seen['limitations'],boundObservation=ref(observation),aiGeometryModelling=False))
    print(dict(sourceImages=4,retainedImages=4,installedJobId=receipt['jobId']))
if __name__=='__main__':main()
