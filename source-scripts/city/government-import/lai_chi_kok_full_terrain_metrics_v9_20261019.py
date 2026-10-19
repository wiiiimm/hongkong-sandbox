"""Complete Float32 overlap proof and actual-renderer capture; private only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
import lai_chi_kok_full_terrain_candidate_v2_20261019 as runner
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v5-20261019'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'],str(p);refs.append(p)
 nom=BASE/'government-xl-lai-chi-kok-upward-upper-source-nomination-v1-20261019';nr=read(nom/'result.json')
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
 out,inset=inset_faces(before,nominees);save(DOC/'additional-source-inset.json.gz',inset)
 prior=BASE/'government-xl-lai-chi-kok-platform-rim-compare-v4-20261019';rr=read(prior/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(rr['jobId'],)).fetchone()==('complete',rr)
 refs.append(prior/'result.json')
 for e in rr['evidenceRefs']:
  q=ROOT/e['path'];assert digest(q.read_bytes())==e['sha256'];refs.append(q)
 missing=read(prior/'comparison.json')['missing'];assert len(missing)==4
 from shapely.geometry import Polygon,Point
 retained_ids=[11723,10045,10837,10901,10919,11330,11344,11391,11808];original_ids=[36140,12972,12974,15787];retained=before.astype(np.float32).astype(np.float64)[retained_ids];original_face=full[original_ids];add=np.concatenate([retained,original_face])
 for r in missing:assert any(Polygon(t[:,[0,2]]).covers(Point(r['point'][0],r['point'][2]))for t in add)
 save(DOC/'complete-source-residual-facets.json',dict(previousTerrain=str((SRC/'private-terrain.json').relative_to(ROOT)),previousTerrainSHA256=digest((SRC/'private-terrain.json').read_bytes()),previousPackedFaceIds=retained_ids,originalModelSHA256=selected['sourceSHA256'],originalModelFaceIds=original_ids,triangles=add.tolist(),missingRuntimeSamples=missing,qualification='Complete unchanged prior packed terrain facets plus complete original upward source face; no fitted heights or building geometry edits. Full current validation pending.'))
 attribution=BASE/'government-xl-lai-chi-kok-wall-gap-attribution-v1-20261019';ar=read(attribution/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(ar['jobId'],)).fetchone()==('complete',ar)
 refs.append(attribution/'result.json')
 for e in ar['evidenceRefs']:
  q=ROOT/e['path'];assert digest(q.read_bytes())==e['sha256'];refs.append(q)
 save(DOC/'wall-gap-repair.json',dict(attributionJobId=ar['jobId'],previousPackedFaceIds=retained_ids,originalSourceFaceIds=original_ids,buildingGeometryChanged=False,installationApproved=False,qualification='Whole unchanged prior terrain and original source facets; final renderer/edge/neighbour checks required. No fitted heights.'))
 out=np.concatenate([out,add])
 mesh['position']=out.reshape(-1).tolist();mesh['index']=list(range(out.size//3));mesh.pop('sourceOverlap',None)
 refs.append(HERE/'source_surface_inset_collection_v1_20261019.py')
 from float32_coverage import approve_roundoff
 save(DOC/'numerical-coverage.json',approve_roundoff(patch,[-2477.5,-5917.5,-1707.5,-5287.5]));refs.append(HERE/'float32_coverage.py')
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
