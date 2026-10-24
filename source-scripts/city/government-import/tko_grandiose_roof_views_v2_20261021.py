"""Inspect exact flagged tower facets and original overhead podium layers; no geometry edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-roof-views-v2-20261021';DOC=BASE/BATCH
FOUND=BASE/'government-xl-tko-grandiose-joint-foundations-v3-20261021';ATTR=BASE/'government-xl-tko-grandiose-burial-attribution-v1-20261021';LAYERS=BASE/'government-xl-tko-flagged-layers-v1-20261021'
def clipped_faces(tri,lower,upper):
 out=[]
 for face in tri:
  polygon=[v.copy()for v in face]
  for axis in range(3):
   for boundary,sign in [(lower[axis],1),(upper[axis],-1)]:
    if not polygon:break
    result=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
     va=sign*(a[axis]-boundary);vb=sign*(b[axis]-boundary)
     if va>=0:result.append(a)
     if(va>=0)!=(vb>=0):result.append(a+(b-a)*(va/(va-vb)))
    polygon=result
  for j in range(1,len(polygon)-1):out.append([polygon[0],polygon[j],polygon[j+1]])
 return np.asarray(out).reshape(-1,3,3)
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [FOUND,ATTR]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][key];used[key]=pins[d][key];refs.append(p);return read(p)
 uids=['landsd/29868:0','landsd/29875:0','landsd/29885:0','landsd/31946:0','landsd/32020:0','landsd/32147:0','landsd/34291:0']
 for uid in uids:
  key=uid.split('/')[1]
  inp=take(FOUND,FOUND/('original/'+key+'/input.json.gz'));r=inp['rows'][0];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];podium=np.asarray(inp['podium']).reshape(-1,3,3)
  attr=take(ATTR,ATTR/'original'/(key+'.json.gz'));assert digest(t.tobytes())==attr['sourceWorldSHA256'] and digest(podium.tobytes())==attr['podiumWorldSHA256']
  ids=sorted(f['faceIndex']for f in attr['results']['combined']['buriedFaces']);above=list(range(len(podium)));flagged=t[ids];lo=flagged.min((0,1))-[3,2,3];hi=flagged.max((0,1))+[3,10,3];origin=(lo+hi)/2;origin[1]=0
  for name,showPodium in [('with-podium',True)]:
   fig=plt.figure(figsize=(16,12),dpi=150)
   for i,az in enumerate([-55,35,125,215]):
    ax=fig.add_subplot(2,2,i+1,projection='3d')
    for tri,color,alpha in [(t,'#3576a5',.06)]+([(podium[above],'#d8a04e',.15)]if showPodium else[]):
     faces=(clipped_faces(tri,lo,hi)-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(faces,facecolor=color,edgecolor=color,alpha=alpha,linewidth=.1))
    ax.add_collection3d(Poly3DCollection((flagged-origin)[:,:,[0,2,1]],facecolor='#d62728',edgecolor='#670000',alpha=1,linewidth=.7))
    ax.set_xlim(lo[0]-origin[0],hi[0]-origin[0]);ax.set_ylim(lo[2]-origin[2],hi[2]-origin[2]);ax.set_zlim(lo[1],hi[1]);ax.view_init(elev=22,azim=az);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]);ax.set_xlabel('Local x');ax.set_ylabel('Local z');ax.set_zlabel('HKPD height')
   fig.suptitle(f'{uid}: {len(ids)} flagged original faces (red), tower (blue), original podium (amber)\nLocal diagnostic; visual-only clipping/transparency, no source changes');DOC.mkdir(exist_ok=True);fig.tight_layout();fig.savefig(DOC/(key+'-'+name+'.png'));plt.close(fig)
  save(DOC/(key+'-context.json'),dict(uids=[uid,'landsd/265489:0'],flaggedFaceIds=ids,overheadPodiumFaceIds=above,flaggedVertices=flagged.tolist(),bounds=[lo.tolist(),hi.tolist()],sourceGeometryChanges=0,installationApproved=False))
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('tko_burial_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-buried-face-and-overhead-layer-views',list(dict.fromkeys(refs)),dict(uids=uids,installationApproved=False))
if __name__=='__main__':main()
