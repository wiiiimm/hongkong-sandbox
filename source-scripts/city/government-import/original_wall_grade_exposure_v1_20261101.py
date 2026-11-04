"""Prove original grade-crossing walls retain exposed source vertices.

No horizontal cap/closed-solid requirement; no physical acceptance or root credit.
"""
import argparse
import sys
import uuid
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as column_gap


def vertex_exposure(point,ground,lo=None,hi=None):
    point=np.asarray(point,dtype='<f8');ground=np.asarray(ground,dtype='<f8')
    assert point.shape==(3,) and ground.ndim==3 and ground.shape[1:]==(3,3)
    assert np.isfinite(point).all() and np.isfinite(ground).all()
    lo=ground.min(1) if lo is None else lo
    hi=ground.max(1) if hi is None else hi
    ids=np.flatnonzero(np.all(lo[:,[0,2]]<=point[[0,2]],axis=1)&np.all(hi[:,[0,2]]>=point[[0,2]],axis=1))
    result=dict(originalVertex=point.tolist(),completeGroundFaces=len(ground),closedXZBoundsCandidateFaces=list(map(int,ids)),exposed=False)
    if not len(ids):
        return dict(result,reason='No closed candidate; no coverage or exposure credit')
    upper=float(hi[ids,1].max())
    gap=Fraction(float(point[1]))-Fraction(upper)
    if gap>0:
        return dict(result,exposed=True,method='conservative-complete-local-ground-vertex-height-bound',groundUpperBound=upper,exactPositiveGapLowerBoundM=str(gap))
    proofs=[];gaps=[]
    for j in ids:
        proof=column_gap(np.repeat(point[None,:],3,axis=0),ground[j])
        proofs.append(dict(groundFace=int(j),proof=proof))
        if proof['exactClosedHorizontalProjectionsMeet']:
            gaps.append(Fraction(proof['exactMinimumFiniteColumnGapM']))
    return dict(result,exposed=bool(gaps) and min(gaps)>0,method='exact-finite-column-point-query-including-vertical-and-collapsed-ground',exactMinimumFiniteColumnGapM=str(min(gaps)) if gaps else None,pointQueryUsesRepeatedVertexOnlyAsLinearProgramEncoding=True,completeCandidateColumnProofs=proofs,noToleranceOrBufferCredit=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','uid','runtime','attributes','context']:p.add_argument('--'+k,required=True)
    p.add_argument('--lease');a=p.parse_args()
    assert all(n.startswith('government-xl-') and '/'not in n for n in [a.batch,a.runtime,a.attributes,a.context])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert not out.exists()
    if not a.lease:
        assert not local.exists();lp=local/'reservation.json'
        claim=reservations.claim('original-wall-exposure-'+str(uuid.uuid4()),['building:'+a.uid],batch=a.batch,ttl=3600)
        assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--lease',str(lp)])
    lease=read(Path(a.lease));assert reservations.owns(lease)and'building:'+a.uid in lease['resources']
    refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    s=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/s['candidate']['path'];assert digest(asset.read_bytes())==s['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);lo=ground.min(1);hi=ground.max(1);summary=[]
    for mode,tri in worlds.items():
        assert reservations.owns(lease)
        context=take(a.context,base/a.context/(mode+'.json.gz'))
        assert context['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())
        assert context['completeGroundSHA256']==digest(ground.tobytes())
        paths={r['sourceFace']:r for r in context['allWallCapPaths']}
        targets=[i for i,r in paths.items()if not r['hasExactSharedEdgeClearCapPath']]
        grade={c['sourceFaceA'] for c in context['completePositiveGradeContacts']}
        reports=[]
        for i in targets:
            normal=np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]);size=np.linalg.norm(normal)
            assert size>0 and abs(normal[1])<=.25*size
            attempts=[]
            for vertex in sorted(range(3),key=lambda j:(-tri[i,j,1],j)):
                proof=vertex_exposure(tri[i,vertex],ground,lo,hi);attempts.append(dict(sourceVertex=vertex,**proof))
                if proof['exposed']:break
            reports.append(dict(sourceFace=i,hasPositiveActualGradeSurfaceContact=i in grade,hasConservativelyOrExactlyExposedOriginalVertex=any(r['exposed']for r in attempts),originalVertexAttempts=attempts,groundRootCredit=False))
        save(out/(mode+'.json.gz'),dict(mode=mode,sourceWorldSHA256=context['sourceWorldSHA256'],completeGroundSHA256=context['completeGroundSHA256'],rows=reports,rawCapFailuresRetained=True))
        row=dict(mode=mode,targets=len(reports),gradeCrossingAndExposed=sum(r['hasPositiveActualGradeSurfaceContact']and r['hasConservativelyOrExactlyExposedOriginalVertex']for r in reports),remainingSourceFaces=[r['sourceFace']for r in reports if not(r['hasPositiveActualGradeSurfaceContact']and r['hasConservativelyOrExactlyExposedOriginalVertex'])])
        summary.append(row);print(row,flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[a.runtime][str(manifest.relative_to(ROOT))];refs.extend([manifest,HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_packed_world_geometry_20261009.py'])
    result=dict(uids=[a.uid],sourceSHA256=s['sourceSHA256'],rows=summary,sourceGeometryChanges=0,sourcePoseChanges=0,rawCapFailuresRetained=True,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Repeated points encode queries at existing source vertices only; source assets/triangles remain unchanged. Every closed-XZ ground candidate is bounded or exactly tested, including vertical/collapsed primitives. This proves partial exposure and actual grade crossing, not strict whole-face clearance, support, root, architectural/physical or publication approval.')
    assert reservations.owns(lease);save(out/'summary.json',result)
    module('wall_grade_exposure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-original-grade-crossing-wall-vertex-exposure-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
