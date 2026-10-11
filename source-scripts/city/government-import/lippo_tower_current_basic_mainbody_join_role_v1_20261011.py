"""Named unchanged Lippo lower-mainbody/current BASIC join PROPOSAL only.

This is not a generic penetration allowance, structural certificate, identity
approval, whole-BASIC reapproval or final current acceptance. Every source face
and raw contact survives. Literal depth is an exact pinned arithmetic fact,
never rounded into the provider's 3/2 metre authored depth.
"""
from fractions import Fraction as F
from collections import defaultdict, deque
import hashlib, importlib.util
from pathlib import Path
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face, intersection_points, cross, sub
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import dimension, finite_intersection_points, exact_finite_contacts

TOWER='landsd/239465:0'; CARRIER='landsd/231645:0'
SOURCE='2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c'
BASIC='c971dcdad745de83ccfce62b75e1ccdeba61b229f3684f183d8b366338859b11'
GROUND='5c01f4f1544174d8c53632004c18b6cf98fcbdd34ba8e5e2f01d750f5614a044'
WORLD={
 'providerOriginal':'627acd398cf2733879d21080bb44049a8ce6038e50bd7cc9a6a976ca0c99308d',
 'actualLiteral':'c3a5a8efd1345e14ad33b1593f4ae471b5593914ea6b1e0b4700bbccb6619b89',
 'explicitLeftAssociatedF32ModelMatrix':'037d46bc6e8084035ad10083ca5e1ee048d1049c447c9970e220874cf80a25b3',
 'explicitBalancedF32ModelMatrix':'037d46bc6e8084035ad10083ca5e1ee048d1049c447c9970e220874cf80a25b3'}
NONRENDER=[13,25,2091,2744]
FOREIGN_UIDS={'landsd/'+str(i)+':0' for i in [156599,208070,208602,211439,211824,233985,233997,234188,237843,239032,239461,240487,240494,250891,250893,313406,313412,313416,21915]}
DEPTH={m:('422212465065985/281474976710656' if m=='actualLiteral' else '3/2') for m in WORLD}
IDENTITY=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]

def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def load_clip():
 p=Path(__file__).with_name('xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011.py')
 s=importlib.util.spec_from_file_location('lippo_frozen_exact_clip',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def edge_map(world,faces):
 out=defaultdict(list)
 for i in faces:
  q=rational_face(world[i])
  for a,b in zip(q,q[1:]+q[:1]):
   if a!=b:out[tuple(sorted((a,b)))].append(i)
 return out

def projected_area(poly):
 if len(poly)<3:return F(0)
 normal=(F(0),)*3
 for a,b in zip(poly,poly[1:]+poly[:1]):
  c=cross(a,b);normal=tuple(normal[k]+c[k] for k in range(3))
 return next((abs(v)/2 for v in normal if v),F(0))

def prism_planes(cap,low,top):
 q=rational_face(cap);area=sum(a[0]*b[2]-b[0]*a[2] for a,b in zip(q,q[1:]+q[:1]));assert area
 sign=1 if area>0 else -1
 return [lambda p:p[1]-low,lambda p:top-p[1]]+[lambda p,a=a,b=b:sign*((b[0]-a[0])*(p[2]-a[2])-(b[2]-a[2])*(p[0]-a[0])) for a,b in zip(q,q[1:]+q[:1])]

def lower_accounting(world,basic,record,component,clipper):
 """Replay every exact original-face/current cap-prism fragment; retain exterior.
 Convex subtraction partitions the original below-roof facet into actual prism
 pieces and exact exterior residues. Boundary duplicates have zero 2D measure;
 no real tiny facet is discarded. Source-degenerate records stay uncredited.
 """
 low,top=F(float(basic[:,:,1].min())),F(float(basic[:,:,1].max()))
 caps=np.flatnonzero(np.all(basic[:,:,1]==float(top),axis=1)).tolist()
 expected=defaultdict(list)
 for p in record['completeFiniteClosedPrismIntersections']:expected[p['sourceFace']].append(p)
 below=[int(i) for i in np.flatnonzero(world[:,:,1].min(1)<float(top))]
 assert record['completeSourceFacesBelowCurrentBasicTop']==below
 assert record['completeSourceFacesAtOrAboveTop']==[i for i in range(3597) if i not in below]
 assert record['completeSourceFacesEntirelyBelowBasicBottom']==[]
 accounting=[];all_pieces=[]
 for i in below:
  face=rational_face(world[i]);lower=clipper.clip(face,lambda p:top-p[1]);remaining=[lower] if projected_area(lower) else []
  pieces=[]
  for cap in caps:
   if any(world[i,:,k].max()<basic[cap,:,k].min() or world[i,:,k].min()>basic[cap,:,k].max() for k in [0,2]):continue
   planes=prism_planes(basic[cap],low,top);poly=face
   for fn in planes:poly=clipper.clip(poly,fn)
   if poly:
    pieces.append((cap,poly));all_pieces.append((i,cap,poly))
   # Exact convex subtraction of this prism from all remaining lower pieces.
   following=[]
   for frag in remaining:
    inside=frag
    for fn in planes:
     outside=clipper.clip(inside,lambda p,fn=fn:-fn(p))
     if projected_area(outside) and any(fn(q)<0 for q in inside):following.append(outside)
     inside=clipper.clip(inside,fn)
     if not inside:break
   remaining=following
  saved=expected.pop(i,[]);assert len(saved)==len(pieces)
  for saved_piece,(cap,poly) in zip(saved,pieces):
   assert saved_piece['currentBasicCapFace']==cap
   assert saved_piece['exactFiniteClippedPolygon']==[[str(v) for v in p] for p in poly]
   assert saved_piece['exactClippedPolygonDimension']==clipper.polygon_dimension(poly)
   assert saved_piece['exactSourcePrimitiveDimension']==dimension(face)
   assert saved_piece['originalRealComponent']==component.get(i)
   assert saved_piece['nonrenderingSourcePrimitiveNoRootCredit']==(i in NONRENDER)
   assert F(saved_piece['exactMaximumDepthBelowCurrentBasicTop'])==top-min(p[1] for p in poly)
   if 'strictCurrentClosedBodyInteriorWitness' in saved_piece:
    assert component.get(i)==6 and dimension(face)==2
    assert saved_piece['strictCurrentClosedBodyInteriorWitness']['strictOddParityInterior'] is True
    centre=tuple(sum(p[k] for p in poly)/len(poly) for k in range(3))
    assert saved_piece['sourceRelativeInteriorPointBarycentreOfCompleteClippedPolygon']==[str(v) for v in centre]
    assert low<centre[1]<top
  accounting.append(dict(sourceFace=i,component=component.get(i),sourceDimension=dimension(face),completeBelowRoofFragment=[[str(v) for v in p] for p in lower],completePrismFragments=[dict(cap=cap,polygon=[[str(v) for v in p] for p in poly]) for cap,poly in pieces],completeExteriorFragments=[[[str(v) for v in p] for p in frag] for frag in remaining],zeroAreaRootCredit=False))
 assert not expected
 assert max((top-min(p[1] for p in poly) for _,_,poly in all_pieces),default=F(0))==F(DEPTH[record['mode']])
 assert record['maximumExactDepthBelowCurrentBasicTop']==DEPTH[record['mode']]
 assert record['originalComponentsWithGenuineCurrentBasicInterior']==[6]
 assert record['allCandidateSourceFacesExamined'] is True and record['sourceFacesOmitted']==0
 assert record['completeNonrenderingOriginalSourceFaceIDs']==NONRENDER and record['zeroAreaRootOrBridgeCredit'] is False
 strict=[p for p in record['completeFiniteClosedPrismIntersections'] if 'strictCurrentClosedBodyInteriorWitness' in p]
 assert strict==record['strictPositiveSourceFacetInteriorPieces'] and strict
 return accounting

def verify(proposal):
 assert proposal['sourceSHA256']==SOURCE
 t,p=proposal['towerCurrentForm'],proposal['carrierCurrentForm']
 assert (t['uid'],t['buildingCSUID'],t['buildingId'],t['structureType'],t['baseHeightHKPD'])==(TOWER,'3551817554T20050430',1108244114,'Tower',18.6)
 assert (p['uid'],p['buildingCSUID'],p['buildingId'],p['structureType'],p['topHeightHKPD'],p['baseHeightHKPD'])==(CARRIER,'3551417531P20050812',1108247418,'Podium',18.6,4.1)
 assert proposal['carrierIdentityModelMatrix']==IDENTITY
 basic=np.asarray(proposal['basic'],dtype='<f8');assert basic.shape==(284,3,3) and np.isfinite(basic).all() and sha(basic)==BASIC
 assert proposal['groundSHA256']==GROUND
 assert set(proposal['worlds'])==set(WORLD) and set(proposal['finite'])==set(WORLD)
 assert len(proposal['otherForeignActors'])==19 and {a['uid'] for a in proposal['otherForeignActors']}==FOREIGN_UIDS
 for actor in proposal['otherForeignActors']:
  assert actor['uid'] not in [TOWER,CARRIER] and actor['trials']
  assert {v['ownedMode'] for v in actor['trials']}==set(WORLD)
  for v in actor['trials']:
   assert v['allPairsExamined'] is True and v['completeOwnedFaces']==3597 and v['completeForeignFaces']>0
   assert v['sourceFacesOmitted']==v['foreignFacesOmitted']==0 and v['completeContacts']==[] and v['positiveFiniteContacts']==0
   assert v['ownedWorldSHA256']==WORLD[v['ownedMode']]
 carrier=proposal['carrierPaths'];assert carrier['completeLiteralBasicWorldSHA256']==BASIC and carrier['completeGroundSHA256']==GROUND
 assert carrier['originalGovernmentPodiumUsedAsSupport'] is False and carrier['wholeBasicReaccepted'] is False
 graph=proposal['basicGraph'];facet=proposal['basicFinite'];assert facet['completeGroundSHA256']==GROUND
 assert [x['actualBasicFace'] for x in facet['faces']]==list(range(284))
 normals=np.cross(basic[:,1]-basic[:,0],basic[:,2]-basic[:,0]);top=float(basic[:,:,1].max())
 caps=[i for i in range(284) if np.all(basic[i,:,1]==top) and normals[i,1]>0]
 assert len(caps)==69 and facet['strictUpwardTopCapIDs']==caps
 for i in caps:
  proof=facet['faces'][i]['proof'];assert proof['sourceFaceSHA256']==sha(basic[i]) and proof['groundProjectionCovered'] is True and F(proof['exactCertifiedLowerClearanceM'])>0
 assert facet['reversedTopPlaneRecordsNoRootOrBridge']==[i for i in range(284) if np.all(basic[i,:,1]==top) and normals[i,1]<0]
 assert facet['upwardWoundBottomRecordsNoRoofCredit']==[17]
 assert len(graph['strictlyExposedGradeWallToCapRoutes'])==70 and len(graph['exactUpperGradeInterfaces'])==294
 edges=edge_map(basic,range(284));reached=set();adj=defaultdict(set)
 for r in graph['strictlyExposedGradeWallToCapRoutes']:
  a,b=r['wall'],r['cap'];assert b in caps and normals[a,1]==0
  edge=tuple(sorted(tuple(F(v) for v in q) for q in r['exactLiteralSharedEdge']));assert a in edges[edge] and b in edges[edge]
  assert r['exactUpperGradeInterfaces'] and all(x['sourceFace']==a for x in r['exactUpperGradeInterfaces'])
  assert r['wholeWallCapPositiveInterface']['strictlyExposedWholePositiveInterface'] is True
  assert F(r['wallExposedOriginalVertexProof']['exactExposureLowerBoundM'])>0;reached.add(b)
 assert reached
 for r in graph['completeRoofToRoofStrictlyExposedSharedEdges']:
  a,b=r['caps'];assert a in caps and b in caps and a!=b
  edge=tuple(sorted(tuple(F(v) for v in q) for q in r['exactLiteralSharedNonzeroEdge']));assert a in edges[edge] and b in edges[edge]
  assert r['completeFacetProofs']==[facet['faces'][a]['proof'],facet['faces'][b]['proof']]
  adj[a].add(b);adj[b].add(a)
 todo=list(reached)
 while todo:
  for j in adj[todo.pop()]:
   if j not in reached:reached.add(j);todo.append(j)
 assert reached==set(caps)
 outputs=[];clipper=load_clip();cache={}
 for mode in WORLD:
  world=np.asarray(proposal['worlds'][mode],dtype='<f8');assert world.shape==(3597,3,3) and np.isfinite(world).all() and sha(world)==WORLD[mode]
  record=next(r for r in proposal['partition']['rows'] if r['mode']==mode);assert record['wholeWorldSHA256']==WORLD[mode]
  upper=next(r for r in carrier['upperRows'] if r['mode']==mode);assert upper['completeOwnedWorldSHA256']==WORLD[mode]
  c=census(world,list(range(3597)));assert c==upper['completeOwnedRealComponentCensus']
  assert c['exactNonrenderingOriginalFaces']==NONRENDER
  # Component IDs 5..9 are the previously frozen complete actor-local census.
  component={i:5+n for n,part in enumerate(c['sharedEdgeConnectedComponents']) for i in part}
  main=[i for i in component if component[i]==6];assert len(main)==3459 and 19 in main
  finite=proposal['finite'][mode];assert finite['completeWorldSHA256']==WORLD[mode] and finite['completeGroundSHA256']==GROUND
  assert [v['sourceFace'] for v in finite['allOwnedFaces']]==list(range(3597))
  for i,v in enumerate(finite['allOwnedFaces']):
   proof=v['proof'];assert proof['sourceFaceSHA256']==sha(world[i]) and proof['groundProjectionCovered'] is True and proof['existingOrdinaryClearanceBoundProved'] is True and F(proof['exactCertifiedLowerClearanceM'])>0
  # Every mainbody face has an actual nonzero shared-edge path to a complete
  # strictly clear original upward cap ABOVE the join; zero-area faces absent.
  normals_t=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);uppercaps=[i for i in main if normals_t[i,1]>0 and np.all(world[i,:,1]>top)];assert uppercaps
  bodyedges=edge_map(world,main);bodyadj=defaultdict(set)
  for ids in bodyedges.values():
   for a in ids:bodyadj[a].update(set(ids)-{a})
  bodyreach=set(uppercaps);todo=list(bodyreach)
  while todo:
   for j in bodyadj[todo.pop()]:
    if j not in bodyreach:bodyreach.add(j);todo.append(j)
  assert bodyreach==set(main)
  key=WORLD[mode]
  if key in cache:
   lower=cache[key]
   # The mode/depth names differ but exact source stream is byte-identical.
   duplicate=dict(record,mode=cache[key+'_mode']);assert duplicate==cache[key+'_record']
  else:
   lower=lower_accounting(world,basic,record,component,clipper);cache[key]=lower;cache[key+'_mode']=mode;cache[key+'_record']=record
  contacts=proposal['carrierContacts'][mode];assert contacts['ownedWorldSHA256']==WORLD[mode] and contacts['foreignWorldSHA256']==BASIC and contacts['allPairsExamined'] is True
  independently_complete=exact_finite_contacts(world,list(range(3597)),basic,list(range(284)))
  assert len(independently_complete['contacts'])==len(contacts['completeContacts'])
  assert [(v['sourceFaceA'],v['sourceFaceB'],v['exactPoints'],v['dimension']) for v in independently_complete['contacts']]==[(v['sourceFaceA'],v['sourceFaceB'],v['exactPoints'],v['dimension']) for v in contacts['completeContacts']]
  classified=[]
  for v in contacts['completeContacts']:
   i,j=v['sourceFaceA'],v['sourceFaceB'];assert 0<=i<3597 and 0<=j<284
   pts=finite_intersection_points(rational_face(world[i]),rational_face(basic[j]));assert pts and v['exactPoints']==[[str(x) for x in q] for q in sorted(pts)]
   measure=contact_measure(pts);assert measure['dimension']==v['dimension'] and v['positiveFiniteContact']==(v['dimension']>0)
   part=component.get(i)
   if part==6:role='connected-mainbody-lower-join-or-roof-boundary'
   else:
    assert all(q[1]==F(top) for q in pts)
    assert part in [7,None]
    role='zero-area-no-support-credit' if part is None else 'separate-part-qualified-roof-boundary-only'
   classified.append(dict(sourceFace=i,currentFace=j,dimension=v['dimension'],role=role,allExactContactPoints=v['exactPoints'],zeroAreaRootCredit=False))
  assert sum(v['positiveFiniteContact'] for v in contacts['completeContacts'])==contacts['positiveFiniteContacts']
  # Recompute each positive component interface and actual clear-cap contact;
  # declared reached-component booleans alone never grant a source path.
  component_adj=defaultdict(set);direct=set()
  for r in upper['exactInternalOwnedPositiveInterfaces']:
   a,b=r['components'];i,j=r['sourceFaces'];assert component[i]==a and component[j]==b
   points=intersection_points(rational_face(world[i]),rational_face(world[j]));assert contact_measure(points)['dimension']>0
   assert r['exactPositiveContactPoints']==[[str(v) for v in q] for q in sorted(points)]
   component_adj[a].add(b);component_adj[b].add(a)
  assert [r['ownedComponent'] for r in upper['completeExposedBasicCapContactProofs']]==[5,6,7,8,9]
  for r in upper['completeExposedBasicCapContactProofs']:
   for v in r['strictExposedCapInterfaces']:
    i,j=v['ownedSourceFace'],v['actualBasicCapFace'];assert component[i]==r['ownedComponent'] and j in reached
    points=intersection_points(rational_face(world[i]),rational_face(basic[j]));assert contact_measure(points)['dimension']>0
    assert v['exactPositiveContactPoints']==[[str(x) for x in q] for q in sorted(points)]
    direct.add(r['ownedComponent'])
  assert sorted(direct)==upper['directComponentsViaExposedBasicRoof']
  component_reach=set(direct);todo=list(direct)
  while todo:
   for j in component_adj[todo.pop()]:
    if j not in component_reach:component_reach.add(j);todo.append(j)
  assert component_reach=={5,6,7,8,9}
  assert upper['unresolvedComponents']==[] and upper['componentsWithBoundedCarrierPaths']==[5,6,7,8,9]
  outputs.append(dict(mode=mode,completeSourceFaces=3597,mainbodyFaces=3459,sourceZeroAreaUncredited=NONRENDER,allLowerFragments=lower,completeRawContactsClassified=classified,actualExactDepth=DEPTH[mode],mainbodyStrictUpperCapSourceFaces=uppercaps,completeMainbodyNonzeroEdgePathProved=True))
 return dict(uid=TOWER,carrierUid=CARRIER,sourceSHA256=SOURCE,rows=outputs,sourceRoleProposal=True,physicalAccepted=False,installationApproved=False,wholeBasicReaccepted=False,governmentPodiumUsedAsRuntimeSupport=False,sourceGeometryChanges=0,terrainGeometryChanges=0,thresholdChanges=0,qualification='Only the pinned connected original mainbody lower interface is proposed as authored current carrier join. All source records/contact negatives retained; other actor collisions, full current identity/ground/native/runtime/foundation/browser remain independent. No legal ownership, load-bearing or fixture function claim.')
