"""Named unchanged Festival sign, roof rail and roof trim visual mounts.

Every credited interface remains inside the existing finite .1m distance band.
The authored open geometry is retained; no back cap, root, bridge or closed solid
is invented. Fresh full physical/foreign/provider gates are mandatory externally.
"""
import hashlib,json,collections
import numpy as np
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as band
WORLD='e748d91dfc7073785a840a0c127f9466c4b2028086fa064c47ff1d4052333a71'
SOURCES={'landsd/91827:0':'786e89452ba921ce3b16ba1b899919d4965f829ea5fb7b1756cd6ab5ed4c2ef8','landsd/104302:0':'4fc3b065399321f7a0a05d8b6c8f47fe813c2924677e009104f13cc7b1d2f0fe'}
FACADE=[46,53,58,92,176,177,178,179,180,201,202,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,276]
ROOF=[122,130,131,132,133,134,135,139,140,141,142,235,236,237,240,241,242,258,259,263]
BACK_OUTER_FACES=[28820,28823,28824,28826,28828,28830,28832,28835,28837,28838,28840,28842,28844,28847,28848,28849,28852,28854,28855,28858,28859,28861,28863,28865,28867,28870,28871,28874,28875,28878,28881,28882,28885,28886,28888,28889,28892,28894,28896,28898,28899,28902,28904,28905,28907]
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(triangles,graph,complete_finite,provider_roles,*,expected_binding,current_binding):
 t=np.asarray(triangles,float);assert t.shape==(35006,3,3) and np.isfinite(t).all() and hashlib.sha256(t.tobytes()).hexdigest()==WORLD,'Complete exact original source differs'
 assert current_binding==expected_binding and current_binding
 for key,value in [('completeOriginalWorldSHA256',WORLD),('completeGraphSHA256',canonical(graph)),('completeFiniteContextsSHA256',canonical(complete_finite)),('providerRolesSHA256',canonical(provider_roles))]:assert current_binding[key]==value,'Frozen full original/context input differs'
 assert {a['uid']:a['sourceSHA256'] for a in graph['actors']}==SOURCES and graph['binding']['completeOriginalWorldTrianglesSHA256']==WORLD
 parts=graph['components'];assert len(parts)==279;partition=[i for p in parts for i in p['globalOriginalFaces']];assert len(partition)==len(set(partition))==35006 and sorted(partition)==list(range(35006))
 roots=graph['resolvedOriginalComponents'];assert roots==sorted(set(roots)) and graph['ordinaryGroundRootComponents'] and not graph['supportInterfaceAccepted']
 claimed=sorted(FACADE+ROOF+[219]);assert len(claimed)==48 and sorted(set(range(279))-set(roots))==claimed,'Visual mounts cannot replace structural failures'
 assert all(k not in claimed for k in graph['groundRootedComponentParents'].values()),'Visual detail cannot root or bridge a component'
 assert provider_roles['contract']=='festival-original-sign-rails-trim-complete-visual-mount-roles-v1' and provider_roles['completeOriginalWorldSHA256']==WORLD and provider_roles['sourceSHA256s']==SOURCES
 roles=provider_roles['roles'];assert [r['component'] for r in roles]==claimed
 assert {r['component']:r['completeOriginalFaces'] for r in roles}=={k:parts[k]['globalOriginalFaces'] for k in claimed}
 assert len(complete_finite['rows'])==2 and {r['uid'] for r in complete_finite['rows']}==set(SOURCES)
 for actor,row in zip(graph['actors'],complete_finite['rows']):
  assert actor['uid']==row['uid'] and actor['sourceSHA256']==row['sourceSHA256'] and actor['originalWorldTrianglesSHA256']==row['completeOriginalWorldSHA256']
  assert not row['unprovedOriginalFaces'] and not row['unprovedActualRenderedFaces'] and row['completeOriginalFaces']==actor['completeOriginalFaceCount']
  fs=row['allFaces'];assert len(fs)==row['completeOriginalFaces'] and [r['sourceFace'] for r in fs]==list(range(len(fs)))
  assert all(r['completeOriginalBoundProved'] is True and r['completeActualRenderedBoundProved'] is True for r in fs),'Ordinary whole-original/rendered finite clearance must remain strict'
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn=np.linalg.norm(n,axis=1);rootfaces=np.array(sorted(i for k in roots for i in parts[k]['globalOriginalFaces']));facades=rootfaces[np.abs(n[rootfaces,1])<=nn[rootfaces]/4];roofs=rootfaces[n[rootfaces,1]>.25*nn[rootfaces]];result=[]
 for role in roles:
  k=role['component'];ids=parts[k]['globalOriginalFaces'];edges=collections.defaultdict(list);va=collections.defaultdict(set)
  for i in ids:
   vs=list(map(tuple,t[i]));assert all(a!=b for a,b in zip(vs,vs[1:]+vs[:1])),'Collapsed original edge requires independent accounting'
   for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((i,a,b));va[a].add(b);va[b].add(a)
  reached={next(iter(va))};todo=list(reached)
  while todo:
   for v in va[todo.pop()]:
    if v not in reached:reached.add(v);todo.append(v)
  assert reached==set(va),'All original detail faces must share authored source connectivity'
  boundary=[e for e,v in sorted(edges.items()) if len(v)==1];assert boundary
  if k in FACADE:
   assert role['kind']=='named-original-facade-sign-complete-open-boundary';chosen=boundary;hosts=facades;order=[0,1,2]
  elif k in ROOF:
   assert role['kind']=='named-original-roof-rail-or-trim-complete-lowest-edges';low=float(t[ids,:,1].min());assert float(t[ids,:,1].max())>low;chosen=[e for e in sorted(edges) if e[0][1]==e[1][1]==low];hosts=roofs;order=[1,0,2]
  else:
   assert k==219 and role['kind']=='named-original-extruded-glyph-complete-outer-back-opening'
   chosen=[e for e in boundary if edges[e][0][0] in BACK_OUTER_FACES];assert len(chosen)==45 and sorted(edges[e][0][0] for e in chosen)==sorted(BACK_OUTER_FACES)
   a=collections.defaultdict(set)
   for x,y in chosen:a[x].add(y);a[y].add(x)
   assert all(len(v)==2 for v in a.values()),'Complete original back mounting loop required'
   seen={min(a)};todo=list(seen)
   while todo:
    for v in a[todo.pop()]:
     if v not in seen:seen.add(v);todo.append(v)
   assert seen==set(a);hosts=facades;order=[0,1,2]
  assert chosen and role['completeOriginalMountEdges']==[[list(v) for v in e] for e in chosen],'Incomplete authored mounting interface'
  proofs=[]
  for e in chosen:
   lo=np.minimum(*map(np.array,e))-.1;hi=np.maximum(*map(np.array,e))+.1;near=hosts[np.all(t[hosts].max(axis=1)>=lo,axis=1)&np.all(t[hosts].min(axis=1)<=hi,axis=1)];assert len(near),'No independent finite original host'
   p=band(np.asarray(e)[:,order],t[near][:,:,order]);assert p['verifiedCompleteOriginalEdgeFiniteFacadeBand'],'Complete actual mounting edge outside fixed .1m band'
   proofs.append(dict(originalEdge=e,allOriginalIncidences=edges[e],completeCandidateOriginalHostFaces=near.tolist(),exactOrthonormalCoordinateOrder=order,finiteDistanceProof=p))
  result.append(dict(component=k,kind=role['kind'],completeOriginalFaces=ids,completeOriginalGeometricBoundary=[dict(edge=e,incidences=edges[e]) for e in boundary],originalNonmanifoldEdges=[dict(edge=e,incidences=v) for e,v in sorted(edges.items()) if len(v)>2],originalWindingConflicts=[dict(edge=e,incidences=v) for e,v in sorted(edges.items()) if len(v)==2 and v[0][1:]!=v[1][1:][::-1]],completeOriginalMountProofs=proofs,closedSolidCertified=False,syntheticBackOrBottomCap=False,structuralRootCredit=False,structuralBridgeCredit=False))
 return dict(contract=provider_roles['contract'],completeOriginalFaces=35006,completeOriginalComponents=279,independentlyStructuralComponents=roots,namedVisualOnlyComponents=claimed,allComponentsAccounted=True,roles=result,strictFiniteMountBandM=.1,rawStrictStructuralReasonsPreserved=graph['reasons'],geometryChanges=0,groundRootCredit=False,structuralBridgeCredit=False,fullAcceptance=False,installationApproved=False,binding=current_binding)
