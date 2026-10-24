"""Eleven complete original uncapped wall bodies: bounded roof-loop leads only.

Every eight-face body/top/bottom edge stays. No cap or function is invented.
Complete roof hosts only have source-only historical sampled reachability;
all clearance/grade/cap/current/host acceptance obligations remain separate.
"""
from pathlib import Path
from collections import defaultdict,Counter
import importlib.util,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-eleven-open-wall-roof-loops-context-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1';RIM=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1';TOPOLOGY=BASE/'government-xl-hoi-shing-unresolved-original-body-topology-v1-20261011';PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
BODIES=[78,125,129,133,136,137,138,139,141,142,144];UID='landsd/318830:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in[GRAPH,RIM,TOPOLOGY,PROBE]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  receipts[folder.name]=receipt;refs.append(ref(folder/'result.json'))
 graph=read(GRAPH/'diagnostic.json.gz');rim=read(RIM/'diagnostic.json.gz');topology=read(TOPOLOGY/'diagnostic.json.gz')
 for folder in[GRAPH,RIM,TOPOLOGY]:assert ref(folder/'diagnostic.json.gz')in receipts[folder.name]['evidenceRefs'];refs.append(ref(folder/'diagnostic.json.gz'))
 selected=read(PROBE/'selection.json.gz');refs.append(ref(PROBE/'selection.json.gz'));sources=[]
 for row in selected['rows']:
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];sources.append(decode_original_world_triangles(asset.read_bytes()));refs.append(ref(asset))
 world=np.concatenate(sources);assert world.shape==(19374,3,3)and digest(world.tobytes())==graph['binding']['completeOriginalWorldSHA256']==topology['completeOriginalWorldSHA256']
 hosts=[b for b in rim['sourceOnlyDerivedGroundReachedBodies']if graph['components'][b]['actorUID']==UID];hostfaces=sorted(fi for b in hosts for fi in graph['components'][b]['globalOriginalFaces']);normals=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);roofids=[fi for fi in hostfaces if normals[fi,1]>0];roof=world[roofids]
 assert len(roof)>0 and not set(hosts)&set(BODIES)
 refs.extend(ref(HERE/n)for n in['exact_packed_world_geometry_20261009.py','exact_original_segment_surface_contact_band_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('hoi-eleven-roof-loop-source-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 def pulse():
  nonlocal last
  if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  fig=plt.figure(figsize=(24,22),dpi=100)
  for panel,body in enumerate(BODIES):
   c=graph['components'][body];t=next(r for r in topology['rows']if r['originalBody']==body);ids=c['globalOriginalFaces'];assert c['actorUID']==UID and ids==t['completeGlobalOriginalFaces']and len(ids)==8
   tri=world[ids];bottom=float(tri[:,:,1].min());top=float(tri[:,:,1].max());assert all(normals[fi,1]==0 for fi in ids)
   edges=defaultdict(list)
   for fi in ids:
    for a,b in zip(world[fi],np.roll(world[fi],-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))].append(fi)
   boundary=sorted(e for e,faces in edges.items()if len(faces)==1);assert len(boundary)==8
   loops=[]
   for name,height in[('entire-original-lower-opening',bottom),('entire-original-upper-opening',top)]:
    loop=[e for e in boundary if e[0][1]==e[1][1]==height];degree=Counter(v for e in loop for v in e);assert len(loop)==4 and len(degree)==4 and set(degree.values())=={2}
    proofs=[]
    for e in loop:
     p=verify_contact_segment(np.asarray(e),roof);p['completeOriginalSurfacePieces']=[{**v,'globalOriginalConditionalHostRoofFace':roofids[v['originalSurfaceFace']]}for v in p['completeOriginalSurfacePieces']];proofs.append(dict(completeOriginalEdge=[list(v)for v in e],proof=p));pulse()
    loops.append(dict(name=name,originalYM=height,allFourOriginalOpeningEdges=[list(map(list,e))for e in loop],completeFourEdgeProofs=proofs,conditionalEntireOriginalLoopWithinExistingBand=all(p['proof']['verifiedCompleteOriginalEdgeContactBand']for p in proofs)))
   low=tri.min((0,1));high=tri.max((0,1));bounds=np.array([low-.6,high+.6]);center=(low+high)/2;near=[fi for fi in hostfaces if np.all(world[fi].max(0)>=bounds[0])and np.all(world[fi].min(0)<=bounds[1])]
   ax=fig.add_subplot(4,3,panel+1,projection='3d');ax.add_collection3d(Poly3DCollection((world[near]-center)[:,:,[0,2,1]],facecolors='#9caab1',edgecolors='#52646d',alpha=.3,linewidths=.25));ax.add_collection3d(Poly3DCollection((tri-center)[:,:,[0,2,1]],facecolors='#df8c35',edgecolors='#713c19',alpha=.85,linewidths=.65));display=(bounds-center)[:,[0,2,1]];ax.set_xlim(display[:,0]);ax.set_ylim(display[:,1]);ax.set_zlim(display[:,2]);ax.set_box_aspect(display[1]-display[0]);ax.view_init(26,-55);ax.set_title('Original body '+str(body)+'; all 8 uncapped wall faces\nTop/bottom openings retained; no function inferred',fontsize=10);ax.set_xlabel('X(m)');ax.set_ylabel('Z(m)');ax.set_zlabel('Y(m)')
   rows.append(dict(originalBody=body,completeOriginalGlobalFaces=ids,completeBodySHA256=digest(tri.tobytes()),completeBounds=[low.tolist(),high.tolist()],allAuthoredEdgeIncidences=[dict(edge=[list(v)for v in e],originalFaces=fs)for e,fs in sorted(edges.items())],bothCompleteOriginalOpeningLoops=loops,generatedCapFaces=0,sourceOnly=True,hostQualification=False,roleAssigned=False,rootOrBridgeCredit=False));print(dict(body=body,conditionalOpeningLoops=[p['conditionalEntireOriginalLoopWithinExistingBand']for p in loops]),flush=True)
  DOC.mkdir();png=DOC/'all-eleven-original-uncapped-wall-bodies-context-2400x2200.png';fig.tight_layout();fig.savefig(png);plt.close(fig);refs.append(ref(png));assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=['landsd/318801:0',UID],complete19374OriginalWorldSHA256=digest(world.tobytes()),conditionalSourceOnlyHostBodies=hosts,completeConditionalOriginalRoofFaces=roofids,completeRoofSHA256=digest(roof.tobytes()),rows=rows,allElevenComplete88WallFacesPreserved=True,allOldZeroContactAndRimNegativesPreserved=True,hostQualificationFalse=True,sourceOnly=True,currentAcceptance=False,generatedCaps=0,roleAssigned=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze_hoi_openwall',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'eleven-authored-openwall-bodies-full-top-bottom-roof-loop-source-context-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,allElevenComplete88WallFacesPreserved=True,rootOrBridgeCredit=False,generatedCaps=0,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
