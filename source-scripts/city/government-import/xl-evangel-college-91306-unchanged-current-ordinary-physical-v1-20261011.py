"""Fresh single original ordinary no-terrain-change physical diagnosis.
Exact reviewed named136 wing-extension identity is replayed; every physical actor stays independent. No physical/support exception is granted by this diagnostic.
"""
import argparse,copy,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from evangel_college_current_bound_wing_extension_identity_20261011 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
EXPECTED={'landsd/91306:0':('4507318353T20070410','B450731835301063C0','73dfaaf90f9dc8433f757ff796f90a0d8e3d02e2d48eb515f3286fa3eddc964b',13960)}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,HERE/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--uid',choices=sorted(EXPECTED),required=True);args=a.parse_args();uid=args.uid;slug=uid.split('/')[1].replace(':','-')
 batch='government-xl-evangel-college-91306-unchanged-current-ordinary-physical-v1-20261011'
 base=ROOT/'docs/astra-city/government-import';doc=base/batch;local=HERE/'local'/batch
 identity_doc=base/'government-xl-evangel-college-91306-current-wing-extension-identity-v1-20261011'
 raw_doc=base/'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011'
 assert not doc.exists() and not local.exists()
 receipt=read(identity_doc/'result.json');assert receipt['identityAccepted'] and not receipt['physicalAccepted']
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
 selected=read(identity_doc/'selection.json.gz');assert selected['manifestSHA256']==digest(before)
 assert len(selected['rows'])==1;row=copy.deepcopy(selected['rows'][0]);assert row['uid']==uid
 context=read(identity_doc/'context.json.gz')['rows'];assert len(context)==1 and context[0]['uid']==uid
 forms=read(raw_doc/'complete-current-forms.json.gz')['rows'];assert len(forms)==len({b['uid'] for b in forms}) and uid in {b['uid'] for b in forms}
 native_entries=[m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']]
 assert len(native_entries)==len({m['uid'] for m in native_entries}) and uid not in {m['uid'] for m in native_entries}
 current_native={m['uid'] for m in native_entries};catalogues=[ref(ROOT/'3d-viewer'/u) for u in read(manifest)['officialModelCatalogues']]
 resources=[('building:' if b['uid'].startswith('landsd/') else 'foreign-form:')+b['uid'] for b in forms]
 claim=reservations.claim('evangel-ordinary-unchanged-terrain-'+str(uuid.uuid4()),resources,batch=batch,ttl=3600);assert claim['ok'],claim
 def call(argv,allowed=(0,)):
  process=subprocess.Popen(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  while True:
   try:stdout,stderr=process.communicate(timeout=30);break
   except subprocess.TimeoutExpired:
    assert process.poll()is None and reservations.owns(claim['reservation'])
    assert reservations.heartbeat(claim['reservation'],ttl=3600)['ok']
    print(json.dumps(dict(activeCommand=argv[1],reservationHeartbeat=True)),flush=True)
  save(doc/('command-'+str(len(list(doc.glob('command-*.json'))))+'.json'),dict(args=argv,exitCode=process.returncode,stdout=stdout,stderr=stderr,activeProcessHeartbeatOnly=True));assert process.returncode in allowed,stderr
 try:
  csuid,model,sha,n=EXPECTED[uid];assert row['sourceSHA256']==sha and row['triangles']==n and row['modelId']==model and row['source']['building']['buildingCSUID']==csuid
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==sha
  original=decode_original_world_triangles(raw);assert original.shape==(n,3,3) and np.isfinite(original).all()
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(uid,)).fetchone()
   assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  identity=verify_files(row,context[0],local/'ordinary-full-identity');assert identity==read(identity_doc/'identity.json') and identity['passed'] and identity['reasons']==[]
  save(doc/'identity.json',identity)
  dest=local/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT))
  cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');cat.update(area=batch,models=[row['candidate']['entry']],counts={'packedModels':1});save(local/'catalogue.json',cat);save(local/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(local/'source-forms.json',{uid:row['source']})
  save(doc/'selection.json.gz',dict(rows=[row],batch=batch,manifestSHA256=digest(before),nativeRun=NATIVE_RUN));save(doc/'terrain-candidates.json',[])
  save(doc/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,existingNative=b['uid'] in current_native,patchIndexes=[]) for b in forms],inputHashes={'3d-viewer/'+path:sha for path,sha in context[0]['neighbourTileHashes'].items()},candidateIds=[uid],patches=[]))
  for path,pin in read(doc/'neighbour-inputs.json.gz')['inputHashes'].items():assert path.startswith('3d-viewer/city/data/tiles/') and (ROOT/path).is_file() and digest((ROOT/path).read_bytes())==pin
  call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((doc/'selection.json.gz').relative_to(ROOT)),'--candidates',str(local.relative_to(ROOT)),'--terrain-candidates',str((doc/'terrain-candidates.json').relative_to(ROOT)),'--out',str((doc/'metrics.json').relative_to(ROOT)),'--geometry-out',str((local/'runtime-geometry.json.gz').relative_to(ROOT))])
  call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(local.relative_to(ROOT)),'--source-forms',str((local/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((doc/'terrain-candidates.json').relative_to(ROOT)),'--out',str((doc/'validation.json').relative_to(ROOT))],(0,1))
  call(['node',str(HERE/'check-neighbours.mjs'),str(doc.relative_to(ROOT))+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),str(doc.relative_to(ROOT))+'/'])
  runtime=read(local/'runtime-geometry.json.gz')['rows'];assert len(runtime)==1 and runtime[0]['uid']==uid
  r=runtime[0];actual=np.array(r['position'],dtype='<f8').reshape(-1,3)[np.array(r['index'],dtype=np.int64).reshape(-1,3)];ground=np.array(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
  assert actual.shape==original.shape and np.isfinite(actual).all() and np.isfinite(ground).all()
  final=module('evangel_independent_full_foundation','xl-final-script-pass.py');b=row['source']['building'];foundation=final.foundation_context(actual,ground,Polygon(b['rings'][0],b['rings'][1:]));accepted=foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
  save(doc/'foundation.json',dict(rows=[dict(uid=uid,sourceSHA256=sha,foundation=foundation,strictFoundationAccepted=accepted)],sourceGeometryChanges=0,terrainGeometryChanges=0))
  metrics=read(doc/'metrics.json');validation=read(doc/'validation.json');policy=module('evangel_independent_ordinary_policy','acceptance-policy.py');numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sha,identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
  save(doc/'diagnostic.json.gz',dict(uid=uid,currentManifest=ref(manifest),completeOwnedFaces=n,completeOriginalWorldSHA256=digest(original.astype('<f8').tobytes()),completeActualLiteralWorldSHA256=digest(actual.astype('<f8').tobytes()),completeDrawnGroundFaces=len(ground),ordinaryNumericReasons=numeric,
   rawRuntimeConcerns=validation['results'],strictFoundationAccepted=accepted,loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],runtimeExceptions=validation['exceptions'],
   completeCurrentNeighbourForms=len(forms),neighbourRegressionReasons=[r for r in read(doc/'neighbour-checks.json')['rows'] if r['reasons']],rawNativeNeighbourChecks=read(doc/'native-neighbour-checks.json'),
   allCurrentCatalogueRefs=catalogues,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,publication=False,
   qualification='Ordinary full current named identity/loader/runtime/wholefoundation/nearby-neighbour screening for one unchanged source. Raw bottom, rim, runtime, foreign and native warnings retained. Complete component support, actual F32/foreign collision and current global native-bounds certification remain independent before any staging/publication. The exact136 wing-extension identity interpretation grants no physical actor or support exemption.'))
  assert manifest.read_bytes()==before and reservations.owns(claim['reservation'])
  for pin in catalogues:assert ref(ROOT/pin['path'])==pin
  for path,pin in context[0]['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==pin
  refs=[Path(__file__),asset,identity_doc/'result.json',identity_doc/'selection.json.gz',identity_doc/'context.json.gz',raw_doc/'complete-current-forms.json.gz',identity_doc/'identity.json',HERE/'evangel_college_current_bound_wing_extension_identity_20261011.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'acceptance-policy.py',HERE/'xl-final-script-pass.py',HERE/'acceptance-metrics.mjs',HERE.parent/'building-batch/validate_candidates.mjs',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours.mjs',*[p for p in local.rglob('*') if p.is_file()],*[ROOT/p['path'] for p in catalogues]]
  for name in ['metrics.json','validation.json','neighbour-checks.json','native-neighbour-checks.json']:
   report=read(doc/name);refs.extend(ROOT/path for path in (report.get('inputHashes') or report.get('hashes') or {}))
  freezer=module('evangel_independent_ordinary_freezer','xl-popcorn-source-investigations-checkpoints-20261009.py');receipt=freezer.freeze(batch,'independent-unchanged-current-ordinary-source-physical-diagnostic',refs+[p for p in doc.rglob('*')if p.is_file()],dict(uids=[uid],completeOwnedFaces=n,ordinaryNumericReasons=numeric,strictFoundationAccepted=accepted,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False))
  print(json.dumps(dict(jobId=receipt['jobId'],uid=uid,ordinaryNumericReasons=numeric,strictFoundationAccepted=accepted,publication=False)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
