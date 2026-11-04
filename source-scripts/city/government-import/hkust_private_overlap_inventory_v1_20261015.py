"""Enumerate every nonzero projected overlap in the private HKUST terrain proposal."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-private-native-seam-v1-20261015';DOC=B/'government-xl-hkust-private-overlap-inventory-v1-20261015'
def main():
 assert not DOC.exists();r=read(OLD/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};p=OLD/'unapproved-native-patch.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];patch=read(p);v=np.array(patch['nativeMesh']['position'],dtype=np.float32).astype(float).reshape(-1,3);idx=np.array(patch['nativeMesh']['index']).reshape(-1,3);tri=v[idx];polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ids=np.flatnonzero(valid);poly=polys[valid];tree=shapely.STRtree(poly);left,right=tree.query(poly,predicate='intersects');rows=[];groups={};constructed=12810;fill=r['fill'];assert len(tri)==constructed+fill['sourceEdgeTriangles']+fill['parentTriangles']
 def role(i):return 'constructed-native' if i<constructed else 'source-edge-fill' if i<constructed+fill['sourceEdgeTriangles'] else 'parent-fill'
 for a,b in zip(left,right):
  if a>=b:continue
  overlap=poly[a].intersection(poly[b])
  if overlap.area<=0:continue
  ia,ib=int(ids[a]),int(ids[b]);key='/'.join(sorted([role(ia),role(ib)]));groups[key]=groups.get(key,0)+1;rows.append({'faceA':ia,'faceB':ib,'roleA':role(ia),'roleB':role(ib),'areaM2':float(overlap.area),'bounds':list(overlap.bounds),'faceVerticesA':tri[ia].tolist(),'faceVerticesB':tri[ib].tolist(),'overlapGeoJSON':shapely.to_geojson(overlap)})
 DOC.mkdir();summary={'uids':r['uids'],'completeCandidateFaces':len(tri),'allPositiveAreaPairs':len(rows),'groups':groups,'pairsAboveExisting1e8ReportingThreshold':sum(x['areaM2']>1e-8 for x in rows),'maximumPairAreaM2':max(x['areaM2'] for x in rows),'introducedFillPairAreaSumM2':sum(x['areaM2'] for x in rows if 'fill' in x['roleA'] or 'fill' in x['roleB']),'qualification':'All positive overlaps retained, including numerical slivers; pair area sums may double-count. Constructed-native includes boundary transition, so it does not imply original-source inheritance. No MAX or overlap acceptance.'};save(DOC/'overlaps.json.gz',{'summary':summary,'rows':rows});save(DOC/'summary.json',summary)
 module('hkust_overlap_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-complete-private-overlap-inventory-v1',[Path(__file__),OLD/'result.json',p],{**summary,'nextStep':'Attribute all material overlap pairs to exact original source facets or transition/fill generation; preserve runtime highest-surface obligations before any approval.'});print(summary,flush=True)
if __name__=='__main__':main()
