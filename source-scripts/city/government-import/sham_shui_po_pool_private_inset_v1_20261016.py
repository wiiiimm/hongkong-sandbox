"""Private source-authored basin inset; building bytes stay immutable."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import inset_faces
BATCH='government-xl-sham-shui-po-pool-private-inset-v1-20261016';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
BASIN=BASE/'government-xl-sham-shui-po-pool-basin-source-v1-20261016';CURRENT=BASE/'government-xl-sham-shui-po-pool-current-ground-v1-20261016';OLD=BASE/'government-xl-uncovered-qualified-sequence-20261006-265480-0'
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__),HERE/'source_surface_inset.py',HERE/'test_source_surface_inset.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [BASIN,CURRENT]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for q in r['evidenceRefs']:assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
  old=read(OLD/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old);refs.append(OLD/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 oldpins={q['path']:q['sha256'] for q in old['evidenceRefs']};candidates=OLD/'terrain-candidates.json';assert digest(candidates.read_bytes())==oldpins[str(candidates.relative_to(ROOT))];original=read(candidates)[0];patchpath=ROOT/original['path'];assert digest(patchpath.read_bytes())==original['sha256'];refs.extend([candidates,patchpath])
 patch=read(patchpath);parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath)
 helper=module('pool_private_validator',HERE/'resolve-pass.py');helper.validate_patch(patch,parent)
 source=read(BASIN/'basin-source.json.gz');assert read(BASIN/'summary.json')['flatOuterRim'];oldfaces=np.asarray(patch['nativeMesh']['position'],dtype=np.float32).astype(float).reshape(-1,3)[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)];basin=np.asarray(source['triangles']);newfaces,proof=inset_faces(oldfaces,basin);assert proof['removedProjectedAreaM2']>0
 DOC.mkdir();LOCAL.mkdir();save(DOC/'inset-proof.json.gz',proof);mesh=patch['nativeMesh'];mesh.pop('sourceOverlap',None);mesh['position']=newfaces.reshape(-1).tolist();mesh['index']=list(range(newfaces.size//3));mesh['source']['authoredBasinInset']=dict(policy=proof['policy'],uid=source['uid'],sourceSHA256=source['sourceSHA256'],sourceFaceIndices=source['sourceFaceIndices'],evidencePath=str((BASIN/'basin-source.json.gz').relative_to(ROOT)),evidenceSHA256=digest((BASIN/'basin-source.json.gz').read_bytes()),removedProjectedAreaM2=proof['removedProjectedAreaM2'],buildingGeometryChanged=False)
 save(DOC/'private-terrain.json',patch);validation={'passed':False}
 try:helper.validate_patch(patch,parent);validation={'passed':True}
 except (AssertionError,ValueError) as e:validation={'passed':False,'error':str(e)}
 save(DOC/'validation.json',validation);candidate=dict(path=str((DOC/'private-terrain.json').relative_to(ROOT)),sha256=digest((DOC/'private-terrain.json').read_bytes()),uids=[source['uid']]);save(DOC/'terrain-candidates.json',[candidate]);selection=read(CURRENT/'selection.json.gz');save(DOC/'selection.json.gz',selection)
 tool=HERE/'acceptance-metrics-retained-group-parent.mjs';cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str((HERE/'local'/CURRENT.name).relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 metrics=read(DOC/'metrics.json');assert not metrics['rows'][0].get('error');g=read(LOCAL/'runtime-geometry.json.gz')['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=selection['rows'][0]['source']['building'];foundation=module('pool_inset_foundation',HERE/'xl-final-script-pass.py').foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=dict(uid=source['uid'],originalTerrainFaces=len(oldfaces),proposedTerrainFaces=len(newfaces),replacedAreaM2=proof['removedProjectedAreaM2'],validation=validation,metrics=metrics['rows'][0],foundation=foundation,privateTerrainGeometryChanged=True,buildingGeometryChanged=False,neighboursChecked=False,fullAcceptance=False,liveAssetsChanged=False);save(DOC/'summary.json',summary);refs.extend([tool,LOCAL/'runtime-geometry.json.gz',HERE/'resolve-pass.py',HERE/'native_patch_resolution.py',HERE/'xl-final-script-pass.py'])
 r=module('pool_inset_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-authored-basin-lower-envelope-proposal-v1',list(dict.fromkeys(refs)),dict(uids=[source['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0,privateTerrainGeometryChanged=True));print(dict(jobId=r['jobId'],validation=validation,foundation=foundation,metrics=metrics['rows'][0]),flush=True)
if __name__=='__main__':main()
