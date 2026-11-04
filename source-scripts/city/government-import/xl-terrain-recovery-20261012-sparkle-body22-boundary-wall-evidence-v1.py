"""UNEXECUTED: bounded low-patch topology and geometric wall/cap evidence only."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict, Counter, deque
import ast, importlib.util, json, subprocess, sys, time, uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from run import ROOT, HERE, read, save, digest, reservations, connect

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261012-sparkle-body22-boundary-wall-evidence-v1'
DOC = BASE/BATCH; LOCAL = HERE/'local'/BATCH; LEASE = LOCAL/'reservation.json'
METHOD = BASE/'government-xl-sparkle-body22-boundary-wall-evidence-method-draft-20261012/METHOD.md'
CONTEXT = BASE/'xl-terrain-recovery-20261012-sparkle-complete-original-current-ground-failure-context-v1'
FINITE = BASE/'xl-terrain-recovery-20261012-sparkle-complete-current-drawn-ground-finite-v1'
ISOLATED = BASE/'xl-terrain-recovery-20261012-sparkle-isolated-source-failure-witness-views-v1'
ATTR = BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
INTEGRATION = BASE/'government-xl-updated-code-integration-20261012/integration.json'
HISTORY = BASE/'government-xl-heya-before-installation-current-history-v1-20261011/root-actual-historical-input-contract.json'
PRIMARY = BASE/'government-xl-sparkle-isolated-source-witness-method-draft-20261012/primary'
FREEZER = HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT = '2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS = ['landsd/242198:0','landsd/228000:0','landsd/113733:0','landsd/138091:0']
MODES = ['originalSource','actualLiteral','explicitLeftAssociatedFloat32','explicitBalancedFloat32']
LOW = [2603,2604,2605,2608,2609,2613,2614,2615,2616,2617,2618]
JOBS = [(CONTEXT,'ea33291b60391b28e587650b6d60abc1817a9897650ee59737cea1285d15188f'),
 (FINITE,'8ea68d031e3c9ff45936804eb6440db7c2fcb4dd6630cf8876578f8522a57dc3'),
 (ISOLATED,'0228442996d157d789ff7b1ed69027bc48315fe1d6661176f24ff7d012a22c18'),
 (ATTR,'80b48d4b97a689b19e34ace263ab907be1f5ebaa7b7a7be57dda9892d656487c')]

def ref(p): return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def exact(pin):
 p=ROOT/pin['path']; assert p.is_file() and ref(p)==pin,pin
 return p
def module_closure():
 # Local Python dependencies are concrete files, pinned before kernel import.
 queue=[Path(__file__).resolve(),FREEZER,HERE/'original_bound_facet_wall_context_v3_20261010.py',
        HERE/'original_strict_clear_cap_wall_paths_20261009.py']; found={}
 roots=[HERE,HERE.parent/'shared-modelling']
 while queue:
  p=queue.pop();p=p.resolve()
  if str(p) in found:continue
  found[str(p)]=ref(p)
  for node in ast.walk(ast.parse(p.read_text())):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else
          [n.name for n in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    for root in roots:
     candidate=root/(name.replace('.','/')+'.py')
     if candidate.is_file():queue.append(candidate)
 return sorted(found.values(),key=lambda x:x['path'])

def edge_census(tri,bodyids):
 from exact_original_shell_intersections_20261009 import rational_face, cross, sub
 all_edges=defaultdict(set);low_edges=defaultdict(set);zero=[]
 for i,t in enumerate(tri):
  rational = rational_face(t)
  if not any(cross(sub(rational[1],rational[0]),sub(rational[2],rational[0]))):zero.append(i)
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   key=tuple(sorted((tuple(a),tuple(b))))
   if key[0]==key[1]:continue
   all_edges[key].add(i)
   if i in LOW:low_edges[key].add(i)
 boundary={k for k,v in low_edges.items() if len(v)==1};adj=defaultdict(set)
 for a,b in boundary:adj[a].add(b);adj[b].add(a)
 unseen=set(adj);groups=[]
 while unseen:
  seed=min(unseen);seen={seed};todo=deque([seed]);unseen.remove(seed)
  while todo:
   for vertex in adj[todo.popleft()]:
    if vertex not in seen:seen.add(vertex);unseen.discard(vertex);todo.append(vertex)
  groups.append(dict(vertices=[list(v) for v in sorted(seen)],
   edges=[[list(a),list(b)] for a,b in sorted(boundary) if a in seen],
   degreeInventory=[dict(vertex=list(v),degree=len(adj[v])) for v in sorted(seen)],
   allBoundaryVertexDegreesTwo=all(len(adj[v])==2 for v in seen),
   closedSimpleLoopCertified=False))
 return dict(completePodiumFaces=len(tri),completeBody22Faces=bodyids,namedLowFaces=LOW,
  completeEdgeRows=[dict(edge=[list(v) for v in k],lowFaceIDs=sorted(v),lowIncidence=len(v),
   allPodiumIncidentFaceIDs=sorted(all_edges[k]),outsideLowIncidentFaceIDs=sorted(all_edges[k]-set(LOW)),
   zeroFacetIncidentFaceIDs=sorted(all_edges[k]&set(zero)),
   globalOriginalFaceIDs=[12875+i for i in sorted(all_edges[k])]) for k,v in sorted(low_edges.items())],
  boundaryEdgeGroups=groups,branchOrNonmanifoldLowEdges=[dict(edge=[list(p) for p in k],faces=sorted(v)) for k,v in sorted(low_edges.items()) if len(v)>2],
  completePodiumZeroFacetIDsRetainedUncredited=zero,roleOrRootCredit=False)

def render_sheet(path,tri,faceids,incident,witnesses,ground,gids,with_ground):
 patch=tri[faceids];lo=patch.min((0,1));hi=patch.max((0,1));centre=(lo+hi)/2
 # Tight low-feature framing is only a camera crop, not source geometry clipping.
 pad=np.maximum((hi-lo)*.15,[.15,.15,.15]);bounds=np.asarray([lo-pad,hi+pad])
 fig=plt.figure(figsize=(24,16),dpi=100)
 for n,(label,elev,azim) in enumerate([('orthographic plan',90,-90),('orthographic X-Y',0,-90),
                                     ('orthographic Z-Y',0,0),('orthographic oblique',25,-50)],1):
  ax=fig.add_subplot(2,2,n,projection='3d');ax.set_proj_type('ortho')
  def draw(arr,color,alpha,lw):
   if len(arr):ax.add_collection3d(Poly3DCollection((arr-centre)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidths=lw))
  draw(tri[sorted(set(incident)-set(faceids))],'#507ca8',.08,.4)
  if with_ground:draw(ground[gids],'#37956c',.10,.3)
  draw(patch,'#d59100',.60,.8)
  if with_ground:
   for mode,color in zip(MODES,['#111111','#8a2be2','#007f66','#c83924']):
    points=[w['savedFiniteVertexVerbatim']['exactOriginalSourcePoint'] for w in witnesses if w['mode']==mode and w['actorLocalOriginalFace'] in faceids]
    if points:
     xyz=np.asarray([[float(F(x)) for x in q] for q in points])-centre
     ax.scatter(xyz[:,0],xyz[:,2],xyz[:,1],c=color,s=9,alpha=.7)
  display=(bounds-centre)[:,[0,2,1]]
  ax.set_xlim(display[:,0]);ax.set_ylim(display[:,1]);ax.set_zlim(display[:,2]);ax.set_box_aspect(np.maximum(display[1]-display[0],.01));ax.view_init(elev,azim)
  ax.set_xlabel('X relative to recorded centre X (m)');ax.set_ylabel('Z relative to recorded centre Z (m)');ax.set_zlabel('Y relative to recorded centre Y (m)')
  ax.set_title(label+'; absolute HKPD Y = plotted Y + '+repr(float(centre[1]))+' m')
 fig.suptitle('All 11 unchanged original low facets, body 22 / source annotations only\n'
  'Blue: complete incident facets (camera-clipped); green: saved ground nominations; no function, role, cap, grade or root certification')
 fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(path);plt.close(fig)
 with Image.open(path) as exported:assert exported.size==(2400,1600);exported.verify()
 return dict(image=ref(path),width=2400,height=1600,diagnosticCentreOriginalXYZ=centre.tolist(),
  absoluteCropBounds=bounds.tolist(),absoluteHKPDYFromPlottedVertical='plotted Y + diagnosticCentreOriginalXYZ[1]',
  projection='orthographic',completeLowFacetIDs=faceids,allIncidentFaceIDs=incident,
  drawnGroundFacetIDs=gids if with_ground else [],cameraCropNotCompleteActorVisibility=True,noRoleOrRootCredit=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists()
 refs=module_closure()+[ref(METHOD),ref(INTEGRATION),ref(HISTORY)]
 refs += [ref(METHOD.parent/name) for name in ['root-reviewed-before-exact-zero-correction.py.txt',
  'review-exact-zero-correction.diff','offline-schema-hash-preflight.json','wall-cap-adverse-validation.json','wall-cap-nonrendering-adverse-tests.log']]
 refs += read(METHOD.parent/'wall-cap-adverse-validation.json')['executedTests']
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;refs.append(start)
 archives={};resolutions=[];integration=read(INTEGRATION);historical=read(HISTORY)
 for r in integration['actualHistoricalVersions']:
  assert r['originalPath']==r['actualBefore']['path'] and r['archive']['sha256']==r['actualBefore']['sha256']
  exact(r['archive']);archives[r['originalPath'],r['actualBefore']['sha256']]=r['archive']
 assert ref(HISTORY)['sha256']=='27e12065a1de099b3d9d6530dc05d5e73462655d16622a309bb050292dae2589'
 assert historical['historicalOnly'] and not historical['hashAliasesOrSignatureOverrides']
 for r in historical['actualHistoricalBytes']:
  old=r['actualPreInstallationInput'];pin=r['unmodifiedHistoricalBytes']
  assert pin['sha256']==old['sha256'] and pin['path']==str((HISTORY.parent/'actual-bytes'/old['path']).relative_to(ROOT))
  exact(pin);archives[old['path'],old['sha256']]=pin
 def resolve(pin):
  p=ROOT/pin['path']
  if p.is_file() and ref(p)==pin:refs.append(pin);pulse();return p
  archive=archives.get((pin['path'],pin['sha256']));assert archive is not None,('unresolved historical bytes',pin)
  p=exact(archive);refs.append(archive);resolutions.append(dict(originalHistoricalPin=pin,actualArchive=archive,historicalOnly=True));pulse();return p
 for folder,job in JOBS:
  receipt=read(folder/'result.json');assert receipt['jobId']==job and receipt['newlyInstalled']==0
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
  for pin in receipt['evidenceRefs']:resolve(pin)
 present=[ref(ROOT/r['originalPath']) for r in integration['actualHistoricalVersions'] if r['originalPath'].endswith('.js')];refs+=present
 for name,sha in [('developer-the-sparkle-floor-plan.pdf','5889ea450e5f7e204d9612576885a66557e19f8ee0b5a7135f3f7ae40ec211a0'),
                  ('developer-ground-floor-page3.png','501056a928c37a9a13b459808eb3adb14a4e151aa863d34a035329253cbcc30b')]:
  pin=ref(PRIMARY/name);assert pin['sha256']==sha;refs.append(pin)
 d=read(CONTEXT/'diagnostic.json.gz');f=read(FINITE/'diagnostic.json.gz');g=read(CONTEXT/'complete-ground-facet-provenance.json.gz')
 isolated=read(ISOLATED/'isolated-source-witness-inspection.json.gz');attrs=read(ATTR/'actual-render-attributes.json.gz')
 pair=np.asarray(d['completePairOriginalWorld'],float);ground=np.asarray(g['completeActualGroundFaces'],float)
 assert pair.shape==(19681,3,3) and ground.shape==(3865,3,3)
 assert d['completeOriginalBodies']==25 and len(d['completeOriginalZeroGlobalFacesRetainedUncredited'])==150
 assert len(d['failureRows'])==920 and len(d['bodyWorldRows'])==100
 actual=next(r for r in attrs['rows'] if r['uid']==UIDS[1]);index=np.asarray(actual['completeOriginalIndex']).reshape(-1,3)
 assert actual['sourceSHA256']=='7429ad91552966b7e5ab6717626cb8e84d195da698140bcaf0b57ce890b89800' and index.shape==(6806,3)
 worlds={'originalSource':pair[12875:]}
 for mode,key in zip(MODES[1:],['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']):
  worlds[mode]=np.asarray(actual[key],float).reshape(-1,3)[index]
 # Module bytes are fenced before importing any geometric evidence kernels.
 for pin in refs:exact(pin)
 from original_bound_facet_wall_context_20261010 import canonical
 from original_bound_facet_wall_context_v3_20261010 import contexts
 from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
 DOC.mkdir(parents=True);rows=[];cache={}
 for mode in MODES:
  pulse(True);tri=worlds[mode];saved=next(r for r in f['rows'] if r['uid']==UIDS[1] and r['mode']==mode)
  assert saved['completeWorldSHA256']==digest(tri.tobytes()) and len(saved['allFaces'])==6806 and len(saved['ordinaryUnprovedFaces'])==230
  body=next(r for r in d['bodyWorldRows'] if r['mode']==mode and r['originalBody']==22)
  assert set(LOW)<=set(body['completeActorLocalFaces']) and len(body['completeActorLocalFaces'])==60
  for i in LOW:assert not saved['allFaces'][i]['existingOrdinaryClearanceBoundProved']
  normalized=[]
  for i,r in enumerate(saved['allFaces']):
   assert r['actorLocalFaceID']==i and r['currentUnionGroundProjectionCovered']
   coarse=r['rawCoarseProofVerbatim'];paired=r.get('rawPairedProofVerbatim')
   if paired is not None:paired=paired['sameConstraintOptimizedOrdinaryPrismProof']
   normalized.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=dict(sourceFace=i,completeOriginal=coarse),
    pairedExactOriginalFiniteBound=paired,completeOriginalBoundProved=r['existingOrdinaryClearanceBoundProved']))
  binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical(normalized))
  key=(binding['completeOriginalWorldTrianglesSHA256'],binding['completeDrawnGroundSHA256'],binding['completeFiniteFacetProofRowsSHA256'])
  reused=key in cache
  if not reused:
   ctx=contexts(tri,ground,normalized,expected_binding=binding,current_binding=binding)
   normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normal,axis=1)
   ratio=np.divide(normal[:,1],size,out=np.zeros(len(tri)),where=size>0)
   excluded=[i for i in range(len(tri)) if not saved['allFaces'][i]['existingOrdinaryClearanceBoundProved'] and (size[i]==0 or abs(ratio[i])>.25)]
   allowed=[i for i in range(len(tri)) if i not in set(excluded)]
   subset=tri[allowed];subsetctx=[dict(ctx[i],sourceFace=j) for j,i in enumerate(allowed)]
   capbinding=dict(completeOriginalWorldTrianglesSHA256=digest(subset.tobytes()),completeCurrentFacetContextsSHA256=canonical(subsetctx),exactOriginalContactListSHA256=canonical([]))
   paths=cap_paths(subset,subsetctx,[],expected_binding=capbinding,current_binding=capbinding)
   mapped=[dict(p,actorLocalOriginalFace=allowed[p['sourceFace']],globalOriginalFace=12875+allowed[p['sourceFace']],
      actorLocalOriginalPath=[allowed[j] for j in p['originalPath']],globalOriginalPath=[12875+allowed[j] for j in p['originalPath']]) for p in paths['paths']]
   cache[key]=dict(contexts=ctx,capSubsetProof=paths,subsetToActorLocalOriginalFace=allowed,
    excludedFailedNonWallFaceIDs=excluded,allMappedStrictCapPaths=mapped)
  proof=cache[key];assert [i for i,c in enumerate(proof['contexts']) if F(c['exactCertifiedLowerClearanceM'])<F(-1,2)]==saved['ordinaryUnprovedFaces']
  rows.append(dict(uid=UIDS[1],mode=mode,binding=binding,completeFiniteRowsVerbatimRef=ref(FINITE/'diagnostic.json.gz'),
   raw230OrdinaryFailures=saved['ordinaryUnprovedFaces'],lowPatchTopology=edge_census(tri,body['completeActorLocalFaces']),
   completePodiumFiniteContexts=proof['contexts'],strictCapEvidence=proof,identicalCompleteTupleReuse=reused,
   gradeSpanningCandidateFaceIDs=[i for i in saved['ordinaryUnprovedFaces'] if proof['contexts'][i]['maximumObservedGapM']>0],
   roleAccepted=False,groundRootCredit=False,installationApproved=False))
  save(DOC/('mode-'+mode+'-progress.json.gz'),rows[-1]);pulse(True)
 original=worlds['originalSource'];topology=rows[0]['lowPatchTopology']
 incident=sorted({i for r in topology['completeEdgeRows'] for i in r['allPodiumIncidentFaceIDs']})
 witness=isolated['savedFiniteWitnessesVerbatim'];gids=sorted({w['originalGroundFace'] for w in witness if w['actorLocalOriginalFace'] in LOW and w['body']==22})
 assert gids and all(0<=i<len(ground) for i in gids)
 images=[]
 for with_ground in [False,True]:
  pulse(True);path=DOC/('body22-low11-'+('saved-ground-witnesses' if with_ground else 'incident-source')+'-orthographic-2400x1600.png')
  images.append(render_sheet(path,original,LOW,incident,witness,ground,gids,with_ground));refs.append(ref(path))
 out=dict(uids=UIDS,completeOriginalOwnedFacets=19681,completeOriginalBodies=25,
  completeOriginalZeroGlobalFacetsRetainedUncredited=d['completeOriginalZeroGlobalFacesRetainedUncredited'],
  all920FailuresVerbatim=d['failureRows'],all100BodyWorldRowsVerbatim=d['bodyWorldRows'],rows=rows,images=images,
  savedGroundFacetProvenanceRef=ref(CONTEXT/'complete-ground-facet-provenance.json.gz'),
  completeActorContextImagesVerbatim=d['images'],previousPerspectiveSheetsVerbatim=isolated['images'],
  previousPerspectiveFramingLimitationPreserved=True,developerPlanRegistration=dict(proved=False,transform=None,
   developerPage=ref(PRIMARY/'developer-ground-floor-page3.png'),exactTiePoints=[],HKPDElevationEvidence=False,
   reason='No independently identified exact source-to-plan tie points or vertical datum; no appearance-based feature assignment.'),
  originalSourceGeometryChanges=0,terrainChanges=0,currentRuntimeAcceptance=False,roleAcceptance=False,rootOrBridgeCredit=False,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',out)
 save(DOC/'historical-resolution-and-present-module-bindings.json',dict(exactHistoricalResolutions=resolutions,presentModulesNotUsedAsHistoricalRuntimeProof=present))
 refs += [ref(DOC/'diagnostic.json.gz'),ref(DOC/'historical-resolution-and-present-module-bindings.json')]
 refs=list({(p['path'],p['sha256']):p for p in refs}.values())
 for pin in refs:exact(pin)
 assert ref(manifest)==start;pulse(True)
 spec=importlib.util.spec_from_file_location('sparkle_body22_wall_freezer',FREEZER);freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
 freezer.freeze(BATCH,'sparkle-body22-boundary-wall-evidence-v1',[exact(p) for p in refs],dict(uids=UIDS,
  completeOriginalOwnedFacets=19681,completeOriginalBodies=25,originalZeroFacetsRetainedUncredited=150,
  failedFaceWorldRows=920,bodyWorldRows=100,lowFacets=11,arithmeticWorlds=4,images=2,
  sourceOnly=True,currentRuntimeAcceptance=False,noRoleRootBridgeOrNativeAcceptance=True,newlyInstalled=0))

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 resources=['building:'+u for u in UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('sparkle-body22-evidence-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
 assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),
  '--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
