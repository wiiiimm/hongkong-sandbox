"""Named original lower skin proposal; raw failure faces never bridge bodies.

Reuses independently bound whole current finite/grade records. Exact original
closed column bases and the two sloping original underside faces are distinct
roles. This helper cannot approve physical/runtime/import acceptance.
"""
from fractions import Fraction as F
from collections import deque
import hashlib
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census
BASES={68:list(range(5137,5147)),69:list(range(5181,5191))}
COLUMNS={68:list(range(5113,5157)),69:list(range(5157,5201))}
SLOPING=[3854,3855]
WORLD_HASHES={'6150374beebfd3c49c267d0c6d0a8ec2f8bf995c030c77bc5a4c5fba423154d2','c681647a318f43ddcb469fd78c33119318f4cf321b28b2fb4f5eba2d76ae2d40'}
GROUND_SHA='1129635d19713b3dbcdf3fe5eff2427e2429d89131d33d8ef7742cd216bcd14f'
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def points(face):return[tuple(F(float(v))for v in p)for p in face]
def edges(face):
 p=points(face);return{tuple(sorted((a,b)))for a,b in zip(p,p[1:]+p[:1])if a!=b}
def normal(face):
 p=points(face);a=tuple(p[1][i]-p[0][i]for i in range(3));b=tuple(p[2][i]-p[0][i]for i in range(3));return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def exposed_segment(edge,ceiling):
 a,b=sorted(edge,key=lambda p:p[1])
 if b[1]<=ceiling:return None
 if a[1]>ceiling:return(a,b)
 middle=(ceiling+b[1])/2;t=(middle-a[1])/(b[1]-a[1]);assert 0<t<1
 return(tuple(a[k]+t*(b[k]-a[k])for k in range(3)),b)
def strict_record(records,i,w):
 r=records[i];assert r['sourceFace']==i;p=r['groundComparisons']['currentDrawn'];proof=p['coarse']if p['coarse']['existingOrdinaryClearanceBoundProved']else p['paired']
 assert p['completeFiniteOrdinaryBoundProved']is True and proof['groundProjectionCovered']is True and F(proof['exactCertifiedLowerClearanceM'])>0 and proof['sourceFaceSHA256']==sha(w[i])and proof['completeCurrentGroundSHA256']==GROUND_SHA
 return proof
def covered_record(records,i,w):
 r=records[i];assert r['sourceFace']==i;p=r['groundComparisons']['currentDrawn'];assert p['coarse']['groundProjectionCovered']is True and p['coarse']['sourceFaceSHA256']==sha(w[i])and p['coarse']['completeCurrentGroundSHA256']==GROUND_SHA
 assert p['completeFiniteOrdinaryBoundProved']is False and p['paired']is not None and p['paired']['existingOrdinaryClearanceBoundProved']is False
 return r
def verify(*,world,ground,finite_row,grade_row,parts):
 w=np.asarray(world,dtype='<f8');g=np.asarray(ground,dtype='<f8');assert w.shape==(13960,3,3)and g.shape==(1849,3,3)and np.isfinite(w).all()and np.isfinite(g).all()
 wh=sha(w);assert wh in WORLD_HASHES and wh==finite_row['completeWholeWorldSHA256']==grade_row['completeWorldSHA256']and sha(g)==GROUND_SHA
 records=finite_row['complete13960FaceComparisons'];assert len(records)==13960 and [r['sourceFace']for r in records]==list(range(13960))and len(parts)==226
 raw=grade_row['rawDownwardFacesRetainedAsUncredited'];assert sorted(raw)==sorted(SLOPING+BASES[68]+BASES[69])and len(raw)==22
 all_grade=grade_row['complete5297CurrentGradeContactInventory'];assert all_grade['allPairsExamined']is True and all_grade['sourceFacesOmitted']==0
 contacts=all_grade['contacts'];floor=min(F(float(v))for v in g[:,:,1].flat);ceiling=max(F(float(v))for v in g[:,:,1].flat)
 columns=[]
 for component,ids in COLUMNS.items():
  assert parts[component]==ids
  inv=census(w[ids],list(range(len(ids))));assert inv['sharedEdgeConnectedComponents']==[list(range(len(ids)))]and inv['boundaryEdges']==inv['nonmanifoldEdges']==inv['twoFaceOrientationConflicts']==0 and inv['exactNonrenderingOriginalFaces']==[]
  ns={i:normal(w[i])for i in ids};bases=BASES[component];assert [i for i in ids if ns[i][1]<0]==bases
  caps=[i for i in ids if ns[i][1]>0];walls=[i for i in ids if ns[i][1]==0];assert len(caps)==10 and len(walls)==24 and all(any(ns[i])for i in ids)
  low={F(float(v))for i in bases for v in w[i,:,1]};assert len(low)==1 and next(iter(low))<floor
  base_records=[covered_record(records,i,w)for i in bases];cap_proofs=[strict_record(records,i,w)for i in caps]
  column_contacts=[c for c in contacts if c['sourceFaceA']in ids];assert {c['sourceFaceA']for c in column_contacts}==set(walls)
  assert all(c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and len(c['exactPoints'])==2 for c in column_contacts)
  # Literal source cap/wall interfaces are wholly above every actual ground
  # vertex, so they are exposed; zero/point glue and buried bases are excluded.
  joins=[];adj={i:set()for i in walls+caps}
  for pos,i in enumerate(walls+caps):
   for j in (walls+caps)[pos+1:]:
    for e in edges(w[i])&edges(w[j]):
     segment=exposed_segment(e,ceiling)
     if segment is not None:
      adj[i].add(j);adj[j].add(i);joins.append(dict(sourceFaceA=i,sourceFaceB=j,completeOriginalSharedEdge=[[str(v)for v in p]for p in e],exactStrictlyExposedOriginalSubsegment=[[str(v)for v in p]for p in segment]))
  paths={i:[i]for i in caps};queue=deque(caps)
  while queue:
   i=queue.popleft()
   for j in sorted(adj[i]):
    if j not in paths:paths[j]=[j]+paths[i];queue.append(j)
  assert set(paths)==set(walls+caps)
  columns.append(dict(originalComponent=component,completeOriginalFaces=ids,completeOriginalClosedSkinTopology=inv,originalEmbeddedBaseFaces=bases,rawBaseFiniteFailuresVerbatim=base_records,completeOriginalStrictClearCapFaces=caps,completeStrictClearCapProofs=cap_proofs,completeActualLateralGradeContacts=column_contacts,completeExposedWallCapInterfaces=joins,completeOriginalExposedWallToClearCapPaths=[dict(originalWallFace=i,originalPath=paths[i])for i in walls],baseClosureBridgeCredit=False,closedSolidOrLoadBearingCertified=False))
 assert all(i in parts[13]for i in SLOPING+[3846]);ns=[normal(w[i])for i in SLOPING];assert all(n[1]<0 and 16*n[1]*n[1]>sum(v*v for v in n)for n in ns)
 raw_slopes=[covered_record(records,i,w)for i in SLOPING];host=strict_record(records,3846,w)
 shared=edges(w[3855])&edges(w[3854]);upper=edges(w[3854])&edges(w[3846]);assert len(shared)==len(upper)==1
 diagonal=next(iter(shared));top=next(iter(upper));assert min(p[1]for p in top)>ceiling
 a,b=sorted(diagonal,key=lambda p:p[1]);assert a[1]<floor and b[1]>ceiling and b in top
 # An exact strictly positive segment above the complete ground maximum.
 # Choosing halfway from the maximum to the original high endpoint changes
 # no source vertex or surface; it only reports a finite exposure witness.
 middle=(ceiling+b[1])/2;t=(middle-a[1])/(b[1]-a[1]);assert 0<t<1;exposed=tuple(a[k]+t*(b[k]-a[k])for k in range(3))
 slope_contacts=[c for c in contacts if c['sourceFaceA']in SLOPING];assert {c['sourceFaceA']for c in slope_contacts}==set(SLOPING)and all(c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in slope_contacts)
 return dict(contract='Evangel-exact20-original-column-base-closures-and-two-sloping-lower-skins-v2',completeWorldSHA256=wh,completeGroundSHA256=GROUND_SHA,completeColumnBaseClosureProposals=columns,completeTwoSlopingOriginalFaceIds=SLOPING,completeSlopingRawFailuresVerbatim=raw_slopes,completeSlopingActualGradeContacts=slope_contacts,originalExposedSharedDiagonal=[[str(v)for v in p]for p in [exposed,b]],completeOriginalSharedDiagonal=[[str(v)for v in p]for p in diagonal],completeStrictClearOriginalHost=3846,completeOriginalUpperSharedEdge=[[str(v)for v in p]for p in top],completeStrictClearHostProof=host,slopingFacesTreatedAsSteepWalls=False,raw22FailureFacesProvideNoInterComponentRootOrBridge=True,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceRoleProposalOnly=True,currentAcceptance=False,installationApproved=False)
