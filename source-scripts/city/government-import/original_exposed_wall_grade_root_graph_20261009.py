"""Exact original exposed exterior wall grade anchors, preserving old roots.

The old lowest-rim graph is replayed unchanged. A separately named anchor is
an actual positive-dimensional zero-gap interface on the finite upper ground,
on an original grade-crossing exposed wall with an exact clear-roof path.
Visual-only components cannot become roots or graph bridges. Full current
identity/foreign/foundation/runtime/provider role gates remain mandatory.
"""
import hashlib,json
import numpy as np
from original_ordinary_ground_root_graph_20261009 import verify as ordinary_graph
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(triangles,actors,components,contacts,indexed_sources,drawn_ground,contexts,original_wall_contacts,visual_only_components,*,expected_binding,current_binding):
 tri=np.asarray(triangles,float);ground=np.asarray(drawn_ground,float)
 assert expected_binding==current_binding
 assert current_binding['completeCurrentFacetContextsSHA256']==canonical(contexts)
 assert current_binding['exactOriginalContactListSHA256']==canonical(original_wall_contacts)
 assert current_binding['visualOnlyComponentsSHA256']==canonical(visual_only_components)
 assert list(visual_only_components)==sorted(set(visual_only_components)) and all(type(i) is int and 0<=i<len(components) for i in visual_only_components)
 old=ordinary_graph(tri,actors,components,contacts,indexed_sources,ground,expected_binding=expected_binding,current_binding=current_binding)
 wall=cap_paths(tri,contexts,original_wall_contacts,expected_binding=expected_binding,current_binding=current_binding)
 assert wall['allAffectedHavePaths'],'Original affected exterior lacks exact clear roof path'
 excluded=set(visual_only_components);excluded_faces={i for k in excluded for i in components[k]['globalOriginalFaces']}
 assert set(wall['rawExposureFailures'])<=excluded_faces,'Unproved buried wall outside independently verified visual role'
 roots=set(old['ordinaryGroundRootComponents'])-excluded;grade_roots=[];witnesses=[]
 byface={i:k for k,c in enumerate(components) for i in c['globalOriginalFaces']}
 eligible=[i for i in wall['affectedOriginalWallFaces'] if byface[i] not in excluded and contexts[i]['maximumObservedGapM'] is not None and contexts[i]['maximumObservedGapM']>0]
 actual=exact_upper_ground_interfaces(tri,eligible,ground);local_paths={};rejected=[]
 for record in actual:
  k=byface[record['sourceFace']];assert k not in excluded
  path=next(r for r in wall['paths'] if r['sourceFace']==record['sourceFace'])
  if not all(byface[i]==k for i in path['originalPath']):
   # Global BFS may choose a shorter external roof path even when an
   # independent authored roof path exists inside this component. Recompute
   # the full eligible graph locally; never credit the external shortcut.
   if k not in local_paths:
    ids=components[k]['globalOriginalFaces'];mapping={i:j for j,i in enumerate(ids)};local_tri=tri[ids];local_ctx=[{**contexts[i],'sourceFace':j} for j,i in enumerate(ids)];local_contacts=[[mapping[a],mapping[b]] for a,b in original_wall_contacts if a in mapping and b in mapping]
    binding={**current_binding,'completeOriginalWorldTrianglesSHA256':hashlib.sha256(local_tri.tobytes()).hexdigest(),'completeCurrentFacetContextsSHA256':canonical(local_ctx),'exactOriginalContactListSHA256':canonical(local_contacts)}
    proof=cap_paths(local_tri,local_ctx,local_contacts,expected_binding=binding,current_binding=binding)
    local_paths[k]={ids[p['sourceFace']]:{**p,'sourceFace':ids[p['sourceFace']],'originalPath':[ids[i] for i in p['originalPath']],'strictClearNonWallFaces':[ids[i] for i in p['strictClearNonWallFaces']]} for p in proof['paths']}
   path=local_paths[k][record['sourceFace']]
   if not path['hasExactOriginalStrictClearCapRoofPath']:
    rejected.append({**record,'originalComponent':k,'reason':'No independent same-component clear roof path'});continue
  assert path['originalPath'] and all(byface[i]==k for i in path['originalPath']) and path['hasExactOriginalStrictClearCapRoofPath']
  roots.add(k);grade_roots.append(k);witnesses.append({**record,'originalComponent':k,'exactOriginalClearRoofPath':path})
 adjacency={k:set() for k in range(len(components)) if k not in excluded}
 for record in old['exactOriginalContacts']:
  a,b=record['components']
  if a in excluded or b in excluded:continue
  adjacency[a].add(b);adjacency[b].add(a)
 reached=set(roots);todo=list(roots);parents={k:None for k in roots}
 while todo:
  a=todo.pop()
  for b in sorted(adjacency[a]):
   if b not in reached:reached.add(b);parents[b]=a;todo.append(b)
 unresolved=sorted(set(adjacency)-reached)
 return dict(contract='original-exposed-wall-finite-upper-grade-root-graph-v1',ordinaryRootGraphPreserved=old,rawOldRootReasons=old['reasons'],exactOriginalClearRoofPaths=wall,ordinaryGroundRootComponents=sorted(set(old['ordinaryGroundRootComponents'])-excluded),exactExposedWallGradeRootComponents=sorted(set(grade_roots)),allIndependentGroundRoots=sorted(roots),exactCurrentUpperGradeInterfaces=witnesses,rejectedOtherComponentRoofGradeInterfaces=rejected,completeOriginalFaces=len(tri),completeOriginalComponents=len(components),visualOnlyComponents=sorted(excluded),visualOnlyGroundRootCredit=False,visualOnlyGraphBridgeCredit=False,resolvedOriginalComponents=sorted(reached),unresolvedOriginalComponents=unresolved,groundRootedComponentParents=parents,supportInterfaceAccepted=bool(roots) and bool(adjacency) and not unresolved,fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0)
