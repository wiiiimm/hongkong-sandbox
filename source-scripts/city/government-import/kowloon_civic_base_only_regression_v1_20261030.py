"""Measure every current BASIC in the new terrain region with all originals absent."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-kowloon-city-civic-five-after-fuying-';BATCH=PREFIX+'base-only-regression-v1-20261030';PRIOR=PREFIX+'full-five-form-checks-v1-20261030';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def main():
    if '--owned'not in sys.argv:
        assert not DOC.exists()and not LOCAL.exists();inputs=read(BASE/PRIOR/'neighbour-inputs.json.gz');keys=sorted({'building:'+r['building']['uid']for r in inputs['rows']}|{'terrain:city/data/terrain.json'})
        claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();_,pins=authenticate(BASE/PRIOR);path=BASE/PRIOR/'neighbour-inputs.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];inputs=read(path);original_candidates=inputs['candidateIds'];assert len(original_candidates)==5
    for path,sha in inputs['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    inputs['candidateIds']=[];save(DOC/'neighbour-inputs.json.gz',inputs);tool=HERE/'check-neighbours.mjs'
    with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(DOC/'neighbour-checks.json');assert len(report['rows'])==len(inputs['rows'])and all(not r['candidate']for r in report['rows'])
    refs=[Path(__file__),BASE/PRIOR/'result.json',BASE/PRIOR/'neighbour-inputs.json.gz',tool]
    for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    result=dict(uids=original_candidates,originalsAvailable=False,allCurrentBasicsChecked=True,forms=len(report['rows']),flagged=[r for r in report['rows']if r['reasons']],sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Explicit Base-only counterfactual: zero candidate exemptions, unchanged8BASIC forms/current tile and exact proposed terrain. Every raw regression retained for original-failure/Base-only/eviction review. No source, fallback geometry, terrain, policy or approval change.')
    save(DOC/'summary.json',result);assert reservations.owns(lease);module('civic_base_only_regression_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-BASIC-regression-with-all-originals-absent',refs,result);print(dict(forms=result['forms'],flags=[(r['uid'],r['reasons'])for r in result['flagged']]),flush=True)
if __name__=='__main__':main()
