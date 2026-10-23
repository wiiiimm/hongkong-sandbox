"""Exact finite-facade association of every existing boundary edge; no mount approval."""
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','context','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch;out=ROOT/'docs/astra-city/government-import'/a.batch;assert not out.exists();base=out.parent;refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    old=take(a.context,base/a.context/'summary.json');assert old['uids']==[a.uid]and not old['visualRoleAccepted'];row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==attr['sourceSHA256']==old['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds=dict(original=decode_original_world_triangles(raw),**{n:np.asarray(attr[k]).reshape(-1,3)[ix]for n,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]});cached={};bindings=[]
    for mode,tri in worlds.items():
        assert len(tri)==row['triangles'];sha=digest(tri.tobytes());assert next(b['completeSourceWorldSHA256']for b in old['coordinateBindings']if b['mode']==mode)==sha;bindings.append(dict(mode=mode,completeSourceWorldSHA256=sha))
        if sha in cached:continue
        prior=old['distinctWorlds'][sha];records=[]
        for group in prior['groups']:
            n=group['group'];context=take(a.context,base/a.context/(prior['proofMode']+'-group-'+str(n)+'.json.gz'));ids=context['completeOriginalFaceIds'];hostids=context['sameSourceMainGroupHostFaceIds'];hosts=tri[hostids];edges=defaultdict(list)
            for i in ids:
                v=[tuple(p)for p in tri[i]]
                for x,y in zip(v,v[1:]+v[:1]):
                    if x!=y:edges[tuple(sorted((x,y)))].append(i)
            boundary=[(e,owners[0])for e,owners in edges.items()if len(owners)==1];proofs=[]
            for edge,owner in boundary:
                proof=edge_band(np.asarray(edge),hosts)if len(hosts)else None;proofs.append(dict(originalBoundaryEdge=[list(v)for v in edge],originalOwnerFace=owner,proof=proof,passed=bool(proof and proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'])))
            result=dict(group=n,completeOriginalFaceIds=ids,sameSourceMainGroupHostFaceIds=hostids,nonzeroBoundaryEdges=len(boundary),nonmanifoldNonzeroEdges=sum(len(v)>2 for v in edges.values()),completeBoundaryProofs=proofs,allNonzeroBoundaryEdgesWithinFixedBand=bool(proofs)and all(p['passed']for p in proofs));save(out/(mode+'-group-'+str(n)+'.json.gz'),result);records.append(dict(group=n,faces=len(ids),boundaryEdges=len(boundary),passingBoundaryEdges=sum(p['passed']for p in proofs),allBoundaryEdgesAssociated=result['allNonzeroBoundaryEdgesWithinFixedBand']));print(dict(mode=mode,**records[-1]),flush=True)
        cached[sha]=dict(proofMode=mode,groups=records,groupsWithCompleteBoundaryAssociation=sum(r['allBoundaryEdgesAssociated']for r in records))
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],coordinateBindings=bindings,distinctWorlds=cached,separateOriginalGroups=old['separateOriginalGroups'],sourceGeometryChanges=0,sourcePoseChanges=0,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every original nonzero one-incidence boundary edge is tested over its complete closed interval against finite same-source main-body facades under unchanged0.1m Euclidean distance. No new edge, backing plane, source welding, point-only load bridge or automatic mount role. Closed/no-boundary and partial failures remain unqualified.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py']);module('separate_boundary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-separate-group-finite-facade-boundary-context',refs,result)


if __name__=='__main__':main()
