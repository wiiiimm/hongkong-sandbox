"""Measure original ground along the implicated wall, without acceptance changes."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-ronsdale-wall-profile-v1-20261022'
DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 refs=[Path(__file__)]
 def take(batch,p):
  folder=BASE/batch;_,pins=authenticate(folder)
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
  refs.extend([folder/'result.json',p]);return read(p)
 old='government-xl-ronsdale-clearance-attribution-v1-20261022'
 context=take(old,BASE/old/'context.json');assert len(context['faces'])==1;context.update(context['faces'][0]);assert context['faceIndex']==1332
 terrainbatch='government-xl-ronsdale-adjacent-ground-v1-20261022'
 terrain=np.asarray(take(terrainbatch,HERE/'local'/terrainbatch/'original-terrain.json.gz')['triangles'])
 polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
 terrain=terrain[valid];tree=shapely.STRtree(polys[valid])
 helper=module('illumination_wall_profile_sampler',HERE/'xl-final-script-pass.py')
 a,b,c=np.asarray(context['vertices'])[[2,1,0]];assert context['normalisedVertical']==0
 fractions=np.linspace(0,1,201);points=a+(b-a)*fractions[:,None]
 heights=helper.s.context.shared.samples(points[:,[0,2]],terrain,tree)
 assert np.isfinite(heights).all()
 # This face narrows to its bottom vertex at t=0; use its actual triangular
 # upper edge, not a fictitious rectangular wall extending past the mesh.
 upper=a[1]+fractions*(c[1]-a[1])
 buried=np.maximum(0,np.minimum(heights,upper)-points[:,1])
 total=upper-points[:,1]
 length=float(np.linalg.norm((b-a)[[0,2]]))
 area=float(np.trapezoid(total,fractions)*length)
 below=float(np.trapezoid(buried,fractions)*length)
 result=dict(uids=['landsd/233771:0'],sourceSHA256=context['sourceSHA256'],faceIndex=1332,
  samples=201,wallAreaM2=area,estimatedBelowOriginalTerrainAreaM2=below,
  estimatedBelowOriginalTerrainFraction=below/area,
  bottomToGroundRangeM=[float((heights-points[:,1]).min()),float((heights-points[:,1]).max())],
  sourceGeometryChanges=0,installationApproved=False,physicalInterpretationAccepted=False,
  rawFailuresPreserved=True,method='201 evenly spaced samples along original bottom edge; trapezoidal area estimate, not an exact clipping proof')
 save(DOC/'profile.json',dict(summary=result,rows=[dict(fraction=float(t),bottom=float(p[1]),wallTop=float(top),originalGround=float(h))for t,p,top,h in zip(fractions,points,upper,heights)]))
 refs.append(HERE/'xl-final-script-pass.py')
 module('illumination_profile_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-wall-ground-profile-diagnostic',refs,result)
 print(result,flush=True)
if __name__=='__main__':main()
