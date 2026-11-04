"""UNEXECUTED complete residual source topology/context; no mount or role qualification."""
from pathlib import Path
from collections import defaultdict,Counter
import json,sys,time,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_six_basic_preserved_ground_feasibility_draft_v1_20261012 as inputs
from upton_geometry_bound_inherited_overlap_replay_draft_v1_20261012 import ref,check,module,CURRENT,UIDS,FOREIGN,FREEZER
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,MODES
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-746-residual-saved-source-role-reconciliation-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
MAIN=BASE/'government-xl-upton-main12728-four-world-grade-cap-interfaces-v1-20261012';FEAS=BASE/'government-xl-upton-six-basic-saved-current-ground-feasibility-v1-20261012';FOLDERS=inputs.FOLDERS+[MAIN,FEAS]
CROSS=BASE/'government-xl-upton-podium12728-12662-complete-original-foreign-conflict-attribution-v1-20261011/diagnostic.json.gz'
CONTEXT=BASE/'government-xl-upton-podium12728-12662-original-boundary-context-v1-20261011/context.json'
def load():
 _,_,worlds,_,_=inputs.load_inputs();main=read(MAIN/'diagnostic.json.gz');cross=read(CROSS);assert len(cross['allExactFiniteOriginalContacts'])==23
 assert main['all13704SourceFacesAnd749BodiesAnd17ZerosPreserved']and not main['wholePairRoleAccepted']and not main['gradeRootAccepted']
 for uid,mode,w,c,p in worlds:
  groups=c['sharedEdgeConnectedComponents'];zeros=c['exactNonrenderingOriginalFaces'];assert sorted(i for g in groups for i in g)==sorted(c['completeRenderableFaceIds'])
  assert sorted([i for g in groups for i in g]+zeros)==list(range(len(w)))
  assert len(groups)=={UIDS[0]:737,UIDS[1]:8,UIDS[2]:4}[uid]and p['wholeWorldSHA256']==sha(w)
  records={q['face']:q['candidate']for q in p['findings']['rows']};assert set(records)==set(range(len(w)))
  for i in range(len(w)):assert records[i]['sourceFaceSHA256']==sha(w[i])and records[i]['ordinaryBoundProved']and records[i]['projectionCovered']
 assert len(worlds)==12 and sum(len(c['sharedEdgeConnectedComponents'])-1 for _,m,_,c,_ in worlds if m=='original')==746
 return worlds,main,cross
def schema_only():
 p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))
 for q in p['inputRefs']+p['codeRefs']:check(q)
 worlds,main,cross=load();assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),residualOriginalComponents=746,fullSourceFaces=13704,sourceZeros=17,priorCrossings=23,fourWorldRows=len(worlds),sourceRoleOrTopologyMathExecuted=False,noDBOrLease=True)
def topology(w,ids):
 edge=defaultdict(list)
 for i in ids:
  assert not exact_nonrendering(w[i]);v=[tuple(map(float,p))for p in w[i]]
  for k in range(3):
   a,b=v[k],v[(k+1)%3];assert a!=b;key=tuple(sorted([a,b]));edge[key].append(dict(sourceFace=i,localEdge=k,winding=1 if a==key[0]else-1))
 records=[dict(edge=[list(p)for p in e],fullSourceIncidences=r)for e,r in sorted(edge.items())];boundary=[q for q in records if len(q['fullSourceIncidences'])==1];degree=Counter(tuple(p)for q in boundary for p in q['edge'])
 return dict(completeOriginalNonzeroEdgeIncidence=records,completeBoundaryEdges=boundary,boundaryVertexDegrees=[dict(vertex=list(p),degree=n)for p,n in sorted(degree.items())],nonmanifoldEdges=[q for q in records if len(q['fullSourceIncidences'])>2],twoFaceWindingConflicts=[q for q in records if len(q['fullSourceIncidences'])==2 and q['fullSourceIncidences'][0]['winding']==q['fullSourceIncidences'][1]['winding']],closedSolidOrMountingOrOpeningInterpretation=False)
def image(w,selected,path,title,pulse):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 full=w.reshape(-1,3);centre=(full.min(0)+full.max(0))/2;t=w-centre;chosen=t[selected];fig=plt.figure(figsize=(22,13),dpi=100);a=fig.add_subplot(121);a.add_collection(PolyCollection(t[:,:,[0,2]],facecolors='#a0a0a0',edgecolors='none',alpha=.12));a.add_collection(PolyCollection(chosen[:,:,[0,2]],facecolors='#287bd4',edgecolors='#16436d',linewidths=.25,alpha=.7));a.autoscale_view();a.set_aspect('equal');a.set_xlabel('viewer X minus diagnostic centre X (m)');a.set_ylabel('viewer Z minus diagnostic centre Z (m)')
 b=fig.add_subplot(122,projection='3d');b.add_collection3d(Poly3DCollection(t,facecolors='#aaaaaa',edgecolors='none',alpha=.055));b.add_collection3d(Poly3DCollection(chosen,facecolors='#287bd4',edgecolors='#16436d',linewidths=.18,alpha=.65));lo=t.reshape(-1,3).min(0);hi=t.reshape(-1,3).max(0)
 for setter,i in[(b.set_xlim,0),(b.set_ylim,1),(b.set_zlim,2)]:setter(lo[i],hi[i])
 b.set_box_aspect(np.maximum(hi-lo,1));b.view_init(elev=25,azim=-65);b.set_xlabel('X - centreX (m)');b.set_ylabel('HKPD Y - centreY (m)');b.set_zlabel('Z - centreZ (m)');fig.suptitle(title+'; complete unchanged actor in grey, named source facets in blue\nAbsolute HKPD Y = plotted Y + centreY; visual context only, no function/mount/root/bridge claim',fontsize=12);fig.tight_layout();fig.savefig(path,dpi=100);plt.close(fig);pulse(True)
 with Image.open(path)as im:assert im.size==(2200,1300);dimensions=list(im.size)
 return dict(image=ref(path),dimensions=dimensions,diagnosticCentreOriginalXYZ=centre.tolist(),absoluteFullActorBounds=[full.min(0).tolist(),full.max(0).tolist()],highlightedSourceFaceIDs=selected,perspectiveAndProjectionOcclusionAreVisualLimitations=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic();refs=[ref(p)for p in inputs.code_paths(Path(__file__))]+[ref(PROPOSAL/n)for n in['METHOD.md','draft-pins.json','schema-preflight.json']];refs+=read(PROPOSAL/'draft-pins.json')['inputRefs']+read(PROPOSAL/'draft-pins.json')['codeRefs']
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic();print(json.dumps(dict(heartbeat=True)),flush=True)
 schema_only()
 for folder in FOLDERS:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();worlds,main,cross=load();DOC.mkdir(parents=True);rows=[];images=[]
 for uid in UIDS[:3]:
  modes={m:(w,c,p)for u,m,w,c,p in worlds if u==uid};w,c,p=modes['original'];groups=c['sharedEdgeConnectedComponents'];families=defaultdict(list);bound={m:dict(worldSHA=sha(v),records={q['face']:q['candidate']for q in proof['findings']['rows']})for m,(v,_,proof)in modes.items()}
  for body,ids in enumerate(groups[1:],1):
   full=[]
   for mode in MODES:
    v,_,proof=modes[mode];records=bound[mode]['records'];full.append(dict(mode=mode,wholeActorWorldSHA256=bound[mode]['worldSHA'],completeBodyWorldSHA256=sha(v[ids]),sameOriginalFaceIDs=ids,actualNonrenderingWorldFaceIDs=[i for i in ids if exact_nonrendering(v[i])],completeOrdinaryAndCoverageRecordsReusedFrom=ref(inputs.AUD/'complete-candidate-clearance.json.gz'),completeFacetBindings=[dict(face=i,sourceFaceSHA256=records[i]['sourceFaceSHA256'],exactLowerM=records[i]['exactLowerM'],ordinaryBoundProved=records[i]['ordinaryBoundProved'],projectionCovered=records[i]['projectionCovered'])for i in ids]))
   n=len(ids);family='2-4'if n<=4 else'6-8'if n<=8 else'9-16'if n<=16 else'24-40'if n<=40 else'larger-than40';families[family]+=ids;points=w[ids].reshape(-1,3);rows.append(dict(uid=uid,originalBody=body,completeSourceFaceIDs=ids,completeOriginalTriangles=w[ids].tolist(),originalPoseBounds=[points.min(0).tolist(),points.max(0).tolist()],fullIntrinsicSourceTopology=topology(w,ids),worlds=full,descriptiveFacetCountFamily=family,savedMainOnlyContactDiagnostic=ref(MAIN/'diagnostic.json.gz'),residualContactsNotMeasuredByThatMainOnlyDiagnostic=True,sourceVisualRole='uninterpreted',mountingRootBridgeHostFunctionAndAcceptanceCredit=False));pulse()
  if uid==UIDS[0]:
   for family,ids in sorted(families.items()):images.append(image(w,sorted(ids),DOC/('tower-residual-family-'+family+'-2200x1300.png'),uid+' all residual bodies in facet-count family '+family,pulse))
  else:images.append(image(w,sorted(i for g in groups[1:]for i in g),DOC/(uid.split('/')[1].replace(':','-')+'-complete-residual-context-2200x1300.png'),uid+' all original residual bodies',pulse))
 assert len(rows)==746 and len(images)==7;save(DOC/'diagnostic.json.gz',dict(rows=rows,images=images,fullSourceBodyCensuses=[dict(uid=u,sourceOriginalBodyCensus=c)for u,m,w,c,p in worlds if m=='original'],all17OriginalNonrenderingFacetsUncredited=True,all23OriginalPodiumCrossingsUncredited=ref(CROSS),priorCompleteContext=ref(CONTEXT),boundedMainOnlyGradeCap=ref(MAIN/'diagnostic.json.gz'),sixActualBasicUpperGapFailures=ref(inputs.RAW/'neighbour-checks.json'),sourceGeometryChanges=0,terrainGeometryChanges=0,roleSupportOrWholePairAcceptance=False,newlyInstalled=0));refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();module(FREEZER,'upton_residual_saved_role_freezer').freeze(BATCH,'746-complete-original-residual-topology-and-saved-four-world-source-context',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS[:3],currentManifestSHA256=CURRENT,sourceOnly=True,newlyInstalled=0,physicalAccepted=False))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--inspect-saved-residual-source-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-residual-source-context-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
