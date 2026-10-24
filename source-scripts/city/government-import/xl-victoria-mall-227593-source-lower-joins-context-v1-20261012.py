"""UNEXECUTED diagram/record closure of completed original census; no predicates."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.collections import PolyCollection
import PIL
from PIL import Image
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-victoria-mall-retained-tower3-complete-source-census-v1-20261012'
JOB='3117c77984a0d7648e7ef61c5613c1a8e5973f204aa59bf52f3e09238edb3d15';RESULT_SHA='78080035be2d1a57d049229d19333288f577f6525c59a755ad0218f8eceba1e1';DATA_SHA='af5c9fe22cf812759f50f1f9333a7d847d5dfec34568fcb71e63d18b618608e7'
MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
P,T,T2,T1='landsd/227593:0','landsd/251609:0','landsd/251614:0','landsd/251615:0'
BATCH='government-xl-victoria-mall-complete-source-lower-joins-context-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
METHOD=BASE/'government-xl-victoria-mall-source-join-context-draft-v1-20261012/METHOD.md'
COLORS={P:'#94a5ad',T:'#3179b3',T2:'#62a893',T1:'#ed9e45'}
def preflight():
 assert not DOC.exists();result_path=PRIOR/'result.json';data_path=PRIOR/'diagnostic.json.gz';assert digest(result_path.read_bytes())==RESULT_SHA and digest(data_path.read_bytes())==DATA_SHA;result=read(result_path);out=read(data_path)
 assert result['jobId']==JOB and len(result['evidenceRefs'])==422 and result['newlyInstalled']==0 and result['currentAcceptance']is False
 assert len(out['allNineOldFailedLowerWitnessContexts'])==9 and len(out['completeMallToRetainedTower3Contacts']['contacts'])==len(out['completeContactClassifications'])==1276 and sum(r['properTriangleInteriorCrossing']for r in out['completeContactClassifications'])==1136 and len(out['completePositiveRealFacetGeometricFamilies'])==9
 assert out['installedTower3AlreadyPresentNotNewImport']and out['intentionalSurveyedFootprintFallbackUnchanged']and out['oldSampleAndSharedEdgeFailuresNotRerun']and all(out[k]is False for k in ['identityAccepted','architecturalRoleAccepted','groundRootsAccepted','structuralSupportAccepted','physicalAccepted','currentAcceptance','installationApproved'])
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 refs=[Path(__file__),METHOD,result_path,data_path,HERE/'exact_packed_world_geometry_20261009.py',HERE/'run.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'popcorn_original_ancillary_identity_20261009.py']+[HERE.parent/'shared-modelling'/p for p in ['db.py','jobs.py','reservations.py','reservation_runner.py']]
 for pin in result['evidenceRefs']:
  path=ROOT/pin['path'];assert digest(path.read_bytes())==pin['sha256'];refs.append(path)
 retained=read(ROOT/'3d-viewer/city/data/official-models/support-review-20260909/catalogue.json');assert [r for r in retained['models']if r['uid']==T]==[out['installedTower3EntryVerbatim']]
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};return result,out,refs,pins

def polygons3(ax,triangles,color,alpha=.22,linewidth=.08):
 if not len(triangles):return
 ax.add_collection3d(Poly3DCollection(triangles[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidths=linewidth))
def frame3(ax,triangles):
 a=triangles[:,:,[0,2,1]].reshape(-1,3);lo=a.min(0);hi=a.max(0);span=np.maximum(hi-lo,.02);margin=span*.04
 ax.set_xlim(lo[0]-margin[0],hi[0]+margin[0]);ax.set_ylim(lo[1]-margin[1],hi[1]+margin[1]);ax.set_zlim(lo[2]-margin[2],hi[2]+margin[2]);ax.set_box_aspect(span);ax.set_xlabel('source X m');ax.set_ylabel('source Z m');ax.set_zlabel('source Y HKPD m');ax.view_init(elev=24,azim=-58)
def polygons2(ax,w,axes,color,alpha=.2):
 if len(w):ax.add_collection(PolyCollection(w[:,:,axes],facecolors=color,edgecolors=color,alpha=alpha,linewidths=.25));ax.autoscale_view();ax.set_aspect('equal',adjustable='datalim')
def finish(fig,name,display):
 fig.suptitle('PROVIDER ORIGINAL DIAGNOSTIC OVERLAY — no role/root/solid/current approval',fontsize=11);fig.tight_layout(rect=[0,0,.99,.96]);path=DOC/name;fig.savefig(path,dpi=150);plt.close(fig)
 with Image.open(path)as image:assert image.size==(2400,1800)
 return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),width=2400,height=1800,displayScope=display,diagnosticOverlayNotGPUScreenshot=True)
def owned(state):
 result,out,refs,pins=state;lease=read(LEASE);resources=['building:'+u for u in sorted([P,T,T2,T1])];assert lease['resources']==resources and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',result)
 worlds={}
 for uid,a in out['originalSources'].items():
  path=ROOT/a['sourceTupleVerbatim']['assetPath'];assert digest(path.read_bytes())==a['sourceTupleVerbatim']['sourceSHA256'];w=decode_original_world_triangles(path.read_bytes());assert w.shape==(a['sourceTupleVerbatim']['faces'],3,3)and digest(w.astype('<f8').tobytes())==a['completeWorldSHA256'];worlds[uid]=w
 groups={u:a['completeOriginalTopology']['sharedEdgeConnectedComponents']for u,a in out['originalSources'].items()};records=out['completeContactClassifications'];proper=[r for r in records if r['properTriangleInteriorCrossing']];contactids={P:sorted({r['contactVerbatim']['sourceFaceA']for r in records}),T:sorted({r['contactVerbatim']['sourceFaceB']for r in records})};properids={P:sorted({r['contactVerbatim']['sourceFaceA']for r in proper}),T:sorted({r['contactVerbatim']['sourceFaceB']for r in proper})};exports=[];DOC.mkdir()
 fig=plt.figure(figsize=(16,12));ax=fig.add_subplot(111,projection='3d')
 for u in [P,T,T2,T1]:polygons3(ax,worlds[u],COLORS[u],.1)
 for u in [P,T]:polygons3(ax,worlds[u][contactids[u]],'#c5008c',.5)
 frame3(ax,np.concatenate(list(worlds.values())));ax.set_title('Complete four originals; magenta = ALL1276 P–retainedT3 contact facet inventories\nT3 already installed; absent T1/T2 are source context only',fontsize=10);exports.append(finish(fig,'complete-four-originals-and-all1276-contact-facets-2400x1800.png','All4 complete source meshes; all cross-contact facet IDs highlighted. Zero primitives retained.'))
 fig=plt.figure(figsize=(16,12))
 for i,axes in enumerate([(0,1),(0,2),(2,1)],1):
  ax=fig.add_subplot(1,3,i)
  for u in [P,T]:polygons2(ax,worlds[u][contactids[u]],axes,COLORS[u],.18);polygons2(ax,worlds[u][properids[u]],axes,'#bd008d',.46)
  ax.set_title('Original axes '+str(axes)+'\n1136 proper crossing records; no role verdict',fontsize=9);ax.tick_params(labelsize=7)
 exports.append(finish(fig,'complete1276-contact-facets-and1136-crossing-overlay-orthographic-2400x1800.png','Complete contacting source facets and all proper-crossing source facets; no clipping or ground.'))
 fig=plt.figure(figsize=(16,12));family_records=[]
 for i,family in enumerate(out['completePositiveRealFacetGeometricFamilies']):
  ax=fig.add_subplot(3,3,i+1,projection='3d');tri=[];ids={}
  for u,c in family:ids.setdefault(u,[]).extend(groups[u][c])
  ids={u:sorted(set(v))for u,v in ids.items()}
  for u,faces in ids.items():polygons3(ax,worlds[u][faces],COLORS[u],.25);tri.append(worlds[u][faces])
  frame3(ax,np.concatenate(tri));ax.set_title('Unrooted family'+str(i)+'; bodies'+str(len(family))+'; facets'+str(sum(map(len,ids.values()))),fontsize=8);ax.tick_params(labelsize=6);family_records.append(dict(family=i,sourceActorComponentIDsVerbatim=family,completeOriginalFaceIDsByActor=ids,rootCredit=False))
 exports.append(finish(fig,'all9-complete-unrooted-original-contact-families-2400x1800.png','Every complete real-facet family shown separately; no ground roots, zero/point bridges or visual interpretations.'))
 fig=plt.figure(figsize=(16,12));failed=out['allNineOldFailedLowerWitnessContexts'];display_local=[]
 for i,row in enumerate(failed):
  u=row['uid'];own=worlds[u][row['oldAnnotatedSourceFaceIDs']];point=np.asarray(row['rawFailedWitnessVerbatim']['position']);lo=own.min((0,1))-2.;hi=own.max((0,1))+2.;pids=np.flatnonzero(np.all(worlds[P].max(1)>=lo,axis=1)&np.all(worlds[P].min(1)<=hi,axis=1)).tolist();localids=np.flatnonzero(np.all(worlds[u].max(1)>=lo,axis=1)&np.all(worlds[u].min(1)<=hi,axis=1)).tolist();ax=fig.add_subplot(3,3,i+1,projection='3d');polygons3(ax,worlds[P][pids],COLORS[P],.17);polygons3(ax,worlds[u][localids],COLORS[u],.12);polygons3(ax,own,'#c5008c',.8,linewidth=.8);ax.scatter(point[0],point[2],point[1],color='black',s=18);ax.text(point[0],point[2],point[1],'old'+str(i),fontsize=8);frame3(ax,own);ax.set_title(u+'\nwhole annotated facets'+str(row['oldAnnotatedSourceFaceIDs'])+'; gap'+str(row['rawFailedWitnessVerbatim']['gap']),fontsize=7);ax.tick_params(labelsize=6);display_local.append(dict(witness=i,uid=u,completeAnnotatedOriginalFaceIDs=row['oldAnnotatedSourceFaceIDs'],displayOnlyPFacetIDs=pids,displayOnlySameActorFacetIDs=localids,displayOnlyBoundsPaddingMetres=2.,fullSourceBodiesPreservedElsewhere=True,noDistanceOrContactPredicateComputed=True))
 exports.append(finish(fig,'all9-original-failed-witnesses-and-source-neighbour-overlays-2400x1800.png','Nine complete annotated original-facet groups highlighted;2m display-only neighbour nomination; view limits follow complete annotated facets. Local display crops are not source omission/clearance.'))
 fig=plt.figure(figsize=(16,12));full_failed_body_records=[]
 for i,u in enumerate([T,T1],1):
  rows=[r for r in failed if r['uid']==u];bodyids=sorted({c for r in rows for c in r['affectedSourceComponentIDs']});faceids=sorted({f for c in bodyids for f in groups[u][c]});highlight=sorted({f for r in rows for f in r['oldAnnotatedSourceFaceIDs']});ax=fig.add_subplot(1,2,i,projection='3d');polygons3(ax,worlds[P],COLORS[P],.08);polygons3(ax,worlds[u][faceids],COLORS[u],.2);polygons3(ax,worlds[u][highlight],'#c5008c',.9);frame3(ax,np.concatenate([worlds[P],worlds[u][faceids]]));ax.set_title(u+' whole affected original bodies'+str(bodyids)+'\nall old annotated failure facets magenta',fontsize=9);full_failed_body_records.append(dict(uid=u,completeAffectedComponentIDs=bodyids,completeAffectedOriginalFaceIDs=faceids,completeOldAnnotatedOriginalFaceIDs=highlight))
 exports.append(finish(fig,'complete-original-failed-tower3-and-tower1-bodies-with-mall-2400x1800.png','Complete affected body0 of retainedT3 and absentT1 alongside complete Mall; no clipped data, engineering or volumetric approval.'))
 context=dict(uids=[P,T,T2,T1],priorCompletedSourceCensus=JOB,sourceActorsVerbatim=out['originalSources'],completeInstalledTower3EntryVerbatim=out['installedTower3EntryVerbatim'],all1276ContactsVerbatim=out['completeMallToRetainedTower3Contacts'],all1276ClassificationsVerbatim=records,all1136ProperCrossingRecordsPreserved=True,complete9FamiliesVerbatim=out['completePositiveRealFacetGeometricFamilies'],completeFamilyFaceCoordinates=[dict(**r,completeCoordinatesByActor={u:worlds[u][ids].tolist()for u,ids in r['completeOriginalFaceIDsByActor'].items()})for r in family_records],all9RawFailureContextsVerbatim=failed,completeFailedBodyRecords=full_failed_body_records,all9DisplayOnlyNeighbourRecords=display_local,completeContactFacetIDsByActor=contactids,completeProperCrossingFacetIDsByActor=properids,all4CompleteOriginalWorldTriangles={u:w.tolist()for u,w in worlds.items()},allZeroPrimitiveOriginalIDsByActor={u:a['completeOriginalTopology']['exactNonrenderingOriginalFaces']for u,a in out['originalSources'].items()},exports=exports,sourceProjectionOnly=True,notCurrentGPUVisibility=True,matplotlibVersion=matplotlib.__version__,pillowVersion=PIL.__version__,oldRimPointDistanceGroundPredicatesNotRerun=True,noArchitecturalInterpretationAccepted=True,interiorCrossingsNotAutomaticallyWrongOrRight=True,noRuntimeOrApprovalTransfer=True,sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0)
 save(DOC/'context.json.gz',context);refs.append(DOC/'context.json.gz');refs.extend(ROOT/r['path']for r in exports)
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 spec=importlib.util.spec_from_file_location('victoria_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.freeze(BATCH,'complete-original-source-nine-failed-joins-and1276-contacts-context-only',refs,dict(uids=[P,T,T2,T1],sourceOnly=True,priorCompletedSourceCensus=JOB,all9RawFailuresPreserved=True,completeContactsPreserved=1276,properCrossingsPreserved=1136,unrootedFamiliesPreserved=9,originalDiagramExports=len(exports),noArchitecturalInterpretationAccepted=True,noRuntimeOrApprovalTransfer=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 assert reservations.owns(lease)
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 print(json.dumps(dict(jobId=r['jobId'],exports=len(exports),currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('victoria-source-join-context-'+str(uuid.uuid4()),['building:'+u for u in sorted([P,T,T2,T1])],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
