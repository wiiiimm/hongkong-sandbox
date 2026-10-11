"""UNEXECUTED read-only full owned/current ground coverage and ordinary bounds.

No terrain construction. Existing retained pair witnesses remain verbatim.
Current drawn union is recaptured, including every intersecting terrain layer.
No clearance result supplies grade/root, architectural role or native approval.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired_verify
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-sparkle-complete-current-drawn-ground-finite-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PREVIOUS=BASE/'xl-terrain-recovery-20261012-sparkle-retained-literal-triangle-height-body-diagnostic-v1'
ATTR=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
V4=BASE/'xl-terrain-recovery-20261012-sparkle-authentic-retained-market-terrain-candidate-v4'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/242198:0','landsd/228000:0'];COUNTS=[12875,6806]
MODES=[('originalSource',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
JS='xl-terrain-recovery-20261012-sparkle-complete-current-drawn-ground-union-v1.mjs'
REUSE='xl-terrain-recovery-20261012-sparkle-authentic-retained-market-terrain-candidate-v4.py'
HELPERS=['exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py',
 'exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py',
 'exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v3_20261011.py',
 'exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py',
 'exact_original_triangle_pair_column_gap_20261010.py','exact_original_closed_projection_intersection_20261010.py',
 'sparkle_current_native_renderer_winding_20261011.py','literal_production_module_dependency_closure_20261010.mjs',
 'xl-popcorn-source-investigations-checkpoints-20261009.py']
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(pin):
 p=ROOT/pin['path'];assert p.is_file()and ref(p)==pin;return p
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def orientation(face):
 a,b,c=[[F(float(v))for v in p]for p in face];u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
 n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 return dict(exactUnnormalisedNormal=list(map(str,n)),orientation='zero'if not any(n)else'upward'if n[1]>0 else'downward'if n[1]<0 else'vertical')
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 refs=[ref(Path(__file__)),ref(HERE/JS),ref(HERE/REUSE),*[ref(HERE/p)for p in HELPERS]]
 assert ref(HERE/REUSE)['sha256']=='02182a7a60b21282c0c912587b3c8fd0fa29be7bc974b0c8d1124eb6e04d4b5a'
 reuse=module('sparkle_current_union_input_gates',REUSE);manifest=ROOT/'3d-viewer/city/data/manifest.json'
 start,current,rebind=reuse.current_rebind(manifest,refs);assert start['sha256']==CURRENT
 for folder,job in [(PREVIOUS,'4de6109e851ec83696fe8c40249e3abfa038e55a1f0e1232d295c2378af715d5'),
  (ATTR,'80b48d4b97a689b19e34ace263ab907be1f5ebaa7b7a7be57dda9892d656487c'),
  (V4,'200a782f35de4e5ecda340d0d2b6e6e31efaacbe39664329b13d235fa289927c')]:reuse.completed(folder,job,refs)
 prior=read(PREVIOUS/'diagnostic.json.gz');assert ref(PREVIOUS/'diagnostic.json.gz')['sha256']=='2f7b71630057d6f23bd9d942a98103b82da694594b6f51202c1adcb77c68ef51'
 assert prior['completeOwnedOriginalFaces']==19681 and prior['completeOriginalBodies']==25 and len(prior['originalZeroGlobalFaceIDsRetainedUncredited'])==150
 protected=read(V4/'whole-retained-collar-inputs.json.gz');raw_retained=np.asarray(protected['wholeRetainedLiteralXYZ'],float)
 assert raw_retained.shape==(3039,3,3)
 retained,winding=drawn_native_faces(dict(position=raw_retained.reshape(-1).tolist(),index=list(range(raw_retained.size//3))))
 inputs=read(ATTR/'literal-source-inputs.json.gz')['rows'];attrs=read(ATTR/'actual-render-attributes.json.gz')['rows']
 assert [r['uid']for r in inputs]==[r['uid']for r in attrs]==UIDS
 worlds={};bounds=[];position_proofs=[]
 for inp,a,uid,count in zip(inputs,attrs,UIDS,COUNTS):
  asset=ROOT/inp['path'];assert ref(asset)['sha256']==a['sourceSHA256'];refs.append(ref(asset));original=decode_original_world_triangles(asset.read_bytes())
  proof=packed_world_bounds(asset.read_bytes());assert proof['worldTrianglesSHA256']==digest(original.tobytes())and proof['completeOriginalTriangles']==count
  position_proofs.append(proof);bounds.append(np.asarray(proof['originalWholeSourceBounds'],float));idx=np.asarray(a['completeOriginalIndex'],int)
  assert idx.shape==(3*count,)and original.shape==(count,3,3)
  for mode,key in MODES:
   if key is None:world=original
   else:
    pos=np.asarray(a[key],float).reshape(-1,3);assert np.isfinite(pos).all()and idx.min()>=0 and idx.max()<len(pos)
    bounds.append(np.asarray([pos.min(0),pos.max(0)]));world=pos[idx].reshape(-1,3,3)
   binding=next(r for r in prior['allFourWorldBindings']if r['uid']==uid and r['mode']==mode)
   assert digest(world.tobytes())==binding['worldSHA256'];worlds[uid,mode]=world
 bounds.append(np.asarray([raw_retained.reshape(-1,3).min(0),raw_retained.reshape(-1,3).max(0)]))
 allbounds=np.asarray(bounds);lo=allbounds[:,0].min(0);hi=allbounds[:,1].max(0);capture=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1]
 for pin in refs:verify(pin)
 DOC.mkdir(parents=True);(DOC/'actual-current-manifest.json').write_bytes(manifest.read_bytes());save(DOC/'current-input-rebind.json',rebind)
 payload=dict(currentManifest=start,completeCaptureBounds=capture,currentCatalogueRefs=[ref(ROOT/'3d-viewer'/p)for p in current['officialModelCatalogues']],
  currentTileRefs=[ref(ROOT/'3d-viewer'/t['url'])for t in current['tiles']],evidenceRefs=list({r['path']:r for r in refs}.values()),
  completeOwnedOriginalPOSITIONProofs=position_proofs,allOwnedFourWorldsAndWholeRetainedLiteralGroundInside=True)
 save(DOC/'ground-union-inputs.json.gz',payload)
 subprocess.run(['node',str(HERE/JS),str((DOC/'ground-union-inputs.json.gz').relative_to(ROOT)),str((DOC/'actual-current-drawn-ground-union.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 captured=read(DOC/'actual-current-drawn-ground-union.json.gz');ground=np.asarray(captured['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert len(ground)==captured['completeCapturedDrawnTriangles']and digest(ground.tobytes())==captured['completeCapturedFloat64WorldSHA256']
 for path,sha in captured['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha;refs.append(ref(ROOT/path))
 # RAW triplets stay bound separately. This assertion uses ONLY the exact
 # current renderer's BC-swap, including signed-zero byte preservation.
 drawn_counts=Counter(f.tobytes()for f in ground);required=Counter(f.tobytes()for f in retained)
 assert all(drawn_counts[k]>=v for k,v in required.items()),'Current drawn union omits a complete protected retained facet'
 refs.extend(ref(p)for p in [DOC/'ground-union-inputs.json.gz',DOC/'actual-current-drawn-ground-union.json.gz',DOC/'actual-current-manifest.json',DOC/'current-input-rebind.json'])
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 # Quantify original frozen exact finite-column witnesses, not bounds-only
 # contacts, against the SAME ordinary -1/2m threshold. No contact is root.
 pair_rows=[]
 for row in prior['rows']:
  world=worlds[row['uid'],row['mode']]
  selected=[r for r in row['proof']['records']if r['classification']in ['finiteColumnHeightContact','sourceStrictlyBelowLiteralTerrain']]
  if row['uid']==UIDS[1]:assert Counter(r['classification']for r in selected)=={'finiteColumnHeightContact':268,'sourceStrictlyBelowLiteralTerrain':14}
  else:assert not selected
  for old in selected:
   h=old['height'];assert 'exactMinimumFiniteColumnGapM'in h and 'exactMaximumFiniteColumnGapM'in h
   pair_rows.append(dict(uid=row['uid'],mode=row['mode'],priorPairVerbatim=old,**orientation(world[old['actorLocalFaceID']]),
    unchangedOrdinaryLowerBoundM='-1/2',pairFiniteMinimumAtLeastOrdinaryBound=F(h['exactMinimumFiniteColumnGapM'])>=F(-1,2),
    notWholeFaceOrUnionAcceptance=True,noRootOrBridgeCredit=True))
 pulse(True);out=[];cache={};gsha=digest(ground.tobytes())
 for uid,count in zip(UIDS,COUNTS):
  for mode,_ in MODES:
   world=worlds[uid,mode];wsha=digest(world.tobytes());key=(wsha,gsha,digest(retained.tobytes()));reused=key in cache
   if reused:faces=cache[key];pulse(True)
   else:
    faces=[]
    for i,face in enumerate(world):
     coverage=exact_coverage(face,ground);retained_coverage=exact_coverage(face,retained);coarse=None;paired=None
     if coverage['exactProjectionCovered']:
      coarse=coarse_verify(face,ground)
      if not coarse['existingOrdinaryClearanceBoundProved']:paired=paired_verify(face,ground)
      proof=paired if paired is not None else coarse
      assert proof['sourceFaceSHA256']==digest(face.tobytes())and proof['completeCurrentGroundSHA256']==gsha
      assert proof['groundProjectionCovered']is True
     else:proof=None
     faces.append(dict(actorLocalFaceID=i,**orientation(face),completeCurrentUnionProjectionCoverage=coverage,
      completeLiteralRetainedProjectionCoverage=retained_coverage,rawCoarseProofVerbatim=coarse,rawPairedProofVerbatim=paired,
      currentUnionGroundProjectionCovered=coverage['exactProjectionCovered'],retainedGroundAloneCoversCompleteFace=retained_coverage['exactProjectionCovered'],
      existingOrdinaryClearanceBoundProved=False if proof is None else proof['existingOrdinaryClearanceBoundProved'],
      exactCertifiedLowerClearanceM=None if proof is None else proof['exactCertifiedLowerClearanceM'],
      uncoveredProjectionHasNoClearanceCredit=proof is None,noRootOrBridgeCredit=True));pulse()
     if i%100==0:save(LOCAL/(uid.replace('/','-').replace(':','-')+'-'+mode+'-partial.json.gz'),dict(worldSHA256=wsha,groundSHA256=gsha,allFaces=faces,complete=False));print(dict(uid=uid,mode=mode,faces=i,total=count),flush=True)
    cache[key]=faces
   assert len(faces)==count
   out.append(dict(uid=uid,mode=mode,completeWorldSHA256=wsha,completeOwnedFaces=count,allFaces=faces,reusedExactWorldAndCompleteGroundTuple=reused,
    uncoveredCurrentUnionFaces=[r['actorLocalFaceID']for r in faces if not r['currentUnionGroundProjectionCovered']],
    ordinaryUnprovedFaces=[r['actorLocalFaceID']for r in faces if not r['existingOrdinaryClearanceBoundProved']],
    retainedOnlyCoverageFaces=[r['actorLocalFaceID']for r in faces if r['retainedGroundAloneCoversCompleteFace']]));pulse(True)
 for pin in refs:verify(pin)
 assert ref(manifest)==start;pulse(True)
 result=dict(uids=UIDS,currentManifest=start,completeOwnedOriginalFaces=19681,completeOriginalBodies=25,
  originalZeroGlobalFaceIDsRetainedUncredited=prior['originalZeroGlobalFaceIDsRetainedUncredited'],
  completeCurrentDrawnUnionFaces=len(ground),completeCurrentDrawnUnionSHA256=gsha,wholeLiteralRetainedRawSHA256=digest(raw_retained.tobytes()),
  exactRetainedRawToDrawnWinding=winding,allProtectedRetainedTripletsPresentInActualUnion=True,
  contactAndBelowPairs=pair_rows,rows=out,ordinaryLowerBoundM='-1/2',sourceGeometryChanges=0,terrainChanges=0,
  noConstructionOrClipping=True,currentAcceptance=False,nativeReacceptance=False,noRoleRootOrBridgeCredit=True,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',result)
 freeze=module('sparkle_complete_current_union_freeze',HELPERS[-1]);freeze.freeze(BATCH,'sparkle-complete-current-drawn-ground-coverage-and-ordinary-finite-v1',
  [verify(r)for r in {r['path']:r for r in refs}.values()]+[DOC/'diagnostic.json.gz']+list(LOCAL.glob('*-partial.json.gz')),
  dict(uids=UIDS,completeOwnedOriginalFaces=19681,completeLabelledWorldRows=8,diagnosticOnly=True,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 resources=['building:'+u for u in UIDS+['landsd/113733:0','landsd/138091:0']]+['terrain-patch:'+u for u in UIDS+['landsd/113733:0','landsd/138091:0']]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('sparkle-full-current-union-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok']
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned','--current-manifest-sha',CURRENT],cwd=ROOT,check=True)
if __name__=='__main__':main()
