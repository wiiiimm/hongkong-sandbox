"""Complete detached three-face original patch: finite host/source context only.

No inferred window/sign/function. Historical source-only sampled host roots
are not current/finite host qualification. All zero-contact failures stay.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify

BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-three-face-original-patch-host-context-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
RIM=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1'
TOPOLOGY=BASE/'government-xl-hoi-shing-unresolved-original-body-topology-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [PROBE,GRAPH,RIM,TOPOLOGY]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 selection=bound(PROBE,PROBE/'selection.json.gz');graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');rim=bound(RIM,RIM/'diagnostic.json.gz');topology=bound(TOPOLOGY,TOPOLOGY/'diagnostic.json.gz');sources=[]
 assert [r['uid']for r in selection['rows']]==['landsd/318801:0','landsd/318830:0']
 for r in selection['rows']:
  p=ROOT/r['candidate']['path'];assert ref(p)['sha256']==r['sourceSHA256'];sources.append(decode_original_world_triangles(p.read_bytes()));refs.append(ref(p))
 world=np.concatenate(sources);assert world.shape==(19374,3,3)and digest(world.tobytes())==graph['binding']['completeOriginalWorldSHA256']==topology['completeOriginalWorldSHA256']
 body=graph['components'][10];t=next(r for r in topology['rows']if r['originalBody']==10);ids=body['globalOriginalFaces'];assert ids==t['completeGlobalOriginalFaces']==[4083,4084,4085]and body['actorUID']=='landsd/318801:0'
 patch=world[ids];assert digest(patch.tobytes())==t['completeBodyWorldSHA256'];hosts=rim['sourceOnlyDerivedGroundReachedBodies'];assert 10 not in hosts
 hostids=sorted(fi for b in hosts for fi in graph['components'][b]['globalOriginalFaces']);assert len(hostids)==len(set(hostids))and not set(ids)&set(hostids)
 proofs=[dict(globalOriginalFace=fi,proof=verify(world[fi],world[hostids]))for fi in ids]
 edgeincidences=defaultdict(list)
 for fi in ids:
  for a,b in zip(world[fi],np.roll(world[fi],-1,axis=0)):edgeincidences[tuple(sorted((tuple(a),tuple(b))))].append(fi)
 boundary=sorted(e for e,fs in edgeincidences.items()if len(fs)==1);assert len(boundary)==3
 refs.extend(ref(HERE/n)for n in ['exact_packed_world_geometry_20261009.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 low=patch.min((0,1));high=patch.max((0,1));center=(low+high)/2;bounds=np.array([low-2,high+2]);near=[i for i in range(len(world))if i not in ids and np.all(world[i].max(0)>=bounds[0])and np.all(world[i].min(0)<=bounds[1])]
 DOC.mkdir();fig=plt.figure(figsize=(18,9),dpi=100)
 for panel,azimuth in enumerate([-55,130]):
  ax=fig.add_subplot(1,2,panel+1,projection='3d');ax.add_collection3d(Poly3DCollection((world[near]-center)[:,:,[0,2,1]],facecolors='#9caab1',edgecolors='#52646d',alpha=.28,linewidths=.25));ax.add_collection3d(Poly3DCollection((patch-center)[:,:,[0,2,1]],facecolors='#df8c35',edgecolors='#713c19',alpha=.9,linewidths=1));display=(bounds-center)[:,[0,2,1]];ax.set_xlim(display[:,0]);ax.set_ylim(display[:,1]);ax.set_zlim(display[:,2]);ax.set_box_aspect(display[1]-display[0]);ax.view_init(22,azimuth);ax.set_title('All three original patch faces and complete nearby source context\nNo function, host qualification or support inferred');ax.set_xlabel('X(m)');ax.set_ylabel('Z(m)');ax.set_zlabel('Y(m)')
 png=DOC/'complete-three-original-faces-source-context-1800x900.png';fig.tight_layout();fig.savefig(png);plt.close(fig);refs.append(ref(png));assert all(ref(ROOT/r['path'])==r for r in refs)
 out=dict(uids=[r['uid']for r in selection['rows']],complete19374OriginalWorldSHA256=digest(world.tobytes()),originalBody=10,completeOriginalFaces=ids,completeOriginalPatchWorldSHA256=digest(patch.tobytes()),allOriginalEdgeIncidences=[dict(edge=list(map(list,e)),originalFaces=fs)for e,fs in sorted(edgeincidences.items())],completeOriginalBoundary=list(map(lambda e:list(map(list,e)),boundary)),completeConditionalSourceOnlyHostBodies=hosts,completeConditionalOriginalHostFaces=hostids,completeHostWorldSHA256=digest(world[hostids].tobytes()),allThreeWholeFiniteFacetProofs=proofs,passingWholeFacetIds=[p['globalOriginalFace']for p in proofs if p['proof']['wholeFacetAssociated']],sourceContextCompleteNearOriginalFaces=near,allOldZeroContactAndRimNegativesPreserved=True,sourceOnly=True,hostQualification=False,roleAssigned=False,currentAcceptance=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze_hoi_patch_context',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'whole-three-original-facet-finite-host-and-source-context-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,hostQualification=False,roleAssigned=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))
if __name__=='__main__':main()
