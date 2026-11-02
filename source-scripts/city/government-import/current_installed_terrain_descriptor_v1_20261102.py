"""Bind one current installed terrain leaf for complete envelope scoping only.

The descriptor references existing bytes. No geometry, targets, acceptance flags,
source reviews or public files change; it is not an approved private candidate.
"""
import argparse,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','inventory','terrain-url']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.inventory])
    assert a.terrain_url.startswith('city/data/')and'..'not in a.terrain_url
    out=BASE/a.batch;lp=HERE/'local'/(a.batch+'-control')/'reservation.json';assert not out.exists()
    _,pins=authenticate(BASE/a.inventory);manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==pins[str(manifest.relative_to(ROOT))]
    assert a.terrain_url in {r['url']for r in read(manifest)['terrainPatches']}
    path=ROOT/'3d-viewer'/a.terrain_url;node=read(path);sha=digest(path.read_bytes());uids=node['meta']['targetUids'];assert uids and len(set(uids))==len(uids)and not node.get('patches')and not node.get('children')
    resources={'building:'+u for u in uids}|{'terrain:'+a.terrain_url,'terrain:city/data/terrain.json'}
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('current-terrain-descriptor-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
    root=ROOT/'3d-viewer/city/data/terrain.json';assert node['meta']['parentTerrain']=='city/data/terrain.json'and node['meta']['parentSha256']==digest(root.read_bytes())
    refs=[__file__,BASE/a.inventory/'result.json',manifest,path,root];owners=[]
    for url in read(manifest)['officialModelCatalogues']:
        cat=ROOT/'3d-viewer'/url
        for entry in read(cat)['models']:
            if entry['uid']in uids:
                assert digest(cat.read_bytes())==pins[str(cat.relative_to(ROOT))];asset=cat.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];owners.append(entry['uid']);refs.extend([cat,asset])
    assert len(owners)==len(set(owners))==len(uids)and set(owners)==set(uids)
    result=dict(uids=uids,candidate=dict(path=str(path.relative_to(ROOT)),sha256=sha),currentManifestSHA256=mh,status='current-installed-terrain-scope-descriptor-only',descriptorOnly=True,sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,physicalAcceptance=False,publication=False,qualification='Exact existing native leaf only, for full affected-domain nomination. Not a new candidate, source identity approval or change to installed target metadata.')
    save(out/'summary.json',result);assert reservations.owns(lease)and digest(manifest.read_bytes())==mh and digest(path.read_bytes())==sha
    from pathlib import Path
    module('current_terrain_descriptor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-installed-native-leaf-read-only-scope-descriptor',list(dict.fromkeys(Path(p)for p in refs)),result)
if __name__=='__main__':main()
