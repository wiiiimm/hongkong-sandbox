"""Locate actual >1m combined support gaps on unchanged complete source arrays."""
from pathlib import Path
import numpy as np, shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import'; DOC=B/'government-xl-hkust-unresolved-rim-source-context-v1-20261015'
OLD=B/'government-xl-hkust-private-compound-foundation-v1-20261015'; PACKET=B/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
def main():
 assert not DOC.exists()
 receipt=read(OLD/'result.json');pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']};p=OLD/'compound.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 samples=read(p)['towerSamples']; failures=[s for s in samples if s['combinedGapM']>1]
 rp=PACKET/'two-original-scope-interface-output-v1/result.json'; report=read(rp); arrays={}; paths=[Path(__file__),p,OLD/'result.json',rp]
 for r in report['arrayRefs']:
  ap=ROOT/r['path'];assert digest(ap.read_bytes())==r['sha256'];a=read(ap);arrays[a['sourceTuple']['uid']]=np.array(a['completeOrderedOriginalTriangles']);paths.append(ap)
 tower=arrays['landsd/309822:0']; podium=arrays['landsd/232155:0']; rows=[]
 # Exact source-face point-to-plane and barycentric-domain distance, in 3D.
 for sample in failures:
  q=np.array(sample['position']);a=tower[:,0];u=tower[:,1]-a;v=tower[:,2]-a;n=np.cross(u,v);nn=np.einsum('ij,ij->i',n,n);w=q-a
  distance=np.full(len(tower),np.inf);ok=nn>1e-20;distance[ok]=abs(np.einsum('ij,ij->i',w,n)[ok])/np.sqrt(nn[ok])
  uu=np.einsum('ij,ij->i',u,u);uv=np.einsum('ij,ij->i',u,v);vv=np.einsum('ij,ij->i',v,v);wu=np.einsum('ij,ij->i',w,u);wv=np.einsum('ij,ij->i',w,v);den=uu*vv-uv*uv
  s=np.full(len(tower),np.nan);t=s.copy();valid=den>1e-20;s[valid]=(vv*wu-uv*wv)[valid]/den[valid];t[valid]=(uu*wv-uv*wu)[valid]/den[valid]
  ids=np.flatnonzero((distance<=1e-6)&(s>=-1e-6)&(t>=-1e-6)&(s+t<=1+1e-6))
  rows.append({'sample':sample,'sourceFaceIndices':ids.tolist(),'faceVertices':tower[ids].tolist(),'normalYRatio':(n[ids,1]/np.sqrt(nn[ids])).tolist(),'qualification':'Numerical source-face incidence only, not a support-role acceptance.'})
 DOC.mkdir();save(DOC/'source-incidence.json.gz',{'rows':rows,'allOriginalSamples':samples,'incidenceToleranceM':1e-6,'barycentricTolerance':1e-6})
 fig,axes=plt.subplots(1,2,figsize=(16,9))
 for ax,coords in zip(axes,[(0,2),(2,1)]):
  for tris,color in [(podium,'#549b8b'),(tower,'#8b98af')]:ax.add_collection(PolyCollection(tris[:,:,coords],facecolors=color,edgecolors='none',alpha=.35))
  points=np.array([s['position'] for s in samples]);ax.scatter(points[:,coords[0]],points[:,coords[1]],s=5,c='#555555')
  pts=np.array([s['position'] for s in failures]);sc=ax.scatter(pts[:,coords[0]],pts[:,coords[1]],s=22,c=[s['combinedGapM'] for s in failures],cmap='autumn',vmin=1,vmax=2.5)
  ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('World '+str(coords[0])+' (m)');ax.set_ylabel('World '+str(coords[1])+' (m)')
 fig.colorbar(sc,ax=axes,label='Gap above combined private terrain/original podium (m)',shrink=.5);fig.suptitle('HKUST unchanged originals: actual >1m support-gap samples\nGrey: tower; green: original podium. Diagnostic only.');fig.savefig(DOC/'unresolved-source-context.png',dpi=130);plt.close(fig)
 out={'samplesOverExistingOneMetreThreshold':len(failures),'samplesWithLocatedOriginalFaces':sum(bool(r['sourceFaceIndices']) for r in rows),'uniqueIncidentFaces':len({i for r in rows for i in r['sourceFaceIndices']}),'maximumCombinedGapM':max(s['combinedGapM'] for s in samples),'sourceBuildingGeometryChanged':False,'liveTerrainGeometryChanged':False,'installationApproved':False}
 save(DOC/'summary.json',out)
 module('hkust_rim_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-unresolved-rim-original-face-context-v1',paths,{**out,'nextStep':'Interpret located original lower facade surfaces against primary source support context. Preserve genuine placement and strict contact guards; this does not accept source identity or support.'});print(out,flush=True)
if __name__=='__main__':main()
