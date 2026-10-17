"""Whole-parent-face replacement-domain feasibility; no terrain modification."""
import collections,numpy as np,shapely
from run import ROOT,read,save,digest
from native_parent_child_flat_composition_20261010 import faces,bounds
BATCH='government-xl-tung-sing-whole-original-parent-domain-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json'
CHILD=ROOT/'source-scripts/city/government-import/local/government-xl-tung-sing-two-nested-original-physical-v3-20261010/government-native-53800-0.json'
INPUT=DOC.parent/'government-xl-tung-sing-nested-current-identity-inputs-20261010/selection.json.gz'
def main():
 assert not DOC.exists();tri=faces(read(PARENT));bb=bounds(read(CHILD));lo,hi=tri[:,:,[0,2]].min(1),tri[:,:,[0,2]].max(1);n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);selected=(lo[:,0]>=bb[0])&(hi[:,0]<=bb[2])&(lo[:,1]>=bb[1])&(hi[:,1]<=bb[3])&(n[:,1]!=0);ids=np.flatnonzero(selected);domain=shapely.union_all(shapely.polygons(tri[ids][:,:,[0,2]]));edges=collections.defaultdict(list)
 for i in ids:
  p=[tuple(v) for v in tri[i]]
  for a,b in zip(p,p[1:]+p[:1]):edges[tuple(sorted((a,b)))].append((int(i),a,b))
 boundary=[e[0] for e in edges.values() if len(e)==1];nonmanifold=[e for e in edges.values() if len(e)>2 or len(e)==2 and e[0][1:]!=tuple(reversed(e[1][1:]))];outgoing=collections.Counter(a for _,a,b in boundary);incoming=collections.Counter(b for _,a,b in boundary);degree_bad=[p for p in set(outgoing)|set(incoming) if outgoing[p]!=1 or incoming[p]!=1]
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 source=[]
 for row in read(INPUT)['rows']:
  original=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());poly=shapely.union_all(shapely.polygons(original[:,:,[0,2]]));source.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'rawGeosSourceOutsideWholeFacetDomainM2':float(shapely.difference(poly,domain).area),'domainCoversFullSourceProjection':bool(shapely.covers(domain,poly))})
 save(DOC/'diagnostic.json.gz',{'originalParentFaces':len(tri),'wholeOriginalParentReplacementFaceIds':ids.tolist(),'retainedLiteralOriginalParentFaceIds':np.flatnonzero(~selected).tolist(),'wholeOriginalBoundaryEdges':boundary,'nonmanifoldFullEdges':nonmanifold,'boundaryDegreeFailures':degree_bad,'domainPolygonWKB':shapely.to_wkb(domain,hex=True),'sourceWholeProjectionDiagnostics':source,'childRectangle':bb,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [PARENT,CHILD,INPUT]},'physicalAccepted':False,'terrainGeometryChanges':0,'qualification':'Read-only finite whole-facet boundary-domain census. Every parent retaining/vertical/degenerate face remains literal. No rectangle-clipped parent output, grid-height assumption, new vertices or seam acceptance. GEOS source coverage is feasibility only and cannot grant exact finite-domain coverage.'});print({'wholeRemovedFaces':len(ids),'literalRetainedFaces':len(tri)-len(ids),'boundaryEdges':len(boundary),'nonmanifold':len(nonmanifold),'degreeFailures':len(degree_bad),'source':source},flush=True)
if __name__=='__main__':main()
