"""Exact current actor binding for reuse of frozen complete actual bounds.
Never grants geometry/identity/physics credit. Caller must bind source bytes,
complete current catalogue/viewer census and identical full loader closure.
"""
from copy import deepcopy

def validate_unchanged_actor(old_input,old_actual,current_entry,current_form,current_source_ref,actual_source_sha):
 uid=old_input['uid'];assert old_actual['uid']==uid==current_entry['uid']==current_form['uid']
 assert old_input['rawCurrentEntry']==current_entry and old_input['currentBuilding']==current_form
 assert old_input['source']==current_source_ref and actual_source_sha==current_source_ref['sha256']==current_entry['sha256']==old_actual['sourceSHA256']
 proof=old_input['completeOriginalPOSITIONProof'];assert proof==old_actual['completeOriginalPOSITIONProof']
 assert proof['allOriginalPositionVerticesAccounted'] is True
 assert old_actual['sourceFacesOmitted']==0 and old_actual['wholeUnusedPositionVerticesIncluded'] is True
 assert old_actual['completeFaces']==current_entry['triangles']==proof['completeOriginalTriangles']
 assert old_actual['completePositionVertices']==proof['completeOriginalPositionVertices']
 meshes=old_actual['actualRenderMeshes'];assert meshes and all(m['wholePositionVerticesIncludingUnused'] is True for m in meshes)
 assert sum(m['completePositionVertices'] for m in meshes)==old_actual['completePositionVertices']
 assert sum(m['completeIndexedFaces'] for m in meshes)==old_actual['completeFaces']
 for m in meshes:
  assert len(m['matrixWorldFloat64'])==len(m['modelMatrixUniformFloat32'])==16
  for key in ['completeLiteralBounds','completeLeftAssociatedF32Bounds','completeBalancedF32Bounds']:
   assert len(m[key])==2 and all(len(v)==3 for v in m[key])
   assert all(m[key][0][k]<=m[key][1][k] for k in range(3))
 return deepcopy(old_actual)

def exact_post_block6_census(old_uids,current_uids):
 assert len(old_uids)==len(set(old_uids))==6637
 assert len(current_uids)==len(set(current_uids))==6638
 assert set(current_uids)-set(old_uids)=={'landsd/255438:0'} and not set(old_uids)-set(current_uids)
 return True
