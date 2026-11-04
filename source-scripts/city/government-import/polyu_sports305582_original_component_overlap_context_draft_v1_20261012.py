"""DRAFT unchanged original context; historical planar regions are not contacts."""
from pathlib import Path
import json,numpy as np,shapely
from shapely.geometry import shape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import'
PROPOSAL=BASE/'government-xl-polyu-sports305582-original-context-proposal-v1-20261012'
DOC=BASE/'government-xl-polyu-sports305582-original-component-overlap-context-v1-20261012'
INPUT=BASE/'government-xl-spatial-surface-roles-20261009/305582-0.json.gz'
SOURCE='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15'
WORLD='b219a54a5163c5b33c2dd9dca7c042275b2c6861fa32743321a0a8940b268459'
UID='landsd/305582:0';FOREIGN=['landsd/305793:0','landsd/72322:0','landsd/258852:0','landsd/305600:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 pins=read(PROPOSAL/'draft-code-input-pins.json')['refs']
 for e in pins:assert ref(ROOT/e['path'])==e
 d=read(INPUT);assert d['uid']==UID and d['modelId']=='B365931850802063C0'and d['sourceSHA256']==SOURCE and d['worldTrianglesSHA256']==WORLD and not d['identityAccepted']
 source=ROOT/d['originalPath'];assert ref(source)['sha256']==SOURCE
 t=decode_original_world_triangles(source.read_bytes());assert t.shape==(10536,3,3)and np.isfinite(t).all()and digest(t.astype('<f8').tobytes())==WORLD
 variant=d['variants']['direct-shared-OSM'];regions={r['uid']:r for r in variant['overlappingForms']};assert sorted(regions)==sorted(FOREIGN)
 topology=census(t,list(range(len(t))));bodies=topology['sharedEdgeConnectedComponents'];labels={face:i for i,ids in enumerate(bodies)for face in ids};assert sorted(list(labels)+topology['exactNonrenderingOriginalFaces'])==list(range(10536))
 projected=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(projected)>1e-10;rows=[];masks={}
 for uid in FOREIGN:
  region=shape(regions[uid]['geometry']);assert region.is_valid and region.area>0
  mask=np.zeros(len(t),bool);ids=np.flatnonzero(valid & shapely.intersects(projected,region))
  for i in ids:
   # Descriptive finite projected area only; same old 1e-10 display filter.
   if projected[i].intersection(region).area>1e-10:mask[i]=True
  masks[uid]=mask;faceids=np.flatnonzero(mask).tolist();groups=[]
  for body,bodyids in enumerate(bodies):
   selected=sorted(set(bodyids)&set(faceids))
   if selected:
    pts=t[selected].reshape(-1,3);groups.append(dict(originalBody=body,completeBodyFaceCount=len(bodyids),selectedOriginalFaceIds=selected,selectedWorldBounds=[pts.min(0).tolist(),pts.max(0).tolist()]))
  rows.append(dict(uid=uid,originalSavedPlanarOverlap=regions[uid],completeProjectedRegionSelectedOriginalFaces=faceids,componentAttribution=groups,projectionOnlyNoSurfaceContactOrSolidProof=True))
 lo,hi=t.min((0,1)),t.max((0,1));DOC.mkdir()
 def plan(name,highlight=None,title=''):
  fig,ax=plt.subplots(figsize=(12,10));colors=['#7291ab'if highlight is None or not highlight[i]else'#e27719'for i in range(len(t))]
  ax.add_collection(PolyCollection(t[:,:,[0,2]],facecolors=colors,edgecolors='none',alpha=.7))
  for f in variant['groupForms']:
   for ring in f['rings']:
    v=np.asarray(ring);ax.plot(v[:,0],v[:,1],'k--',linewidth=.7)
  for uid in FOREIGN:
   g=shape(regions[uid]['geometry'])
   for poly in ([g]if g.geom_type=='Polygon'else g.geoms):
    x,z=poly.exterior.xy;ax.plot(x,z,linewidth=1,label=uid)
  ax.set_xlim(lo[0]-3,hi[0]+3);ax.set_ylim(lo[2]-3,hi[2]+3);ax.set_aspect('equal');ax.set_xlabel('Original world X (m)');ax.set_ylabel('Original world Z (m)');ax.set_title(title);ax.legend(loc='upper left',fontsize=7);fig.savefig(DOC/name,dpi=150);plt.close(fig)
 def view(name,azim,mask=None,title=''):
  fig=plt.figure(figsize=(12,10));ax=fig.add_subplot(111,projection='3d');colors=['#7291ab'if mask is None or not mask[i]else'#e27719'for i in range(len(t))];ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=colors,edgecolors='none',alpha=.65));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=25,azim=azim);ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('World Y');ax.set_title(title);fig.savefig(DOC/name,dpi=150);plt.close(fig)
 plan('complete-original-and-saved-regions-1800x1500.png',title='All10536 original faces + historical target/three BlockX forms\nFour saved projected foreign overlap regions; no ownership/contact credit')
 anymask=np.logical_or.reduce(list(masks.values()));view('complete-original-3d-minus60-1800x1500.png',-60,anymask,'All10536 original faces; orange saved-region incidence\nDisplay only; occlusion is not absence')
 view('complete-original-3d120-1800x1500.png',120,anymask,'All10536 original faces; original pose/heights preserved')
 for uid in FOREIGN:plan('foreign-region-'+uid.split('/')[1].replace(':','-')+'-1800x1500.png',masks[uid],'All10536 originals; orange projected incidence with '+uid+'\nHistorical planar evidence only; no 3D foreign actor drawn')
 for e in pins:assert ref(ROOT/e['path'])==e
 images=[]
 for p in sorted(DOC.glob('*.png')):
  with Image.open(p)as im:assert im.size==(1800,1500);images.append(dict(**ref(p),width=im.width,height=im.height))
 save(DOC/'context.json',dict(uid=UID,sourceOnly=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,unwarpedOriginalPose=True,completeOriginalFaces=10536,completeOriginalWorldSHA256=WORLD,source=ref(source),originalTopology=topology,completeSavedFourForeignRegionAttribution=rows,originalHistoricalProjectionStatsRetained=variant['stats'],historicalSourceTileHashes=d['sourceTileHashes'],actualCurrentFormsOrPhysicsProved=False,drawnOriginalFacesPerExport=10536,no3DForeignContactProved=True,qualification='Full original/source topology and saved projected-region incidence context only. Zero faces retained as topology obligations, no point bridges. All source triangles submitted to every export; transparency/occlusion/duplicate projected layers are display context, not GPU visibility. No fitting/scale/pose, current identity/foreign/support/root or intended joint inference.',inputRefs=pins,exportedImages=images))
 print(json.dumps(dict(outputs=images,originalBodies=len(bodies),originalZeroFaces=len(topology['exactNonrenderingOriginalFaces']),identityAccepted=False)),flush=True)
if __name__=='__main__':main()
