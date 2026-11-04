"""Check the retained current basic podium path, without importing podium geometry."""
from copy import deepcopy
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-remaining-current-basic-podium-contacts-v1-20261023';out=base/batch;assert not out.exists();prior='government-xl-remaining-floating-podium-discovery-v1-20261023';receipt,pins=authenticate(base/prior)
    path=base/prior/'support-candidates.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];rows=deepcopy(read(path));refs=[Path(__file__),base/prior/'result.json',path]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==receipt['manifestSHA256'];refs.append(manifest)
    for row in rows:
        r=row['source'];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
        r['candidate']['entry']['proceduralWindows']=False
        for f in [r['source'],row['supportForm']]:
            p=ROOT/'3d-viewer'/f['tile'];assert digest(p.read_bytes())==f['tileSHA256'];assert[f['building']]==[b for b in read(p)['buildings']if b['uid']==f['building']['uid']];refs.append(p)
    save(out/'input.json.gz',dict(rows=rows,manifestSHA256=receipt['manifestSHA256'],evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in dict.fromkeys(refs)]))
    tool=HERE/'current_basic_podium_original_contact_v1_20261023.mjs'
    with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(out/'checks.json.gz');assert len(report['rows'])==len(rows)
    for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    compact=[dict(uid=r['uid'],supportUid=r['supportUid'],canonicalContactPassed=r['canonicalContactPassed'],usableBasicSupportDiagnostic=r['usableBasicSupportDiagnostic'],basicIsCurrentFinalSupport=r['basicIsCurrentFinalSupport'],samples=r['proof']['samples'],strictContacts=r['proof']['strictContacts'],unresolved=len(r['proof']['unresolved']))for r in report['rows']]
    result=dict(uids=[r['uid']for r in rows],pairs=len(rows),canonicalContactPassed=sum(r['canonicalContactPassed']for r in compact),usableBasicSupportDiagnostics=sum(r['usableBasicSupportDiagnostic']for r in compact),rows=compact,sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,status='current-basic-podium-original-tower-contact-diagnostics',qualification='Production constructor for every exact current basic podium, actual original tower loader and canonical source interface. Native support actors are identified from the current catalogues: basic-only passes never replace a currently installed detailed support requirement. Full support stability, all-world, collision, identity, scene/browser and publication remain unapproved.')
    save(out/'summary.json',result);refs.append(tool);module('current_basic_podium_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-basic-podium-original-tower-canonical-contacts',list(dict.fromkeys(refs)),result);print({k:result[k]for k in ['pairs','canonicalContactPassed','usableBasicSupportDiagnostics']},flush=True)

if __name__=='__main__':main()
