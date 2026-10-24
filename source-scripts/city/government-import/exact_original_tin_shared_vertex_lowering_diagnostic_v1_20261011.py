"""Whole-indexed-TIN source-only lowering/incident/seam certificate.

No unchanged-government-TIN, source-role, root, foreign/current or installation
credit. Every original indexed triangle is retained in order. Duplicate original
XYZ values share the same derived Y. All changed incident facets are enumerated;
every source edge between changed/unchanged facets is exactly unchanged and its
complete affine segment therefore remains the same. Existing nonmanifold edges
are explicitly reported, never silently repaired or certified as manifold.
"""
from fractions import Fraction as F
import hashlib,json
import numpy as np
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def canonical(a):return hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify(original,derived,*,expected_binding,current_binding,maximum_downward_delta=.65):
 old=np.asarray(original,dtype='<f8');new=np.asarray(derived,dtype='<f8');assert old.shape==new.shape and old.ndim==3 and old.shape[1:]==(3,3)and len(old)>0 and np.isfinite(old).all()and np.isfinite(new).all()
 assert expected_binding==current_binding and expected_binding['completeOriginalGroundSHA256']==sha(old)and expected_binding['completeDerivedGroundSHA256']==sha(new)
 cap=F(float(maximum_downward_delta));assert cap==F(.65),'This named diagnostic retains its explicit hypothetical correction cap'
 assert np.array_equal(old[:,:,[0,2]],new[:,:,[0,2]]),'Original XZ, facet order and projection must remain identical'
 changed=old[:,:,1]!=new[:,:,1];faces=np.flatnonzero(changed.any(axis=1)).tolist();assert faces,'Distinct derived terrain must disclose a real change'
 corrections={};occurrences={}
 for fi,vi in np.argwhere(changed):
  p=tuple(float(x)for x in old[fi,vi]);target=float(new[fi,vi,1]);delta=F(p[1])-F(target);assert 0<delta<=cap,'Terrain must lower only, within the proposed bound'
  assert p not in corrections or corrections[p]==target,'Duplicate source vertex received inconsistent height';corrections[p]=target
 for p,target in corrections.items():
  mask=np.all(old==np.asarray(p),axis=2);assert np.all(new[:,:,1][mask]==target),'Every original duplicate XYZ occurrence must be changed consistently';occurrences[p]=int(mask.sum())
 expected=np.zeros(old.shape[:2],bool)
 for p in corrections:expected|=np.all(old==np.asarray(p),axis=2)
 assert np.array_equal(changed,expected);assert np.array_equal(old[~changed],new[~changed]),'Every unmodified vertex must retain all three original bytes'
 exterior=np.flatnonzero(~changed.any(axis=1)).tolist();assert old[exterior].tobytes()==new[exterior].tobytes()
 # Exact authored XYZ incidence: no welding, threshold or discarded facet.
 edge_incidence={}
 for fi,triangle in enumerate(old):
  vertices=[tuple(float(x)for x in p)for p in triangle]
  for a,b in zip(vertices,vertices[1:]+vertices[:1]):
   edge=tuple(sorted((a,b)));edge_incidence.setdefault(edge,set()).add(fi)
 changed_set=set(faces);seams=[];nonmanifold=[]
 for edge,incidence in edge_incidence.items():
  if len(incidence)>2:nonmanifold.append(dict(originalEdge=[list(p)for p in edge],wholeOriginalIncidentFaces=sorted(incidence)))
  if incidence&changed_set and incidence-changed_set:
   assert all(p not in corrections for p in edge),'Changed/unchanged source seam endpoint differs'
   seams.append(dict(originalEdge=[list(p)for p in edge],changedIncidentFaces=sorted(incidence&changed_set),unchangedIncidentFaces=sorted(incidence-changed_set),exactEndpointsAndCompleteAffineEdgeUnchanged=True))
 changes=[dict(originalXYZ=list(p),derivedFloat64Y=y,exactDownwardDeltaM=str(F(p[1])-F(y)),allOriginalDuplicateRecords=occurrences[p])for p,y in sorted(corrections.items())]
 return dict(contract='complete-original-indexed-tin-shared-vertex-lowering-diagnostic-v1',completeOriginalGroundSHA256=sha(old),completeDerivedGroundSHA256=sha(new),completeOriginalIndexedFaces=len(old),completeOriginalFacetOrderAndXZIdentical=True,allOriginalIndicesAndFacesAccounted=True,completeChangedOriginalFaceIDs=faces,completeUnchangedExteriorFaceIDs=exterior,unchangedExteriorFacetBytesSHA256=hashlib.sha256(old[exterior].tobytes()).hexdigest(),allSharedOriginalXYZDuplicatesUpdated=True,allChangedIncidentFacetsEnumerated=True,completeSourceBoundaryAffineSeams=seams,allSourceChangedUnchangedSeamsExactlyPreserved=True,rawOriginalNonmanifoldEdges=nonmanifold,closedOrManifoldTINClaim=False,completeOriginalVertexCorrections=changes,maximumDownwardDeltaM=str(max(F(r['exactDownwardDeltaM'])for r in changes)),sourceOnly=True,alteredTerrainDisclosed=True,unchangedGovernmentTINCredit=False,sourceRoleOrRootCredit=False,currentForeignOrSurfaceAccepted=False,fullAcceptance=False,installationApproved=False)
