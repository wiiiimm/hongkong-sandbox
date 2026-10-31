"""Record ROOT's explicitly named, already-inspected private sheets; no publication approval."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','sheets','browser','observation']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--viewed-sheet',action='append',required=True);a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
    for name in [a.sheets,a.browser]:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
    path=base/a.sheets/'summary.json';assert digest(path.read_bytes())==pins[a.sheets][str(path.relative_to(ROOT))];sheets=read(path);refs.append(path);browser=read(base/a.browser/'result.json');assert browser['allBrowserDiagnosticsPassed']and sheets['browserBatch']==a.browser and sheets['mode']=='staged'
    assert len(a.viewed_sheet)==len(set(a.viewed_sheet));wanted=set(a.viewed_sheet);available={Path(r['path']).name:r for r in sheets['sheets']};assert wanted<=set(available);images=[];viewed=[]
    for name in a.viewed_sheet:
        r=available[name];p=ROOT/r['path'];assert r['scale']==1 and not r['cropped']and digest(p.read_bytes())==r['sha256']==pins[a.sheets][r['path']];refs.append(p);viewed.append(dict(path=r['path'],sha256=r['sha256']))
        for image in r['sourceImages']:
            p=ROOT/image['path'];assert digest(p.read_bytes())==image['sha256']==pins[a.sheets][image['path']]==pins[a.browser][image['path']];refs.append(p);images.append(image)
    assert len(images)==len({r['path']for r in images})
    note=(ROOT/a.observation).resolve();assert note.is_relative_to(base);observation=read(note);assert observation['reviewer']=='ROOT'and observation['browser']==a.browser and observation['sheets']==a.sheets;refs.append(note)
    complete=wanted==set(available);result=dict(uids=browser['uids'],reviewer='ROOT',browserBatch=a.browser,sheetsBatch=a.sheets,viewedSheets=viewed,sourceExportsActuallySeenWithinSheets=images,completePrivateExportObservation=complete,observations=observation['observations'],sourceGeometryChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='ROOT explicitly supplied only sheets actually opened. Exact unscaled uncropped sheets and every represented original export are hash-bound to both completed receipts. This records visual observation, not architectural/physical acceptance or installation approval.')
    save(out/'ROOT-PRIVATE-EXPORT-OBSERVATION.json',result);module('root_private_sheet_observation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-explicit-private-browser-sheet-observation',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
