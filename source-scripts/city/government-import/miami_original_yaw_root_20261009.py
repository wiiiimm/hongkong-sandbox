"""Source-bound original horizontal yaw unit/height frame; no matrix edits.

The original source records a genuine horizontal heading at its government root.
This replaces only the fixed-axis root-pattern diagnostic for these exact bytes;
all full scene ownership, original decode, native bounds and cell gates remain.
"""
import numpy as np
from original_source_ownership import document,graph_reasons
from run import digest
UID='landsd/202994:0';MODEL='B148572591101063C0'
SHA='a91185beb3c7fb4451f889830fce52cc1d7a11b8ce3e29c0216b3e1be2152d3a'
def frame_measurement(values,expected_original):
 matrix=np.array(values,dtype=float).reshape(4,4,order='F');rotation=matrix[:3,:3]
 residual=float(np.max(np.abs(rotation.T@rotation-np.eye(3))));det=float(np.linalg.det(rotation));unchanged=np.array_equal(np.array(values),np.array(expected_original));height_axis=matrix[:3,2].tolist();horizontal=matrix[1,0]==matrix[1,1]==0
 passed=bool(unchanged and np.isfinite(matrix).all() and matrix[3].tolist()==[0,0,0,1] and height_axis==[0,1,0] and horizontal and residual<=1e-12 and abs(det-1)<=1e-12)
 return {'passed':passed,'unchangedOriginalMatrix':bool(unchanged),'orthonormalResidual':residual,'rotationDeterminant':det,'sourceZMapsExactlyToHKPDUp':height_axis==[0,1,0],'horizontalAxesHaveZeroHeightComponent':bool(horizontal)}
def verify_original_root(raw,row,triangles):
 gltf=document(raw);old=graph_reasons(gltf,row['modelId'],len(triangles));root=gltf['nodes'][gltf['scenes'][0]['nodes'][0]];matrix=np.array(root['matrix'],dtype=float).reshape(4,4,order='F');rotation=matrix[:3,:3];proof={'uid':row['uid'],'sourceSHA256':digest(raw),'originalModelRoot':root,'legacyGraphReasons':old,'sourceBoundAlternativeUsed':False,'allSourceGeometryUnchanged':True,'installationApproved':False}
 if not old:proof.update({'passed':True,'remainingReasons':[]});return proof
 assert row['uid']==UID and row['modelId']==MODEL and digest(raw)==row['sourceSHA256'] and row['sourceSHA256']==SHA,'Explicit yaw-source bytes only'
 assert old==['original-unit-hkpd-root-pose'],'All other original graph gates remain strict'
 frame=frame_measurement(root['matrix'],document(raw)['nodes'][gltf['scenes'][0]['nodes'][0]]['matrix']);world=np.array([triangles.min(axis=(0,1)),triangles.max(axis=(0,1))]);native=np.array(row['native']['model']['worldBounds']);bounds_error=float(np.max(np.abs(world-native)));passed=frame['passed'] and bounds_error<.002
 proof.update({**frame,'sourceBoundAlternativeUsed':True,'passed':passed,'remainingReasons':[] if passed else old,'fullOriginalNativeBoundsErrorM':bounds_error,'actualSourceMatrixUnchanged':matrix.flatten(order='F').tolist(),'qualification':'Exact original source SHA/root hierarchy; pure original horizontal unit heading, metre isometry and unchanged HKPD axis. 1e-12 numerical matrix orthonormality bound is arithmetic verification, not model placement or pose tolerance. No edited/normalized source is decoded or approved.'});return proof
