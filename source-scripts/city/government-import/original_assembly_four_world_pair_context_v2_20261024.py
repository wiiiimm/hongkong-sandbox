"""Complete four-world pair contacts for an explicit original assembly of up to16 actors; no approval."""
import argparse
from itertools import combinations
from collections import Counter
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from primrose_compound_foundation_v2_20261015 import module

BASE=ROOT/'docs/astra-city/government-import'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes']:parser.add_argument('--'+key,required=True)
    args=parser.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [args.batch,args.runtime,args.attributes])
    out=BASE/args.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=args.runtime;attrs=args.attributes
    selection=take(runtime,BASE/runtime/'selection.json.gz');attributes={r['uid']:r for r in take(attrs,BASE/attrs/'attributes.json.gz')['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    worlds={};hashes={}
    for r in selection['rows']:
        uid=r['uid'];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);a=attributes[uid];assert a['sourceSHA256']==r['sourceSHA256'];ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(a[field]).reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]});hashes[uid]=r['sourceSHA256']
    assert 2<=len(worlds)<=16
    pair_count=len(worlds)*(len(worlds)-1)//2
    summaries=[]
    for u,v in combinations(sorted(worlds),2):
        for mode in ['original','literal','leftF32','balancedF32']:
            a,b=worlds[u][mode],worlds[v][mode];gaps=np.maximum(a.min((0,1))-b.max((0,1)),b.min((0,1))-a.max((0,1)))
            if np.any(gaps>0):
                row=dict(uid=u,peerUid=v,mode=mode,strictBoundsSeparated=True,axisGapsM=gaps.tolist(),completeSourceFaces=len(a),completePeerFaces=len(b))
            else:
                raw=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))));path=out/(u.split('/')[1]+'--'+v.split('/')[1]+'--'+mode+'.json.gz');save(path,raw)
                row=dict(uid=u,peerUid=v,mode=mode,strictBoundsSeparated=False,completeSourceFaces=len(a),completePeerFaces=len(b),contactDimensions=dict(Counter(str(c['dimension'])for c in raw['contacts'])),positiveSurfaceContacts=sum(c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in raw['contacts']),rawPath=str(path.relative_to(ROOT)))
            summaries.append(row);print(row,flush=True)
    assert len(summaries)==pair_count*4 and digest(manifest.read_bytes())==selection['manifestSHA256']
    result=dict(uids=sorted(worlds),sourceSHA256ByUid=hashes,rows=summaries,completeUnorderedPairs=pair_count,coordinateModes=4,installationApproved=False,physicalAcceptance=False,sourceGeometryChanges=0,qualification='All complete original source pairs in all four renderer coordinate streams. Strict disjoint bounds or exact finite surface/degenerate contact evidence; no related ownership, architecture or collision approval.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py'])
    module('yoho_pair_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'complete-four-world-original-assembly-pair-context',refs,result)

if __name__=='__main__':main()
