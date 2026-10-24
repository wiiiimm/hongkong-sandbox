"""UNEXECUTED source/current hole routing and bounded main955 diagnostic.

No production terrain candidate, geometry/pose edit, or acceptance credit.
Exact planar subtraction/lifting and wall/grade kernels are unchanged.
"""
from pathlib import Path
from fractions import Fraction as F
import ast,importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_projection_coverage_v2_20261010 import point,subtract,signed_area,clip
from exact_source_planar_domain_recovery_seams_v1_20261011 import source_height,overlap_interval
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_bound_facet_wall_context_20261010 import canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment_exposure
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-yoho-source-holes-preserved-routing-main955-wall-cap-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PRIOR=BASE/'xl-terrain-recovery-20261012-yoho-untouched-sheets-parent-mask-failures-v1'
PROBE=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
ATTRS=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-attributes-v1'
CONTEXT=BASE/'xl-terrain-recovery-20261012-yoho-main955-ground-residual-context-v1'
METHOD=BASE/'government-xl-yoho-source-holes-preserved-routing-main955-method-draft-20261012/METHOD.md'
PREFLIGHT=METHOD.parent/'unexecuted-schema-syntax-pin-check.json'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/146396:0','landsd/231756:0'];MODES=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert p.is_file()and ref(p)==pin,pin;return p
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def closure():
 todo=[Path(__file__),FREEZER];out={}
 while todo:
  p=todo.pop().resolve()
  if str(p)in out:continue
  out[str(p)]=ref(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for folder in[HERE,HERE.parent/'shared-modelling']:
     q=folder/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return list(out.values())
def poly(face):return [point(p)for p in face[:,[0,2]]]
def orient(p):return list(reversed(p))if signed_area(p)<0 else p
def encode(p):return [[str(x)for x in v]for v in p]
def routing(authentic,current,attribution,pulse):
 """Subtract authentic projected union from each complete current ROI facet.

 Retained polygons are lifted ONLY on the exact original current facet plane.
 All authentic original triplets and collapsed current facets stay unchanged.
 This private diagnostic union is not a production terrain asset.
 """
 axz=authentic[:,:,[0,2]];amin=axz.min(1);amax=axz.max(1)
 projected=[poly(t)for t in authentic];nonzero=[i for i,p in enumerate(projected)if signed_area(p)!=0]
 owners={}
 for s in attribution['completeAttributedSources']:
  assert len(s['allSelectedMeshFaceIDs'])==len(s['completeSelectedDrawnTriplets'])
  for f,t in zip(s['allSelectedMeshFaceIDs'],s['completeSelectedDrawnTriplets']):
   owners.setdefault(tuple(t),[]).append(dict(sourcePath=s['sourcePath'],lineage=s['lineage'],meshName=s['meshName'],actualMeshFace=f))
 remaining_owners={k:list(v)for k,v in owners.items()};new=list(authentic);records=[];seams=[]
 for ci,t in enumerate(current):
  key=tuple(t.reshape(-1));assert key in remaining_owners and remaining_owners[key];origin=remaining_owners[key].pop(0)
  p=poly(t);area=abs(signed_area(p));lo=t[:,[0,2]].min(0);hi=t[:,[0,2]].max(0)
  candidates=[int(i)for i in np.flatnonzero(np.all(amax>=lo,axis=1)&np.all(amin<=hi,axis=1))if i in nonzero]
  if not area:
   new.append(t.copy());records.append(dict(currentCapturedFace=ci,provenance=origin,collapsedProjectionRetainedVerbatim=True,originalCurrentTriplet=t.tolist(),sourceCandidateFacets=candidates));pulse();continue
  pieces=[orient(p)]
  for ai in candidates:
   pieces=[q for old in pieces for q in subtract(old,projected[ai])]
   if not pieces:break
  kept=sum(abs(signed_area(q))for q in pieces);assert F(0)<=kept<=area
  exact_pieces=[];packed=[]
  for q in pieces:
   # Independently verify every retained polygon has no positive-area source overlap.
   for ai in candidates:
    inside=q
    for a,b in zip(orient(projected[ai]),orient(projected[ai])[1:]+orient(projected[ai])[:1]):inside=clip(inside,a,b,True)
    assert signed_area(inside)==0,'Retained current polygon overlaps authentic source interior'
   xyz=[(x,source_height(t,(x,z)),z)for x,z in q];exact_pieces.append(encode(xyz))
   if len(pieces)==1 and kept==area and set(q)==set(p):
    triangles=[t.copy()] # Preserve literal untouched triangle bytes/winding.
   else:
    triangles=[np.asarray([[float(v)for v in xyz[j]]for j in[0,n,n+1]],float)for n in range(1,len(xyz)-1)]
   start=len(new);new.extend(triangles);packed.extend(range(start,len(new)))
   for a,b in zip(q,q[1:]+q[:1]):
    for ai in candidates:
     ap=projected[ai]
     for c,d in zip(ap,ap[1:]+ap[:1]):
      iv=overlap_interval(a,b,c,d)
      if iv is None:continue
      ends=[tuple(a[k]+s*(b[k]-a[k])for k in[0,1])for s in iv]
      gaps=[source_height(authentic[ai],v)-source_height(t,v)for v in ends]
      seams.append(dict(currentCapturedFace=ci,originalSheetROIFacet=ai,exactInterval=list(map(str,iv)),exactProjectedEndpoints=encode(ends),exactSourceMinusCurrentHeightM=list(map(str,gaps)),exactHeightCompatible=all(g==0 for g in gaps)))
  records.append(dict(currentCapturedFace=ci,provenance=origin,originalCurrentTriplet=t.tolist(),exactOriginalProjectedAreaM2=str(area),exactRetainedProjectedAreaM2=str(kept),exactReplacedByAuthenticatedAreaM2=str(area-kept),exactRetainedSourcePlanarPolygons=exact_pieces,packedRoutedFacetIDs=packed,sourceCandidateFacets=candidates,packingOnlyFloat64=True,noClaimPackedBoundaryEqualsRationalBoundary=True));pulse()
 assert all(not v for v in remaining_owners.values()),'Missing complete current provenance'
 return np.asarray(new,float),dict(completeAuthenticROIFacets=len(authentic),authenticTripletsVerbatim=True,completeCurrentCapturedFacets=len(current),allCurrentFacetRecords=records,allExactPositiveDimensionalSeams=seams,allEnumeratedSeamsHeightCompatible=all(s['exactHeightCompatible']for s in seams),packedGroundSHA256=digest(np.asarray(new,float).tobytes()),productionTerrainCandidate=False,exactBoundaryCoverageCertificate=False,realRuntimeValidatorPassed=False)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic();refs=closure()+[ref(METHOD),ref(PREFLIGHT)]+[ref(p)for p in sorted(METHOD.parent.rglob('*'))if p.is_file()and p not in[METHOD,PREFLIGHT]]
 pre=read(PREFLIGHT);assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['method']==ref(METHOD)
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 for folder in[PRIOR,PROBE,ATTRS,CONTEXT]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
  for pin in r['evidenceRefs']:check(pin);refs.append(pin);pulse()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;refs.append(start)
 d=read(PRIOR/'untouched-sheets-versus-actual-parent-failures.json.gz');assert sum(s['completeSourceFaces']for s in d['wholeSourceSheetInventory'])==74137
 attr=read(PRIOR/'actual-parent-mask-attribution.json.gz')
 for p,h in attr['inputHashes'].items():pin=dict(path=p,sha256=h);check(pin);refs.append(pin)
 currentrow=next(r for r in attr['rows']if r['uid']==UIDS[1]);current=np.asarray(currentrow['completeActualDrawnTriplets'],float).reshape(-1,3,3);assert len(current)==1696
 roi=read(PRIOR/'1-all-slope-degenerate-original-sheet-ROI.json.gz');authentic=np.asarray(roi['allRetainedOriginalTriplets'],float);assert len(authentic)==2303 and roi['completeSourceSheetFaces']==74137
 assert len(roi['selectedOriginalSheetFaceIDs'])+roi['strictlyDisjointSourceSheetFaces']==74137 and digest(authentic.tobytes())==roi['completeROIWorldSHA256']
 selected=read(PROBE/'selection.json.gz')['rows'];a=read(ATTRS/'actual-render-attributes.json.gz')['rows'][1];assert selected[1]['uid']==a['uid']==UIDS[1]
 source=ROOT/selected[1]['candidate']['path'];assert ref(source)['sha256']==a['sourceSHA256'];refs.append(ref(source));index=np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3);assert len(index)==7731
 ws=[decode_original_world_triangles(source.read_bytes())]+[np.asarray(a[k],float).reshape(-1,3)[index]for k in['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']]
 ctx=read(CONTEXT/'main955-interface-and-residual-source-context.json.gz');body=next(b for b in ctx['fullOriginalBodyInventoryVerbatim']if b['body']==955);ids=[int(i)-14792 for i in body['globalOriginalFaces']];assert len(ids)==4019 and all(i>=0 for i in ids)and {6810,6814,6815}<=set(ids)
 # Re-derive entire routing domain from actual base georef and all unused bounds.
 base=read(ROOT/'3d-viewer/city/data/terrain.json');parent=read(ROOT/'3d-viewer/city/data/government-native-121143-0.json');g=base['meta']['georef'];pg=parent['meta']['georef']
 bounds=[b for r in attr['rows']for b in r['completeFourWorldUnusedBounds']];xmin=min(b[0][0]for b in bounds);xmax=max(b[1][0]for b in bounds);zmin=min(b[0][2]for b in bounds);zmax=max(b[1][2]for b in bounds)
 xnode=lambda x:(F(float(x))+F(834500)-F(g['bE']))/F(g['aE']);znode=lambda z:(F(816500)-F(float(z))-F(g['bN']))/F(g['aN'])
 floor=lambda v:v.numerator//v.denominator;ceil=lambda v:-floor(-v)
 nominated=[floor(xnode(xmin)),floor(znode(zmin)),ceil(xnode(xmax)),ceil(znode(zmax))];old=parent['coarseCells'];domain=[min(old[0],nominated[0]),min(old[1],nominated[1]),max(old[2],nominated[2]),max(old[3],nominated[3])]
 assert old==[310,204,313,206]and domain==[310,203,313,207]
 pextent=[pg['bE']-834500,816500-pg['bN'],pg['bE']+pg['aE']*(pg['W']-1)-834500,816500-(pg['bN']+pg['aN']*(pg['H']-1))]
 assert pextent==[-12767.5,-17187.5,-12557.5,-17047.5]
 DOC.mkdir(parents=True);ground,routes=routing(authentic,current,currentrow,pulse)
 save(DOC/'source-hole-routing-diagnostic.json.gz',dict(wholeOriginalSheetInventory=d['wholeSourceSheetInventory'],completeSourceSheetFaces=74137,selectedOriginalSheetFacetIDs=roi['selectedOriginalSheetFaceIDs'],strictlyDisjointOriginalSourceFacets=roi['strictlyDisjointSourceSheetFaces'],originalAuthenticROITripletsVerbatim=authentic.tolist(),proposedDiagnosticGround=ground.tolist(),routing=routes,actualParent=ref(ROOT/'3d-viewer/city/data/government-native-121143-0.json'),completeUnusedFourWorldBounds=bounds,rederivedCoarseDomain=domain,currentBurialAndCoverageFailuresVerbatim=d['rows'],productionCandidate=False,newlyInstalled=0));refs.append(ref(DOC/'source-hole-routing-diagnostic.json.gz'))
 rows=[];cache={}
 for mode,w in zip(MODES,ws):
  assert digest(w.tobytes())==next(r['completeWorldSHA256']for r in d['rows']if r['uid']==UIDS[1]and r['mode']==mode)
  main=w[ids];key=(digest(main.tobytes()),digest(ground.tobytes()));reused=key in cache
  if not reused:
   proofs=[]
   for j,t in enumerate(main):
    c=coarse(t,ground);p=None if c['existingOrdinaryClearanceBoundProved']else paired(t,ground);final=c if p is None else p
    proofs.append(dict(sourceFace=j,actorLocalOriginalFace=ids[j],priorCoarseBoundProofVerbatim=dict(sourceFace=j,completeOriginal=c),pairedExactOriginalFiniteBound=p,completeOriginalBoundProved=final['existingOrdinaryClearanceBoundProved'],groundProjectionCovered=final['groundProjectionCovered']));pulse()
    if j%100==0:save(LOCAL/(mode+'-finite-progress.json.gz'),dict(complete=False,main955OriginalIDs=ids,worldSHA256=key[0],groundSHA256=key[1],rows=proofs))
   uncovered=[r['actorLocalOriginalFace']for r in proofs if not r['groundProjectionCovered']];context_rows=None;cap=None;blocked=None
   if uncovered:blocked=dict(reason='Existing full wall-context kernel requires complete finite coverage',actorLocalOriginalUncoveredFaces=uncovered)
   else:
    binding=dict(completeOriginalWorldTrianglesSHA256=key[0],completeDrawnGroundSHA256=key[1],completeFiniteFacetProofRowsSHA256=canonical(proofs));context_rows=contexts(main,ground,proofs,expected_binding=binding,current_binding=binding)
    cb=dict(completeOriginalWorldTrianglesSHA256=key[0],completeCurrentFacetContextsSHA256=canonical(context_rows),exactOriginalContactListSHA256=canonical([]))
    try:cap=cap_paths(main,context_rows,[],expected_binding=cb,current_binding=cb)
    except AssertionError as e:blocked=dict(reason='Unchanged complete cap kernel rejected the main-body context',assertion=str(e))
   links=[]
   for f,h in[(6815,6814),(6814,6810)]:
    common=sorted(set(map(tuple,w[f]))&set(map(tuple,w[h])))
    if len(common)!=2:links.append(dict(actorLocalOriginalFaces=[f,h],completeExactSharedEdge=False,actualCommonVertices=common));continue
    links.append(dict(actorLocalOriginalFaces=[f,h],completeExactSharedEdge=True,fullSharedEdgeFiniteExposure=segment_exposure([[str(F(float(v)))for v in p]for p in common],ground)))
   eligible=[j for j,t in enumerate(main)if all(np.any(t[0]!=t[k])for k in[1,2])]
   # Kernel preserves its own positive-area ground nomination; exact source zeros are skipped explicitly.
   def nonzero(t):
    q=[[F(float(v))for v in p]for p in t];u=[q[1][k]-q[0][k]for k in range(3)];v=[q[2][k]-q[0][k]for k in range(3)];return any(u[(k+1)%3]*v[(k+2)%3]!=u[(k+2)%3]*v[(k+1)%3]for k in range(3))
   eligible=[j for j in eligible if nonzero(main[j])];zero=[j for j in range(len(main))if not nonzero(main[j])]
   grade=exact_upper_ground_interfaces(main,eligible,ground);pulse(True)
   cache[key]=dict(completeMain955OriginalIDs=ids,completeFiniteRows=proofs,completeMainContexts=context_rows,completeCapPaths=cap,unchangedKernelBlockedReason=blocked,nominatedTwoWallSharedEdges=links,genuineUpperGroundInterfaces=grade,exactZeroSourceLocalIDs=zero,qualifiedMainSeed=False,actualCurrentGround=False,groundIsPrivateProposedRoutingDiagnostic=True)
  rows.append(dict(uid=UIDS[1],mode=mode,completeMainWorldSHA256=key[0],completeProposedDiagnosticGroundSHA256=key[1],exactTupleReuse=reused,**cache[key]));pulse(True)
 save(DOC/'four-world-main955-wall-cap-grade-diagnostic.json.gz',dict(uids=UIDS,rows=rows,wholePairFaces=22523,wholePairBodies=1068,allPairObligationsRemain=True,currentAcceptance=False,sourceGeometryChanges=0,productionTerrainCandidate=False,newlyInstalled=0));refs.append(ref(DOC/'four-world-main955-wall-cap-grade-diagnostic.json.gz'))
 for pin in refs:check(pin);pulse()
 assert ref(manifest)==start;pulse(True)
 module('yoho_hole_routing_freezer',FREEZER).freeze(BATCH,'yoho-exact-source-hole-current-ground-routing-and-bounded-main955-wall-cap-diagnostic-v1',[check(p)for p in{(p['path'],p['sha256']):p for p in refs}.values()],dict(uids=UIDS,currentAcceptance=False,productionTerrainCandidate=False,newlyInstalled=0,completeOriginalSheetFaces=74137,completeMain955Faces=4019))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();controlled=UIDS+['landsd/121143:0','landsd/55568:0'];claim=reservations.claim('yoho-source-hole-route-'+str(uuid.uuid4()),['building:'+u for u in controlled]+['terrain-patch:'+u for u in controlled]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
