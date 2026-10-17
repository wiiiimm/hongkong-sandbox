"""Separate explicitly changed terrain proposal preserving a disjoint current actor.

Reuses the frozen v2 numerical candidate, never rewrites it. All seventeen
current forms and the named source identity remain independently checked. The
original school geometry and all downward/base/root negatives remain intact.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid,shutil,copy
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_post_elements_current_bound_wing_extension_identity_v3_20261011 import verify_files,UID,SOURCE_SHA
from exact_cell_replay_with_original_routed_callable_20261011 import verify_files as explicit_original_raw_verify
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-evangel-college-91306-authentic-tin-current-physical-v2-20261011'
OLD=HERE/'local'/PRIOR.name
CAPTURE=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011'
INPUT=BASE/'government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011'
BATCH='government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';NEIGHBOUR='way/134495631:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 receipt=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);prior=read(PRIOR/'diagnostic.json.gz');assert start==prior['currentManifest']and prior['completeProtectedCurrentForms']==17 and prior['rawGuardFailure']is None
 assert prior['rawOrdinaryReasons']==['terrain-intersects-source-over-0.5m','terrain-regresses-neighbour:'+NEIGHBOUR,'whole-source-foundation']
 inputs=read(PRIOR/'neighbour-inputs.json.gz');saved=read(INPUT/'complete-protected-current-forms.json.gz');assert len(inputs['rows'])==17
 assert {r['building']['uid']:r['building']for r in inputs['rows']}=={r['building']['uid']:r['building']for r in saved['rows']}
 for p,h in inputs['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 for pin in prior['completeCurrentCatalogueRefs']:assert ref(ROOT/pin['path'])==pin
 selected=read(PRIOR/'selection.json.gz');assert len(selected['rows'])==1
 pipeline_row=selected['rows'][0];identity_selection=read(INPUT/'check-selection.json.gz');assert len(identity_selection['rows'])==1;row=identity_selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE_SHA
 expected_pipeline_row=copy.deepcopy(row);expected_pipeline_row['candidate']['path']=pipeline_row['candidate']['path'];assert pipeline_row==expected_pipeline_row
 original_asset=(ROOT/row['candidate']['path']).read_bytes();relocated_asset=(ROOT/pipeline_row['candidate']['path']).read_bytes();assert original_asset==relocated_asset and digest(original_asset)==SOURCE_SHA
 context=read(INPUT/'context.json.gz')['rows'];assert len(context)==1
 identity=verify_files(row,context[0],LOCAL/'current-identity',raw_identity_replay=explicit_original_raw_verify);assert identity==read(INPUT/'owned-source-identity.json')and identity['passed']and identity['reasons']==[]
 source_data=read(CAPTURE/'complete-four-stream-ground-inputs.json.gz');assert source_data['sourceSHA256']==SOURCE_SHA
 b=next(r['building']for r in inputs['rows']if r['building']['uid']==NEIGHBOUR);assert not next(r['existingNative']for r in inputs['rows']if r['building']['uid']==NEIGHBOUR)
 foot=Polygon(b['rings'][0],b['rings'][1:]);assert foot.is_valid and not foot.is_empty
 protected=foot.buffer(.01,join_style='mitre');separation=[]
 for mode,stream in source_data['completeWorldStreams'].items():
  tri=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert tri.shape==(13960,3,3)and digest(tri.tobytes())==stream['completeWorldTriangleSHA256']
  projected=unary_union([Polygon(t[:,[0,2]])for t in tri if Polygon(t[:,[0,2]]).area])
  assert protected.disjoint(projected)and protected.distance(projected)>0
  separation.append(dict(arithmetic=mode,sourceWorldSHA256=digest(tri.tobytes()),rawFootprintIntersectionM2=foot.intersection(projected).area,protectedEnvelopeIntersectionM2=protected.intersection(projected).area,completeSourceSeparationM=protected.distance(projected)))
 original=read(PRIOR/'terrain.json')['patch'];assert ref(ROOT/original['path'])==dict(path=original['path'],sha256=original['sha256'])
 patch=read(ROOT/original['path']);bounds=original['bounds'];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);assert not parent.get('nativeMesh'),'This specific proposal requires the actual unchanged grid parent, never a native height fallback'
 parentpin=ref(parentpath);assert read(PRIOR/'metrics.json')['inputHashes'][parentpin['path']]==parentpin['sha256']
 second=module('evangel_parent_preservation_second','xl-second-pass.py');second.LOCAL=LOCAL
 patches=module('evangel_disjoint_preservation','native_patch_resolution.py');final=module('evangel_preserved_foundation','xl-final-script-pass.py')
 # Copy only original model catalogue/source inputs byte-for-byte. Numeric prior
 # terrain and every raw previous result stay under their original frozen paths.
 for name in ['catalogue.json','catalogue-index.json','source-forms.json']:
  (LOCAL/name).write_bytes((OLD/name).read_bytes());assert (LOCAL/name).read_bytes()==(OLD/name).read_bytes()
 for name in ['assets','unpacked']:
  if (OLD/name).exists():shutil.copytree(OLD/name,LOCAL/name)
 save(DOC/'selection.json.gz',selected);save(DOC/'owned-source-identity.json',identity);(DOC/'captured-manifest.json').write_bytes(manifest.read_bytes())
 sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
 proof=patches.preserve_parent_under_projection(patch,bounds,protected,sampler)
 model=second.glb_triangles(row);projection=unary_union([Polygon(t[:,[0,2]])for t in model if Polygon(t[:,[0,2]]).area]);assert protected.disjoint(projection)
 patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
 patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler)
 target=LOCAL/'neighbour-protected'/Path(original['path']).name;save(target,patch)
 sourcefiles=read(PRIOR/'terrain.json')['sourceFiles']
 if patches.projected_context(patch,bounds)[3]>1e-8:
  patches.approve_original_overlap(patch,target,DOC/'protected-overlap.json',sourcefiles);patches.finalize_overlap_evidence(patch,DOC/'protected-overlap.json')
 else:patch['nativeMesh'].pop('sourceOverlap',None)
 second.resolution.validate_patch(patch,parent);assert len(patch['nativeMesh']['index'])//3<=100000;save(target,patch)
 revised={**original,'path':str(target.relative_to(ROOT)),'sha256':digest(target.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3}
 save(DOC/'terrain-candidates.json',[revised]);inputs['patches']=[revised];save(DOC/'neighbour-inputs.json.gz',inputs)
 save(DOC/'neighbour-preservation.json',dict(originalFrozenPatch=original,changedTerrainProposal=revised,currentBasic=b,completeCurrentParent=parentpin,declaredProtectedMarginM=.01,completeFourStreamSourceDisjointness=separation,existingParentPreservation=proof,originalSchoolGeometryChanges=0,sourceFoundationAndRootCredit=False,currentAcceptance=False))
 def call(args,allowed=(0,)):
  process=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  while True:
   try:stdout,stderr=process.communicate(timeout=30);break
   except subprocess.TimeoutExpired:
    assert process.poll()is None and reservations.owns(lease)and reservations.heartbeat(lease,ttl=3600)['ok'];print(json.dumps(dict(activeCommand=args[1],heartbeat=True)),flush=True)
  save(DOC/('command-'+str(len(list(DOC.glob('command-*.json'))))+'.json'),dict(args=args,exitCode=process.returncode,stdout=stdout,stderr=stderr));assert process.returncode in allowed,(args,stderr)
  assert ref(manifest)==start and reservations.owns(lease)
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz')['rows'];assert len(runtime)==1 and runtime[0]['uid']==UID
 tri=np.asarray(runtime[0]['position']).reshape(-1,3)[np.asarray(runtime[0]['index']).reshape(-1,3)];ground=np.asarray(runtime[0]['drawnGroundGeometry']).reshape(-1,3,3)
 f=final.foundation_context(tri,ground,Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]));save(DOC/'foundation.json',dict(rows=[dict(uid=UID,sourceSHA256=SOURCE_SHA,foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0)],modelGeometryChanges=0))
 metrics=read(DOC/'metrics.json');reasons=module('evangel_preserved_ordinary_policy','acceptance-policy.py').reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE_SHA,identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
 if not read(DOC/'foundation.json')['rows'][0]['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 reasons.extend(read(DOC/'validation.json')['results'][0].get('concerns',[]));native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']and r['uid']not in resolved)
 assert reservations.owns(lease)and ref(manifest)==start
 for pin in prior['completeCurrentCatalogueRefs']:assert ref(ROOT/pin['path'])==pin
 for p,h in inputs['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 for pin in receipt['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],currentManifest=start,rawOrdinaryReasons=sorted(set(reasons)),all17CurrentActorGuardsRetained=True,previousRawOrdinaryReasonsVerbatim=prior['rawOrdinaryReasons'],changedTerrainProposal=True,modelGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 failure_archive=BASE/'government-xl-evangel-college-91306-disjoint-neighbour-retention-v3-failure-archive-20261011';refs.extend(p for p in failure_archive.rglob('*')if p.is_file());refs.append(HERE/'xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v3-20261011.py')
 failure_v4=BASE/'government-xl-evangel-college-91306-disjoint-neighbour-retention-v4-failure-archive-20261011';refs.extend(p for p in failure_v4.rglob('*')if p.is_file());refs.append(HERE/'xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v4-20261011.py')
 refs+=[CAPTURE/'result.json',CAPTURE/'complete-four-stream-ground-inputs.json.gz',parentpath,HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'acceptance-policy.py',HERE/'evangel_college_post_elements_current_bound_wing_extension_identity_v3_20261011.py',HERE/'exact_cell_replay_with_original_routed_callable_20261011.py']
 refs.extend(p for p in DOC.rglob('*')if p.is_file());refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 receipt=module('evangel_preserved_freezer','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-disjoint-current-neighbour-parent-preservation-complete17-ordinary-diagnostic-only',refs,dict(uids=[UID],rawOrdinaryReasons=sorted(set(reasons)),currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=receipt['jobId'],rawReasons=reasons)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();inputs=read(PRIOR/'neighbour-inputs.json.gz');assert len(inputs['rows'])==17
 # Fail orchestration prerequisites before claiming or constructing a candidate.
 metrics=read(PRIOR/'metrics.json');parentpath=ROOT/'3d-viewer/city/data/terrain.json';assert metrics['inputHashes'][str(parentpath.relative_to(ROOT))]==digest(parentpath.read_bytes());assert not read(parentpath).get('nativeMesh')
 assert read(PRIOR/'diagnostic.json.gz')['rawGuardFailure']is None and len(read(PRIOR/'terrain-candidates.json'))==1
 for name in ['catalogue.json','catalogue-index.json','source-forms.json']:assert (OLD/name).is_file()
 prior_row=read(PRIOR/'selection.json.gz')['rows'][0];input_row=read(INPUT/'check-selection.json.gz')['rows'][0];expected=copy.deepcopy(input_row);expected['candidate']['path']=prior_row['candidate']['path'];assert prior_row==expected
 assert (ROOT/prior_row['candidate']['path']).read_bytes()==(ROOT/input_row['candidate']['path']).read_bytes()
 assert digest((ROOT/input_row['candidate']['path']).read_bytes())==SOURCE_SHA
 assert all(ref(ROOT/p)==dict(path=p,sha256=h)for p,h in inputs['inputHashes'].items())
 resources=[('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid']for r in inputs['rows']]+['terrain-patch:'+UID]
 claim=reservations.claim('evangel-disjoint-neighbour-preservation-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
