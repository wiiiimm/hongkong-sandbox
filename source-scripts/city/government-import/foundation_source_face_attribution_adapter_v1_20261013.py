"""Isolated sampled-foundation attribution. No admission or source-body inference."""
from pathlib import Path
from types import FunctionType
import hashlib,marshal
import numpy as np

def code_sha(function):
 return hashlib.sha256(marshal.dumps(function.__code__)).hexdigest()

def canonical_pin(function):
 path=Path(function.__code__.co_filename).resolve()
 delegate=function.__globals__['connected_components']
 return dict(scriptPath=str(path),scriptSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),foundationCodeSHA256=code_sha(function),connectedComponentsCodeSHA256=code_sha(delegate))

def _indices(values,total):
 result=list(values)
 assert all(isinstance(i,(int,np.integer))and not isinstance(i,(bool,np.bool_))and 0<=i<total for i in result)
 assert len(set(result))==len(result)
 return [int(i)for i in result]

def attribute(function,triangles,terrain,target_polygon,complete_saved_bodies,*,expected_canonical_pin,nonrendering_source_face_indices=()):
 """Return canonical metrics verbatim and independently ordered exact face IDs.

 Caller must bind the complete saved body inventory/source arithmetic/terrain
 and current inputs. This function does not certify the body's true-edge census.
 The canonical failure groups use rounded shared vertices in a buried subset;
 they are NOT complete true-edge source bodies or architectural role labels.
 """
 assert canonical_pin(function)==expected_canonical_pin
 assert isinstance(triangles,np.ndarray)and triangles.ndim==3 and triangles.shape[1:]==(3,3)and len(triangles)>0
 assert isinstance(terrain,np.ndarray)and terrain.ndim==3 and terrain.shape[1:]==(3,3)
 assert np.isfinite(triangles).all()and np.isfinite(terrain).all()
 total=len(triangles);nonrendering=_indices(nonrendering_source_face_indices,total)
 bodies=[];body_ids=set();all_ids=[]
 for index,row in enumerate(complete_saved_bodies):
  body_id=row.get('bodyId',index);assert isinstance(body_id,(int,np.integer))and not isinstance(body_id,(bool,np.bool_))and int(body_id)not in body_ids
  ids=_indices(row['sourceFaceIndices'],total);assert ids
  body_ids.add(int(body_id));all_ids+=ids;bodies.append(dict(bodyId=int(body_id),sourceFaceIndices=ids))
 assert len(all_ids)==total and sorted(all_ids)==list(range(total)) # No duplicate, omitted or renumbered source slots.
 original_globals=function.__globals__;globals_before=dict(original_globals)
 delegate=original_globals['connected_components'];journal=[]
 source_bytes=triangles.tobytes();terrain_bytes=terrain.tobytes();target_bytes=target_polygon.wkb
 def recording_components(actual_triangles,selected):
  assert actual_triangles is triangles and len(selected)==total and np.asarray(selected).dtype==np.dtype(bool)
  groups=delegate(actual_triangles,selected)
  group_ids=[_indices(g,total)for g in groups];flat=[i for group in group_ids for i in group]
  selected_ids=np.flatnonzero(selected).tolist();assert len(flat)==len(set(flat))and sorted(flat)==selected_ids
  journal.append(dict(selectedSourceFaceIndices=selected_ids,groupsInDelegateOrder=group_ids))
  return groups # Exact objects/order returned by the canonical delegate.
 cloned_globals=dict(original_globals);cloned_globals['connected_components']=recording_components
 clone=FunctionType(function.__code__,cloned_globals,function.__name__,function.__defaults__,function.__closure__)
 if function.__kwdefaults__ is not None:clone.__kwdefaults__=dict(function.__kwdefaults__)
 assert clone.__code__ is function.__code__ and clone.__globals__ is not original_globals
 metrics=clone(triangles,terrain,target_polygon)
 assert len(journal)==1
 assert original_globals.keys()==globals_before.keys()and all(original_globals[k]is v for k,v in globals_before.items())
 assert canonical_pin(function)==expected_canonical_pin and triangles.tobytes()==source_bytes and terrain.tobytes()==terrain_bytes and target_polygon.wkb==target_bytes
 selected=journal[0]['selectedSourceFaceIndices'];buried=np.zeros(total,dtype=bool);buried[selected]=True
 # Identical canonical cross/norm/upward arithmetic, solely for source-ID tags.
 cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
 area=np.linalg.norm(cross,axis=1)/2
 upward=cross[:,1]>0.25*np.linalg.norm(cross,axis=1)
 upward_ids=np.flatnonzero(buried&upward).tolist()
 assert len(selected)==metrics['fullyBuriedTriangles']and len(upward_ids)==metrics['fullyBuriedUpwardTriangles']
 assert float(area[buried].sum())==metrics['fullyBuriedAreaM2']and float(area[buried&upward].sum())==metrics['fullyBuriedUpwardAreaM2']
 nonrendering_set=set(nonrendering);upward_set=set(upward_ids);selected_set=set(selected);failure_groups=[]
 for ordinal,ids in enumerate(journal[0]['groupsInDelegateOrder']):
  group_set=set(ids);intersections=[]
  for body in bodies:
   overlap=[i for i in body['sourceFaceIndices']if i in group_set]
   intersections.append(dict(bodyId=body['bodyId'],completeSavedBodyFaceCount=len(body['sourceFaceIndices']),failureGroupSourceFaceIndices=overlap,buriedUpwardSourceFaceIndices=[i for i in overlap if i in upward_set]))
  assert sum(len(r['failureGroupSourceFaceIndices'])for r in intersections)==len(ids)
  failure_groups.append(dict(delegateOrdinal=ordinal,sourceFaceIndices=ids,buriedUpwardSourceFaceIndices=[i for i in ids if i in upward_set],nonrenderingSourceFaceIndices=[i for i in ids if i in nonrendering_set],intersectionsWithEveryCompleteSavedBody=intersections))
 assert len(failure_groups)==len(metrics['components'])
 return dict(canonicalFoundationMetrics=metrics,canonicalPin=expected_canonical_pin,completeSourceFaceCount=total,completeSourceFaceIndices=list(range(total)),fullyBuriedSourceFaceIndices=selected,fullyBuriedUpwardSourceFaceIndices=upward_ids,notFullyBuriedSourceFaceIndices=[i for i in range(total)if i not in selected_set],nonrenderingSourceFaceIndices=nonrendering,completeSavedBodyInventoryVerbatim=bodies,failureGroupsInCanonicalDelegateOrder=failure_groups,sortedCanonicalAggregatesNotHeuristicallyMatchedToJournal=True,canonicalFunctionCodeClonedExactly=True,canonicalGlobalsAndInputBytesUnchanged=True,savedTrueEdgeBodyInventoryRecomputed=False,classificationIsExistingVertexPlusCentroidSamplesOnly=True,nonrenderingFacetsReceiveNoSupportCredit=True,bodyRoleRootPhysicalOrInstallationAccepted=False)
