"""Exact finite missing-region coverage by unchanged upward platform surfaces."""
import json,numpy as np,shapely
from pathlib import Path
from fractions import Fraction
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_slab_projection_coverage_20261010 import slab_coverage
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-commercial-exact-missing-platform-coverage-20261010';BASE=DOC.parent

def area(ring):return abs(sum(Fraction(float(a[0]))*Fraction(float(b[1]))-Fraction(float(a[1]))*Fraction(float(b[0])) for a,b in zip(ring,ring[1:]+ring[:1])))/2

def main():
 assert not DOC.exists();contextpath=BASE/'government-xl-tung-sing-commercial-missing-original-platform-surfaces-20261010/diagnostic.json.gz';selectionpath=BASE/'government-xl-tung-sing-interior-current-identity-inputs-v2-20261010/selection.json.gz';r=next(r for r in read(selectionpath)['rows'] if r['uid']=='landsd/126434:0');p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];a=decode_original_world_triangles(raw);parts=read(contextpath)['allMissingRegionOriginalSurfaceDispositions'];n=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);ids=np.flatnonzero(n[:,1]>0).tolist();ground=a[ids];rows=[]
 for part in parts:
  shape=shapely.from_geojson(json.dumps(part['completeMissingCurrentTargetGeoJSON']));triangles=shapely.get_parts(shapely.constrained_delaunay_triangles(shape));rings=[list(shape.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in shape.interiors];wanted=area(rings[0])-sum(area(ring) for ring in rings[1:]);faces=[];actual=Fraction(0)
  for index,t in enumerate(triangles):
   q=np.asarray(t.exterior.coords)[:3];actual+=area(q.tolist());face=np.column_stack([q[:,0],np.zeros(3),q[:,1]]);proof=slab_coverage(face,ground);faces.append({'index':index,'literalMissingRegionProofTriangle':face.tolist(),'exactFiniteCoverage':proof})
  assert actual==wanted,'Target polygon finite-facet accounting differs'
  rows.append({'missingRegionIndex':part['missingPolygonIndex'],'completeLiteralMissingPolygonGeoJSON':part['completeMissingCurrentTargetGeoJSON'],'exactPolygonAreaFraction':str(wanted),'exactTriangleAreaFraction':str(actual),'completeFiniteTargetTriangles':faces,'allFiniteFacetsAndClosedEdgesCovered':all(f['exactFiniteCoverage']['exactProjectionCovered'] for f in faces)})
 out={'uid':'landsd/254604:0','platformUid':r['uid'],'platformOriginalSourceSHA256':r['sourceSHA256'],'completeOriginalWorldSHA256':digest(a.astype('<f8').tobytes()),'wholePlatformOriginalFaces':len(a),'wholeOriginalUpwardPlatformFaceIds':ids,'allMissingRegionProofs':rows,'allMissingTargetFacetsAndClosedEdgesCovered':all(row['allFiniteFacetsAndClosedEdgesCovered'] for row in rows),'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [Path(__file__),contextpath,selectionpath,p,HERE/'exact_original_slab_projection_coverage_20261010.py']},'identityAccepted':False,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Every recorded missing polygon has an exact rational finite triangulation area census, and every finite proof facet plusallclosededges is checked against complete original upward platform surfaces. These proof triangles do not alter any government source geometry; no source support or95% threshold waiver.'}
 save(DOC/'diagnostic.json.gz',out);print(json.dumps({'allCovered':out['allMissingTargetFacetsAndClosedEdgesCovered'],'rows':[{'id':r['missingRegionIndex'],'facets':len(r['completeFiniteTargetTriangles']),'covered':r['allFiniteFacetsAndClosedEdgesCovered']} for r in rows]}),flush=True)
if __name__=='__main__':main()
