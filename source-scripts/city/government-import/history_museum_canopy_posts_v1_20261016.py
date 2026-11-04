"""Stage existing illustrative-post foundations against exact drawn terrain."""
from pathlib import Path
import subprocess
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from rendered_patch_sampler import RenderedPatchSampler
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-canopy-posts-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-history-museum-roof-context-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 b=read(PRIOR/'context.json.gz')['roofForm'];DOC.mkdir();save(DOC/'input.json',dict(building=b));tool=HERE/'history_museum_canopy_posts_v1_20261016.mjs'
 def call(mode):
  with(DOC/(mode+'.log')).open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/',mode],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
 call('describe');parts=read(DOC/'description.json')['parts'];posts=shapely.union_all([Polygon(p['rings'][0],p['rings'][1:])for p in parts if p['kind']=='post'])
 geometry=HERE/'local/government-xl-history-museum-preserved-neighbours-v1-20261016/runtime-geometry.json.gz';g=read(geometry)['rows'][0];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;coverage=shapely.union_all(polys[valid]);assert posts.difference(coverage).area<1e-8
 heights=[];faceids=[]
 for i in np.flatnonzero(valid&shapely.intersects(polys,posts)):
  intersection=polys[i].intersection(posts)
  if intersection.area<=1e-10:continue
  coords=shapely.get_coordinates(intersection);a,c,d=ground[i];n=np.cross(c-a,d-a);assert abs(n[1])>1e-12;ys=a[1]-(n[0]*(coords[:,0]-a[0])+n[2]*(coords[:,1]-a[2]))/n[1];heights.extend(ys.tolist());faceids.append(int(i))
 assert heights;foundation=float(min(heights));assert foundation<b['base']-.02
 save(DOC/'proposal.json',dict(uid=b['uid'],foundationBase=foundation,originalBase=b['base'],roofElevationUnchanged=True,source='minimum of exact drawn terrain faces clipped to current illustrative post footprints',terrainFaces=faceids,groundRange=[min(heights),max(heights)],noNewGovernmentGeometry=True,publication=False));call('propose')
 proof=read(DOC/'render-proof.json');actual=read(DOC/'geometry.json.gz');helper=module('museum_post_surface',HERE/'resolve-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');grid=helper.terrain.fine.DemSampler(parent,rendered=True);lo=ground.reshape(-1,3).min(0);hi=ground.reshape(-1,3).max(0);synthetic=dict(w=2,h=2,meta=dict(georef=dict(bE=lo[0]+834500,bN=816500-lo[2],aE=hi[0]-lo[0],aN=-(hi[2]-lo[2]))),nativeMesh=dict(position=ground.reshape(-1).tolist(),index=list(range(len(ground)*3))));surface=RenderedPatchSampler(synthetic,grid,grid)
 low=np.asarray(actual['after']['position']).reshape(-1,3);low=low[np.abs(low[:,1]-foundation)<.002];gaps=[float(v[1]-surface.height(v[0],v[2]))for v in low];summary=dict(uid=b['uid'],proposal=read(DOC/'proposal.json'),renderProof=proof,postBottomSamples=len(gaps),minimumPostGap=min(gaps),maximumPostGap=max(gaps),existingHalfMetreBurialAndOneMetreGapSatisfied=min(gaps)>=-.5 and max(gaps)<=1,fullAcceptance=False,liveChanges=False)
 save(DOC/'summary.json',summary)
 for p,h in proof['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs += [tool,geometry,PRIOR/'context.json.gz',HERE/'rendered_patch_sampler.py',HERE/'resolve-pass.py'];out=module('museum_posts_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-existing-illustrative-canopy-post-foundation-proposal-v1',list(dict.fromkeys(refs)),dict(uids=[b['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],foundationBase=foundation,postGap=[min(gaps),max(gaps)],passed=summary['existingHalfMetreBurialAndOneMetreGapSatisfied']),flush=True)
if __name__=='__main__':main()
