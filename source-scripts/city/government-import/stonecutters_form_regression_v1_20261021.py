"""Check all current forms in the replaced wrapper domain against private terrain."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stonecutters-form-regression-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,p):
 r,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
sn='government-xl-stonecutters-regional-scope-v2-20261021';forms=take(sn,BASE/sn/'form-obligations.json.gz');scope=take(sn,BASE/sn/'scope.json');assert len(forms)==scope['intersectingForms']==48
iv='government-xl-stonecutters-current-inventory-v1-20261021';native={r['uid']for r in take(iv,BASE/iv/'complete-bounds.json.gz')['rows']};manifestp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(iv,manifestp);tiles={r['id']:r for r in manifest['tiles']};current={};inputHashes={str(manifestp.relative_to(ROOT)):digest(manifestp.read_bytes())}
for b in forms:
 tid=b['tile'];p=ROOT/'3d-viewer'/tiles[tid]['url']
 if tid not in current:current[tid]={b['uid']:b for b in read(p)['buildings']};inputHashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());refs.append(p)
 assert current[tid][b['uid']]==b
cn='government-xl-stonecutters-private-terrain-v1-20261021';assert take(cn,BASE/cn/'summary.json')['terrainValidationPassed'];patches=take(cn,BASE/cn/'terrain-candidates.json')
inputs=dict(inputHashes=inputHashes,candidateIds=['landsd/127037:0'],patches=patches,rows=[dict(building=b,existingNative=b['uid']in native,patchIndexes=[0])for b in forms]);save(DOC/'neighbour-inputs.json.gz',inputs)
tool=HERE/'check-neighbours.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(DOC.relative_to(ROOT))+'/']
with(DOC/'worker.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
assert p.returncode==0;result=read(DOC/'neighbour-checks.json');assert len(result['rows'])==48
for path,h in {**result['inputHashes'],**inputHashes}.items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
flagged=[r for r in result['rows']if r['reasons']];summary=dict(uids=['landsd/127037:0'],forms=len(forms),flagged=flagged,ordinaryFlagged=sum(not r['existingNative']for r in flagged),installationApproved=False)
save(DOC/'summary.json',summary);r=module('china_form_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-current-wrapper-form-regression',list(dict.fromkeys(refs+[tool])),summary);print(dict(jobId=r['jobId'],forms=len(forms),flagged=len(flagged),ordinaryFlagged=summary['ordinaryFlagged']),flush=True)
