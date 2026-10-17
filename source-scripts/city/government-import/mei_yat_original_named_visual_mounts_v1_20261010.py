"""Source-specific Mei Yat visual mounts; never structural roots or bridges.

All 121 original detail components are retained and enumerated. The original
source defines authored shape; literal rendered interfaces are independently
checked. Full current source/provider/foreign/physical gates remain mandatory.
"""
import collections,hashlib,json
import numpy as np
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify as facet_band
from mei_yat_original_open_ended_ledge_geometry_v2_20261010 import verify_rendered as ledge
from exact_shell_context_accelerated_20261009 import shell_self_intersections
SOURCE='ca03730a32beed8bd41aea1ef631517746bf20861dc83000364b39040abfcb82'
WORLD='89f8ba84f7f5058e18fa23a77f704587bb7d82d9f7ac05276090b79bb5c91f59'
ACTUAL='6f0aa350ffe39fa243b91065bfcddddf658daeea6a017756d9e5bf2bafcbd511'
PANELS=[*range(17),*range(62,78),*range(193,202)]
LEDGES=[k for k in range(721,800) if k!=722]
DETAILS=sorted(PANELS+LEDGES+[722])
TRIM_PARTS={'lowerLedge':[6189,6190,*range(7009,7015)],'upperLedge':[6343,6344,*range(7471,7477)],'verticalTrim':list(range(6987,7003))}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def topology(t,ids):
 edges=collections.defaultdict(list);adj=collections.defaultdict(set)
 for i in ids:
  v=list(map(tuple,t[i]));assert len(set(v))==3
  assert np.linalg.norm(np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]))>0
  for a,b in zip(v,v[1:]+v[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
 for e,inc in edges.items():
  assert len(inc)<=2,'Named subpart must retain actual manifold authored surface'
  if len(inc)==2:
   assert inc[0][1:]==inc[1][1:][::-1],'Reversed shared authored edge'
   a,b=inc[0][0],inc[1][0];adj[a].add(b);adj[b].add(a)
 seen={ids[0]};todo=list(seen)
 while todo:
  for i in adj[todo.pop()]-seen:seen.add(i);todo.append(i)
 assert seen==set(ids),'Detached subpart cannot receive visual mount'
 check=shell_self_intersections(t[ids]);assert check['selfIntersectionFree']
 boundary=[inc[0] for _,inc in sorted(edges.items()) if len(inc)==1];assert boundary
 directed={a:b for _,a,b in boundary};assert len(directed)==len(boundary) and set(directed)==set(directed.values())
 loops=[];remaining=set(directed)
 while remaining:
  start=min(remaining);loop=[];p=start
  while p not in loop:loop.append(p);p=directed[p]
  assert p==start;remaining-=set(loop);loops.append(loop)
 return edges,boundary,loops,check
def complete_boundary_mounts(t,w,ids,hosts,expected_lengths):
 edges,boundary,loops,selfcheck=topology(t,ids);assert sorted(map(len,loops))==sorted(expected_lengths)
 proofs=[]
 for i,a,b in boundary:
  ia=np.flatnonzero(np.all(t[i]==a,axis=1));ib=np.flatnonzero(np.all(t[i]==b,axis=1));assert len(ia)==len(ib)==1
  original=edge_band(np.array([a,b]),t[hosts]);literal=edge_band(w[i,[int(ia[0]),int(ib[0])]],w[hosts])
  assert original['verifiedCompleteOriginalEdgeFiniteFacadeBand'] is True and literal['verifiedCompleteOriginalEdgeFiniteFacadeBand'] is True,'Every complete original and literal mounting edge stays within fixed .1m'
  proofs.append(dict(sourceFace=i,originalEdge=[a,b],literalVertexIndices=[int(ia[0]),int(ib[0])],originalMountProof=original,literalMountProof=literal))
 return dict(completeBoundaryMounts=proofs,originalBoundaryLoops=loops,originalSelfIntersection=selfcheck)
def panel_shape(t,ids):
 assert len(ids)==8;vertices=set(map(tuple,t[ids].reshape(-1,3)));levels={p[1] for p in vertices};plans={(p[0],p[2]) for p in vertices}
 assert len(vertices)==8 and len(levels)==2 and len(plans)==4 and {(x,y,z) for x,z in plans for y in levels}==vertices
 horizontal=[];vertical=[]
 for i in ids:
  n=np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]);assert np.linalg.norm(n)>0
  if len(set(t[i,:,1]))==1:assert n[0]==n[2]==0;horizontal.append(i)
  else:assert n[1]==0;vertical.append(i)
 assert len(horizontal)==len(vertical)==4
 _,_,loops,_=topology(t,ids);assert sorted(map(len,loops))==[4,4]
 return vertical
def verify(original,rendered,graph,finite,provider_roles,*,expected_binding,current_binding):
 t=np.asarray(original,float);w=np.asarray(rendered,float)
 assert t.shape==w.shape==(10209,3,3) and np.isfinite(t).all() and np.isfinite(w).all()
 assert hashlib.sha256(t.tobytes()).hexdigest()==WORLD and hashlib.sha256(w.tobytes()).hexdigest()==ACTUAL
 assert np.max(np.abs(t-w))<=1e-9,'Actual literal correspondence, never contact welding'
 assert expected_binding==current_binding and current_binding
 for key,value in [('completeOriginalWorldSHA256',WORLD),('completeLiteralWorldSHA256',ACTUAL),('completeGraphSHA256',canonical(graph)),('completeFiniteContextsSHA256',canonical(finite)),('providerRolesSHA256',canonical(provider_roles))]:assert current_binding[key]==value,'Full bound source/context differs'
 assert len(graph['actors'])==1 and graph['actors'][0]['uid']=='landsd/183776:0' and graph['actors'][0]['sourceSHA256']==SOURCE
 parts=graph['components'];assert len(parts)==878;partition=[i for p in parts for i in p['globalOriginalFaces']];assert len(partition)==len(set(partition))==10209 and sorted(partition)==list(range(10209))
 roots=graph['resolvedOriginalComponents'];assert roots==sorted(set(roots)) and len(roots)==757 and graph['ordinaryGroundRootComponents']==[124]
 assert sorted(set(range(878))-set(roots))==DETAILS and len(DETAILS)==121
 assert all(k not in DETAILS for k in graph['groundRootedComponentParents'].values()),'No visual part may root or bridge an ordinary part'
 assert graph['supportInterfaceAccepted'] is False and graph['binding']['completeOriginalWorldTrianglesSHA256']==WORLD
 assert provider_roles['contract']=='mei-yat-authored-panels-open-ended-ledges-and-corner-trim-visual-only-v1' and provider_roles['sourceSHA256']==SOURCE and provider_roles['completeOriginalWorldSHA256']==WORLD
 roles=provider_roles['roles'];assert [r['component'] for r in roles]==DETAILS and {r['component']:r['completeOriginalFaces'] for r in roles}=={k:parts[k]['globalOriginalFaces'] for k in DETAILS}
 assert len(finite['rows'])==1;f=finite['rows'][0];assert f['completeOriginalWorldSHA256']==WORLD and f['completeActualRenderedWorldSHA256']==ACTUAL and f['completeOriginalFaces']==10209 and f['uid']=='landsd/183776:0'
 assert not f['unprovedOriginalFaces'] and not f['unprovedActualRenderedFaces'];assert len(f['allFaces'])==10209 and [r['sourceFace'] for r in f['allFaces']]==list(range(10209))
 assert all(r['completeOriginalBoundProved'] is True and r['completeActualRenderedBoundProved'] is True for r in f['allFaces']),'Every ordinary/detail facet retains strict original and literal clearance'
 hosts=sorted(i for k in roots for i in parts[k]['globalOriginalFaces']);result=[]
 for role in roles:
  k=role['component'];ids=parts[k]['globalOriginalFaces'];q={}
  if k in LEDGES:
   assert role['kind']=='original-eight-face-open-ended-facade-ledge';q=ledge(t,w,ids,hosts,expected_original_sha256=WORLD,expected_rendered_sha256=ACTUAL)
  elif k in PANELS:
   vertical=panel_shape(t,ids)
   if k not in [76,77]:
    assert role['kind']=='original-panel-two-complete-mounted-open-boundaries';q=complete_boundary_mounts(t,w,ids,hosts,[4,4])
   else:
    assert role['kind']=='original-projecting-panel-complete-mounted-front-facets';front=[610,611] if k==76 else [618,619];assert set(front)<=set(vertical)
    vertices=set(map(tuple,t[front].reshape(-1,3)));assert len(vertices)==4 and len({p[1] for p in vertices})==2 and len({(p[0],p[2]) for p in vertices})==2
    n=np.cross(t[front[0],1]-t[front[0],0],t[front[0],2]-t[front[0],0]);assert all(np.dot(n,t[i,j]-t[front[0],0])==0 for i in front for j in range(3))
    proofs=[]
    for i in front:
     a=facet_band(t[i],t[hosts]);b=facet_band(w[i],w[hosts]);assert a['verifiedWholeOriginalFacetFiniteFacadeBand'] is True and b['verifiedWholeOriginalFacetFiniteFacadeBand'] is True,'Whole original/literal finite front surfaces must independently mount'
     proofs.append(dict(originalFace=i,originalFiniteMount=a,literalFiniteMount=b))
    q=dict(completeMountedOriginalFrontFaces=front,wholeOriginalAndLiteralFrontProofs=proofs,originalTwoOpeningsRetained=True,allOtherOriginalFacesRetained=sorted(set(ids)-set(front)),rawWholeBackLoopFailurePreserved=True)
  else:
   assert k==722 and role['kind']=='original-complete-corner-trim-and-two-open-ended-ledges'
   assert sorted(i for x in TRIM_PARTS.values() for i in x)==sorted(ids) and len(set(i for x in TRIM_PARTS.values() for i in x))==32
   q={name:(complete_boundary_mounts(t,w,sub,hosts,[6]) if name=='verticalTrim' else ledge(t,w,sub,hosts,expected_original_sha256=WORLD,expected_rendered_sha256=ACTUAL)) for name,sub in TRIM_PARTS.items()}
   full=collections.defaultdict(list)
   for i in ids:
    v=list(map(tuple,t[i]))
    for a,b in zip(v,v[1:]+v[:1]):full[tuple(sorted((a,b)))].append((i,a,b))
   nonmanifold=[dict(edge=e,incidences=inc) for e,inc in sorted(full.items()) if len(inc)>2];assert len(nonmanifold)==2 and all(len(x['incidences'])==3 for x in nonmanifold)
   q['completeOriginalTripleIncidenceInterfacesRetained']=nonmanifold;q['wholeAssemblyManifoldOrClosedSolidCertification']=False
  result.append(dict(component=k,kind=role['kind'],completeOriginalFaces=ids,completeLiteralFacetSHA256s=[hashlib.sha256(w[i].tobytes()).hexdigest() for i in ids],actualMountGeometry=q,sourceGeometryChanges=0,syntheticBackOrEndCapCreated=False,closedSolidCertified=False,structuralRootCredit=False,structuralBridgeCredit=False))
 return dict(contract=provider_roles['contract'],completeOriginalFaces=10209,completeOriginalComponents=878,independentlyStructuralComponents=roots,namedVisualOnlyComponents=DETAILS,allComponentsAccounted=True,completeOriginalAndLiteralVisualMounts=result,rawStrictStructuralReasonsPreserved=graph['reasons'],sourceGeometryChanges=0,visualDetailsSupplyNoStructuralRootsOrBridges=True,fullAcceptance=False,installationApproved=False,mandatoryFreshCurrentProviderForeignFoundationRuntimeGates=True,binding=current_binding)
