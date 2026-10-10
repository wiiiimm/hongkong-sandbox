"""Literal actual-parent facet retention under whole-source-disjoint current forms.

No clipping, interpolation, vertex shifts or height exemptions. Full source
finite projections include triangles, collinear lines and isolated points.
Fresh native overlap/surface/current actor/physical checks remain independent.
"""
import copy,json
from fractions import Fraction as F
import numpy as np,shapely
from run import digest
from native_parent_child_flat_composition_20261010 import faces
def finite_projection(triangles):
 a=np.asarray(triangles,float);assert a.ndim==3 and a.shape[1:]==(3,3) and len(a) and np.isfinite(a).all();out=[]
 for tri in a:
  xy=tri[:,[0,2]];p,q,r=[tuple(F(float(x)) for x in p) for p in xy];area=(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
  if area:out.append(shapely.Polygon(xy))
  elif len(set(map(tuple,xy)))>1:out.append(shapely.LineString(xy))
  else:out.append(shapely.Point(xy[0]))
 return shapely.union_all(out)
def form_polygon(rings):
 q=shapely.Polygon()
 for r in rings:q=q.symmetric_difference(shapely.Polygon(r))
 assert q.is_valid and q.area>0
 return q
def propose(candidate,parent,sources,forms,expected_parent_world_sha,*,budget=100000):
 assert budget==100000;pt=faces(parent);assert np.isfinite(pt).all();assert digest(pt.astype('<f8').tobytes())==expected_parent_world_sha
 assert sources and len(forms)==len({b['uid'] for b in forms});source=shapely.union_all([finite_projection(a) for a in sources.values()]);polys=[finite_projection(np.asarray([t])) for t in pt];tree=shapely.STRtree(polys);regions=[];selected=set()
 for b in forms:
  q=form_polygon(b['rings']);assert not source.intersects(q),'Current form intersects complete original source';ids=sorted(map(int,tree.query(q,predicate='intersects')));assert ids,'No literal parent facets under current form'
  region=shapely.union_all([polys[i] for i in ids]);assert not region.intersects(source),'A whole selected parent facet intersects original source'
  selected.update(ids);regions.append({'uid':b['uid'],'completeCurrentForm':b,'allIntersectingOriginalParentFaceIds':ids,'minimumWholeOriginalSourceDistanceM':float(q.distance(source)),'minimumSelectedWholeParentProjectionDistanceM':float(region.distance(source)),'selectedParentProjectionGeoJSON':json.loads(shapely.to_geojson(region))})
 out=copy.deepcopy(candidate);mesh=out['nativeMesh'];oldp=copy.deepcopy(mesh['position']);oldi=copy.deepcopy(mesh['index']);raw=np.asarray(parent['nativeMesh']['position'],float).reshape(-1,3);idx=np.asarray(parent['nativeMesh']['index'],int).reshape(-1,3);mapping={};records=[];existing={t.astype('<f8').tobytes() for t in faces(candidate)}
 for i in sorted(selected):
  new=[];key=pt[i].astype('<f8').tobytes();already=key in existing
  if not already:
   for j in idx[i]:
    j=int(j)
    if j not in mapping:mapping[j]=len(mesh['position'])//3;mesh['position'].extend(raw[j].tolist())
    new.append(mapping[j])
   mesh['index'].extend(new);existing.add(key)
  records.append({'originalParentFace':i,'originalSourceIndices':idx[i].tolist(),'originalRawPositionTriples':raw[idx[i]].tolist(),'actualRenderedFloat32Triples':pt[i].tolist(),'newCandidateIndices':new,'alreadyLiteralInCandidate':already})
 assert mesh['position'][:len(oldp)]==oldp and mesh['index'][:len(oldi)]==oldi;assert len(mesh['index'])//3<=budget
 final={t.astype('<f8').tobytes() for t in faces(out)};assert all(pt[i].astype('<f8').tobytes() in final for i in selected)
 return out,{'completeOriginalParentFaces':len(pt),'originalParentWorldSHA256':expected_parent_world_sha,'completeSourceWorldSHA256s':{u:digest(np.asarray(a).astype('<f8').tobytes()) for u,a in sources.items()},'completeSourceFaceCounts':{u:len(a) for u,a in sources.items()},'allCurrentDisjointForms':regions,'allRetainedLiteralParentFacetDispositions':records,'existingCandidatePositionAndIndexPrefixesUnchanged':True,'sourceGeometryChanges':0,'terrainClippingOrInterpolation':False,'finalCandidateFacets':len(mesh['index'])//3,'unchangedRuntimeCap':budget,'physicalAccepted':False,'qualification':'A candidate adds only literal original indexed parent facets whose entire finite projection is disjoint from every full unchanged original source. Every actual parent facet intersecting each complete current form is retained. No source omission, region clip, sampler/height tolerance, actor exemption or acceptance credit.'}
