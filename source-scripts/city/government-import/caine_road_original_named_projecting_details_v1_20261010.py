"""Pinned original Caine Road cantilever and slanted strip; visual roles only.

The two complete authored components supply no structural root or graph edge.
Their already-rooted original hosts and every current physical/foreign gate
must independently replay in the source adapter. No free edge is fabricated.
"""
import hashlib,json
import numpy as np
from mei_yat_original_named_visual_mounts_v1_20261010 import topology
from original_local_perpendicular_boundary_diagnostic_20261010 import prepare_hosts,diagnose
from exact_original_perpendicular_edge_facet_band_20261010 import verify as edge_band
WORLD='c24164f8d954951fb9aeca34a1fa7175a2f240fb1446a090e4e20499d425e1ca'
SOURCES={'landsd/101781:0':'6e92dc2a141a672e8f0ca22b9d08d321bbd9418fc77d159c2720824766c8f5ec','landsd/268032:0':'4d907ca0b46ae5edbb9b2fa6c070f677e776e73b4dea7d61303a1ea50853b4ba'}
DETAILS={70:list(range(7983,7993)),202:[10943,10944]}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(v):return hashlib.sha256(np.asarray(v,dtype=np.float64).tobytes()).hexdigest()
def verify(original,rendered,graph,finite,provider_roles,*,expected_binding,current_binding):
 t=np.asarray(original,float);w=np.asarray(rendered,float)
 assert t.shape==w.shape==(10947,3,3) and np.isfinite(t).all() and np.isfinite(w).all()
 assert sha(t)==sha(w)==WORLD,'Every source/literal face remains exact pinned original; no pose change or welding'
 assert expected_binding==current_binding
 for key,value in [('completeOriginalWorldSHA256',WORLD),('completeLiteralWorldSHA256',WORLD),('completeGraphSHA256',canonical(graph)),('completeFiniteContextsSHA256',canonical(finite)),('providerRolesSHA256',canonical(provider_roles))]:assert current_binding[key]==value,'Changed source/context/role'
 assert {r['uid']:r['sourceSHA256'] for r in graph['actors']}==SOURCES and [r['globalFaceRange'] for r in graph['actors']]==[[0,354],[354,10947]]
 parts=graph['components'];assert len(parts)==204
 partition=[i for p in parts for i in p['globalOriginalFaces']];assert len(partition)==len(set(partition))==10947 and sorted(partition)==list(range(10947))
 assert {k:parts[k]['globalOriginalFaces'] for k in DETAILS}==DETAILS
 roots=graph['resolvedOriginalComponents'];assert roots==sorted(set(range(204))-set(DETAILS)) and graph['ordinaryGroundRootComponents']==[0,4]
 assert graph['supportInterfaceAccepted'] is False and graph['binding']['completeOriginalWorldTrianglesSHA256']==WORLD
 assert all(k not in DETAILS for k in graph['groundRootedComponentParents'].values()),'Visual details cannot root or bridge any body'
 assert provider_roles==dict(contract='caine-road-pinned-open-back-cantilever-and-one-end-slanted-strip-visual-only-v1',sourceSHA256s=SOURCES,completeOriginalWorldSHA256=WORLD,roles=[dict(component=70,kind='original-ten-face-open-back-cantilever',completeOriginalFaces=DETAILS[70]),dict(component=202,kind='original-two-face-one-end-mounted-slanted-strip',completeOriginalFaces=DETAILS[202])])
 assert [r['uid'] for r in finite['rows']]==list(SOURCES)
 assert sum(r['completeOriginalFaces'] for r in finite['rows'])==10947
 for f in finite['rows']:
  assert f['sourceSHA256']==SOURCES[f['uid']]
  assert not f['unprovedOriginalFaces'] and not f['unprovedActualRenderedFaces']
  assert [r['sourceFace'] for r in f['allFaces']]==list(range(f['completeOriginalFaces']))
  assert all(r['completeOriginalBoundProved'] is True and r['completeActualRenderedBoundProved'] is True for r in f['allFaces']),'Every complete original/literal facet keeps strict clearance'
 hosts=sorted(i for k in roots for i in parts[k]['globalOriginalFaces']);results=[]
 for k,ids in DETAILS.items():
  _,boundary,loops,selfcheck=topology(t,ids)
  assert sorted(map(len,loops))==[4] and len(boundary)==4
  assert sorted(set(tuple(v) for face in t[ids] for v in face))==sorted(set(tuple(v) for face in w[ids] for v in face))
  if k==70:
   assert len(set(map(tuple,t[ids].reshape(-1,3))))==8
   proofs=[]
   for i,a,b in boundary:
    ia=np.flatnonzero(np.all(t[i]==a,axis=1));ib=np.flatnonzero(np.all(t[i]==b,axis=1));assert len(ia)==len(ib)==1
    x=edge_band(np.asarray([a,b]),t[hosts]);y=edge_band(w[i,[int(ia[0]),int(ib[0])]],w[hosts])
    assert x['verifiedCompleteOriginalEdgePerpendicularBand'] is True and y['verifiedCompleteOriginalEdgePerpendicularBand'] is True,'All four complete authored open-back edges must mount'
    proofs.append(dict(sourceFace=i,completeOriginalEdge=[a,b],literalVertexIndices=[int(ia[0]),int(ib[0])],originalMount=x,literalMount=y))
   q=dict(completeOriginalFourEdgeBackLoop=loops[0],completeOriginalAndLiteralMounts=proofs,authoredFreeClosedFarEndRetained=True,rawMinimumYRoofPerimeterFailurePreserved=True)
  else:
   assert len(set(map(tuple,t[ids].reshape(-1,3))))==4
   x=t[ids].reshape(-1,3);maxz=float(x[:,2].max());minz=float(x[:,2].min())
   mount=[e for e in boundary if e[1][2]==e[2][2]==maxz];opposite=[e for e in boundary if e[1][2]==e[2][2]==minz];assert len(mount)==len(opposite)==1
   proofs=[]
   for name,(i,a,b) in [('completeMountedEnd',mount[0]),('separateOppositeLowerCorner',opposite[0])]:
    if name=='separateOppositeLowerCorner' and a[1]>b[1]:a,b=b,a
    ia=np.flatnonzero(np.all(t[i]==a,axis=1));ib=np.flatnonzero(np.all(t[i]==b,axis=1));assert len(ia)==len(ib)==1
    original=edge_band(np.asarray([a,b]),t[hosts]);literal=edge_band(w[i,[int(ia[0]),int(ib[0])]],w[hosts])
    if name=='completeMountedEnd':assert original['verifiedCompleteOriginalEdgePerpendicularBand'] is True and literal['verifiedCompleteOriginalEdgePerpendicularBand'] is True,'The whole end edge must mount, not only a point'
    else:
     assert any(a=='0' for a,b in original['exactCertifiedMergedIntervals']) and any(a=='0' for a,b in literal['exactCertifiedMergedIntervals']),'Separate opposite lower authored corner must have finite host band witness'
     assert not original['verifiedCompleteOriginalEdgePerpendicularBand'] and not literal['verifiedCompleteOriginalEdgePerpendicularBand'],'Free opposite upper edge retained, not a fabricated full-edge interface'
    proofs.append(dict(kind=name,sourceFace=i,completeOriginalEdge=[a,b],literalVertexIndices=[int(ia[0]),int(ib[0])],originalMount=original,literalMount=literal))
   q=dict(wholeOriginalAndLiteralMountedEndAndSeparateCorner=proofs,completeAuthoredBoundary=loops[0],everyFreeOriginalEdgeRetained=True,rawWholeFacetAndWholeBoundaryMountFailuresPreserved=True)
  results.append(dict(component=k,completeOriginalFaces=ids,wholeOriginalSelfIntersection=selfcheck,mountGeometry=q,sourceGeometryChanges=0,closedSolidCertified=False,structuralRootCredit=False,structuralBridgeCredit=False))
 return dict(contract=provider_roles['contract'],completeOriginalFaces=10947,completeOriginalComponents=204,independentlyStructuralComponents=roots,namedVisualOnlyComponents=sorted(DETAILS),allComponentsAccounted=True,completeOriginalAndLiteralVisualMounts=results,rawStrictStructuralReasonsPreserved=graph['reasons'],fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0,visualDetailsSupplyNoStructuralRootsOrBridges=True,mandatoryFreshCurrentProviderForeignFoundationRuntimeGates=True,binding=current_binding)
