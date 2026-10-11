"""Original source panel/host-loop visual context, no fabricated geometry."""
from pathlib import Path
import importlib.util,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-panel-original-loop-context-v1';DOC=BASE/BATCH;INPUT=BASE/'xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1';UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 d=read(INPUT/'diagnostic.json.gz');asset=next(ROOT/r['path']for r in d['evidenceRefs']if r['path'].endswith('.glb.gz'));t=decode_original_world_triangles(asset.read_bytes());assert digest(t.tobytes())==d['completeOriginalWorldSHA256'];matched=[p for p in d['allDisconnectedSinglePanels']if p['completeReciprocalBoundaryMatches']];assert len(matched)==76
 representatives=[matched[0],next(p for p in matched if p['sourceFace']==8434),matched[-1]];allpanelids=[p['sourceFace']for p in matched];fig=plt.figure(figsize=(18,10),dpi=100);numeric=[]
 for k in range(4):
  ax=fig.add_subplot(2,2,k+1,projection='3d')
  if k==0:
   shown=t;center=(shown.min((0,1))+shown.max((0,1)))/2;s=(shown-center)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(s,facecolors='#bec4ca',alpha=.22,linewidths=0));ax.add_collection3d(Poly3DCollection((t[allpanelids]-center)[:,:,[0,2,1]],facecolors='#db8734',alpha=1,linewidths=.3));lo=s.min((0,1));hi=s.max((0,1));title='Complete original source; 76 loop-associated panel facets in orange'
  else:
   p=representatives[k-1];g=d['completeOriginalHostBoundaryGroups'][p['completeReciprocalBoundaryMatches'][0]];ids=sorted(set(e['completeOriginalHostIncidences'][0]['originalHostFace']for e in g['allOriginalHostBoundaryEdges']));panel=t[p['sourceFace']];center=panel.mean(0);host=(t[ids]-center)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(host,facecolors='#70a3bc',edgecolors='#28566d',alpha=.68,linewidths=.35));ax.add_collection3d(Poly3DCollection((panel[None]-center)[:,:,[0,2,1]],facecolors='#df8b32',edgecolors='#743e13',alpha=.95,linewidths=.8))
   vertices=np.asarray(g['originalBoundaryVertices']);n=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]);normal=np.cross(panel[1]-panel[0],panel[2]-panel[0]);plane_offset=np.max(abs((panel-vertices[0])@n))/np.linalg.norm(n);s=(panel-center)[:,[0,2,1]];lo=s.min(0)-.12;hi=s.max(0)+.12;title=f"Original face {p['sourceFace']}; 3 actual host-boundary incidences; cropped context";numeric.append(dict(sourceFace=p['sourceFace'],body=p['body'],hostBoundaryGroup=p['completeReciprocalBoundaryMatches'][0],allActualNeighbourHostFaces=ids,actualHostBoundaryVertices=vertices.tolist(),diagnosticLoopAreaM2=float(np.linalg.norm(n)/2),diagnosticAbsolutePanelLoopNormalCosine=float(abs(n@normal)/(np.linalg.norm(n)*np.linalg.norm(normal))),diagnosticMaximumPanelLoopPlaneSeparationM=float(plane_offset)))
  pad=max(float((hi-lo).max())*.02,.005);lo-=pad;hi+=pad;ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(23,-65);ax.set_title(title,fontsize=9);ax.set_xlabel('Original X (m)');ax.set_ylabel('Original Z (m)');ax.set_zlabel('Original Y (m)')
 fig.tight_layout();DOC.mkdir(parents=True);png=DOC/'original-panel-host-loop-context-1800x1000.png';fig.savefig(png);plt.close(fig);refs=[ref(p)for p in [Path(__file__),asset,png,INPUT/'diagnostic.json.gz',INPUT/'result.json',HERE/'exact_packed_world_geometry_20261009.py']];result=dict(uids=[UID],completeOriginalWorldSHA256=digest(t.tobytes()),all76MatchedOriginalPanelsShown=allpanelids,selectedExactOriginalPanelHostContexts=numeric,equalMetricAxis=True,closeViewsCroppedOnlyNoGeometryEdited=True,hostLoopLinesNotInventedCaps=True,sourceOnly=True,noFreshCurrentCapture=True,authoredRoleAccepted=False,structuralRootCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze_loop_visual',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'exact-original-langham-panel-host-boundary-loop-proportional-visual-context-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnly=True,authoredRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
