"""Provider-authored ledge shape, independently literal-rendered back U mounts.

Binary shader transform rounding is recorded; no welding/contact tolerance or
runtime solid certification. Complete physical/provider/root gates still needed.
"""
import hashlib
import numpy as np
from mei_yat_original_open_ended_ledge_geometry_20261010 import verify
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as finite_band
def verify_rendered(original,rendered,faces,rooted_host_faces,*,expected_original_sha256,expected_rendered_sha256):
 t=np.asarray(original,float);w=np.asarray(rendered,float);assert w.shape==t.shape and np.isfinite(w).all();assert hashlib.sha256(w.tobytes()).hexdigest()==expected_rendered_sha256
 difference=float(np.max(np.abs(t-w)));assert difference<=1e-9,'Full provider-to-runtime original vertex correspondence bound'
 authored=verify(t,faces,rooted_host_faces,expected_world_sha256=expected_original_sha256);actual=[]
 for p in authored['completeMountedBackUEdges']:
  i=p['sourceFace'];a,b=np.asarray(p['originalEdge']);ia=np.flatnonzero(np.all(t[i]==a,axis=1));ib=np.flatnonzero(np.all(t[i]==b,axis=1));assert len(ia)==len(ib)==1
  edge=w[i,[int(ia[0]),int(ib[0])]];q=finite_band(edge,w[rooted_host_faces]);assert q['verifiedCompleteOriginalEdgeFiniteFacadeBand'],'Every literal actual-rendered complete back edge must independently satisfy unchanged0.1m finite host band'
  actual.append(dict(originalFace=i,originalFaceVertexIndices=[int(ia[0]),int(ib[0])],literalActualEdge=edge.tolist(),independentLiteralFiniteHostBand=q))
 assert len(actual)==3
 return dict(contract='named-original-eight-face-open-ended-ledge-geometry-and-literal-mount-v2',verifiedOriginalLedgeGeometry=True,originalGeometryProof=authored,completeOriginalFaces=list(faces),completeLiteralRenderedFacetSHA256s=[hashlib.sha256(w[i].tobytes()).hexdigest() for i in faces],completeLiteralRenderedBackUEdges=actual,providerToLiteralRuntimeMaximumCoordinateDifferenceM=difference,authoredTopologyEstablishedOnExactProviderSourceOnly=True,literalRuntimeBinaryHeightLevelCount=len(set(w[faces,:,1].reshape(-1))),literalRuntimeHorizontalOrClosedSolidCertification=False,sourceGeometryChanges=0,syntheticBackOrEndCapCreated=False,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False,mandatoryIndependentWholeOriginalAndLiteralFacetClearance=True,mandatoryIndependentRootedHostProviderCurrentBinding=True)
