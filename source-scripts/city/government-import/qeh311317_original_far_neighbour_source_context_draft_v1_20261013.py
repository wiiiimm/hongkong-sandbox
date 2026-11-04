"""Unexecuted QEH source-view draft; no current identity or physical approval."""
import json
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,shape
from run import ROOT,read,save,digest
B=ROOT/'docs/astra-city/government-import'
P=B/'government-xl-qeh311317-original-source-context-proposal-v1-20261013'
D=B/'government-xl-qeh311317-original-far-neighbour-source-context-v1-20261013'
INPUT=B/'government-xl-spatial-surface-roles-20261009/311317-0.json.gz'
SOURCE='6feeea5687b060e9b39d17be3d6336c0668e92c23a15955602ec7256be4268a1'
WORLD='03c1065e676a44c80805e6693f4f998b4cdc7476d13b3aeb654c70af39ead006'
UID='landsd/311317:0';MODEL='B361581883001063C0';FACES=11584
FOREIGN='landsd/161194:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check_pins(refs,root=ROOT):
 for e in refs:
  p=(root/e['path']).resolve();assert p.is_relative_to(root.resolve()),'Path escape'
  assert digest(p.read_bytes())==e['sha256'],'Changed exact input'
def selections(t,target,region):
 t=np.asarray(t,dtype='<f8');assert t.ndim==3 and t.shape[1:]==(3,3) and np.isfinite(t).all()
 assert target.is_valid and target.area>0 and region.is_valid and region.area>0
 dist=shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3)
 far=np.flatnonzero(dist.max(1)>10).tolist()
 polys=shapely.polygons(t[:,:,[0,2]])
 # Exact same historical display selector: positive projection area, intersects.
 # Boundary touches count; no claim of positive finite 3D contact.
 neighbour=np.flatnonzero((shapely.area(polys)>1e-10)&shapely.intersects(polys,region)).tolist()
 return far,neighbour
def validate_partition(top,n):
 bodies=top['sharedEdgeConnectedComponents'];zeros=top['exactNonrenderingOriginalFaces']
 ids=[i for body in bodies for i in body]+zeros
 assert sorted(ids)==list(range(n)) and len(ids)==len(set(ids))
 return {i:body for body,faces in enumerate(bodies) for i in faces},zeros
def main():
 # ROOT must review before actual source decode/export. No DB or reservations.
 assert not D.exists();pins=read(P/'input-contract.json')['refs'];check_pins(pins)
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 from exact_original_shared_edge_component_census_v2_20261011 import census
 d=read(INPUT);assert d['uid']==UID and d['modelId']==MODEL and d['sourceSHA256']==SOURCE and d['worldTrianglesSHA256']==WORLD
 source=ROOT/d['originalPath'];assert ref(source)['sha256']==SOURCE
 t=decode_original_world_triangles(source.read_bytes());assert t.shape==(FACES,3,3) and digest(t.astype('<f8').tobytes())==WORLD
 v=d['variants']['direct-shared-OSM'];target=shapely.union_all([Polygon(f['rings'][0],f['rings'][1:]) for f in v['groupForms']]);assert len(v['overlappingForms'])==1 and v['overlappingForms'][0]['uid']==FOREIGN
 region=shape(v['overlappingForms'][0]['geometry']);far,near=selections(t,target,region);assert len(far)==52 and len(near)==8
 top=census(t,list(range(FACES)));labels,zeros=validate_partition(top,FACES)
 groups=[]
 for body,ids in enumerate(top['sharedEdgeConnectedComponents']):
  selected=sorted(set(ids)&set(far+near))
  if selected:groups.append(dict(originalBody=body,completeBodyFaceIDs=ids,farFaceIDs=sorted(set(ids)&set(far)),neighbourRegionFaceIDs=sorted(set(ids)&set(near))))
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 D.mkdir();lo,hi=t.min((0,1)),t.max((0,1));colors=['#d47a20' if i in far else '#c72e64' if i in near else '#7291ab' for i in range(FACES)]
 def plan():
  fig,ax=plt.subplots(figsize=(12,10));ax.add_collection(PolyCollection(t[:,:,[0,2]],facecolors=colors,edgecolors='none',alpha=.65))
  for f in v['groupForms']:
   for ring in f['rings']:
    r=np.asarray(ring);ax.plot(r[:,0],r[:,1],'k--',linewidth=1)
  for poly in ([region] if region.geom_type=='Polygon' else region.geoms):
   x,z=poly.exterior.xy;ax.plot(x,z,color='#c72e64',linewidth=1)
  ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[2]-2,hi[2]+2);ax.set_aspect('equal');ax.set_xlabel('Original world X (m)');ax.set_ylabel('Original world Z (m)');ax.set_title('All11584 original QEH source faces; orange52 beyond historical10m\nPink8 historical neighbour-region facets; no identity/contact credit');fig.savefig(D/'whole-plan-1800x1500.png',dpi=150);plt.close(fig)
 def view(name,azim,focus):
  ids=sorted(set(far+near)) if focus else list(range(FACES));pts=t[ids];a,b=pts.min((0,1)),pts.max((0,1));span=b-a;span=np.maximum(span,1)
  fig=plt.figure(figsize=(12,10));ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(pts[:,:,[0,2,1]],facecolors=[colors[i] for i in ids],edgecolors='none',alpha=.8));ax.set_xlim(a[0]-1,b[0]+1);ax.set_ylim(a[2]-1,b[2]+1);ax.set_zlim(a[1]-1,b[1]+1);ax.set_box_aspect(span[[0,2,1]]);ax.view_init(elev=25,azim=azim);ax.set_xlabel('Original X');ax.set_ylabel('Original Z');ax.set_zlabel('Original Y');ax.set_title(('Explicit complete52far +8neighbour saved-selector facet subset' if focus else 'Complete unchanged11584-face original source')+'\nSource display only; transparency/occlusion, no GPU or ownership proof');fig.savefig(D/name,dpi=150);plt.close(fig)
 plan();view('whole-source-3d-minus60-1800x1500.png',-60,False);view('whole-source-3d120-1800x1500.png',120,False);view('explicit-far-neighbour-facet-subset-1800x1500.png',120,True)
 check_pins(pins);images=[]
 for p in sorted(D.glob('*.png')):
  with Image.open(p) as im:assert im.size==(1800,1500);images.append(dict(**ref(p),width=im.width,height=im.height))
 save(D/'context.json',dict(uid=UID,modelId=MODEL,source=ref(source),completeWorldSHA256=WORLD,completeSourceFaces=FACES,completeTopology=top,selectedBodyContext=groups,farFaceIDs=far,neighbourRegionFaceIDs=near,sourceZerosPreserved= zeros,fullExportFaceIDs=list(range(FACES)),focusedExportFaceIDs=sorted(set(far+near)),savedHistoricalStatsUnchanged=v['stats'],inputRefs=pins,exportedImages=images,identityAccepted=False,physicalAccepted=False,installationApproved=False,currentAcceptance=False,sourceGeometryChanges=0,noActualNeighbour3DGeometry=True,qualification='Historical source/footprint context only. Complete source submitted to whole views; focused view names explicit subset. No fitted pose, legal ownership, intentional interface or 3D collision assertion. No current runtime/terrain or source-role qualification.'))
 print(json.dumps(dict(images=images,farFaces=len(far),neighbourFaces=len(near),realBodies=len(top['sharedEdgeConnectedComponents']),zeros=len(zeros),noAcceptance=True)))
if __name__=='__main__':main()
