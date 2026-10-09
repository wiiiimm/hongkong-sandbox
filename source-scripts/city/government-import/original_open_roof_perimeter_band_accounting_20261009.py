"""Authored open roof footing, within the existing finite contact band.

This separately named route is not exact source contact. It invents no cap,
edge, welding or ground root; complete lower boundary edges must continuously
lie in the existing +/-0.1m band of independently rooted original roofs.
Current physical/source/foreign acceptance is mandatory in the source adapter.
"""
import collections,hashlib,json
import numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
from exact_original_shell_intersections_20261009 import shell_self_intersections
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(triangles,components,contexts,independent_roots,visual_only,roles,*,expected_binding,current_binding):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 assert current_binding==expected_binding
 for key,value in [('completeOriginalWorldTrianglesSHA256',hashlib.sha256(tri.tobytes()).hexdigest()),('completeComponentsSHA256',canonical(components)),('completeCurrentFacetContextsSHA256',canonical(contexts)),('independentRootedComponentsSHA256',canonical(independent_roots)),('visualOnlyComponentsSHA256',canonical(visual_only)),('sourceRolesSHA256',canonical(roles))]:assert current_binding[key]==value,'Bound original input changed'
 n=len(tri);assert len(contexts)==n and [r['sourceFace'] for r in contexts]==list(range(n))
 partition=[i for c in components for i in c['globalOriginalFaces']];assert sorted(partition)==list(range(n)) and len(partition)==n
 for group in [independent_roots,visual_only]:assert group==sorted(set(group)) and all(type(i) is int and 0<=i<len(components) for i in group)
 assert independent_roots and not set(independent_roots)&set(visual_only)
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(n),where=length>0)
 scope=sorted(i for k in independent_roots for i in components[k]['globalOriginalFaces']);roof_ids=[i for i in scope if ratio[i]>.25]
 assert roof_ids,'No independently rooted upward source roof'
 for i in roof_ids:assert contexts[i]['groundProjectionCovered'] is True and contexts[i]['minimum']['minimumGapM'] is not None and contexts[i]['minimum']['minimumGapM']>=-.5
 roofs=tri[roof_ids];results=[];claimed=[]
 for role in roles:
  k=role['component'];assert type(k) is int and 0<=k<len(components) and k not in independent_roots+visual_only+claimed;claimed.append(k)
  ids=components[k]['globalOriginalFaces'];assert role['completeOriginalFaces']==ids and 1<=len(ids)<=300
  part=tri[ids];assert all(length[i]>0 for i in ids),'Zero-area faces need separate original classification'
  for i in ids:assert contexts[i]['groundProjectionCovered'] is True and contexts[i]['minimum']['minimumGapM'] is not None and contexts[i]['minimum']['minimumGapM']>=-.5,'Ordinary whole-facet clearance failed'
  edges=collections.defaultdict(list);adj={i:set() for i in ids}
  for i in ids:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    assert tuple(a)!=tuple(b);edge=tuple(sorted((tuple(a),tuple(b))));edges[edge].append((i,bool(tuple(a)<tuple(b))))
  assert all(len(v)<=2 for v in edges.values()),'Original nonmanifold edge'
  for e,members in edges.items():
   if len(members)==2:
    assert members[0][1]!=members[1][1],'Original winding conflict'
    a,b=[r[0] for r in members];adj[a].add(b);adj[b].add(a)
  reached={ids[0]};todo=list(reached)
  while todo:
   for j in adj[todo.pop()]:
    if j not in reached:reached.add(j);todo.append(j)
  assert reached==set(ids),'Detached original face'
  boundary=sorted(e for e,m in edges.items() if len(m)==1);assert boundary,'No original open boundary'
  bottom=float(part[:,:,1].min());top=float(part[:,:,1].max());assert top>bottom
  if role['kind']=='open-vertical-roof-post':
   assert all(abs(ratio[i])<=.05 for i in ids),'Post contains non-wall surfaces'
   assert top-bottom>2*max(np.ptp(part[:,:,0]),np.ptp(part[:,:,2])),'Source is not a narrow vertical post'
   assert all((e[0][1]==e[1][1]==bottom) or (e[0][1]==e[1][1]==top) for e in boundary),'Unaccounted side opening'
   lower=[e for e in boundary if e[0][1]==e[1][1]==bottom]
   upper=[e for e in boundary if e[0][1]==e[1][1]==top];assert upper
   groups=[lower,upper]
  else:
   assert role['kind']=='open-bottom-upright-roof-equipment'
   assert all(ratio[i]>=-.05 for i in ids) and any(ratio[i]>.25 for i in ids),'Missing upward cap or downward buried feature'
   assert max(v[1] for e in boundary for v in e)-bottom<=.1,'Boundary is not the authored lower perimeter'
   lower=boundary;groups=[lower]
  assert role['completeOriginalLowerBoundary']==[[list(v) for v in e] for e in lower],'Incomplete lower perimeter'
  for group in groups:
   a=collections.defaultdict(set)
   for p,q in group:a[p].add(q);a[q].add(p)
   assert a and all(len(v)==2 for v in a.values()),'Open or branching boundary cycle'
   seen={min(a)};todo=list(seen)
   while todo:
    for j in a[todo.pop()]:
     if j not in seen:seen.add(j);todo.append(j)
   assert seen==set(a),'Multiple disconnected boundary rings'
  selfcheck=shell_self_intersections(part,maximum_faces=300);assert selfcheck['selfIntersectionFree'],'Original self intersection'
  bands=[]
  for edge in lower:
   proof=verify_contact_segment(np.asarray(edge),roofs);assert proof['verifiedCompleteOriginalEdgeContactBand'],'Original lower perimeter outside existing finite contact band'
   proof['completeOriginalSurfacePieces']=[{**p,'originalSourceFace':roof_ids[p['originalSurfaceFace']]} for p in proof['completeOriginalSurfacePieces']]
   bands.append(dict(originalLowerBoundary=edge,proof=proof))
  results.append(dict(component=k,kind=role['kind'],completeOriginalFaces=ids,completeOriginalLowerBoundaryBandProof=bands,completeOriginalSelfIntersectionProof=selfcheck,contactQualification='within existing finite contact band; not exact original contact',groundRootCredit=False,closedSolidCertified=False,syntheticBottomCap=False,sourceGeometryChanges=0))
 return dict(contract='original-authored-open-roof-lower-perimeter-existing-finite-band-v1',sourceRoofFootingComponents=claimed,independentlyRootedRoofComponents=independent_roots,completeIndependentlyRootedUpwardRoofFaces=roof_ids,originalPerimeterRoles=results,strictContactBandM=.1,exactOriginalNoncontactPreserved=True,visualOnlyRootOrBridgeCredit=False,groundRootCredit=False,fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0)
