"""Compare unchanged original podiums in the exact flagged projection overlap."""
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-inone-original-pair-overlap-v1-20261022';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)];sources=[]
 for batch,uid in [('government-xl-remaining-forty-podium-identity-v1-20261021','landsd/277890:0'),('government-xl-inone-adjoining-identity-v1-20261022','landsd/277973:0')]:
  folder=BASE/batch;_,pins=authenticate(folder);p=folder/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];row=next(r for r in read(p)['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[str(asset.relative_to(ROOT))];refs.extend([folder/'result.json',p,asset]);t=decode_original_world_triangles(asset.read_bytes());assert len(t)==row['triangles'];b=row['source']['building'];foot=shapely.make_valid(shapely.Polygon(b['rings'][0],b['rings'][1:]));sources.append((row,t,foot))
 polys=shapely.polygons(sources[0][1][:,:,[0,2]]);proj=shapely.union_all(polys[shapely.area(polys)>1e-10]);domain=proj.difference(sources[0][2]).intersection(sources[1][2]);assert domain.area>800
 records=[];selected=[]
 for row,tri,foot in sources:
  indices=[i for i,f in enumerate(tri)if shapely.MultiPoint(f[:,[0,2]]).convex_hull.intersects(domain)];faces=tri[indices];selected.append(faces)
  # Entire intersecting triangles give conservative bounds, including verticals.
  lo,hi=faces.min((0,1)),faces.max((0,1));records.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],wholeSourceFaces=len(tri),intersectingOriginalFaceIds=indices,conservativeIntersectingBounds=[lo.tolist(),hi.tolist()],sourceFootprintWKT=foot.wkt))
 sets=[]
 for faces in selected:sets.append({tuple(sorted(tuple(float(v)for v in point)for point in face))for face in faces})
 same=sets[0]&sets[1];a,b=[r['conservativeIntersectingBounds']for r in records];heightDisjoint=a[1][1]<b[0][1]or b[1][1]<a[0][1]
 DOC.mkdir(parents=True);fig,axes=plt.subplots(1,3,figsize=(18,6))
 for ax,coords,title in zip(axes,[(0,2),(0,1),(2,1)],['Plan X/Z','Elevation X/Y','Elevation Z/Y']):
  for faces,color in zip(selected,['#2563eb','#f97316']):ax.add_collection(PolyCollection(faces[:,:,coords],facecolors=color,edgecolors=color,linewidths=.2,alpha=.4))
  ax.autoscale_view();ax.set_aspect('equal');ax.set_title(title);ax.ticklabel_format(useOffset=False)
 fig.suptitle('Flagged overlap: original277890 blue, adjoining original277973 orange; full intersecting triangles');fig.tight_layout();fig.savefig(DOC/'pair-overlap.png',dpi=160);plt.close(fig)
 summary=dict(uids=[r['uid']for r in records],overlapAreaM2=domain.area,overlapWKT=domain.wkt,sources=records,exactDuplicateTriangleGeometries=len(same),conservativeHeightRangesDisjoint=heightDisjoint,sourceGeometryChanges=0,installationApproved=False,qualification='Exact float-coordinate triangle equality and conservative bounds only. Non-disjoint bounds are not proof of collision; no ownership or identity acceptance.')
 save(DOC/'comparison.json',summary);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('inone_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-overlap-geometry-context',refs,summary);print(dict(overlapArea=domain.area,heightRanges=[r['conservativeIntersectingBounds']for r in records],exactDuplicates=len(same),heightDisjoint=heightDisjoint),flush=True)
if __name__=='__main__':main()
