"""Bound complete simple minimum-height opening to finite nonzero source hosts.

Arbitrary cycle length changes no band or role policy. No structural/root/bridge,
solid/function/current acceptance credit. Source/host bytes bind independently.
"""
from collections import defaultdict
from fractions import Fraction as F
import numpy as np
from complete_original_lower_opening_mounts_v2_20261011 import binding
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment

def orientation(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def on_segment(a,b,p):return orientation(a,b,p)==0 and all(min(a[i],b[i])<=p[i]<=max(a[i],b[i])for i in range(2))
def intersects(a,b,c,d):
 o1,o2,o3,o4=orientation(a,b,c),orientation(a,b,d),orientation(c,d,a),orientation(c,d,b)
 return (o1*o2<0 and o3*o4<0)or on_segment(a,b,c)or on_segment(a,b,d)or on_segment(c,d,a)or on_segment(c,d,b)
def complete_lower_cycle(t,body_faces):
 inc=defaultdict(list)
 for i in body_faces:
  xyz=list(map(tuple,t[i]))
  for a,b in zip(xyz,xyz[1:]+xyz[:1]):
   assert a!=b,'Collapsed original body edge';inc[tuple(sorted([a,b]))].append((i,a,b))
 boundary=[]
 for rows in inc.values():
  assert len(rows)<=2,'Nonmanifold original body edge'
  if len(rows)==1:boundary.append(rows[0])
  else:assert rows[0][1:]==rows[1][1:][::-1],'Original body winding conflict'
 n=len(boundary);assert 3<=n<=4096,'Complete finite opening cycle required (bounded4096edges)'
 out={};incoming={}
 for i,a,b in boundary:
  assert a not in out and b not in incoming,'Boundary must have exactly one incoming/outgoing original edge'
  out[a]=(i,b);incoming[b]=a
 assert set(out)==set(incoming),'Boundary directed endpoints must close'
 start=min(out);a=start;loop=[];visited=set()
 for _ in range(n):
  assert a not in visited,'Disconnected boundary cycles';visited.add(a);i,b=out[a];loop.append((i,a,b));a=b
 assert a==start and len(visited)==n,'All original boundary edges must form one directed cycle'
 low=t[body_faces,:,1].min();high=t[body_faces,:,1].max();assert high>low and all(a[1]==b[1]==low for _,a,b in loop),'Opening must be complete coplanar exact body minimum'
 points=[(F(float(a[0])),F(float(a[2])))for _,a,b in loop];area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(points,points[1:]+points[:1]))/2;assert area!=0,'Opening must have nonzero finite projected area'
 for i in range(n):
  a,b=points[i],points[(i+1)%n]
  for j in range(i+1,n):
   c,d=points[j],points[(j+1)%n];adjacent=j==i+1 or(i==0 and j==n-1)
   if adjacent:
    common=set([a,b])&set([c,d]);assert len(common)==1,'Adjacent boundary edges need exactly one endpoint';shared=next(iter(common));assert not any(on_segment(c,d,p)for p in [a,b]if p!=shared)and not any(on_segment(a,b,p)for p in [c,d]if p!=shared),'Adjacent boundary edges overlap'
   else:assert not intersects(a,b,c,d),'Opening boundary must be simple (no crossings/touching)'
 return loop,str(area)
def verify(triangles,body_faces,host_faces,*,expected_binding):
 t=np.asarray(triangles,float);assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all();assert body_faces and host_faces and len(set(body_faces))==len(body_faces)and len(set(host_faces))==len(host_faces)and not set(body_faces)&set(host_faces);assert all(type(i)is int and 0<=i<len(t)for i in body_faces+host_faces);current=binding(t,body_faces,host_faces);assert current==expected_binding,'Exact source/body/host binding mismatch'
 body=census(t,body_faces);assert not body['exactNonrenderingOriginalFaces']and len(body['sharedEdgeConnectedComponents'])==1,'Exactly one genuine nonzero shared-edge body required';hosts=t[host_faces];assert np.all(np.any(np.cross(hosts[:,1]-hosts[:,0],hosts[:,2]-hosts[:,0])!=0,axis=1)),'Degenerate original hosts provide no band credit'
 loop,area=complete_lower_cycle(t,body_faces);edges=[dict(originalBodyFace=i,originalEdge=[list(a),list(b)],proof=verify_contact_segment(np.asarray([a,b]),hosts))for i,a,b in loop];passed=all(e['proof']['verifiedCompleteOriginalEdgeContactBand']for e in edges)
 return dict(contract='bound-complete-simple-coplanar-minimum-original-opening-fixed-band-association-v1',binding=current,completeOriginalBodyFaces=body_faces,completeOriginalHostFaces=host_faces,completeNonzeroOriginalBodyEdgeCensus=body,completeDirectedLowerOpening=loop,exactSignedProjectedOpeningAreaM2=area,completeFiniteMounts=edges,completeLowerOpeningAssociated=passed,strictBandM=.1,allOriginalHostFacetsNonzero=True,hostGroundingOrVisualEligibilityNotInferred=True,closedSolidCertified=False,architecturalFunctionInferred=False,structuralRootCredit=False,structuralBridgeCredit=False,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0)
