"""Freeze a completed desktop and failed mobile attempt without partial approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from completed_viewport_contract_v1_20261023 import validate_completed


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-browser-v2-terminal-evidence-v1-20261023';out=base/batch;assert not out.exists();failed='government-xl-island-cheong-shing-four-original-private-browser-v2-20261023';local=HERE/'local'/failed;assert not reservations.owns(read(local/'reservation.json'))
    wrapper='government-xl-island-cheong-shing-private-browser-retry-v2-20261023';r,_=authenticate(base/wrapper);assert r['exitCode']==1 and r['status']=='private-device-observation-or-script-investigation'
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs=[Path(__file__),base/wrapper/'result.json',manifest];sources={m['uid']:m for m in read(local/'catalogue.json')['models']};cfg=read(local/'browser-config-390.json');uids=set(cfg['additionalRetainedUids']);assert len(sources)==4 and len(uids)==32;retained={}
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;refs.append(p)
        for m in read(p)['models']:
            if m['uid']in uids:
                assert m['uid']not in retained;asset=p.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256'];refs.append(asset);retained[m['uid']]=m
    assert set(retained)==uids;desktop=read(base/failed/'1280/staged-browser.json');validate_completed(desktop,1280,sources,retained);mobile=read(base/failed/'390/staged-browser.json');assert not mobile.get('passed')and mobile['errors']==['page.waitForFunction: Timeout 120000ms exceeded.'];assert len(mobile['retainedNativeOwnViews'])==36
    runtime='government-xl-island-cheong-shing-four-original-runtime-v4-20261023';_,pins=authenticate(base/runtime);sp=base/runtime/'selection.json.gz';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))];assert digest(manifest.read_bytes())==read(sp)['manifestSHA256'];refs.extend([base/runtime/'result.json',sp])
    refs.extend(p for folder in [base/failed,local]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json');refs.extend(HERE/n for n in ['completed_viewport_contract_v1_20261023.py','test_completed_viewport_contract_v1_20261023.py'])
    result=dict(uids=sorted(sources),sourceSHA256ByUid={u:m['sha256']for u,m in sources.items()},retainedSourceSHA256ByUid={u:m['sha256']for u,m in retained.items()},completedViewportWidths=[1280],incompleteViewportWidths=[390],incompleteMobileRetainedViews=36,requiredRetainedViewsPerViewport=64,failingRetainedActor='landsd/106413:0',failure='Retained detailed activation wait exceeded120000ms; source views/failure recovery and desktop complete, full mobile viewport not complete',oldLeaseReleased=True,currentManifestSHA256=digest(manifest.read_bytes()),sourceGeometryChanges=0,sourceCorruptionProved=False,permanentRejection=False,visualAcceptance=False,installationApproved=False)
    save(out/'summary.json',result);module('v2_terminal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-private-desktop-completion-and-mobile-activation-timeout',refs,result)

if __name__=='__main__':main()
