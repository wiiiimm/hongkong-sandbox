"""UNEXECUTED: exact saved Yoho main/interface/failure context; no predicates."""
from pathlib import Path
import ast,importlib.util,json,subprocess,sys,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from run import ROOT,HERE,read,save,digest,connect,reservations

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-yoho-main955-ground-residual-context-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PROBE=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
ATTRS=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-attributes-v1'
FINITE=BASE/'xl-terrain-recovery-20261012-yoho-eight-pair-four-stream-finite-edge-interfaces-v1'
METHOD=BASE/'government-xl-yoho-main955-ground-residual-context-method-draft-20261012/METHOD.md'
PREFLIGHT=METHOD.parent/'no-worker-schema-pin-preflight.json'
UIDS=['landsd/146396:0','landsd/231756:0'];RELATED=['landsd/121143:0','landsd/55568:0','landsd/4757:0']
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
JOBS=[(PROBE,'6da18fbe3cb5a91c8fa1b24e5f9f6b8ed378eb09607299e0b8aeca4ec3691a1e','778c6658ea3eced67f90fdbc5d02bcef631def48d509e57e896e1bcddc99dd06'),(ATTRS,'368ed4a50d83f7912ee585334877d163f1740d25d271015c551832844786198d','659f67cb25797fa6b4063826bd5098ef6ba85eecb00bc6d728ff9440b0424e9c'),(FINITE,'693e02926f1181b890f4fb2adb46b0c030ee2e604e585931c8c56f02ca0461b2','ba62d8c36b91fc070a881fae8d7a759f76bf00f349b2ebc522a1f1675c3bd3dc')]

def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert p.is_file() and ref(p)==pin,pin
 return p
def local_closure():
 queue=[Path(__file__),FREEZER,HERE/'exact_packed_world_geometry_20261009.py'];out={}
 while queue:
  p=queue.pop().resolve()
  if str(p) in out:continue
  out[str(p)]=ref(p)
  for node in ast.walk(ast.parse(p.read_text())):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else [x.name for x in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    for parent in [HERE,HERE.parent/'shared-modelling']:
     q=parent/(name.replace('.','/')+'.py')
     if q.is_file():queue.append(q)
 return sorted(out.values(),key=lambda p:p['path'])
def purely_geometric_reached(interfaces,seed):
 reached={seed}
 while True:
  before=set(reached)
  for p in interfaces:
   a,b=p['bodies']
   if a in reached or b in reached:reached.update([a,b])
  if reached==before:return sorted(reached)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists()
 preflight=read(PREFLIGHT);assert preflight['passed'] and preflight['workerOrDatabaseStarted']==False and preflight['caller']==ref(Path(__file__)) and preflight['method']==ref(METHOD)
 refs=local_closure()+[ref(METHOD),ref(PREFLIGHT)]+preflight['checkedRefs'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 for folder,job,sha in JOBS:
  r=read(folder/'result.json');assert r['jobId']==job and ref(folder/'result.json')['sha256']==sha and r['newlyInstalled']==0
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
  for pin in r['evidenceRefs']:check(pin);refs.append(pin);pulse()
  refs.append(ref(folder/'result.json'))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;refs.append(start)
 for pin in refs:check(pin)
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 selection=read(PROBE/'selection.json.gz')['rows'];runtime=read(HERE/'local'/PROBE.name/'runtime-geometry.json.gz')['rows'];d=read(FINITE/'diagnostic.json.gz');attrs=read(ATTRS/'actual-render-attributes.json.gz')
 assert [r['uid'] for r in selection]==[r['uid'] for r in runtime]==UIDS and d['completeOriginalFaces']==22523
 worlds=[]
 for row in selection:
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];refs.append(ref(asset));worlds.append(decode_original_world_triangles(asset.read_bytes()))
 tri=np.concatenate(worlds);assert tri.shape==(22523,3,3)
 original=next(g for g in d['interfaceRows'] if g['mode']=='providerOriginal');bodies=original['bodies'];assert digest(tri.tobytes())==original['completeWorldSHA256'] and len(bodies)==1068
 assert bodies[955]['uid']==UIDS[1] and len(bodies[955]['globalOriginalFaces'])==4019
 assert bodies[135]['uid']==UIDS[0] and len(bodies[135]['globalOriginalFaces'])==2084
 body_members={i:b['body'] for b in bodies for i in b['globalOriginalFaces']};assert len(body_members)==22523
 graphs=[];failures=[];crossrows=[];contactsets=[]
 assert [g['mode']for g in d['interfaceRows']]==['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 for g in d['interfaceRows']:
  assert [(b['uid'],b['globalOriginalFaces']) for b in g['bodies']]==[(b['uid'],b['globalOriginalFaces'])for b in bodies]
  cross=[p for p in g['onePositiveDimensionalWitnessPerContactingBodyPair'] if bodies[p['bodies'][0]]['uid']!=bodies[p['bodies'][1]]['uid']]
  assert len(cross)==1 and cross[0]['bodies']==[135,955] and cross[0]['globalOriginalFaces']==[11323,21253]
  reached=purely_geometric_reached(g['onePositiveDimensionalWitnessPerContactingBodyPair'],955)
  graphs.append(dict(mode=g['mode'],unqualifiedSeed=955,purelyGeometricReachable=reached,remainingBodies=sorted(set(range(1068))-set(reached)),noRootExposureOrRoleCredit=True))
  contactsets.append({tuple(p['bodies'])for p in g['onePositiveDimensionalWitnessPerContactingBodyPair']})
  endpoints=[]
  for uid,localface in [(UIDS[0],11323),(UIDS[1],6461)]:
   f=next(r for r in d['finiteRows']if r['uid']==uid and r['mode']==g['mode']);endpoints.append(dict(uid=uid,sourceFace=localface,completeFiniteRowVerbatim=f['allFaces'][localface]))
  crossrows.append(dict(mode=g['mode'],savedCrossInterfaceVerbatim=cross[0],completeEndpointFacetRowsVerbatim=endpoints))
 for f in d['finiteRows']:
  offset=0 if f['uid']==UIDS[0]else 14792
  for i in f['ordinaryUnprovedSourceFaces']:
   failures.append(dict(uid=f['uid'],mode=f['mode'],actorLocalOriginalFace=i,globalOriginalFace=offset+i,originalBody=body_members[offset+i],completeSavedFiniteRowVerbatim=f['allFaces'][i]))
 sourcepairs=contactsets[0];literalpairs=contactsets[1];common=set.intersection(*contactsets)
 assert len(sourcepairs-literalpairs)==67 and len(literalpairs-sourcepairs)==0 and len(common)==1288
 source_remaining=set(graphs[0]['remainingBodies']);literal_extra=set(graphs[1]['remainingBodies'])-source_remaining
 graphdifferences=dict(sourcePositivePairsLostInLiteral=[list(p)for p in sorted(sourcepairs-literalpairs)],literalNewPositivePairs=[],allFourWorldCommonPositivePairs=[list(p)for p in sorted(common)],sourceResidualBodies=sorted(source_remaining),additionalLiteralDisconnectedBodies=sorted(literal_extra),noAffineAssociationOrToleranceReinterpretation=True)
 ground=[np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3)for r in runtime];assert all(len(g)and np.isfinite(g).all()for g in ground)
 # Source topology display: complete undirected edge incidence, including
 # every recorded source facet. No shell closure or new connectivity credit.
 edges={}
 for i,face in enumerate(tri):
  for a,b in zip(face,np.roll(face,-1,axis=0)):edges.setdefault(tuple(sorted([tuple(a),tuple(b)])),[]).append(i)
 mainfaces=bodies[955]['globalOriginalFaces'];main_fail=[p['globalOriginalFace']for p in failures if p['mode']=='providerOriginal' and p['originalBody']==955]
 incident=set(main_fail)
 for i in main_fail:
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):incident.update(edges[tuple(sorted([tuple(a),tuple(b)]))])
 lower=min(tri[mainfaces,:,1].ravel());lower_ids=[i for i in mainfaces if lower in tri[i,:,1]]
 mainset=set(mainfaces)
 lower_edges=[dict(originalXYZ=[list(p)for p in edge],allOriginalFacetIncidences=ids)for edge,ids in edges.items()if edge[0][1]==lower and edge[1][1]==lower and set(ids)&mainset]
 # These are exact min-height nominations only, not a floor/function/rim/grade.
 seed_context=dict(body955=bodies[955],allFourWorldFailureRows=[p for p in failures if p['originalBody']==955],completeIncidentOriginalFaceIDs=sorted(incident),minimumOriginalVertexHeightHKPD=float(lower),completeMainOriginalFacetsIncidentToMinimumHeightVertices=lower_ids,completeMainMinimumHeightEdges=lower_edges,noGradeSeedClaim=True)
 DOC.mkdir(parents=True);images=[]
 def sheet(name,faceids,highlight,contextids,groundids,ground_actor,caption):
  pulse(True);arr=tri[faceids];lo=arr.min((0,1));hi=arr.max((0,1));pad=np.maximum((hi-lo)*.05,[.3,.3,.3]);bounds=np.asarray([lo-pad,hi+pad]);centre=(lo+hi)/2
  fig=plt.figure(figsize=(24,16),dpi=100)
  specs=[('isolated original plan',90,-90,False,False),('original X-Y',0,-90,False,False),('full named source-body context',22,-55,True,False),('same source plus captured ground',22,-55,True,True)]
  for n,(label,elev,azim,showcontext,showground)in enumerate(specs,1):
   ax=fig.add_subplot(2,2,n,projection='3d')
   def draw(a,color,alpha,lw):
    if len(a):ax.add_collection3d(Poly3DCollection((a-centre)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidths=lw))
   if showcontext:draw(tri[contextids],'#6689a7',.15,.12)
   if showground:draw(ground[ground_actor][groundids],'#7c8f79',.18,.12)
   draw(tri[faceids],'#2373a5',.32,.18);draw(tri[highlight],'#cf2937',.62,.6)
   display=(bounds-centre)[:,[0,2,1]];ax.set_xlim(display[:,0]);ax.set_ylim(display[:,1]);ax.set_zlim(display[:,2]);ax.set_box_aspect(display[1]-display[0]);ax.view_init(elev,azim)
   ax.set_xlabel('X relative to recorded centre X (m)');ax.set_ylabel('Z relative to recorded centre Z (m)');ax.set_zlabel('Y relative to recorded centre Y (m)');ax.set_title(label+'; absolute HKPD Y = plotted Y + '+repr(float(centre[1]))+'m')
  fig.suptitle(caption+'\nAll full source facets unchanged. Colours/opacity are diagnostic annotations only; no function, grade, root or browser claim.');fig.tight_layout(rect=[0,0,1,.94]);p=DOC/(name+'-2400x1600.png');fig.savefig(p);plt.close(fig)
  with Image.open(p)as exported:assert exported.size==(2400,1600);exported.verify()
  refs.append(ref(p));images.append(dict(image=ref(p),width=2400,height=1600,completeDisplayedOriginalFaceIDs=faceids,highlightedOriginalFaceIDs=highlight,contextOriginalFaceIDs=contextids,capturedGroundActorUID=UIDS[ground_actor],completeDisplayedGroundFacetIDs=groundids,diagnosticCentreOriginalXYZ=centre.tolist(),absoluteCropBounds=bounds.tolist(),absoluteHKPDYFromPlottedVertical='plotted Y + diagnosticCentreOriginalXYZ[1]',framingLimitations='Context/ground whole polygons can extend past crop axes and obscure annotations; isolated panels separately omit them.',sourceCoordinatesUnchanged=True,noRoleGradeRootClaim=True));pulse(True)
 sheet('podium955-full-main-and-local-ground',mainfaces,main_fail,list(range(14792,22523)),list(range(len(ground[1]))),1,'Original podium955: complete4019 facets; retained current coverage/burial failures red')
 sheet('podium955-isolated-failure-and-incident',sorted(incident),main_fail,mainfaces,list(range(len(ground[1]))),1,'Complete failed955 facets and exact original incident facets; saved finite witnesses bound separately')
 sheet('podium955-minimum-height-source-nominations',lower_ids,lower_ids,mainfaces,list(range(len(ground[1]))),1,'Original main955 facets touching its exact minimum vertex height; red is nomination only, no floor/rim/grade claim')
 tfaces=bodies[135]['globalOriginalFaces'];tfail=[p['globalOriginalFace']for p in failures if p['mode']=='providerOriginal' and p['originalBody']==135]
 sheet('tower135-own-main-and-interface',tfaces,tfail,[11323,21253],list(range(len(ground[0]))),0,'Original tower135: complete2084 facets; cross interfaceT11323/P6461 is contact evidence only')
 for uid in UIDS:
  members=[b for b in bodies if b['uid']==uid and b['body']in source_remaining];ids=[i for b in members for i in b['globalOriginalFaces']]
  if ids:sheet(('tower'if uid==UIDS[0]else'podium')+'-source-geometric-residual-family',ids,ids,[],[],0 if uid==UIDS[0]else 1,'Complete original '+uid+' source-geometric residual family; no role/function inference')
 for b in bodies:
  if b['body']in source_remaining and b['uid']==UIDS[1]:
   ids=b['globalOriginalFaces'];lo=tri[ids].min((0,1))-[3,3,3];hi=tri[ids].max((0,1))+[3,3,3];context=[i for i in mainfaces if np.all(tri[i].max(0)>=lo)and np.all(tri[i].min(0)<=hi)]
   sheet('podium-source-residual-body'+str(b['body']),ids,ids,context,[],1,'Complete original podium residual body'+str(b['body'])+'; nearby main955 facets are display context only')
 if literal_extra:
  ids=[i for b in bodies if b['body']in literal_extra for i in b['globalOriginalFaces']];sheet('literal-lost-route-source-context',ids,ids,[],[],0,'Original facets in additional literal disconnected bodies; exact67 missing pairs are retained, no weld/association claim')
 save(DOC/'main955-interface-and-residual-source-context.json.gz',dict(uids=UIDS,completeOriginalFaces=22523,fullOriginalBodyInventoryVerbatim=bodies,allFourWorldSavedFiniteFailures=failures,main955SeedContext=seed_context,allFourWorldCrossInterfaceRowsVerbatim=crossrows,unqualifiedGeometricGraphs=graphs,crossWorldLiteralDifferences=graphdifferences,sourceEntryAndProviderPoses=[dict(uid=r['uid'],entry=r['candidate']['entry'],completeOriginalPOSITIONProof=r['completeOriginalPOSITIONProof'])for r in selection],actualMatrixAttributeReceipt=ref(ATTRS/'actual-render-attributes.json.gz'),completeLocalGroundArraysVerbatim=[g.tolist()for g in ground],groundFacetIDsLocalToCapturedUnion=True,noPerFacetPatchIdentityAssumed=True,imageGeometryStream='providerOriginal',renderPackageVersions=dict(numpy=np.__version__,matplotlib=matplotlib.__version__),images=images,currentGroundReceipt=ref(PROBE/'result.json'),sourceGeometryChanges=0,gradeOrRootAccepted=False,newlyInstalled=0))
 refs.append(ref(DOC/'main955-interface-and-residual-source-context.json.gz'))
 for pin in refs:check(pin);pulse()
 assert ref(manifest)==start;pulse(True)
 spec=importlib.util.spec_from_file_location('yoho_context_freezer',FREEZER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'yoho-exact-main955-local-ground-interface-residual-source-context-v1',[check(p)for p in {(r['path'],r['sha256']):r for r in refs}.values()],dict(uids=UIDS,completeOriginalFaces=22523,main955Faces=4019,body135Faces=2084,images=images,noClearanceOrContactRecheck=True,noRootRoleGradeOrNativeAcceptance=True,currentAcceptance=False,newlyInstalled=0))

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();controlled=UIDS+RELATED[:2]
 claim=reservations.claim('yoho-main955-context-'+str(uuid.uuid4()),['building:'+u for u in controlled]+['terrain-patch:'+u for u in controlled]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
