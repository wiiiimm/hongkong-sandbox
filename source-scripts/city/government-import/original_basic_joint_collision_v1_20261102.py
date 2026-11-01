"""Authenticate and lease complete current scope for simultaneous BASIC probes."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--proposal',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.scope,*a.proposal]);assert len(set(a.proposal))==len(a.proposal)
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    forms=take(a.scope,'form-obligations.json.gz');scope=take(a.scope,'scope.json');assert len(forms)==len({b['uid']for b in forms})==scope['intersectingForms']
    resources={('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms};resources.update('building:'+u for u in scope['uids']);resources.add('terrain:city/data/terrain.json');resources.update('terrain:'+r['url']for r in scope['terrainContacts'])
    leasefile=local/'reservation.json'
    if not a.owned:
        assert not local.exists();claim=reservations.claim('joint-basic-foundation-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],leasefile,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(leasefile);assert reservations.owns(lease)and set(lease['resources'])==resources
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[a.scope][str(manifest.relative_to(ROOT))];refs.append(manifest);hashes={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())}
    for b in forms:
        tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');key=str(tile.relative_to(ROOT));assert digest(tile.read_bytes())==pins[a.scope][key];assert [r for r in read(tile)['buildings']if r['uid']==b['uid']]==[b];hashes[key]=digest(tile.read_bytes());refs.append(tile)
    proposals=[]
    for batch in a.proposal:
        summary=take(batch,'summary.json');b=take(batch,'input.json')['building'];proof=take(batch,'render-proof.json');assert b in forms and b['uid']==summary['uid'];assert summary['installationApproved']is False
        if b['structureType']=='Open-sided Structure':
            assert summary['fullPostFootprintsMeetGround']and summary['wholeRoofClear'];p=take(batch,'proposal.json');assert p['foundationBase']==summary['foundationBase']
            assert all(proof[k]is True for k in ['roofPartsExactlyUnchanged','allXZExactlyUnchanged','onlyIllustrativePostBottomVerticesChanged'])
        else:
            assert b['uid']in ['landsd/309838:0','landsd/339024:0']and b['structureType']=='Temporary Structure';assert summary['fullFootprintGroundCovered']and summary['wholeOriginalRoofClear'];assert proof['originalBodyVerticesAndWindowMasksExactlyUnchanged']is True
        for path,h in proof['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path);hashes[path]=h
        proposals.append(dict(uid=b['uid'],building=b,foundationBase=summary['foundationBase']))
    assert len({p['uid']for p in proposals})==len(proposals)
    kernel=HERE/'basic_foundation_joint_collision_v1_20261102.mjs';refs.append(kernel)
    save(out/'input.json',dict(currentForms=forms,expectedFormCount=len(forms),proposals=proposals,inputHashes=hashes))
    with(out/'worker.log').open('w')as log:subprocess.run(['node',str(kernel),str((out/'input.json').relative_to(ROOT)),str((out/'collision.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(out/'collision.json');assert report['simultaneousBasicFoundationProbesPassed']is True and report['installationApproved']is False
    for path,h in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
    assert reservations.owns(lease)
    result=dict(uids=[p['uid']for p in proposals],forms=len(forms),rows=report['rows'],probes=report['probes'],simultaneousBasicFoundationProbesPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,productionChanges=0,physicalAcceptance=False,collisionReviewApproved=False,jointSceneApproved=False,installationApproved=False,publication=False,qualification=report['qualification'])
    save(out/'summary.json',result);module('joint_basic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-current-scope-simultaneous-basic-foundation-collision-probes-only',list(dict.fromkeys(refs)),result);print(dict(forms=len(forms),proposals=len(proposals),probes=report['probes']),flush=True)
if __name__=='__main__':main()
