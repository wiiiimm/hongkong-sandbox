"""Fresh unchanged-source identity/runtime/foundation checks; no installation credit."""
import json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-podium-current-checks-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CASES={'landsd/233002:0':'government-xl-orchards-podium-original-recovery-v1-20261017'}
def inputs():
 return [(next(r for r in read(BASE/name/'check-selection.json.gz')['rows']if r['uid']==uid),BASE/name/'check-selection.json.gz')for uid,name in CASES.items()]
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes());current=read(manifest);refs=[Path(__file__),manifest];catalogues={}
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues[p]=digest(p.read_bytes());assert not any(e['uid']in CASES for e in read(p)['models'])
 final=module('three_current_final',HERE/'xl-final-script-pass.py');rows=[];contexts=[];identities=[];decoded={}
 for row,path in inputs():
  row=dict(row,triangles=row['native']['model']['triangles'])
  refs.append(path);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset)
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];decoded[row['uid']]=tri;lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);b,_,tile=next(f for f in forms if f[0]['uid']==row['uid']);assert b['buildingCSUID']==row['source']['building']['buildingCSUID']
  row['source']=dict(building=b,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()));dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']=dict(row['candidate'],path=str(dest.relative_to(ROOT)));refs.append(dest)
  context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});contexts.append(context);identities.append(verify_files(row,context,LOCAL/'identity'/row['uid'].split('/')[1]));refs.extend(ROOT/'3d-viewer'/t for _,_,t in forms);rows.append(row)
  print(dict(uid=row['uid'],identityPassed=identities[-1]['passed'],identityReasons=identities[-1]['reasons']),flush=True)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifest_sha));save(DOC/'identity-proofs.json',dict(rows=identities));save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'terrain-candidates.json',[])
 closure=DOC/'production-module-closure.json';js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root)));"
 subprocess.run(['node','--input-type=module','-e',js,str(closure)],cwd=ROOT,check=True);cl=read(closure);assert cl['completeAuditedLiteralImportClosure']and cl['unsupportedDynamicImports']==0
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 rt=read(LOCAL/'runtime-geometry.json.gz');assert len(rt['rows'])==1;foundations=[]
 for row in rows:
  g=next(x for x in rt['rows']if x['uid']==row['uid']);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert tri.shape==decoded[row['uid']].shape and np.max(np.abs(tri-decoded[row['uid']]))<=1e-9;ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));passed=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0;foundations.append(dict(uid=row['uid'],foundation=f,strictFoundationAccepted=passed));print(dict(uid=row['uid'],foundationPassed=passed,buried=f['fullyBuriedTriangles']),flush=True)
 save(DOC/'foundations.json',dict(rows=foundations));metrics=read(DOC/'metrics.json');assert not any(m.get('error')for m in metrics['rows'])
 for p,h in {**cl['inputHashes'],**rt['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert reservations.owns(lease)and digest(manifest.read_bytes())==manifest_sha
 for p,h in catalogues.items():assert digest(p.read_bytes())==h
 refs.extend([LOCAL/'runtime-geometry.json.gz',closure,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 summary=[dict(uid=r['uid'],identityPassed=i['passed'],identityReasons=i['reasons'],strictFoundationAccepted=f['strictFoundationAccepted'],buriedTriangles=f['foundation']['fullyBuriedTriangles'])for r,i,f in zip(rows,identities,foundations)]
 out=module('three_current_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-original-current-identity-runtime-foundation-v1',list(set(refs)),dict(uids=list(CASES),summary=summary,fullAcceptance=False,nextStep='Use exact current reasons to pursue source identity or installed support/terrain recovery, then complete neighbour/browser/publication requirements.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 # Supporting original is outside the XL freeze; recovery is explicitly scoped to Orchards.
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in CASES],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
