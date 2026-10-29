"""Complete clipped original-facet height context; diagnostic, not an admission rule."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fuying181489-complete-excess-facets-v1-20261029'
RUNTIME='government-xl-fuying181489-five-member-runtime-v2-20261029'

def clipped_height(face, region):
    """Bound the entire finite facet outside region, including vertical projections."""
    footprint=shapely.MultiPoint(face[:,[0,2]]).convex_hull
    outside=footprint.difference(region)
    if outside.is_empty:return None
    a,b,c=face
    den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if abs(den)<1e-10:
        return dict(minY=float(face[:,1].min()),maxY=float(face[:,1].max()),verticalConservative=True)
    points=shapely.get_coordinates(outside)
    assert len(points)
    x,z=points[:,0],points[:,1]
    u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
    v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
    heights=u*a[1]+v*b[1]+(1-u-v)*c[1]
    return dict(minY=float(heights.min()),maxY=float(heights.max()),verticalConservative=False)

def main():
    out=BASE/BATCH;assert not out.exists()
    _,pins=authenticate(BASE/RUNTIME);path=BASE/RUNTIME/'selection.json.gz'
    assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    row=next(r for r in read(path)['rows']if r['uid']=='landsd/181489:0')
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
    form=row['source']['building'];assert next(b for b in read(tile)['buildings']if b['uid']==row['uid'])==form
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==14692
    polygon=shapely.Polygon(form['rings'][0],form['rings'][1:]);assert polygon.is_valid
    bands=[]
    for distance in [0,2,5,10,20]:
        # Polygonal buffer is INSIDE the circular buffer: its complement is a
        # superset of the true distance band, so reported height is conservative.
        region=polygon if distance==0 else polygon.buffer(distance,quad_segs=32)
        facets=[]
        for i,face in enumerate(tri):
            report=clipped_height(face,region)
            if report is not None:facets.append(dict(face=i,**report))
        bands.append(dict(distanceGreaterThanM=distance,facets=facets,clippedFacetCount=len(facets),minY=min(r['minY']for r in facets),maxY=max(r['maxY']for r in facets)))
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],wholeOriginalFaces=len(tri),everyOriginalFaceExaminedAtEveryBand=True,bands=bands,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Complete finite projected facets clipped against exact current footprint and conservative inscribed distance buffers. Linear plane extrema cover every clipped polygon vertex; vertical projections conservatively retain the entire face height. Diagnostic context only: distances are not acceptance thresholds, no source edits or ownership/structural certification.')
    save(out/'summary.json',result)
    refs=[Path(__file__),BASE/RUNTIME/'result.json',path,asset,tile,HERE/'exact_packed_world_geometry_20261009.py']
    module('fuying_complete_excess_facets_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-clipped-facet-height-context-no-acceptance',refs,result)
    print([{k:v for k,v in b.items()if k!='facets'}for b in bands],flush=True)
if __name__=='__main__':main()
