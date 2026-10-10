"""Independent ordinary single-original runtime/foundation/current-neighbour diagnosis.
Terrain is unchanged; strict ordinary ground-bottom failures remain unaccepted.
"""
from pathlib import Path
import importlib.util,json,subprocess,uuid,copy
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
BATCH='government-xl-lippo-tower-only-unchanged-current-ordinary-physical-v3-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=DOC.parent/'government-xl-lippo-tower-only-current-complete-inputs-v5-20261011'
IDENTITY=DOC.parent/'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v5-20261011'
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def call(args,allowed=(0,)):
 result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/('command-'+str(len(list(DOC.glob('command-*.json'))))+'.json'),dict(args=args,exitCode=result.returncode,stdout=result.stdout,stderr=result.stderr));print(result.stdout,flush=True);assert result.returncode in allowed,result.stderr

def main():
 assert not DOC.exists() and not LOCAL.exists();inp=read(INPUT/'input.json.gz');geometry=read(INPUT/'complete-current-geometry.json.gz');before=(ROOT/inp['currentManifest']['path']).read_bytes();assert digest(before)==inp['currentManifest']['sha256']
 for folder in [INPUT,IDENTITY]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 row=copy.deepcopy(inp['rows'][0]);uid=row['uid'];assert uid=='landsd/239465:0';context=next(r for r in read(IDENTITY/'context.json.gz')['rows'] if r['uid']==uid)
 resources=['building:'+r['building']['uid'] for r in inp['completeCurrentForms']];claim=reservations.claim('lippo-tower-no-terrain-physical-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],);assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(uid,)).fetchone()
  identity=verify_files(row,context,LOCAL/'current-original-identity-replay');assert identity['passed'] and identity['reasons']==[]
  saved=read(IDENTITY/'identity.json');assert identity==saved,'Fresh production ordinary identity must exactly match captured raw proof'
  save(DOC/'identity.json',identity);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT))
  catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area=BATCH,models=[row['candidate']['entry']],counts={'packedModels':1});save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{uid:row['source']})
  save(DOC/'selection.json.gz',dict(rows=[row],batch=BATCH,manifestSHA256=digest(before),nativeRun=NATIVE_RUN));save(DOC/'terrain-candidates.json',[])
  save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=r['building'],existingNative=r['existingNative'],patchIndexes=[]) for r in inp['completeCurrentForms']],inputHashes=inp['currentTileHashes'],candidateIds=[uid],patches=[]))
  call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))])
  call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))],(0,1))
  call(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'])
  runtime=read(LOCAL/'runtime-geometry.json.gz')['rows'];assert len(runtime)==1 and runtime[0]['uid']==uid;r=runtime[0];tri=np.array(r['position'],dtype='<f8').reshape(-1,3)[np.array(r['index'],dtype=np.int64).reshape(-1,3)];ground=np.array(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
  captured=geometry['row'];ci=np.array(captured['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);ct=np.array(captured['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[ci];assert np.array_equal(ct,tri)
  final=module('lippo_tower_ordinary_whole_foundation','xl-final-script-pass.py');b=row['source']['building'];foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));accepted=foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
  save(DOC/'foundation.json',dict(rows=[dict(uid=uid,sourceSHA256=row['sourceSHA256'],foundation=foundation,strictFoundationAccepted=accepted)],modelGeometryChanges=0,terrainGeometryChanges=0))
  metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module('lippo_tower_ordinary_numeric_policy','acceptance-policy.py');numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
  result=dict(uid=uid,currentManifest=inp['currentManifest'],ordinaryNumericReasons=numeric,rawRuntimeConcerns=validation['results'],strictFoundationAccepted=accepted,completeOwnedFaces=3597,loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],runtimeExceptions=validation['exceptions'],currentNeighbourForms=len(inp['completeCurrentForms']),neighbourRegressionReasons=[r for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons']],rawNativeNeighbourChecks=read(DOC/'native-neighbour-checks.json'),sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Independent ordinary loader/picking/collision/whole foundation/current neighbour screening for single untouched Tower. Current terrain unchanged. Every ordinary bottom/rim numeric/runtime warning remains raw. Bounded actual BASIC carrier role, complete full-world foreign separation/penetration and source/actual roof graph still require independent reviewed final composition; no automatic acceptance.')
  save(DOC/'diagnostic.json.gz',result);assert (ROOT/inp['currentManifest']['path']).read_bytes()==before and reservations.owns(claim['reservation'])
  for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
  refs=[Path(__file__),INPUT/'input.json.gz',INPUT/'complete-current-geometry.json.gz',INPUT/'result.json',IDENTITY/'context.json.gz',IDENTITY/'result.json',IDENTITY/'identity.json',asset,HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'acceptance-policy.py',HERE/'xl-final-script-pass.py',HERE/'acceptance-metrics.mjs',HERE.parent/'building-batch/validate_candidates.mjs',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours.mjs',*[p for p in LOCAL.rglob('*') if p.is_file()],*[ROOT/path for path in geometry['inputHashes']]]
  for path in [DOC/'metrics.json',DOC/'validation.json',DOC/'neighbour-checks.json',DOC/'native-neighbour-checks.json']:
   report=read(path);refs += [ROOT/path for path in (report.get('inputHashes') or report.get('hashes') or {})]
  m=module('lippo_single_current_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');receipt=m.freeze(BATCH,'single-original-unchanged-current-ordinary-full-foundation-runtime-neighbour-diagnostic-v3-post-block17',refs,dict(uids=[uid],completeOwnedFaces=3597,ordinaryNumericReasons=numeric,strictFoundationAccepted=accepted,loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False))
  print(json.dumps(dict(jobId=receipt['jobId'],ordinaryNumericReasons=numeric,strictFoundationAccepted=accepted,runtimeChecksPassed=validation['checksPassed'],terrainGeometryChanges=0)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
