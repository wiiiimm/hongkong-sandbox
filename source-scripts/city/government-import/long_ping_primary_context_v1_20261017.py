"""Current unchanged Long Ping source context for official-plan review; no publication."""
import numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from require_remaining_xl import require_remaining
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-long-ping-primary-evidence-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/107382:0';SHA='f462a97834afe39e5f66932c562eaa1daa4fa9f6958d5879663d1878b4251add'
def main():
 assert not DOC.exists();require_remaining(BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json',UID,SHA)
 prior=BASE/'government-xl-spatial-surface-roles-20261009/107382-0.json.gz';r=read(prior);source=ROOT/r['originalPath'];assert digest(source.read_bytes())==SHA;t=decode_original_world_triangles(source.read_bytes())
 final=module('long_ping_current_forms',HERE/'xl-final-script-pass.py');lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);target=next(x for x in forms if x[0]['uid']==UID);foreign=next(x for x in forms if x[0]['uid']=='way/227090446:0')
 projected=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));intersection=projected.intersection(foreign[1]);save(DOC/'current-context.json',dict(uid=UID,sourceSHA256=SHA,triangles=len(t),target=target[0],foreign=foreign[0],targetCoverage=projected.intersection(target[1]).area/target[1].area,foreignOverlapM2=intersection.area,identityAccepted=False,installationApproved=False))
 fig,ax=plt.subplots(figsize=(14,5),dpi=180)
 for poly,color,label in [(projected,'#498bb5','Original source projection'),(target[1],'#45a36a','Recorded station footprint'),(foreign[1],'#d65050','Unnamed OSM structure')]:
  parts=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
  for i,p in enumerate(parts):
   coords=np.asarray(p.exterior.coords);coords[:,0]+=834500;coords[:,1]=816500-coords[:,1];ax.add_patch(Patch(coords,facecolor=color,edgecolor=color,alpha=.35,label=label if i==0 else None))
 ax.autoscale_view();ax.set_aspect('equal');ax.set_xlabel('HK1980 easting (m)');ax.set_ylabel('HK1980 northing (m)');ax.ticklabel_format(style='plain',useOffset=False);ax.legend();ax.set_title('Complete unchanged Long Ping source and current footprints');fig.tight_layout();fig.savefig(DOC/'source-footprint-plan.png');plt.close(fig)
 refs=[Path(__file__),prior,source,ROOT/'3d-viewer/city/data/manifest.json']+[ROOT/'3d-viewer'/tile for _,_,tile in forms]+list(LOCAL.glob('*.pdf'))+[LOCAL/'provenance.json']
 save(DOC/'primary-source-provenance.json',read(LOCAL/'provenance.json'))
 result=module('long_ping_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-current-original-official-plan-context-v1',list(set(refs)),dict(uids=[UID],sourceSHA256=SHA,foreignUid=foreign[0]['uid'],foreignOverlapM2=intersection.area,fullAcceptance=False,nextStep='Compare exact source extent and north-side OSM structure with official MTR plans; protection-area inclusion alone is not building ownership or physical acceptance.'))
 print(dict(jobId=result['jobId'],triangles=len(t),foreignOverlapM2=intersection.area),flush=True)
if __name__=='__main__':main()
