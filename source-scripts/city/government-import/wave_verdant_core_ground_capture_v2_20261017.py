"""Capture full current ground and BASIC actors for exact museum-neighbour preservation."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module

BATCH='government-xl-wave-verdant-core-ground-capture-v2-20261017'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
SCOPE=BASE/'government-xl-wave275510-current-native-scope-v1-20261017'
CANDIDATE=BASE/'government-xl-wave275510-verdant-core-terrain-candidate-v2-20261017'

def main():
    assert not DOC.exists()
    refs=[Path(__file__)];pins={}
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [SCOPE,CANDIDATE]:
            result=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result);refs.append(folder/'result.json')
            for r in result['evidenceRefs']:
                assert r['path']not in pins or pins[r['path']]==r['sha256'];pins[r['path']]=r['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    summary=read(CANDIDATE/'summary.json');scope=read(SCOPE/'scope.json');bounds=read(SCOPE/'complete-bounds.json.gz')['rows'];touch=set(scope['touchingNativeUids'])
    candidate=read(CANDIDATE/'terrain-candidates.json')[0]
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    input_data=dict(currentManifestSHA256=digest(manifest.read_bytes()),currentNativeCount=scope['currentNativeActors'],ownUids=['landsd/275510:0','landsd/301560:0'],domain=read(CANDIDATE/'scope.json')['parentExtent'],candidate=candidate,cells=read(ROOT/candidate['path'])['coarseCells'],parentURL='city/data/terrain.json',additionalWholeActorBounds=[box for r in bounds if r['uid']in touch for box in r['completeFourWorldBounds']])
    claim=reservations.claim('museum-full-ground-capture-'+str(uuid.uuid4()),['private-wave-full-ground-capture'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();save(DOC/'input.json.gz',input_data);tool=HERE/'wave_basic_ground_capture_v1_20261017.mjs'
        with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        report=read(DOC/'capture-report.json.gz');assert report['strictExteriorUnchanged']and report['startEndAllInputsVerified']
        for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        refs += [tool,SCOPE/'scope.json',SCOPE/'complete-bounds.json.gz',CANDIDATE/'summary.json']
        record=module('opus_full_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'full-parent-actual-basic-actors-and-native-extent-ground-v1',list(dict.fromkeys(refs)),dict(uids=sorted(touch)+['landsd/275510:0','landsd/301560:0'],completeCurrentForms=report['completeCurrentForms'],basicActors=report['basicActors'],strictExteriorUnchanged=True,fullAcceptance=False,newlyInstalled=0))
        print(dict(jobId=record['jobId'],basicActors=report['basicActors'],roi=report['roi'],strictExteriorUnchanged=True),flush=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
