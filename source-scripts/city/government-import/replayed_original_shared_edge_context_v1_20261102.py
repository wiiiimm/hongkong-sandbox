"""Freeze a fresh replayable shared-edge context; never approve publication."""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_terrain_shared_edge_v1_20261102 import verify

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','prior']:p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.prior])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json';assert not out.exists()
    _,pins=authenticate(base/a.prior);refs=[Path(__file__),base/a.prior/'result.json']
    def take(binding):
        path=ROOT/binding['path'];assert digest(path.read_bytes())==binding['sha256']==pins[binding['path']];refs.append(path);return read(path)
    path=base/a.prior/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);context=read(path)
    scope,candidate,parent=[take(context[k])for k in ['scopeBinding','candidateBinding','parentBinding']]
    old={b['url']:take(b)for b in context['oldTerrainBindings']}
    resources={'terrain:city/data/terrain.json'}|{'terrain:'+u for u in old}|{'building:'+u for u in scope['uids']}
    for node in old.values():resources.update('building:'+u for u in node['meta']['targetUids'])
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('replay-shared-edge-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==context['currentManifestSHA256']==pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
    replay=verify(scope,candidate,parent,old);assert replay['rows']==context['rows']
    result={**context,**replay,'admissionGranted':False,'qualification':'Explicit replayable shared-edge context using the unchanged finite boundary limit and all current source/parent/candidate/old-terrain hashes. No geometry changes or model/publication approval.'}
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['original_terrain_shared_edge_v1_20261102.py','coordinated_native_boundary_v1_20261023.py','original_terrain_point_contact_v1_20261025.py','test_original_terrain_shared_edge_v1_20261102.py']);refs.append(ROOT/'3d-viewer/city/native-terrain.js')
    assert reservations.owns(lease)
    module('replayed_shared_edge_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'replayed-original-shared-edge-context-no-publication',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
