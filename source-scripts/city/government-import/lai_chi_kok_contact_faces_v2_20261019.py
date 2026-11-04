"""Bind remaining contact failures to exact original source faces; no acceptance."""
from pathlib import Path
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-contact-faces-v2-20261019';DOC=BASE/BATCH;CAP=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v3-20261019';UID='landsd/281463:0'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),CAP/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 path=HERE/'local'/CAP.name/'runtime-geometry.json.gz';g=read(path)['rows'][0];assert g['uid']==UID;t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 final=module('ocean_contact_samples',HERE/'xl-final-script-pass.py');polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;terrain=ground[valid];points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain,shapely.STRtree(polys[valid])).reshape(-1,4);gaps=points[:,:,1]-heights;assert np.isfinite(gaps).all();buried=np.flatnonzero((gaps<-.5).all(1));intersects=np.flatnonzero(gaps.min(1)<-.5);bottom=float(t[:,:,1].min());rim=np.flatnonzero((t[:,:,1]<=bottom+.35).any(1));cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);norm=np.linalg.norm(cross,axis=1)
 records=[]
 for i in sorted(set(intersects)|set(rim)):
  records.append(dict(faceId=int(i),vertices=t[i].tolist(),gaps=gaps[i].tolist(),normalYRatio=float(cross[i,1]/norm[i])if norm[i]else 0,fullyBuried=bool(i in buried),globalLowRim=bool(i in rim)))
 save(DOC/'faces.json',dict(uid=UID,sourceSHA256=g['sourceSHA256'],completeFaceCount=len(t),fullyBuriedFaceIds=buried.tolist(),intersectingFaceIds=intersects.tolist(),lowRimFaceIds=rim.tolist(),globalMinimumY=bottom,faces=records,installationApproved=False))
 fig=plt.figure(figsize=(16,8))
 for n,(ids,title)in enumerate([(intersects,'Faces intersecting terrain by over 0.5 m'),(rim,'Global low-rim source faces')],1):
  ax=fig.add_subplot(1,2,n,projection='3d');a=t[ids];lo=a.min((0,1))-3;hi=a.max((0,1))+3;near=t[(t[:,:,0].max(1)>=lo[0])&(t[:,:,0].min(1)<=hi[0])&(t[:,:,2].max(1)>=lo[2])&(t[:,:,2].min(1)<=hi[2])];gg=ground[(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2])]
  ax.add_collection3d(Poly3DCollection(near[:,:,[0,2,1]],facecolor='grey',edgecolor='none',alpha=.12));ax.add_collection3d(Poly3DCollection(gg[:,:,[0,2,1]],facecolor='green',edgecolor='none',alpha=.3));ax.add_collection3d(Poly3DCollection(a[:,:,[0,2,1]],facecolor='red',edgecolor='darkred',linewidth=.3,alpha=.95));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect(np.maximum((hi-lo)[[0,2,1]],1));ax.view_init(25,-55);ax.set_title(title)
 fig.tight_layout();fig.savefig(DOC/'contact-faces.png',dpi=150);plt.close(fig)
 summary=dict(uid=UID,buried=buried.tolist(),intersectingFaces=len(intersects),lowRimFaces=len(rim),globalMinimumY=bottom,installationApproved=False);print(summary,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([path,HERE/'xl-final-script-pass.py']);module('ocean_faces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-original-contact-face-context',list(dict.fromkeys(refs)),dict(uids=[UID],summary=summary,installationApproved=False))
if __name__=='__main__':main()
