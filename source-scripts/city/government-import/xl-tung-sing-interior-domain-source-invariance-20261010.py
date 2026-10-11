"""Independent complete finite-domain, boundary-loop and source-region comparison."""
from fractions import Fraction as F
import numpy as np,shapely
from run import ROOT,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from actual_native_parent_transition_v3_20261010 import nondegenerate,rational
BATCH='government-xl-tung-sing-interior-domain-source-invariance-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-v3-20261010';OLD=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-20261010';SELECT=DOC.parent/'government-xl-tung-sing-nested-current-identity-inputs-20261010/selection.json.gz';PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json'
def main():
 assert not DOC.exists();x=read(BASE/'diagnostic.json.gz');t=faces(read(BASE/'candidate-single-native-original-surface.json'));old=faces(read(OLD/'candidate-single-native-original-surface.json'));parent=faces(read(PARENT));child=t[x['retainedExactlyEquivalentFacets']:];bb=x['childBounds'];sides=[]
 for axis,value,other,lo,hi in [(0,bb[0],2,bb[1],bb[3]),(0,bb[2],2,bb[1],bb[3]),(2,bb[1],0,bb[0],bb[2]),(2,bb[3],0,bb[0],bb[2])]:
  intervals=[]
  for triangle in child:
   for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
    if a[axis]==b[axis]==value:intervals.append(sorted([F(float(a[other])),F(float(b[other]))]))
  reach=F(float(lo));gaps=[]
  for low,high in sorted(intervals):
   if low>reach:gaps.append([str(reach),str(low)])
   reach=max(reach,high)
  if reach<F(float(hi)):gaps.append([str(reach),str(F(float(hi)))])
  sides.append({'axis':axis,'fixedCoordinate':value,'completeIntervalCount':len(intervals),'exactUncoveredIntervals':gaps,'coveredCompleteSide':not gaps})
 rows=[];hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [BASE/'diagnostic.json.gz',BASE/'candidate-single-native-original-surface.json',OLD/'candidate-single-native-original-surface.json',SELECT,PARENT,__import__('pathlib').Path(__file__)]}
 for row in read(SELECT)['rows']:
  p=ROOT/row['candidate']['path'];source=decode_original_world_triangles(p.read_bytes());hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());lo,hi=source.min((0,1))[[0,2]],source.max((0,1))[[0,2]]
  def scope(a):return a[np.all(a[:,:,[0,2]].max(1)>=lo,axis=1)&np.all(a[:,:,[0,2]].min(1)<=hi,axis=1)]
  a,b=scope(old),scope(t);rows.append({'uid':row['uid'],'wholeOriginalFaces':len(source),'completeConservativeGroundFacetsOld':len(a),'completeConservativeGroundFacetsNew':len(b),'oldCompleteLocalGroundSHA256':digest(a.astype('<f8').tobytes()),'newCompleteLocalGroundSHA256':digest(b.astype('<f8').tobytes()),'completeLocalFiniteGroundByteIdentical':np.array_equal(a,b),'wholeOriginalWorldBounds':[lo.tolist(),hi.tolist()]})
 projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));original_projection=shapely.union_all(shapely.polygons(parent[:,:,[0,2]]));rectangle=shapely.box(*bb);missing=rectangle.difference(projection);baseline=rectangle.difference(original_projection)
 save(DOC/'diagnostic.json.gz',{'completeBoundarySides':sides,'allFourCompleteSidesExactlyCovered':all(r['coveredCompleteSide'] for r in sides),'sourceRegionCompleteFiniteGroundRows':rows,'allOriginalSourceRegionsByteIdenticalToUpwardPass':all(r['completeLocalFiniteGroundByteIdentical'] for r in rows),'rawChildRectangleMissingProjectionM2':missing.area,'baselineParentRectangleMissingProjectionM2':baseline.area,'rawChildRectangleMissingProjectionWKB':shapely.to_wkb(missing,hex=True),'baselineParentRectangleMissingProjectionWKB':shapely.to_wkb(baseline,hex=True),'currentManifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'inputHashes':hashes,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'All four complete outer child boundary loops covered by exact dyadic interval unions. Conservative AABB source-region selection includes every possibly intersecting finite ground facet; exact byte equality reuses existing1470-face upward result only when true. Floating polygon-domain differences are raw diagnostics, not exact gap acceptance. Full current physical/foreign/retained actor gates remain separate.'});print({'all4SidesExact':all(r['coveredCompleteSide'] for r in sides),'allSourceGroundByteSame':all(r['completeLocalFiniteGroundByteIdentical'] for r in rows),'rawMissingM2':missing.area,'baselineMissingM2':baseline.area},flush=True)
if __name__=='__main__':main()
