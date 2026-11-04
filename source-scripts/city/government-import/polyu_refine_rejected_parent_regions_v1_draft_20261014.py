"""Bounded own-parent subdivision; rejected terrain stays uncredited, no point fit."""
from fractions import Fraction as F
from collections import deque
import hashlib
import numpy as np
from polyu_compatible_current_parent_regions_v1_draft_20261014 import downward_parent_pieces,compatible_piece

def refine(poly,parent,worlds,*,max_depth=12,max_attempts=2048,packer=downward_parent_pieces,checker=compatible_piece):
    assert type(max_depth)is int and 0<=max_depth<=20
    assert type(max_attempts)is int and 0<max_attempts<=16384
    points=[tuple(F(v)for v in p)for p in poly];assert len(points)>=3 and all(len(p)==3 for p in points)
    a,b,c=[tuple(F(v)for v in p)for p in parent]
    u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
    n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]!=0
    assert all(sum(n[k]*(p[k]-a[k])for k in range(3))==0 for p in points)
    turns=[(q[0]-p[0])*(z[2]-q[2])-(q[2]-p[2])*(z[0]-q[0])for p,q,z in zip(points,points[1:]+points[:1],points[2:]+points[:2])]
    assert any(turns)and (all(v>=0 for v in turns)or all(v<=0 for v in turns)),'saved ideal region must be convex'
    area=lambda t:abs(sum(p[0]*q[2]-p[2]*q[0]for p,q in zip(t,t[1:]+t[:1])))
    queue=deque((i,(),[points[0],points[i],points[i+1]])for i in range(1,len(points)-1)if area([points[0],points[i],points[i+1]]))
    required=sum(area(t)for _,_,t in queue);accepted=[];unresolved=[];journal=[];shared={};cache={};attempts=0;accepted_area=F(0);unresolved_area=F(0)
    while queue:
        fan,path,t=queue.popleft()
        if attempts>=max_attempts:
            unresolved.append(dict(fan=fan,path=list(path),idealTriangle=t,reason='bounded-attempt-limit'));unresolved_area+=area(t);continue
        attempts+=1;pieces=packer(t,parent,shared);proofs=[]
        for piece in pieces:
            key=np.asarray(piece['packedTriplet'],dtype='<f8').tobytes()
            if key not in cache:cache[key]=checker(piece['packedTriplet'],worlds)
            proofs.append(cache[key])
        eligible=bool(pieces)and all(q['eligible']for q in proofs)
        journal.append(dict(fan=fan,path=list(path),idealTriangle=t,packedPieces=pieces,completeCompatibility=proofs,eligible=eligible))
        if eligible:
            accepted_area+=area(t)
            for piece,q in zip(pieces,proofs):accepted.append(dict(fan=fan,path=list(path),idealTriangle=t,packing=piece,completeNewPieceOrdinaryCompatibility=q))
            continue
        if len(path)>=max_depth:
            unresolved.append(dict(fan=fan,path=list(path),idealTriangle=t,reason='bounded-depth-limit',failedAttempt=attempts-1));unresolved_area+=area(t);continue
        edges=[((t[(i+1)%3][0]-t[i][0])**2+(t[(i+1)%3][2]-t[i][2])**2,i)for i in range(3)]
        _,i=max(edges,key=lambda q:(q[0],-q[1]));j=(i+1)%3;k=(i+2)%3;m=tuple((t[i][d]+t[j][d])/2 for d in range(3))
        children=[[t[i],m,t[k]],[m,t[j],t[k]]]
        assert sum(area(q)for q in children)==area(t)
        for child,sub in enumerate(children):queue.append((fan,path+(child,),sub))
    assert accepted_area+unresolved_area==required
    return dict(acceptedPieces=accepted,unresolvedIdealTriangles=unresolved,completeAttemptJournal=journal,attempts=attempts,
      requiredIdealTwiceProjectedArea=required,acceptedIdealTwiceProjectedArea=accepted_area,unresolvedIdealTwiceProjectedArea=unresolved_area,
      exactIdealSourcePlaneSubdivisionAccounted=True,allAcceptedPackedPiecesIndependentlyOrdinaryEligible=True,
      noClaimUnresolvedRegionsCovered=True,noGuardSiteInputsOrSourceGeometryChanges=True,actualProductionCoverageAndGuardsStillRequired=True)
