"""Exact641-face Mount podium: two named conditional visual-only proposals.

Thin original open-BACK strip270..279 (authored upper278/279 kept) needs every
edge of its4edge open back rectangle in the existing finite host band. Original
12face projecting part448..459 needs BOTH backing facets456/457 and their whole
4edge perimeter in that band. Every free/source boundary stays untouched.
This certifies association only. Whole current clearance/grounded host and all
physical/source/identity/foreign/runtime gates remain independent requirements.
"""
from collections import Counter
import hashlib,json
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_verify
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_verify
SOURCE='4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781';UID='landsd/75782:0'
def sha(a):return hashlib.sha256(np.asarray(a,np.float64).tobytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def edges(tri,ids):return Counter(tuple(sorted((tuple(a),tuple(b))))for i in ids for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0))if not np.array_equal(a,b))
def loop(records):
 out=sorted(e for e,n in records.items()if n==1);assert len(out)==4 and all(n==2 for n in Counter(v for e in out for v in e).values()),'Complete original backing perimeter must be a4edge cycle';return out

def verify(triangles,hostids,*,expected_binding,current_binding):
 tri=np.asarray(triangles,float);assert tri.shape==(641,3,3)and np.isfinite(tri).all();assert expected_binding==current_binding
 assert current_binding['uid']==UID and current_binding['sourceSHA256']==SOURCE
 assert current_binding['completeWorldTrianglesSHA256']==sha(tri)and current_binding['completeHostSourceFaceIdsSHA256']==canonical(hostids)
 inv=census(tri,list(range(641)));parts=inv['sharedEdgeConnectedComponents'];assert [len(p)for p in parts]==[576,10,10,10,10,10,12]
 assert hostids==parts[0] and parts[1]==list(range(270,280))and parts[6]==list(range(448,460));assert not set(hostids)&set(parts[1]+parts[6]);hosts=tri[hostids]
 rows=[]
 for part,ids in [(1,parts[1]),(6,parts[6])]:
  c=census(tri,ids);assert c['sharedEdgeConnectedComponents']==[ids]and not c['exactNonrenderingOriginalFaces']and c['twoFaceOrientationConflicts']==0 and c['nonmanifoldEdges']==0
  for i in ids:assert not exact_nonrendering(tri[i])
  normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lengths=np.linalg.norm(normals,axis=1);ratio=np.divide(normals[:,1],lengths,out=np.zeros(len(tri)),where=lengths!=0)
  if part==1:
   assert c['boundaryEdges']==4;lo=tri[ids].min((0,1));hi=tri[ids].max((0,1));assert 0<hi[1]-lo[1]<=.1,'This exact source role is a thin original strip'
   assert all(np.all(tri[i,:,1]==hi[1])and ratio[i]>.25 for i in [278,279]),'Original upper faces must remain'
   assert all(np.all(tri[i,:,1]==lo[1])and ratio[i]<-.25 for i in [272,273]),'Original lower faces must remain'
   boundary=loop(edges(tri,ids));horizontal=[e for e in boundary if e[0][1]==e[1][1]];vertical=[e for e in boundary if e[0][0]==e[1][0]and e[0][2]==e[1][2]]
   assert len(horizontal)==len(vertical)==2 and all(np.linalg.norm(np.asarray(e[1])-e[0])>9 for e in horizontal),'Authored opening is the long BACK side, never an invented upper opening'
   backed=[];name='original-thin-open-back-mounted-strip'
  else:
   assert c['boundaryEdges']==0;backed=[456,457];sideedges=edges(tri,backed);assert sorted(sideedges.values())==[1,1,1,1,2];boundary=loop(sideedges);backproofs=[dict(sourceFace=i,proof=facet_verify(tri[i],hosts))for i in backed];assert all(r['proof']['wholeFacetAssociated']for r in backproofs),'Both whole original backing facets must be associated';name='original-complete-back-side-mounted-projecting-detail'
  proofs=[dict(wholeOriginalBackingEdge=[list(v)for v in e],proof=edge_verify(e,hosts))for e in boundary];assert all(r['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in proofs),'Every original backing edge must remain in the fixed finite host band'
  rows.append(dict(proposedRole=name,completeOriginalSourceFaces=ids,completeOriginalPartEdgeCensus=c,completeOriginalBackingSideFaces=backed,wholeBackingFacetProofs=[]if part==1 else backproofs,completeAuthoredBackingPerimeterProofs=proofs,originalUpperFaceIds=[278,279]if part==1 else[458,459],originalOpenBoundariesPreserved=c['boundaryEdges'],mountAssociationVerified=True,structuralRootCredit=False,structuralBridgeCredit=False,hostTransferCredit=False,closedSolidCertification=False,authoredFunctionInferred=False))
 return dict(contract='mount-verdant-exact-original-two-complete-back-mounted-visual-proposals-v1',binding=current_binding,rows=rows,completeOwned641OriginalFacesAccountedInCensus=True,all22OriginalDetailFacesRetained=True,rawLowerLoopAndWholeFacetFailuresMustRemain=True,independentGroundedHostAndWholeCurrentClearanceStillRequired=True,uninstalledTowerHostOrBridgeAllowed=False,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,currentAcceptance=False,installationApproved=False)
