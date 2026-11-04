"""Visual display crops of unmodified original triangles, NEVER acceptance mesh.

Original full sources/face inventories stay bound; clipping here only draws an
explicit viewport crop in PNG. No function, architecture or physical credit.
"""
from pathlib import Path
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-tower-backing-display-crops-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1';LONG=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-long-original-backing-facets-v1';CLOSED=BASE/'xl-terrain-recovery-20261011-mount-verdant-34-complete-backing-patches-context-v1';SOURCE=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def crop_display_triangle(triangle,bounds):
 # Visual viewport clipping only; never supplied to a physical/source checker.
 polygon=list(np.asarray(triangle,float))
 for dimension in range(3):
  for sign,edge in [(1,bounds[0,dimension]),(-1,bounds[1,dimension])]:
   result=[]
   for a,b in zip(polygon,polygon[1:]+polygon[:1]):
    sa,sb=sign*(a[dimension]-edge),sign*(b[dimension]-edge)
    if sa>=0:result.append(a)
    if (sa>=0)!=(sb>=0):result.append(a+(b-a)*(sa/(sa-sb)))
   polygon=result
   if not polygon:return []
 return [np.asarray([polygon[0],polygon[i],polygon[i+1]])for i in range(1,len(polygon)-1)]
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PRIOR,LONG,CLOSED]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert ref(folder/'diagnostic.json.gz')in receipt['evidenceRefs'];refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 d=read(PRIOR/'diagnostic.json.gz');selected=read(SOURCE/'selection.json.gz');pieces=[]
 for uid in ['landsd/261717:0','landsd/75782:0']:
  row=next(r for r in selected['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(ref(asset));pieces.append(decode_original_world_triangles(asset.read_bytes()))
 tri=np.concatenate(pieces);assert digest(tri.tobytes())==d['complete15579PairWorldSHA256'];refs.extend([ref(SOURCE/'selection.json.gz'),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')]);hosts=d['completeHostGlobalFaceIDs'];long=read(LONG/'diagnostic.json.gz')['all30OriginalLongStripFaces'];closed=read(CLOSED/'diagnostic.json.gz')['completeAll34OriginalClosed28FaceBodies'];scenes=[]
 for r in long:
  ids=r['all10CompleteOriginalFaces'];part=tri[ids];low=part.min((0,1));high=part.max((0,1));back=r['completePositiveFacetPatch']['completeBackingOriginalFaceIDs']
  for where in ['lower','upper']:
   bounds=np.asarray([low-.6,high+.6]);bounds[0,1]=low[1]-.6 if where=='lower'else high[1]-3.4;bounds[1,1]=low[1]+3.4 if where=='lower'else high[1]+.6;scenes.append(dict(body=r['originalBody'],faces=ids,backFaces=back,bounds=bounds.tolist(),description=where+' 4m display crop; full98.69m source retained'))
 r=closed[0];ids=r['all28OriginalBodyFaces'];part=tri[ids];scenes.append(dict(body=r['originalBody'],faces=ids,backFaces=r['completeBackingPatch']['completeBackingOriginalFaceIDs'],bounds=[(part.min((0,1))-.4).tolist(),(part.max((0,1))+.4).tolist()],description='complete28-face source / six-face backing'))
 openpart=next(r for r in d['all207Bodies2682Faces']if r.get('completeBoundaryWithinFixedBand'));ids=openpart['completeOriginalGlobalFaceIDs'];part=tri[ids];scenes.append(dict(body=openpart['originalBody'],faces=ids,backFaces=[],bounds=[(part.min((0,1))-.4).tolist(),(part.max((0,1))+.4).tolist()],description='complete10-face source / authored opening'))
 scenes.append({**scenes[6],'description':'same complete28-face source / reverse view','reverse':True});fig=plt.figure(figsize=(18,15),dpi=100)
 for panel,scene in enumerate(scenes):
  bounds=np.asarray(scene['bounds']);center=bounds.mean(0);hostids=[i for i in hosts if np.all(tri[i].max(0)>=bounds[0])and np.all(tri[i].min(0)<=bounds[1])];ax=fig.add_subplot(3,3,panel+1,projection='3d')
  for ids,color,alpha,line in [(hostids,'#95acb8',.42,.25),(scene['faces'],'#e49a40',.98,.55),(scene['backFaces'],'#287b58',.99,.6)]:
   clipped=[p for fi in ids for p in crop_display_triangle(tri[fi],bounds)]
   if clipped:ax.add_collection3d(Poly3DCollection((np.asarray(clipped)-center)[:,:,[0,2,1]],facecolors=color,edgecolors='#3f5056',alpha=alpha,linewidths=line))
  extent=(bounds-center)[:,[0,2,1]];ax.set_xlim(extent[:,0]);ax.set_ylim(extent[:,1]);ax.set_zlim(extent[:,2]);ax.set_box_aspect(extent[1]-extent[0]);ax.view_init(24,118 if scene.get('reverse')else-62);ax.set_title('Original body '+str(scene['body'])+'\n'+scene['description'],fontsize=10);ax.set_xlabel('X(m)');ax.set_ylabel('Z(m)');ax.set_zlabel('Y(m)')
  scene['completeOriginalUnclippedHostFaceIDs']=hostids
 DOC.mkdir(parents=True);png=DOC/'original-conditional-backing-context-display-crops-1800x1500.png';fig.tight_layout();fig.savefig(png);plt.close(fig);refs.append(ref(png));assert all(ref(ROOT/r['path'])==r for r in refs)
 out=dict(uid='landsd/261717:0',complete15579OriginalWorldSHA256=digest(tri.tobytes()),scenes=scenes,viewportClippingForPNGOnly=True,allSourceGeometryUntouched=True,noDisplayGeometryUsedByAnyAcceptanceChecker=True,sourceOnly=True,functionInferred=False,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'mount-original-backing-explicit-display-crops-source-only-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[out['uid']],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
