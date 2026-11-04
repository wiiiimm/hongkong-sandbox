"""Fresh nonaccepting complete current/native/provider/source/literal capture."""
from copy import deepcopy
from pathlib import Path
import importlib.util,json,subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from lippo_three_original_current_inventory_20261010 import EXPECTED,native_rows,verify_native_rows,catalogue_inventory
from lippo_original_six_roof_shared_boundary_proposal_20261010 import OWN,FOREIGN,TOWER
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin
BATCH='government-xl-lippo-current-bound-six-roof-inputs-v4-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
OLD=DOC.parent/'government-xl-lippo-current-complete-original-identity-diagnostic-v2-20261011'
PREPARED=DOC.parent/'government-xl-lippo-silvercord-three-prepared-source-inputs-v1-20261010/check-selection.json.gz'
PRIMARY_WHERE="BuildingCSUID IN ('3550417624P20050812','3551417531P20050812','3551817554T20050430')"
REASONS=['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap']
def module(name,filename):
 s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert not DOC.exists()
 claim=reservations.claim('lippo-complete-current-inputs-'+str(uuid.uuid4()),['building:'+u for u in EXPECTED],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  manifest=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert manifest==(OLD/'captured-manifest.json').read_bytes()
  row=deepcopy(read(OLD/'selection.json.gz')['rows'][0]);context=deepcopy(read(OLD/'context.json.gz')['rows'][0]);identity=read(OLD/'identity.json');assert identity['reasons']==REASONS and identity['passed'] is False
  prepared={r['uid']:deepcopy(r) for r in read(PREPARED)['rows']};assert set(prepared)==set(EXPECTED);prepared[OWN]=row
  own=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());lo,hi=own.min((0,1)),own.max((0,1))
  final=module('lippo_complete_current_capture_forms','xl-final-script-pass.py');loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded]
  hashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in loaded};assert hashes==context['neighbourTileHashes'];assert next(b for b in forms if b['uid']==OWN)==row['source']['building']
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');lookup=native_rows(c);verify_native_rows(lookup)
  by={r['model']['modelId']:r for r in lookup};pins={};literal_rows=[];refs=[]
  for uid,(mid,sha,count) in EXPECTED.items():
   r=prepared[uid];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==sha==r['sourceSHA256']
   n=by[mid];assert n['model']==r['native']['model'] and n['resultSHA256']==r['native']['resultSha'] and n['sourceKey']==r['native']['cacheKey']+'/'+mid
   b=next(b for b in forms if b['uid']==uid);assert b['buildingCSUID']==r['source']['building']['buildingCSUID']
   r['source']=dict(building=b,tile='city/data/tiles/'+b['tile']+'.json',tileSHA256=hashes['city/data/tiles/'+b['tile']+'.json'])
   pins[uid]=stream_pin(raw,mid,count);literal_rows.append(dict(uid=uid,entry=r['candidate']['entry'],building=b,path=r['candidate']['path']));refs.append(ROOT/r['candidate']['path'])
  inventory=catalogue_inventory(manifest);DOC.mkdir(parents=True)
  primary=module('lippo_fresh_three_exact_primary','xl-man-fuk-man-oi-primary-relations-20261010.py');primary.DOC=DOC;features=primary.query(0,PRIMARY_WHERE,'exact-current-primary',True);assert len(features)==3
  save(DOC/'selection.json.gz',dict(rows=list(prepared.values()),manifestSHA256=digest(manifest)));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'raw-identity.json',identity)
  save(DOC/'current-inputs.json.gz',dict(manifestSHA256=digest(manifest),tileHashes=hashes,forms=forms,exactRouteTileHashes=identity['exactRouteTileHashes'],catalogueInventory=inventory))
  save(DOC/'source-lookup.json.gz',dict(rows=lookup,nativeRunID=NATIVE_RUN));save(DOC/'complete-original-stream-pins.json.gz',pins);save(DOC/'literal-source-inputs.json.gz',dict(rows=literal_rows))
  subprocess.run(['node',str(HERE/'xl-lippo-current-literal-production-geometry-v2-20261011.mjs'),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
  literal=read(DOC/'literal-production-geometry.json.gz');assert literal['completeProductionLoaderDependencyClosure'] and {r['uid'] for r in literal['rows']}==set(EXPECTED)
  bindings={}
  for r in literal['rows']:
   p=np.asarray(r['position'],dtype='<f8').reshape((-1,3));i=np.asarray(r['index'],dtype=np.int64).reshape((-1,3));a=p[i];source=decode_original_world_triangles((ROOT/prepared[r['uid']]['candidate']['path']).read_bytes())
   assert a.shape==source.shape and np.isfinite(a).all();bindings[r['uid']]=dict(literal=dict(completeFaces=len(a),worldTrianglesSHA256=digest(a.tobytes())),original=dict(completeFaces=len(source),worldTrianglesSHA256=digest(source.astype('<f8').tobytes())))
  save(DOC/'literal-complete-geometry-bindings.json.gz',bindings);(DOC/'captured-manifest.json').write_bytes(manifest)
  render=DOC/'actual-render-attribute-geometry.json.gz'
  subprocess.run(['node',str(HERE/'xl-lippo-original-actual-render-attribute-geometry-v1-20261010.mjs'),str((DOC/'literal-source-inputs.json.gz').relative_to(ROOT)),str(render.relative_to(ROOT))],cwd=ROOT,check=True)
  from lippo_actual_render_float32_diagnostic_20261010 import verify as verify_render
  actual_render=read(render)
  for path,pin in actual_render['inputHashes'].items():assert digest((ROOT/path).read_bytes())==pin
  originals={u:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for u,r in prepared.items()}
  render_proof=verify_render(actual_render,literal,originals,forms,features)
  save(DOC/'complete-actual-render-f32-diagnostic.json.gz',render_proof)
  assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==manifest and catalogue_inventory(manifest)==inventory
  assert all(digest((ROOT/'3d-viewer'/t).read_bytes())==h for t,h in hashes.items())
  refs += [Path(__file__),PREPARED,OLD/'result.json',OLD/'identity.json',HERE/'lippo_three_original_current_inventory_20261010.py',HERE/'lippo_original_six_roof_shared_boundary_proposal_20261010.py',HERE/'xl-lippo-current-literal-production-geometry-v2-20261011.mjs',HERE/'tung_sing_current_bound_identity_20261010.py',HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'exact_packed_world_geometry_20261009.py']
  refs += [HERE/'lippo_actual_render_float32_diagnostic_20261010.py',HERE/'test_lippo_actual_render_float32_diagnostic_20261010.py',HERE/'xl-lippo-original-actual-render-attribute-geometry-v1-20261010.mjs',HERE/'lippo_current_bound_six_roof_identity_v1_20261010.py',HERE/'lippo_original_six_roof_current_scope_proposal_v2_20261010.py',HERE/'exact_original_finite_triangle_contacts_20261010.py']+[ROOT/path for path in actual_render['inputHashes']]
  refs += [ROOT/'3d-viewer'/p for p in [*hashes,*inventory['completeCatalogueHashes']]]+[ROOT/p for p in literal['inputHashes']]
  result=module('lippo_complete_capture_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lippo-complete-current-three-native-primary-original-literal-and-f32-inputs-v4',refs,dict(uids=list(EXPECTED),manifestSHA256=digest(manifest),identityAccepted=False,physicalAccepted=False,completeOwnFaces=13725,completeCurrentForms=len(forms),qualification='Fresh input capture only. All three unchanged native originals, root/BIN/POS/index streams, actual production literal geometry and independent complete Float32 render diagnostic, complete current catalogue and nearby actor scope and exact primary records pinned. Recovered Silvercord is evidence only; remains a full current basic physical foreign actor. No interpretation acceptance, support/terrain/collision exemption or installation.'))
  print(json.dumps(dict(jobId=result['jobId'],manifestSHA256=digest(manifest),forms=len(forms))),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
