"""Preserve a terminal private observation timeout without granting model credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-first-browser-terminal-evidence-v1-20261023';out=base/batch;assert not out.exists();failed='government-xl-island-cheong-shing-four-original-private-browser-v1-20261023';local=HERE/'local'/failed;lease=read(local/'reservation.json');assert not reservations.owns(lease)
    chain='government-xl-island-cheong-shing-repaired-acceptance-chain-v1-20261023';r,_=authenticate(base/chain);assert r['stoppedAt']=='browser'and r['exitCode']!=0
    log=(base/chain/'browser.log').read_text();assert 'TimeoutExpired'in log and '1199.999'in log
    assert not(base/failed/'1280/staged-browser.json').exists()and not(base/failed/'390/staged-browser.json').exists()
    runtime='government-xl-island-cheong-shing-four-original-runtime-v4-20261023';_,pins=authenticate(base/runtime);p=base/runtime/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];selection=read(p);manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']
    refs=[Path(__file__),base/chain/'result.json',base/runtime/'result.json',p,manifest,HERE/'selected_original_coordinated_staged_browser_v1_20261023.py',ROOT/'docs/astra-city/government-import/government-xl-scripted-continuation-20261023/island-cheong-shing-first-browser-terminal-cleanup-v1.json']
    refs.extend(p for folder in [base/failed,local]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json')
    result=dict(uids=[r['uid']for r in selection['rows']],failure='Private desktop subprocess observation timed out after1200seconds; full viewport report absent',partialExportImages=len(list((base/failed/'1280').glob('*.png'))),viewportReportsCompleted=0,oldLeaseReleased=True,publicManifestUnchanged=True,sourceGeometryChanges=0,sourceCorruptionProved=False,permanentRejection=False,visualAcceptance=False,installationApproved=False)
    save(out/'summary.json',result);module('terminal_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'terminal-private-browser-observation-failure-evidence',refs,result)

if __name__=='__main__':main()
