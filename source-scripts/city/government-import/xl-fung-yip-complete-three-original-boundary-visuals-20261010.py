"""Complete untouched three-original exports; distinct permits, no physical credit."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from no1_garden_original_overhead_roof_edge_identity_20261010 import primary_polygon

BATCH='government-xl-fung-yip-complete-three-original-boundary-visuals-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
CONTEXT=DOC.parent/'government-xl-fung-yip-distinct-original-shared-boundary-diagnostic-v2-20261010'
INPUTS=[DOC.parent/'government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010/selection.json.gz',DOC.parent/'government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010/selection.json.gz']
UID='landsd/79883:0'; OTHERS=['landsd/12728:0','landsd/79882:0']

def main():
 assert not DOC.exists();DOC.mkdir(parents=True)
 x=read(CONTEXT/'diagnostic.json.gz');rows={r['uid']:r for p in INPUTS for r in read(p)['rows']};world={};assets=[]
 for u in [UID,*OTHERS]:
  p=ROOT/rows[u]['candidate']['path'];assets.append(p);raw=p.read_bytes();assert digest(raw)==x['completeSourceVersions'][u];world[u]=decode_original_world_triangles(raw);assert digest(world[u].tobytes())==x['completeWorldVersions'][u]
 all_faces=np.concatenate(list(world.values()));centre=all_faces.mean((0,1));colors={UID:'#a7adb4',OTHERS[0]:'#78a6d6',OTHERS[1]:'#b6c98b'}
 marks=sorted(set(i for r in x['rows'] for i in r['checks']['current']['allExcessFaceIds']))
 def xyz(a):return np.stack([a[...,0]-centre[0],centre[2]-a[...,2],a[...,1]],axis=-1)
 fig=plt.figure(figsize=(16,10),dpi=180);ax=fig.add_subplot(121,projection='3d')
 for u in [UID,*OTHERS]:ax.add_collection3d(Poly3DCollection(xyz(world[u]),facecolors=colors[u],edgecolors='none',alpha=.85))
 ax.add_collection3d(Poly3DCollection(xyz(world[UID][marks]),facecolors='#e63426',edgecolors='#961a0c',linewidths=.3))
 full=xyz(all_faces);lo=full.min((0,1));hi=full.max((0,1));ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[1]-1,hi[1]+1);ax.set_zlim(0,hi[2]+2);ax.set_box_aspect((hi[0]-lo[0],hi[1]-lo[1],hi[2]+2));ax.view_init(35,-68)
 ax.set_xlabel('East offset m');ax.set_ylabel('North offset m');ax.set_zlabel('HKPD m');ax.set_title('Complete original 398 + 1,655 + 616 faces\nRed: every own projected-excess face, none omitted')
 for pos,other in [(222,OTHERS[0]),(224,OTHERS[1])]:
  top=fig.add_subplot(pos);rr=next(r for r in x['rows'] if r['foreignUID']==other);ids=rr['checks']['current']['allExcessFaceIds'];marked=world[UID][ids]
  for u in [UID,other]:top.add_collection(PolyCollection(world[u][:,:,[0,2]],facecolors=colors[u],edgecolors='none',alpha=.3))
  top.add_collection(PolyCollection(marked[:,:,[0,2]],facecolors='#e63426',edgecolors='#961a0c',linewidths=.3))
  for u,color in [(UID,'#222222'),(other,'#165aa8')]:
   b=next(b for b in x['allCurrentForms'] if b['uid']==u)
   for ring in b['rings']:a=np.asarray(ring);top.plot(a[:,0],a[:,1],color=color,lw=1.2)
   primary=primary_polygon(x['primary'][u]);a=np.asarray(primary.exterior.coords);top.plot(a[:,0],a[:,1],color=color,lw=.6,linestyle='--')
  a=marked[:,:,[0,2]];l=a.min((0,1));h=a.max((0,1));top.set_xlim(l[0]-1.5,h[0]+1.5);top.set_ylim(l[1]-1.5,h[1]+1.5);top.set_aspect('equal');top.invert_yaxis();top.set_xlabel('World X m');top.set_ylabel('World Z m')
  c=rr['checks']['current'];top.set_title(f'Distinct {other}: {len(ids)} own excess faces\nRaw {c["rawForeignExcessM2"]:.6f} m²; shared edge {c["exactSharedBoundaryLengthM"]:.3f} m')
 fig.suptitle('Fung Yip original source boundary diagnosis — three distinct permits and physical actors',fontsize=15);fig.text(.5,.015,'Grey: Fung Yip H234/75; blue: adjacent HK32/2015(OP); green: adjacent H29/86. Exact interfaces and projected strips imply no common ownership/support/collision waiver.',ha='center',fontsize=10);fig.tight_layout(rect=[0,.04,1,.94])
 p=DOC/'complete-three-originals-and-two-boundary-details-2880x1800.png';fig.savefig(p);plt.close(fig)
 save(DOC/'render.json',dict(width=2880,height=1800,sourceVersions=x['completeSourceVersions'],worldVersions=x['completeWorldVersions'],completeOriginalFaceCounts={u:len(t)for u,t in world.items()},allOwnExcessFaceIds=marks,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False))
 spec=importlib.util.spec_from_file_location('fung_three_visual_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);o=m.freeze(BATCH,'complete-three-original-boundary-visuals-v1',[Path(__file__),CONTEXT/'diagnostic.json.gz',CONTEXT/'result.json',*INPUTS,*assets],dict(uids=[UID,*OTHERS],sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,qualification='Complete original exports inspected independently before any proposed identity interpretation. Distinct original actors/permits remain full collision/terrain/support actors; no surveyed legal property boundary claim.'))
 print(json.dumps(dict(jobId=o['jobId'],path=str(p.relative_to(ROOT)))),flush=True)

if __name__=='__main__':main()
