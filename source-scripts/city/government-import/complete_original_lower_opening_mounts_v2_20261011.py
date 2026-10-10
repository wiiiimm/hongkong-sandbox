"""Binding-aware complete lower opening: fixed existing ±.1m finite source band.
No cap/repair/function inference, structural credit or full acceptance.
"""
import hashlib,json
import numpy as np
from parkview_block6_four_original_roof_opening_mounts_20261011 import opening
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment

def binding(triangles,body_faces,host_faces):
 t=np.asarray(triangles,float);sha=lambda b:hashlib.sha256(b).hexdigest();canonical=lambda x:sha(json.dumps(x,separators=(',',':')).encode())
 return dict(completeWorldSHA256=sha(t.tobytes()),completeBodyFaceIDsSHA256=canonical(body_faces),completeBodyGeometrySHA256=sha(t[body_faces].tobytes()),completeHostFaceIDsSHA256=canonical(host_faces),completeHostGeometrySHA256=sha(t[host_faces].tobytes()))
def verify(triangles,body_faces,host_faces,*,expected_binding):
 t=np.asarray(triangles,float);assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all()
 assert body_faces and host_faces and len(body_faces)==len(set(body_faces))and len(host_faces)==len(set(host_faces))and not set(body_faces)&set(host_faces)
 assert all(type(i)is int and 0<=i<len(t)for i in body_faces+host_faces)
 current=binding(t,body_faces,host_faces);assert current==expected_binding,'Exact source/body/host binding mismatch'
 part=t[body_faces];assert np.all(np.any(np.cross(part[:,1]-part[:,0],part[:,2]-part[:,0])!=0,axis=1)),'Nonzero original body facets required'
 loop=opening(t,body_faces);low=part[:,:,1].min();high=part[:,:,1].max();assert high>low and all(a[1]==b[1]==low for _,a,b in loop),'Opening must be the complete exact lowest boundary'
 edges=[dict(originalBodyFace=i,originalEdge=[list(a),list(b)],proof=verify_contact_segment(np.asarray([a,b]),t[host_faces]))for i,a,b in loop]
 passed=all(p['proof']['verifiedCompleteOriginalEdgeContactBand']for p in edges)
 return dict(contract='bound-complete-original-lower-opening-fixed-band-association-v2',binding=current,completeOriginalBodyFaces=body_faces,completeOriginalHostFaces=host_faces,completeDirectedLowerOpening=loop,completeFiniteMounts=edges,completeLowerOpeningAssociated=passed,strictBandM=.1,closedSolidCertified=False,structuralRootCredit=False,structuralBridgeCredit=False,architecturalFunctionInferred=False,sourceGeometryChanges=0,currentAcceptance=False,installationApproved=False)
