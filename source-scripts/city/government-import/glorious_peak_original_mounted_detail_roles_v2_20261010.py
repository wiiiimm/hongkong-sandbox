"""Six named unchanged Glorious Peak visual details: no roots or bridges.

A complete authored lower edge, side edge, entire upper opening, or both
original end openings meet already-rooted original host surfaces within the
existing exact finite ±.1 m band. No near-point or invented cap credit.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib,json
import numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from exact_original_face_conservative_clearance_v4_20261010 import verify as finite_clearance
SOURCES={'landsd/23004:0':'ac2f8a18e21c8baa07e9ec31c1a20a7b6aaf336fcb90549b204a66684b5b0d59','landsd/233193:0':'c39add0a40833c7ae87ba659d952608f176f0a0e9230b800fe4a397a862c9fb2'}
SPECS={152:dict(role='authored-lower-edge-mounted-visual-panel',host=150,faces=[5829,5830]),160:dict(role='authored-side-edge-mounted-visual-panel',host=87,faces=[6258,6259]),357:dict(role='authored-two-ended-mounted-visual-sleeve',host=364,faces=list(range(18662,18670))),359:dict(role='authored-upper-opening-mounted-visual-sleeve',host=364,faces=list(range(18678,18686))),362:dict(role='authored-upper-opening-mounted-visual-sleeve',host=364,faces=list(range(18702,18710))),363:dict(role='authored-upper-opening-mounted-visual-sleeve',host=364,faces=list(range(18710,18718)))}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def boundaries(tri,faces):
 edges=defaultdict(list)
 for i in faces:
  xyz=list(map(tuple,tri[i]))
  for a,b in zip(xyz,xyz[1:]+xyz[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
 outside=[]
 for k,inc in edges.items():
  assert len(inc)<=2
  if len(inc)==2:assert inc[0][1:]==inc[1][1:][::-1],'Original winding conflict'
  else:outside.append(inc[0])
 outgoing={};incoming={}
 for i,a,b in outside:assert a not in outgoing and b not in incoming;outgoing[a]=(i,b);incoming[b]=a
 assert outgoing and set(outgoing)==set(incoming),'Complete directed original openings required'
 loops=[];unused=set(outgoing)
 while unused:
  start=min(unused);v=start;loop=[]
  while True:
   assert v in unused;unused.remove(v);i,b=outgoing[v];loop.append((i,v,b));v=b
   if v==start:break
  loops.append(loop)
 assert sum(map(len,loops))==len(outside)
 return loops

def mount_edge(tri,edge,hosts,axis,*,host_scope_faces):
 i,a,b=edge;perm=[k for k in range(3) if k!=axis];perm=[perm[0],axis,perm[1]];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=[j for j in hosts if n[j,axis]!=0];assert valid
 band=verify_contact_segment(np.asarray([a,b])[:,perm],tri[valid][:,:,perm])
 return dict(originalSourceFace=i,completeOriginalEdge=[list(a),list(b)],coordinatePermutation=perm,completeAlreadyRootedOriginalHostScope=host_scope_faces,finiteIntersectingHostFaces=valid,band=band)
def nearby_hosts(tri,faces,hosts):
 lo=tri[faces].min(axis=(0,1));hi=tri[faces].max(axis=(0,1));near=[];outside=[]
 for j in hosts:
  a=tri[j].min(axis=0);b=tri[j].max(axis=0);gaps=[max(F(float(lo[k]))-F(float(b[k])),F(float(a[k]))-F(float(hi[k])),F(0)) for k in range(3)];lb=sum(x*x for x in gaps)
  if lb>F(.1)**2:outside.append(dict(sourceFace=j,exactLowerSquaredDistance=str(lb)))
  else:near.append(j)
 assert near and len(near)+len(outside)==len(hosts)
 return near,outside

def component_role(tri,faces,hostfaces,mode):
 part=tri[faces];normals=np.cross(part[:,1]-part[:,0],part[:,2]-part[:,0]);assert np.all(np.linalg.norm(normals,axis=1)>0),'Nonzero complete original detail facets required';loops=boundaries(tri,faces);selfcheck=shell_self_intersections(part);assert selfcheck['selfIntersectionFree'];near,excluded=nearby_hosts(tri,faces,hostfaces);selected=[]
 if mode=='authored-lower-edge-mounted-visual-panel':
  assert len(faces)==2 and len(loops)==1 and len(loops[0])==4
  edge=min(loops[0],key=lambda e:(max(e[1][1],e[2][1]),min(e[1][1],e[2][1]),e[1],e[2]));assert max(edge[1][1],edge[2][1])<part[:,:,1].max();selected=[mount_edge(tri,edge,near,1,host_scope_faces=hostfaces)]
 elif mode=='authored-side-edge-mounted-visual-panel':
  assert len(faces)==2 and len(loops)==1 and len(loops[0])==4;low=part[:,:,1].min();high=part[:,:,1].max()
  for e in loops[0]:
   if min(e[1][1],e[2][1])==low and max(e[1][1],e[2][1])==high and e[1][0]==e[2][0] and e[1][2]==e[2][2]:
    for axis in [0,2]:
     if not any(np.cross(tri[j,1]-tri[j,0],tri[j,2]-tri[j,0])[axis]!=0 for j in near):continue
     r=mount_edge(tri,e,near,axis,host_scope_faces=hostfaces)
     if r['band']['verifiedCompleteOriginalEdgeContactBand']:selected.append(r)
  assert selected,'Complete full-height authored side mount required'
 elif mode=='authored-two-ended-mounted-visual-sleeve':
  assert len(faces)==8 and len(loops)==2 and all(len(v)==4 for v in loops)
  for loop in loops:
   for e in loop:
    trials=[mount_edge(tri,e,near,k,host_scope_faces=hostfaces) for k in [0,2] if any(np.cross(tri[j,1]-tri[j,0],tri[j,2]-tri[j,0])[k]!=0 for j in near)];passed=[r for r in trials if r['band']['verifiedCompleteOriginalEdgeContactBand']];assert passed,'Both complete original end openings must mount';selected.append(passed[0])
 elif mode=='authored-upper-opening-mounted-visual-sleeve':
  assert len(faces)==8 and len(loops)==2 and all(len(v)==4 for v in loops);upper=max(loops,key=lambda v:min(min(a[1],b[1]) for _,a,b in v));lower=next(v for v in loops if v is not upper);assert min(min(a[1],b[1]) for _,a,b in upper)>max(max(a[1],b[1]) for _,a,b in lower)
  assert all(abs(n[1])<=.25*np.linalg.norm(n) for n in normals),'Only original vertical open sleeve, no upward roof/body'
  selected=[mount_edge(tri,e,near,1,host_scope_faces=hostfaces) for e in upper]
 else:raise AssertionError('Unknown source-specific detail role')
 assert selected and all(r['band']['verifiedCompleteOriginalEdgeContactBand'] for r in selected),'Every credited complete original mount stays within unchanged finite band'
 return dict(role=mode,allOriginalFaces=faces,allOriginalDirectedOpeningLoops=[[dict(sourceFace=i,vertices=[list(a),list(b)]) for i,a,b in v] for v in loops],completeOriginalMounts=selected,rigorouslyOutsideFixedBandOriginalHostFaces=excluded,originalSelfIntersection=selfcheck,closedSolidCertified=False,syntheticCapCreated=False,structuralRootCredit=False,structuralBridgeCredit=False)

def verify(triangles,contexts,graph,ground,world,*,expected_role,expected_binding,current_binding):
 tri=np.asarray(triangles,float);world=np.asarray(world,float);ground=np.asarray(ground,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and world.shape==tri.shape and np.isfinite(tri).all() and np.isfinite(world).all() and np.max(np.abs(world-tri))<=1e-9;assert ground.ndim==3 and ground.shape[1:]==(3,3) and np.isfinite(ground).all();assert expected_binding==current_binding
 for key,value in [('completeOriginalWorldTrianglesSHA256',hashlib.sha256(tri.tobytes()).hexdigest()),('completeActualRenderedWorldSHA256',hashlib.sha256(world.tobytes()).hexdigest()),('completeCurrentDrawnGroundSHA256',hashlib.sha256(ground.tobytes()).hexdigest()),('completeContinuousContextsSHA256',canonical(contexts)),('completeRootedOriginalGraphSHA256',canonical(graph)),('frozenProviderRoleSHA256',canonical(expected_role))]:assert current_binding[key]==value
 for key in ['actualProviderRootAndStreamsSHA256','completeCurrentPhysicalSHA256','completeCurrentForeignScopeSHA256','currentManifestSHA256']:assert len(current_binding[key])==64
 assert expected_role['sources']==SOURCES and expected_role['contract']=='glorious-peak-six-complete-original-visual-details-v1'
 components=graph['components'];partition=[i for c in components for i in c['globalOriginalFaces']];assert len(components)==365 and len(tri)==18944 and sorted(partition)==list(range(len(tri))) and len(partition)==len(set(partition));assert len(contexts)==len(tri) and all(c['sourceFace']==i for i,c in enumerate(contexts));rooted=set(graph['resolvedOriginalComponents']);assert sorted(set(range(len(components)))-rooted)==list(SPECS);assert graph['exactExposedWallGradeRootComponents'] and all(v not in SPECS for v in graph['groundRootedComponentParents'].values());results=[]
 for k,spec in SPECS.items():
  c=components[k];assert c['globalOriginalFaces']==spec['faces'];host=spec['host'];assert host in rooted and components[host]['actorUID']==c['actorUID'];faces=c['globalOriginalFaces'];proof=component_role(tri,faces,components[host]['globalOriginalFaces'],spec['role']);clearance=[]
  for i in faces:
   ctx=contexts[i];assert ctx['groundProjectionCovered'] is True and ctx['minimum']['minimumGapM']>=-.5
   a=finite_clearance(tri[i],ground);b=finite_clearance(world[i],ground);assert a['existingOrdinaryClearanceBoundProved'] and b['existingOrdinaryClearanceBoundProved'];clearance.append(dict(sourceFace=i,completeOriginal=a,completeRendered=b,rawMinimumVerbatim=ctx['minimum']))
  results.append(dict(component=k,actorUID=c['actorUID'],alreadyRootedHostComponent=host,**proof,independentCompleteFacetClearance=clearance))
 return dict(contract='glorious-peak-six-complete-original-visual-details-v1',allOriginalFaces=len(tri),allOriginalComponents=len(components),accountedVisualComponents=list(SPECS),allComponentsAccounted=True,completeOriginalVisualRoles=results,rawUnresolvedOriginalComponentsPreserved=graph['unresolvedOriginalComponents'],visualGroundRootCredit=False,visualStructuralBridgeCredit=False,sourceGeometryChanges=0,installationApproved=False,binding=current_binding,mandatoryIndependentFullCurrentGates=True)
