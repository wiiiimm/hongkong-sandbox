"""Orthographic original-junction evidence; no geometry or acceptance changes."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-facet32-subdivision-v2-20261017';CONTEXT=BASE/'government-xl-aqua272788-conflict-source-context-v1-20261017';BATCH='government-xl-aqua272788-junction-role-views-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rt=HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz';tri={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in read(rt)['rows']};source=tri['landsd/272788:0'];host=tri['landsd/193086:0'];context=read(CONTEXT/'context.json.gz');assert str((CONTEXT/'context.json.gz').relative_to(ROOT))in pins
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 fig,axes=plt.subplots(2,3,figsize=(15,10));rows=[]
 for row,axrow in zip(context['rows'],axes):
  i=row['face'];t=source[i];centre=t.mean(0);lo=t.min(0)-.2;hi=t.max(0)+.2;ids=np.flatnonzero((host.max(1)>=lo).all(1)&(host.min(1)<=hi).all(1));hs=host[ids];cross=np.cross(hs[:,1]-hs[:,0],hs[:,2]-hs[:,0]);norm=np.linalg.norm(cross,axis=1);normals=np.divide(cross,norm[:,None],out=np.zeros_like(cross),where=norm[:,None]>0)
  rows.append(dict(sourceFace=i,sourceTriangle=t.tolist(),sourceNormal=row['normal'],nearbyHostFaces=[dict(face=int(j),vertices=host[j].tolist(),normal=n.tolist())for j,n in zip(ids,normals)],sourceConnectedNeighbours=[dict(face=j,vertices=source[j].tolist())for j in row['threeRingFaces']]))
  for ax,dims,labels in zip(axrow,[(0,2),(0,1),(2,1)],[('East','South'),('East','Height'),('South','Height')]):
   ax.add_collection(PolyCollection((hs-centre)[:,:,dims],facecolors='#329fb4',edgecolors='#267b8b',alpha=.22,linewidths=.5))
   ax.add_collection(PolyCollection((source[row['threeRingFaces']]-centre)[:,:,dims],facecolors='none',edgecolors='#aa7a00',linewidths=1))
   ax.add_collection(PolyCollection((t-centre)[None,:,dims],facecolors='#ef3340',edgecolors='#b00020',alpha=.8,linewidths=2))
   ax.set_xlim(lo[dims[0]]-centre[dims[0]],hi[dims[0]]-centre[dims[0]]);ax.set_ylim(lo[dims[1]]-centre[dims[1]],hi[dims[1]]-centre[dims[1]]);ax.set_aspect('equal');ax.set_xlabel(labels[0]+' offset m');ax.set_ylabel(labels[1]+' offset m');ax.set_title('Original face '+str(i));ax.grid(alpha=.2)
 fig.suptitle('Original tower/podium junction: failed face red; connected tower edges gold; nearby podium facets blue\nOrthographic geometry evidence only; no placement approval');fig.tight_layout();DOC.mkdir();fig.savefig(DOC/'junction-orthographic.png',dpi=150);plt.close(fig)
 save(DOC/'role-context.json.gz',dict(rows=rows,sourceGeometryChanges=0,roleAssigned=False,sourceFaces=len(source),hostFaces=len(host)))
 out=module('aqua_role_views_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-original-junction-orthographic-context-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]],dict(uids=['landsd/272788:0'],sourceFaces=[32,1836],fullAcceptance=False,nextStep='Review the complete original-junction geometry against exact whole-facet association and raw physical failures.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
