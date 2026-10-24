"""Plot all original source faces and exact excessive components; no geometry edits."""
import json,importlib.util
import numpy as np,shapely
from shapely.geometry import shape,Polygon
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009';LOCAL=HERE/'local/government-xl-spatial-surface-roles-20261009'
s=importlib.util.spec_from_file_location('lead_original_context',HERE/'xl-second-pass.py');dec=importlib.util.module_from_spec(s);s.loader.exec_module(dec)
for uid in ['173512-0','263423-0']:
 r=read(DOC/(uid+'.json.gz'));v=r['variants']['direct-shared-OSM'];forms=v['groupForms'];foot=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:]) for b in forms]);model=HERE/'local/government-xl-spatial-surface-roles-20261009/unpacked'/r['modelId']/'model.gltf';tri=dec.context.triangles(model);assert digest(tri.astype('<f8').tobytes())==r['worldTrianglesSHA256'];far=np.load(LOCAL/'surface-faces'/(uid+'-direct-shared-OSM.npz'))['farTriangles'];projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));fig,axs=plt.subplots(1,3,figsize=(16,6))
 for ax in axs[:2]:
  for p in ([projection] if projection.geom_type=='Polygon' else projection.geoms):x,z=p.exterior.xy;ax.fill(x,z,color='#2a9d8f',alpha=.5)
  for f in forms:
   for ring in f['rings']:x,z=np.array(ring).T;ax.plot(x,z,color='black',linewidth=.7)
  ax.scatter(far[:,:,0].reshape(-1),far[:,:,2].reshape(-1),c=far[:,:,1].reshape(-1),s=4,cmap='plasma');ax.set_aspect('equal');ax.invert_yaxis();ax.set_xlabel('Original viewer x(m)');ax.set_ylabel('Original viewer z(m)')
 lo,hi=far.min(axis=(0,1)),far.max(axis=(0,1));axs[1].set_xlim(lo[0]-12,hi[0]+12);axs[1].set_ylim(hi[2]+12,lo[2]-12);axs[0].set_title(r['name']+' / complete original');axs[1].set_title('Exact >10m faces; colour=HKPD height')
 ax=axs[2];points=far.reshape(-1,3);ax.scatter(points[:,0]-.4*points[:,2],points[:,1]+.3*points[:,2],c=points[:,1],s=5,cmap='plasma');ax.set_aspect('equal');ax.set_title('Excess original faces, oblique');ax.set_xlabel('x−0.4z');ax.set_ylabel('height+0.3z');fig.tight_layout();fig.savefig(DOC/uid/'original-excess-surface-roles.png',dpi=200);plt.close(fig)
 print(uid,r['modelId'],v['stats'],flush=True)
