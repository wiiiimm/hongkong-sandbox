"""Exact failed source-face context for original tower; no acceptance or mesh edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-75351-failed-face-context-v1-20261019';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-pacifica-interface-distances-v1-20261019';CAP=BASE/'government-xl-pacifica-original-assembly-v1-20261019';UID='landsd/75351:0';POD='landsd/283036:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PRIOR,CAP]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'];geo={r['uid']:r for r in rows};tri=lambda r:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
 t=tri(geo[UID]);pod=tri(geo[POD]);check=next(r for r in read(PRIOR/'support-checks.json.gz')['rows'] if r['uid']==UID);assert check['uid']==UID
 failures=check['unresolved'];ids=sorted({f['faceIndex']for r in failures for f in r['originalSourceFaces']})
 for r in failures:
  for f in r['originalSourceFaces']:assert np.max(np.abs(t[f['faceIndex']]-np.asarray(f['vertices'])))<1e-8
 normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);lens=np.linalg.norm(normals,axis=1);records=[]
 for i in ids:
  records.append(dict(faceId=i,vertices=t[i].tolist(),normal=(normals[i]/lens[i]).tolist()if lens[i]else[0,0,0],minimumY=float(t[i,:,1].min()),maximumY=float(t[i,:,1].max()),areaM2=float(lens[i]/2)))
 save(DOC/'faces.json',dict(uid=UID,sourceSHA256=check['sourceSHA256'],supportSHA256=check['supportSHA256'],failedSamples=failures,incidentFaces=records,installationApproved=False))
 fig=plt.figure(figsize=(16,9));pts=np.array([r['position']for r in failures]);lo=t[ids].min((0,1))-2;hi=t[ids].max((0,1))+2
 near=pod[(pod[:,:,0].max(1)>=lo[0])&(pod[:,:,0].min(1)<=hi[0])&(pod[:,:,2].max(1)>=lo[2])&(pod[:,:,2].min(1)<=hi[2])]
 for n,az in enumerate([-55,125],1):
  ax=fig.add_subplot(1,2,n,projection='3d');ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor='gray',alpha=.08));ax.add_collection3d(Poly3DCollection(near[:,:,[0,2,1]],facecolor='green',alpha=.14));ax.add_collection3d(Poly3DCollection(t[ids][:,:,[0,2,1]],facecolor='red',edgecolor='darkred',linewidth=.4,alpha=.7));ax.scatter(pts[:,0],pts[:,2],pts[:,1],c='black',s=8)
  ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect(np.maximum((hi-lo)[[0,2,1]],1));ax.view_init(22,az);ax.set_title('Original tower red failures / original podium green')
 fig.tight_layout();fig.savefig(DOC/'failed-faces.png',dpi=150);plt.close(fig)
 summary=dict(uid=UID,failedSamples=len(failures),incidentFaceCount=len(ids),faces=records,installationApproved=False);save(DOC/'summary.json',summary);print(dict(uid=UID,failedSamples=len(failures),incidentFaceCount=len(ids),faceYRange=[[r['faceId'],r['minimumY'],r['maximumY'],r['normal'][1]]for r in records]),flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-tower-failed-face-context',list(dict.fromkeys(refs)),dict(uids=[UID,POD],failedSamples=len(failures),incidentFaceCount=len(ids),installationApproved=False))
if __name__=='__main__':main()
