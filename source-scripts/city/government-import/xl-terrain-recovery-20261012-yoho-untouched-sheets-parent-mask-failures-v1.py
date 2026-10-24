"""UNEXECUTED: source-sheet versus actual masked-ground failure attribution only."""
from pathlib import Path
import ast,importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-yoho-untouched-sheets-parent-mask-failures-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PROBE=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
ATTRS=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-attributes-v1'
FINITE=BASE/'xl-terrain-recovery-20261012-yoho-eight-pair-four-stream-finite-edge-interfaces-v1'
CONTEXT=BASE/'xl-terrain-recovery-20261012-yoho-main955-ground-residual-context-v1'
TIN=BASE/'government-xl-yoho-original-pair-source-tin-context-20261010'
METHOD=BASE/'government-xl-yoho-untouched-sheets-parent-mask-method-draft-20261012/METHOD.md'
PREFLIGHT=METHOD.parent/'unexecuted-schema-syntax-source-pin-check.json'
JS=HERE/'xl-terrain-recovery-20261012-yoho-current-parent-mask-attribution-v1.mjs'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
UIDS=['landsd/146396:0','landsd/231756:0'];COUNTS=[14792,7731]
MODES=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(p):
 q=ROOT/p['path'];assert q.is_file()and ref(q)==p,p
 return q
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def closure():
 todo=[Path(__file__),FREEZER,HERE/'pending-context.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_paired_finite_clearance_v3_20261011.py',HERE/'exact_packed_world_geometry_20261009.py'];out={}
 while todo:
  p=todo.pop().resolve()
  if str(p)in out:continue
  out[str(p)]=ref(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else [x.name for x in n.names]if isinstance(n,ast.Import)else []
   for name in names:
    for folder in [HERE,HERE.parent/'shared-modelling']:
     q=folder/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return list(out.values())
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic();refs=closure()+[ref(JS),ref(METHOD)]
 pre=read(PREFLIGHT);assert pre['passed']and pre['noWorkerImportDBLeaseOrGeometryDecode']and pre['caller']==ref(Path(__file__))and pre['exporter']==ref(JS)and pre['method']==ref(METHOD)
 refs.append(ref(PREFLIGHT));refs.extend(ref(p)for p in sorted((METHOD.parent/'before-base-hydro-applicability-correction').rglob('*'))if p.is_file())
 for name,sha in [('exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579'),('dependency-closure-vendor/acorn-8.8.1/acorn.mjs','a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55')]:
  pin=ref(HERE/name);assert pin['sha256']==sha;refs.append(pin)
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 for folder in [PROBE,ATTRS,FINITE,CONTEXT]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for pin in r['evidenceRefs']:check(pin);refs.append(pin);pulse()
  refs.append(ref(folder/'result.json'))
 old=read(TIN/'result.json');assert old['jobId']=='631991793b8923c29e640029aa4fa8b2aaa00aff7659e3775ac172bb858002cf'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 refs += [ref(TIN/'result.json'),ref(TIN/'complete-original-source-tin.json.gz')]
 source=read(TIN/'complete-original-source-tin.json.gz')
 for p,h in source['sourceFileHashes'].items():pin=dict(path=p,sha256=h);check(pin);refs.append(pin)
 assert sorted(r['sheet']for r in source['completeSourceReceipts'])==['6-NW-10D','6-NW-15B']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;refs.append(start)
 selection=read(PROBE/'selection.json.gz')['rows'];actual=read(ATTRS/'actual-render-attributes.json.gz')['rows'];d=read(FINITE/'diagnostic.json.gz');assert [r['uid']for r in selection]==[r['uid']for r in actual]==UIDS
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
 from exact_original_paired_finite_clearance_v3_20261011 import verify as paired
 source_decoder=module('yoho_untouched_source_decoder',HERE/'pending-context.py')
 # Direct triangles() only; no historical repair/filter/source_sheet fallback.
 sheets=[];sheet_inventory=[]
 for receipt in source['completeSourceReceipts']:
  for f in receipt['terrainFiles']:
   if not f['name'].endswith('.gltf'):continue
   path=ROOT/receipt['cache']/'terrain'/f['name'];assert ref(path)['sha256']==f['sha256']
   t=source_decoder.triangles(path);assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all();pulse(True)
   sheets.append(t);sheet_inventory.append(dict(sheet=receipt['sheet'],sourceGltf=ref(path),completeSourceFaces=len(t),completeSourceWorldSHA256=digest(t.tobytes()),completeSourceWorldBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],noSlopeAreaOrDegenerateFilter=True))
 fullsource=np.concatenate(sheets);assert len(fullsource);inputs=[];worlds=[]
 for k,(row,a)in enumerate(zip(selection,actual)):
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']==a['sourceSHA256'];refs.append(ref(asset));index=np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3);assert len(index)==COUNTS[k]
  ws=[decode_original_world_triangles(asset.read_bytes()),np.asarray(a['completeLiteralWorldPosition'],float).reshape(-1,3)[index],np.asarray(a['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3)[index],np.asarray(a['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)[index]];worlds.append(ws)
  lo,hi=np.asarray(row['candidate']['entry']['worldBounds']);bounds=[float(lo[0]-1),float(lo[2]-1),float(hi[0]+1),float(hi[2]+1)]
  scope=[row['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],a['completeLiteralWorldBounds'],a['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],a['completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
  assert all(b[0][0]>=bounds[0]and b[0][2]>=bounds[1]and b[1][0]<=bounds[2]and b[1][2]<=bounds[3]for b in scope)
  assert all(w.shape==(COUNTS[k],3,3)and digest(w.tobytes())==next(f['completeWorldSHA256']for f in d['finiteRows']if f['uid']==row['uid']and f['mode']==mode)for mode,w in zip(MODES,ws))
  inputs.append(dict(uid=row['uid'],closedCaptureBounds=bounds,completeFourWorldUnusedBounds=scope))
 DOC.mkdir(parents=True);save(DOC/'input.json.gz',dict(rows=inputs,currentManifestSHA256=CURRENT,capturedRuntimePath=str((HERE/'local'/PROBE.name/'runtime-geometry.json.gz').relative_to(ROOT)),noTerrainProposal=True))
 refs.append(ref(DOC/'input.json.gz'));subprocess.run(['node',str(JS),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);pulse(True)
 provenance=read(DOC/'actual-parent-mask-attribution.json.gz');refs.append(ref(DOC/'actual-parent-mask-attribution.json.gz'))
 for p,h in provenance['inputHashes'].items():pin=dict(path=p,sha256=h);check(pin);refs.append(pin)
 output=[];cache={}
 for k,row in enumerate(selection):
  # Strictly disjoint whole-sheet facets alone may be omitted from this ROI.
  bounds=inputs[k]['closedCaptureBounds'];xz=fullsource[:,:,[0,2]];keep=np.flatnonzero((xz.max(1)[:,0]>=bounds[0])&(xz.min(1)[:,0]<=bounds[2])&(xz.max(1)[:,1]>=bounds[1])&(xz.min(1)[:,1]<=bounds[3]));ground=fullsource[keep];assert len(ground)
  save(DOC/(str(k)+'-all-slope-degenerate-original-sheet-ROI.json.gz'),dict(completeSourceSheetFaces=len(fullsource),selectedOriginalSheetFaceIDs=keep.tolist(),strictlyDisjointSourceSheetFaces=len(fullsource)-len(keep),allRetainedOriginalTriplets=ground.tolist(),completeROIWorldSHA256=digest(ground.tobytes()),noSlopeAreaOrDegenerateFilter=True));refs.append(ref(DOC/(str(k)+'-all-slope-degenerate-original-sheet-ROI.json.gz')))
  for mode,w in zip(MODES,worlds[k]):
   saved=next(f for f in d['finiteRows']if f['uid']==row['uid']and f['mode']==mode);ids=saved['ordinaryUnprovedSourceFaces'];key=(row['uid'],digest(w.tobytes()),digest(ground.tobytes()),tuple(ids));reused=key in cache
   if reused:proofs=cache[key]
   else:
    proofs=[]
    for i in ids:
     first=coarse(w[i],ground);exact=None if first['existingOrdinaryClearanceBoundProved']else paired(w[i],ground);final=first if exact is None else exact
     assert final['sourceFaceSHA256']==digest(w[i].tobytes())and final['completeCurrentGroundSHA256']==digest(ground.tobytes())
     proofs.append(dict(sourceFace=i,untouchedSourceSheetCoarseProof=first,untouchedSourceSheetPairedFallback=exact,untouchedSourceSheetProjectionCovered=final['groundProjectionCovered'],untouchedSourceSheetOrdinaryBoundProved=final['existingOrdinaryClearanceBoundProved']))
     pulse();
     if len(proofs)%20==0:save(LOCAL/(str(k)+'-'+mode+'-progress.json.gz'),dict(complete=False,allRows=proofs,binding=dict(key=[row['uid'],key[1],key[2],list(ids)],caller=ref(Path(__file__)))))
    cache[key]=proofs
   output.append(dict(uid=row['uid'],mode=mode,completeWorldSHA256=key[1],completeSourceSheetROIWorldSHA256=key[2],completeCurrentUncoveredFaces=saved['uncoveredSourceFaces'],completeCurrentCoveredOrdinaryFailureFaces=sorted(set(ids)-set(saved['uncoveredSourceFaces'])),completeSavedCurrentFailureRowsVerbatim=[saved['allFaces'][i]for i in ids],newUntouchedSourceSheetProofs=proofs,exactImmutableTupleReuse=reused,noCurrentSourceSheetSubstitutionOrGradeCredit=True));pulse(True)
 save(DOC/'untouched-sheets-versus-actual-parent-failures.json.gz',dict(uids=UIDS,completeOriginalFaces=22523,completeOriginalBodyCount=1068,wholeSourceSheetInventory=sheet_inventory,rows=output,currentParentAttribution=ref(DOC/'actual-parent-mask-attribution.json.gz'),historicalFilteredSheetArrayNotReused=True,allCurrentFailuresRetained=True,noTerrainProposal=True,noRootRoleNativeOrCurrentAcceptance=True,newlyInstalled=0));refs.append(ref(DOC/'untouched-sheets-versus-actual-parent-failures.json.gz'))
 for pin in refs:check(pin);pulse()
 assert ref(manifest)==start;pulse(True)
 m=module('yoho_source_attribution_freezer',FREEZER);m.freeze(BATCH,'yoho-untouched-government-sheets-versus-current-parent-mask-failure-diagnostic-v1',[check(p)for p in {(r['path'],r['sha256']):r for r in refs}.values()],dict(uids=UIDS,completeOriginalFaces=22523,allOriginalCurrentFailureRowsPreserved=True,noTerrainConstruction=True,currentAcceptance=False,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();controlled=UIDS+['landsd/121143:0','landsd/55568:0']
 claim=reservations.claim('yoho-sheet-parent-attribution-'+str(uuid.uuid4()),['building:'+u for u in controlled]+['terrain-patch:'+u for u in controlled]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
