"""Diagnostic only: complete boundaries and unchanged fixed-band finite host context."""
from collections import defaultdict
from fractions import Fraction as Q
import numpy as np
from complete_original_lower_opening_mounts_v3_20261011 import binding,verify as opening_v3
from parkview_block6_four_original_roof_opening_mounts_20261011 import opening
from exact_original_shared_edge_component_census_v2_20261011 import census
from complete_original_simple_lower_opening_mounts_v1_20261011 import intersects,on_segment
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
from exact_original_source_surface_contact_band_20261009 import verify_contact
from west_wing26195_complete_current_finite_ground_draft_v3_20261012 import exact_orientation

def boundary(t,ids):
 t=np.asarray(t,dtype='<f8');assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all();assert ids and len(ids)==len(set(ids))and all(type(i)is int and 0<=i<len(t)for i in ids);c=census(t,ids);assert not c['exactNonrenderingOriginalFaces']and len(c['sharedEdgeConnectedComponents'])==1
 inc=defaultdict(list)
 for i in ids:
  points=list(map(tuple,t[i]))
  for a,b in zip(points,points[1:]+points[:1]):assert a!=b;inc[tuple(sorted((a,b)))].append((i,a,b))
 outside=[]
 for rows in inc.values():
  assert len(rows)<=2,'Nonmanifold source incidence'
  if len(rows)==1:outside.append(rows[0])
  else:assert rows[0][1:]==rows[1][1:][::-1],'Source winding conflict'
 out={};incoming={}
 for i,a,b in outside:assert a not in out and b not in incoming;out[a]=(i,b);incoming[b]=a
 assert set(out)==set(incoming);remaining=set(out);cycles=[]
 while remaining:
  start=min(remaining);a=start;cycle=[]
  while True:
   assert a in remaining;remaining.remove(a);i,b=out[a];cycle.append((i,a,b));a=b
   if a==start:break
  cycles.append(cycle)
 low=float(t[ids,:,1].min());mins=[e for e in outside if e[1][1]==e[2][1]==low]
 return dict(nonzeroBodyCensus=c,completeDirectedBoundaryCycles=cycles,completeDirectedBoundaryEdges=outside,completeMinimumHeightBoundaryEdges=mins,exactMinimumHeightM=str(Q(low)))

def lower4_context(t,ids):
 r=boundary(t,ids);cycles=r['completeDirectedBoundaryCycles'];assert len(ids)==8 and len(cycles)==2 and sorted(map(len,cycles))==[4,4]and len(r['completeDirectedBoundaryEdges'])==8
 minimum=r['completeMinimumHeightBoundaryEdges'];assert len(minimum)==4;lowcycle=next(c for c in cycles if set(c)==set(minimum));assert all(e[1][1]==e[2][1]==float(t[ids,:,1].min())for e in lowcycle)
 ps=[(Q(float(e[1][0])),Q(float(e[1][2])))for e in lowcycle];area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(ps,ps[1:]+ps[:1]))/2;assert area!=0
 for i in range(4):
  for j in range(i+1,4):
   a,b=ps[i],ps[(i+1)%4];c,d=ps[j],ps[(j+1)%4]
   if j==i+1 or i==0 and j==3:
    common=set([a,b])&set([c,d]);assert len(common)==1;shared=next(iter(common));assert not any(on_segment(c,d,p)for p in [a,b]if p!=shared)and not any(on_segment(a,b,p)for p in [c,d]if p!=shared)
   else:assert not intersects(a,b,c,d)
 return {**r,'exactSignedMinimumLoopProjectedAreaM2':str(area),'completeMinimumDirectedCycle':lowcycle,'higherBoundaryCycleRetainedUnfilled':True,'openingV3WholeBoundaryRequirementNotChanged':True}

def strict_hosts(t,main_ids,body_ids,records):
 eligible=[];orientations={}
 for i in main_ids:
  if not records[i]['strictPositiveFiniteProved']:continue
  assert records[i]['ordinaryFiniteProved']and records[i]['completeProjectionCovered'];o=exact_orientation(t[i]);n=list(map(Q,o['exactNormal']))
  if n[1]>0 and 16*n[1]*n[1]>sum(v*v for v in n):eligible.append(i);orientations[i]=o
 xz=t[body_ids][:,:,[0,2]];lo=xz.min((0,1));hi=xz.max((0,1));selected=[];excluded=[]
 for i in eligible:
  x=t[i][:,[0,2]];a=x.min(0);b=x.max(0)
  (selected if np.all(b>=lo)and np.all(a<=hi)else excluded).append(i)
 return dict(completeBody0StrictUpwardNonsteepHostIDs=eligible,selectedWholeFiniteHostIDs=selected,allExcludedStrictHostIDs=excluded,closedBodyProjectedBounds=[lo.tolist(),hi.tolist()],allExclusionsStrictlyProjectedAABBDisjoint=True,noHeightOrNearestWitnessPruning=True,selectedSavedFullFacetProofs=[dict(sourceFace=i,proof=records[i],orientation=orientations[i])for i in selected],body0GroundRoleStillConditional=True)

def associate(t,ids,host_ids,kind,*,expected_binding):
 assert len(host_ids)==len(set(host_ids))and not set(ids)&set(host_ids)and all(type(i)is int and 0<=i<len(t)for i in host_ids);assert binding(t,ids,host_ids)==expected_binding,'Exact whole-source/body/host binding mismatch';base=dict(binding=expected_binding,completeBodyFaces=ids,completeHostFaces=host_ids,fixedBandM=.1,bodySupportAccepted=False,gradeRootAccepted=False,physicalAccepted=False,installationApproved=False,structuralCredit=False,architecturalFunctionInferred=False,sourceGeometryChanges=0)
 if kind=='body108-minimum-edge-context':
  topology=lower4_context(t,ids)
  try:
   if host_ids:opening_v3(t,ids,host_ids,expected_binding=expected_binding)
   else:opening(t,ids)
  except AssertionError as error:rejection=dict(rejected=True,exception='AssertionError',message=str(error),actualFunction='opening-v3'if host_ids else'opening-v3-inherited-complete-boundary-topology')
  else:raise AssertionError('Two complete boundary cycles unexpectedly accepted by unchanged opening-v3')
  proofs=[dict(sourceFace=i,unchangedOriginalEdge=[list(a),list(b)],proof=verify_contact_segment(np.asarray([a,b]),t[host_ids]))for i,a,b in topology['completeMinimumDirectedCycle']]if host_ids else[]
  return {**base,'kind':kind,'completeSourceTopology':topology,'unchangedOpeningV3Rejection':rejection,'allFourMinimumEdgeProofs':proofs,'allFourMinimumEdgesWithinFixedBandContextOnly':len(proofs)==4 and all(p['proof']['verifiedCompleteOriginalEdgeContactBand']for p in proofs),'completeLowerOpeningAssociated':False,'higherOpeningClosed':False,'wholeBodyOpeningCredit':False}
 assert kind=='body113-whole-two-face-surface-context'and len(ids)==2;topology=boundary(t,ids);assert len(topology['completeDirectedBoundaryCycles'])==1 and len(topology['completeDirectedBoundaryEdges'])==4
 proofs=[dict(sourceFace=i,proof=verify_contact(t[i],t[host_ids]))for i in ids]if host_ids else[]
 return {**base,'kind':kind,'completeSourceTopology':topology,'allTwoWholeFacetProofs':proofs,'completeTwoFaceFixedBandAssociationContextOnly':len(proofs)==2 and all(p['proof']['verifiedCompleteFacetContactBand']for p in proofs),'literalPointOnlyContactNegativeNotRewritten':True,'wholeBodySupportCredit':False}
