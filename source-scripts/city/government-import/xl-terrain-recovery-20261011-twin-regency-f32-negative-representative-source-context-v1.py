"""Images-only complete original Float32-contact-negative bodies in authored surroundings.
No mounting/function/root/role qualification is inferred from these views.
AABB-cropped surroundings are display-only; every highlighted body is complete.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-twin-regency-f32-negative-representative-source-context-v1';DOC=BASE/BATCH
CROSS=BASE/'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'
GRAPH=BASE/'xl-terrain-recovery-20261011-twin-regency-complete-internal-original-contact-graph-v1'
IDS=[89, 112, 202, 268, 403, 677, 844, 845, 1031, 90, 105, 110]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();cross=read(CROSS/'diagnostic.json.gz');graph=read(GRAPH/'diagnostic.json.gz');refs=[ref(BASE/'xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v2/failed-context-writer.json'),ref(HERE/'xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v2.py'),ref(Path(__file__)),ref(CROSS/'diagnostic.json.gz'),ref(CROSS/'result.json'),ref(GRAPH/'diagnostic.json.gz'),ref(GRAPH/'result.json'),ref(HERE/'exact_packed_world_geometry_20261009.py')];worlds=[]
 for r in cross['completeSourceInputs']:
  p=ROOT/r['asset']['path'];assert ref(p)==r['asset'];refs.append(ref(p));worlds.append(decode_original_world_triangles(p.read_bytes()))
 world=np.concatenate(worlds);assert len(world)==13519 and digest(world.tobytes())==cross['completeOriginalWorldSHA256'];pathdoc=BASE/'xl-terrain-recovery-20261011-twin-regency-bounded-four-stream-current-podium-paths-v1';pathdata=read(pathdoc/'diagnostic.json.gz');refs.extend([ref(pathdoc/'diagnostic.json.gz'),ref(pathdoc/'result.json')]);assert set(IDS).issubset(pathdata['rows'][2]['unprovedGeometricCandidates'])
 DOC.mkdir(parents=True);rows=[];images=[]
 for azimuth,label in [(-58,'south-east'),(118,'north-west')]:
  fig=plt.figure(figsize=(28,21),dpi=100)
  for k,i in enumerate(IDS):
   row=cross['bodies'][i];ids=row['globalOriginalFaces'];body=world[ids];lo=body.min((0,1));hi=body.max((0,1));pad=np.maximum((hi-lo)*.3,.65);scope_lo=lo-pad;scope_hi=hi+pad
   hostids=np.flatnonzero(np.all(world.max(1)>=scope_lo,axis=1)&np.all(world.min(1)<=scope_hi,axis=1));hostids=[int(f) for f in hostids if f not in ids]
   origin=(lo+hi)/2;plot=(body-origin)[:,:,[0,2,1]];near=(world[hostids]-origin)[:,:,[0,2,1]];ax=fig.add_subplot(3,4,k+1,projection='3d')
   ax.add_collection3d(Poly3DCollection(near,facecolors=(.35,.48,.60,.3),edgecolors=(.25,.32,.4,.2),linewidths=.15))
   ax.add_collection3d(Poly3DCollection(plot,facecolors=(.95,.3,.08,1),edgecolors=(.2,.12,.04,.8),linewidths=.6))
   l=(scope_lo-origin)[[0,2,1]];h=(scope_hi-origin)[[0,2,1]];ax.set_xlim(l[0],h[0]);ax.set_ylim(l[1],h[1]);ax.set_zlim(l[2],h[2]);ax.set_box_aspect(h-l);ax.view_init(elev=21,azim=azimuth)
   ax.set_xlabel('relative X');ax.set_ylabel('relative Z');ax.set_zlabel('world Y relative');ax.set_title('Original body '+str(i)+' | '+str(len(ids))+' full facets\nY '+format(lo[1],'.3f')+'..'+format(hi[1],'.3f')+' m',fontsize=12)
   if label=='south-east':rows.append(dict(originalBody=i,uid=row['actorUID'],completeGlobalOriginalFaces=ids,wholeOriginalBodyBounds=[lo.tolist(),hi.tolist()],displayCroppedSurroundingGlobalFaces=hostids,displayOriginOnly=origin.tolist(),noEligibilityOrHostQualification=True))
  fig.suptitle('Twin Regency: complete original Float32-contact-negative bodies and authored surrounding source geometry\nOrange complete bodies; transparent blue nearby original facets (display-only crop, no host qualification)',fontsize=20)
  fig.subplots_adjust(left=.015,right=.98,bottom=.035,top=.93,wspace=.04,hspace=.12);fig.text(.02,.015,'Source arrays and georeferenced pose unchanged. No inferred function, mounting, visual role, ground/root/bridge or current acceptance.',fontsize=14)
  p=DOC/('complete-original-f32-contact-negative-representatives-'+label+'-2800x2100.png');fig.savefig(p,dpi=100);plt.close(fig);images.append(ref(p))
 assert all(ref(ROOT/r['path'])==r for r in refs);save(DOC/'context.json',dict(uids=cross['uids'],completeSourceFacets=13519,representativeBodyRows=rows,all50F32NegativeOriginalBodyIDs=pathdata['rows'][2]['unprovedGeometricCandidates'],sourceWorldSHA256=cross['completeOriginalWorldSHA256'],images=images,sourceGeometryChanges=0,noFunctionRoleRootOrBridgeCredit=True,evidenceRefs=refs))
 print(images,flush=True)
if __name__=='__main__':main()
