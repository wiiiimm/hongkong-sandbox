"""Complete Float32 overlap proof and actual-renderer capture; private only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
import lai_chi_kok_full_terrain_candidate_v2_20261019 as runner
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-full-terrain-metrics-v7-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v6-20261019'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'],str(p);refs.append(p)
 nom=BASE/'government-xl-lai-chi-kok-complete-upper-source-nomination-v2-20261019';nr=read(nom/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(nr['jobId'],)).fetchone()==('complete',nr)
 refs.append(nom/'result.json')
 for e in nr['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 import numpy as np
 from source_surface_inset_collection_v1_20261019 import inset_faces
 DOC.mkdir(parents=True);patch=read(SRC/'private-terrain.json');mesh=patch['nativeMesh'];before=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 selected=read(SRC/'selection.json.gz')['rows'][0];sourcepath=ROOT/selected['candidate']['path'];raw=sourcepath.read_bytes();assert digest(raw)==selected['sourceSHA256'];full=decode_original_world_triangles(raw);nomination=read(nom/'surface-nomination.json.gz');ids=sorted(set(nomination['sourceFaceIndices']));assert nomination['summary']['sourceSHA256']==selected['sourceSHA256'];assert ids;nominees=np.asarray(nomination['triangles']);assert len(nominees)>0
 save(DOC/'complete-upper-source-nomination.json.gz',dict(sourceSHA256=selected['sourceSHA256'],faceIds=ids,triangles=nominees.tolist(),qualification='Complete exact original upper source surfaces, including partially obscured faces; no building geometry edits.',installationApproved=False));refs.extend([sourcepath,HERE/'exact_packed_world_geometry_20261009.py'])
 from float32_coverage import approve_roundoff,geometry_sha
 original_geometry=geometry_sha(patch);out=before
 numerical=approve_roundoff(patch,[-2477.5,-5917.5,-1707.5,-5287.5]);assert geometry_sha(patch)==original_geometry
 save(DOC/'numerical-coverage.json',numerical);refs.append(HERE/'float32_coverage.py')
 save(DOC/'geometry-preservation.json',dict(previousGeometrySHA256=original_geometry,currentGeometrySHA256=geometry_sha(patch),geometryUnchanged=True,policy='Existing sub-2mm and <=0.25m2 Float32 coverage policy; full runtime and physical checks still required.'))
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
