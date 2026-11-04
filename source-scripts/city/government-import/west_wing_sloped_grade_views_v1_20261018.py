"""Diagnostic views of exact original grade faces and candidate terrain; no approval."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-sloped-grade-views-v1-20261018';DOC=BASE/BATCH
GRADE=BASE/'government-xl-west-wing-grade-face-context-v1-20261018';CAP=BASE/'government-xl-west-wing-group-four-world-v1-20261018';RUNTIME=HERE/'local/government-xl-west-wing-runtime-checks-v3-20261018/runtime-geometry.json.gz'
def main():
 assert not DOC.exists();r=read(GRADE/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),GRADE/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'worlds.json.gz')['original'];runtime={r['uid']:r for r in read(RUNTIME)['rows']};records=[];DOC.mkdir()
 for uid in ['landsd/26195:0','landsd/315069:0']:
  d=read(GRADE/(uid.split('/')[1]+'-original.json.gz'));ids=[i for i in d['continuousNegativeFaceIds']if abs(d['faces'][i]['normalYRatio'])>=.005];assert ids=={'landsd/26195:0':[42722,42723,42809],'landsd/315069:0':[492,901,904,905]}[uid];tri=np.asarray(worlds[uid]);selected=tri[ids];ground=np.asarray(runtime[uid]['drawnGroundGeometry']).reshape(-1,3,3);lo=selected.min((0,1));hi=selected.max((0,1));bounds=[lo[0]-6,lo[2]-6,hi[0]+6,hi[2]+6];ceiling=max(hi[1]+3,9)
  def local(t):return t[(t[:,:,0].max(1)>=bounds[0])&(t[:,:,0].min(1)<=bounds[2])&(t[:,:,2].max(1)>=bounds[1])&(t[:,:,2].min(1)<=bounds[3])&(t[:,:,1].max(1)<=ceiling)]
  g=local(ground);context=local(tri)
  fig=plt.figure(figsize=(16,7))
  for n,az in enumerate([-55,125]):
   ax=fig.add_subplot(1,2,n+1,projection='3d')
   for t,color,alpha in [(g,'#96ac85',.35),(context,'#aebac7',.28),(selected,'#c63333',1)]:ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor=color,edgecolor='none',alpha=alpha))
   ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[1],bounds[3]);ax.set_zlim(min(lo[1]-1,g[:,:,1].min()),ceiling);ax.set_box_aspect((bounds[2]-bounds[0],bounds[3]-bounds[1],ceiling-min(lo[1]-1,g[:,:,1].min())));ax.view_init(elev=25,azim=az);ax.set_xlabel('world x');ax.set_ylabel('world z');ax.set_zlabel('height')
  fig.suptitle(uid+' — exact seven sloped grade faces in red; actual terrain green');fig.tight_layout();fig.savefig(DOC/(uid.split('/')[1].replace(':','-')+'.png'),dpi=140);plt.close(fig)
  ratios=[d['faces'][i]['normalYRatio']for i in ids];records.append(dict(uid=uid,originalFaceIds=ids,exactSourceTriangles=selected.tolist(),sourceSHA256=d['sourceSHA256'],maximumAbsNormalYRatio=max(abs(v)for v in ratios),bounds=bounds,diagnosticCeiling=ceiling))
 save(DOC/'views.json',dict(rows=records,publication=False,qualification='Whole original triangles only. Diagnostic context omits faces above the stated ceiling; no geometry edits or source-role approval.'))
 refs.extend(ROOT/p for p in pins);out=module('west_grade_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-exact-seven-sloped-grade-context-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in records],publication=False,fullAcceptance=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
