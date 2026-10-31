"""Fresh named source/native/installed catalogue/primary/literal capture only."""
from copy import deepcopy
import importlib.util,json,subprocess,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import OWN,FOREIGN,OWN_SHA,FOREIGN_SHA,OWN_WORLD,FOREIGN_WORLD
from one_peking_current_installed_foreign_inventory_20261010 import native_rows,verify_native_rows,installed_inventory
from one_peking_current_bound_installed_foreign_identity_20261010 import DOC,PRIMARY_WHERE,EXPECTED_RAW_REASONS
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin
BATCH=DOC.name;OLD=DOC.parent/'government-xl-one-peking-current-complete-record-identity-diagnostic-v1-20261010'
def module(name,filename):
 s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists()
 claim=reservations.claim('one-peking-current-bound-inputs-'+str(uuid.uuid4()),['building:'+OWN,'building:'+FOREIGN],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert before==(OLD/'captured-manifest.json').read_bytes(),'Fresh raw current capture required'
  row=deepcopy(read(OLD/'selection.json.gz')['rows'][0]);context=deepcopy(read(OLD/'context.json.gz')['rows'][0]);raw_identity=read(OLD/'identity.json');assert raw_identity['reasons']==EXPECTED_RAW_REASONS and raw_identity['passed'] is False
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==OWN_SHA;own=decode_original_world_triangles(raw);assert digest(own.astype('<f8').tobytes())==OWN_WORLD
  final=module('peking_capture_complete_forms','xl-final-script-pass.py');lo,hi=own.min((0,1)),own.max((0,1));loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded]
  hashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in loaded};assert hashes==context['neighbourTileHashes'];assert next(b for b in forms if b['uid']==OWN)==row['source']['building']
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');rows=native_rows(c);verify_native_rows(rows)
  assert rows[0]['model']==row['native']['model'] and rows[0]['resultSHA256']==row['native']['resultSha'] and rows[0]['sourceKey']==row['native']['cacheKey']+'/'+row['modelId']
  inventory=installed_inventory(before);f=inventory['installedForeign'];foreign_raw=(ROOT/f['assetPath']).read_bytes();assert digest(foreign_raw)==FOREIGN_SHA;foreign=decode_original_world_triangles(foreign_raw);assert digest(foreign.astype('<f8').tobytes())==FOREIGN_WORLD
  DOC.mkdir(parents=True)
  primary=module('peking_fresh_exact_primary','xl-man-fuk-man-oi-primary-relations-20261010.py');primary.DOC=DOC
  features=primary.query(0,PRIMARY_WHERE,'exact-current-primary',True);assert len(features)==3
  save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(before)));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'raw-identity.json',raw_identity)
  save(DOC/'current-inputs.json.gz',dict(manifestSHA256=digest(before),tileHashes=hashes,forms=forms,exactRouteTileHashes=raw_identity['exactRouteTileHashes'],installedInventory=inventory))
  save(DOC/'source-lookup.json.gz',dict(rows=rows,nativeRunID=NATIVE_RUN))
  save(DOC/'complete-original-stream-pins.json.gz',{OWN:stream_pin(raw,row['modelId'],4114),FOREIGN:stream_pin(foreign_raw,f['entry']['modelId'],32635)})
  save(DOC/'literal-source-inputs.json.gz',dict(ownEntry=row['candidate']['entry'],foreignEntry=f['entry'],ownBuilding=next(b for b in forms if b['uid']==OWN),foreignBuilding=next(b for b in forms if b['uid']==FOREIGN),ownPath=row['candidate']['path'],foreignPath=f['assetPath']))
  subprocess.run(['node',str(HERE/'xl-one-peking-current-literal-production-geometry-v1-20261010.mjs'),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
  literal=read(DOC/'literal-production-geometry.json.gz');assert literal['completeProductionLoaderDependencyClosure'] and {r['uid'] for r in literal['rows']}=={OWN,FOREIGN}
  bindings={}
  for r in literal['rows']:
   p=np.asarray(r['position'],dtype='<f8').reshape((-1,3));i=np.asarray(r['index'],dtype=np.int64).reshape((-1,3));a=p[i];source=own if r['uid']==OWN else foreign
   assert a.shape==source.shape and np.isfinite(a).all()
   bindings[r['uid']]={'literal':dict(completeFaces=len(a),worldTrianglesSHA256=digest(a.tobytes())),'original':dict(completeFaces=len(source),worldTrianglesSHA256=digest(source.astype('<f8').tobytes()))}
  save(DOC/'literal-complete-geometry-bindings.json.gz',bindings);(DOC/'captured-manifest.json').write_bytes(before)
  assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before and installed_inventory(before)==inventory
  assert all(digest((ROOT/'3d-viewer'/t).read_bytes())==h for t,h in hashes.items())
  refs=[Path(__file__),HERE/'one_peking_current_installed_foreign_inventory_20261010.py',HERE/'one_peking_current_bound_installed_foreign_identity_20261010.py',HERE/'one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'test_one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'xl-one-peking-current-literal-production-geometry-v1-20261010.mjs',HERE/'tung_sing_current_bound_identity_20261010.py',HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'exact_packed_world_geometry_20261009.py',OLD/'result.json',OLD/'identity.json',ROOT/row['candidate']['path'],ROOT/f['assetPath']]
  refs += [ROOT/'3d-viewer'/t for t in hashes];refs += [ROOT/'3d-viewer'/t for t in inventory['completeCatalogueHashes']];refs += [ROOT/p for p in literal['inputHashes']]
  result=module('peking_current_capture_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-native-installed-foreign-primary-and-literal-inputs-v1',refs,dict(uids=[OWN,FOREIGN],manifestSHA256=digest(before),identityAccepted=False,physicalAccepted=False,completeOwnFaces=4114,completeInstalledForeignFaces=32635,completeCurrentForms=len(forms),qualification='Fresh immutable complete input capture only. Exact unique current own source plus complete actual installed foreign original/native catalogue, root/BIN/attribute streams, production literal geometry/dependencies, all actual nearby forms and active primary records pinned. No physics/collision/support exemption or installation.'))
  print(json.dumps(dict(jobId=result['jobId'],manifestSHA256=digest(before),forms=len(forms))),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
