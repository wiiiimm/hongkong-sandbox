"""Complete Float32 overlap proof and actual-renderer capture; private only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
import lai_chi_kok_full_terrain_candidate_v2_20261019 as runner
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-full-terrain-metrics-v2-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v1-20261019'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'],str(p);refs.append(p)
 nom=BASE/'government-xl-lai-chi-kok-runtime-buried-coverage-v1-20261019';nr=read(nom/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(nr['jobId'],)).fetchone()==('complete',nr)
 refs.append(nom/'result.json')
 for e in nr['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 import numpy as np
 from source_surface_inset_collection_v1_20261019 import inset_faces
 DOC.mkdir(parents=True);patch=read(SRC/'private-terrain.json');mesh=patch['nativeMesh'];before=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
 out,inset=inset_faces(before,np.asarray(read(nom/'surface-nomination.json.gz')['triangles']));save(DOC/'additional-source-inset.json.gz',inset)
 mesh['position']=out.reshape(-1).tolist();mesh['index']=list(range(out.size//3));mesh.pop('sourceOverlap',None)
 refs.append(HERE/'source_surface_inset_collection_v1_20261019.py')
 proof=module('lai_complete_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=DOC
 proof.overlap_proof(patch,[SRC/'private-terrain.json',HERE/'lai_chi_kok_full_terrain_candidate_v2_20261019.py'])
 path=DOC/'private-terrain.json';save(path,patch);validator=module('lai_runtime_validator',HERE/'resolve-pass-indexed-parent-clipping.py');error=None
 try:validator.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
 except Exception as exc:error=str(exc)
 candidates=read(SRC/'terrain-candidates.json');candidates[0].update(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()));save(DOC/'terrain-candidates.json',candidates)
 selection=read(SRC/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';selection['manifestSHA256']=digest(manifest.read_bytes());row=selection['rows'][0];asset=LOCAL/row['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset.write_bytes(raw);row['candidate']['path']=str(asset.relative_to(ROOT));save(DOC/'selection.json.gz',selection)
 metrics=None
 if error is None:
  tool=HERE/'acceptance-metrics-multi-retained.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
  with (DOC/'worker.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
  metrics=read(DOC/'metrics.json')
  for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=dict(uid=runner.UID,nativeValidatorError=error,metrics=metrics['rows']if metrics else None,installationApproved=False,liveAssetsChanged=False);save(DOC/'summary.json',summary);refs.extend([manifest,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'resolve-pass-indexed-parent-clipping.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 assert reservations.owns(lease);module('lai_metrics_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-full-terrain-overlap-and-runtime-capture',refs,dict(uids=[runner.UID],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':
 runner.BATCH,runner.DOC,runner.LOCAL=BATCH,DOC,LOCAL;runner.owned=owned;runner.__file__=str(Path(__file__).resolve());runner.main()
