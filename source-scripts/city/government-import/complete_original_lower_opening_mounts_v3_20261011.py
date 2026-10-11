"""Lower-opening v3: one complete nonzero body and only nonzero host facets.
The fixed-band v2 proof is retained, with no source/topology/threshold change.
"""
import numpy as np
from complete_original_lower_opening_mounts_v2_20261011 import binding,verify as prior_verify
from exact_original_shared_edge_component_census_v2_20261011 import census

def verify(triangles,body_faces,host_faces,*,expected_binding):
 t=np.asarray(triangles,float)
 assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all()
 assert body_faces and host_faces and len(body_faces)==len(set(body_faces))and len(host_faces)==len(set(host_faces))and not set(body_faces)&set(host_faces)
 assert all(type(i)is int and 0<=i<len(t)for i in body_faces+host_faces)
 assert binding(t,body_faces,host_faces)==expected_binding,'Exact source/body/host binding mismatch'
 body=census(t,body_faces)
 assert not body['exactNonrenderingOriginalFaces']and len(body['sharedEdgeConnectedComponents'])==1,'Exactly one genuine nonzero shared-edge body required'
 hosts=t[host_faces];normals=np.cross(hosts[:,1]-hosts[:,0],hosts[:,2]-hosts[:,0]);assert np.all(np.any(normals!=0,axis=1)),'Degenerate original host facets provide no band credit'
 p=prior_verify(t,body_faces,host_faces,expected_binding=expected_binding)
 return {**p,'contract':'bound-single-nonzero-original-lower-opening-nondegenerate-host-fixed-band-association-v3','completeNonzeroOriginalBodyEdgeCensus':body,'allOriginalHostFacetsNonzero':True,'priorV2MountProofVerbatim':p}
