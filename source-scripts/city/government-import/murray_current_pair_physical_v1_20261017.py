"""Complete four-part Oi Sin originals on the private corrected terrain; no publication."""
import json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-murray-original-support-20261006'
BATCH='government-xl-murray-current-pair-physical-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/265825:0','landsd/248655:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);refs=[Path(__file__),manifest,OLD/'support-inputs.json'];catalogues={};matches=[]
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues[p]=digest(p.read_bytes())
  for e in read(p)['models']:
   if e['uid']in UIDS:matches.append(dict(uid=e['uid'],entry=e,catalogue=ref(p)))
 assert not matches,'Original pair already present: reconcile existing state first'
 rows=read(OLD/'support-inputs.json')['sources'];refs.append(OLD/'result.json');assert {r['uid']for r in rows}==set(UIDS)
 final=module('oi_sin_current_forms',HERE/'xl-final-script-pass.py');identities=[];decoded={};contexts=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for row in rows:
   assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 for row in rows:
  source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(source);tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];decoded[row['uid']]=tri
  lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);b,_,tile=next(f for f in forms if f[0]['uid']==row['uid']);assert b['buildingCSUID']==row['source']['building']['buildingCSUID']
  row['source']=dict(building=b,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()));dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']=dict(row['candidate'],path=str(dest.relative_to(ROOT)));refs.append(dest)
  context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});contexts.append(context);identities.append(verify_files(row,context,LOCAL/'identity'/row['uid'].split('/')[1]));refs.extend(ROOT/'3d-viewer'/t for _,_,t in forms)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=start['sha256']));save(DOC/'identity-proofs.json',dict(rows=identities));save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'terrain-candidates.json',[])
 save(DOC/'support-inputs.json',dict(pairs=[dict(uid=u,supportUid=UIDS[1])for u in UIDS if u!=UIDS[1]],sources=rows))
 closure=DOC/'production-module-closure.json'
 js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root)));"
 subprocess.run(['node','--input-type=module','-e',js,str(closure)],cwd=ROOT,check=True);cl=read(closure);assert cl['completeAuditedLiteralImportClosure']and cl['unsupportedDynamicImports']==0
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 rt=read(LOCAL/'runtime-geometry.json.gz');assert len(rt['rows'])==2;foundations=[]
 for row in rows:
  g=next(x for x in rt['rows']if x['uid']==row['uid']);t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert t.shape==decoded[row['uid']].shape and np.max(np.abs(t-decoded[row['uid']]))<=1e-9;ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];polygon=Polygon(b['rings'][0],b['rings'][1:])
  if row['uid']!=UIDS[1]:ground=np.concatenate([ground,decoded[UIDS[1]]])
  f=final.foundation_context(t,ground,polygon);foundations.append(dict(uid=row['uid'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0));print(dict(uid=row['uid'],identityPassed=next(x['passed']for x in identities if x['uid']==row['uid']),strictFoundationAccepted=foundations[-1]['strictFoundationAccepted']),flush=True)
 save(DOC/'foundations.json',dict(rows=foundations))
 for p,h in {**cl['inputHashes'],**rt['inputHashes'],**read(DOC/'support-checks.json.gz')['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert reservations.owns(lease)and ref(manifest)==start
 for p,h in catalogues.items():assert digest(p.read_bytes())==h
 refs.extend([LOCAL/'runtime-geometry.json.gz',closure,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 metrics=read(DOC/'metrics.json');assert not any(r.get('error')for r in metrics['rows'])
 out=module('oi_sin_current_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-two-original-current-identity-foundation-v1',list(set(refs)),dict(uids=UIDS,identity=[dict(uid=x['uid'],passed=x['passed'],reasons=x['reasons'])for x in identities],foundation=[dict(uid=x['uid'],strictFoundationAccepted=x['strictFoundationAccepted'])for x in foundations],interfaces=[dict(uid=x['uid'],interface=x['interface'])for x in read(DOC/'support-checks.json.gz')['rows']],fullAcceptance=False,currentInstalledTerrainOnly=True,nextStep='Resolve exact recorded current failures, then complete neighbouring actors, browser and publication checks. Distance proofs alone do not clear support.'))
 print(dict(jobId=out['jobId']),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 require_remaining(BASE/'government-xl-oi-sin-original-installed-v1-20261017/full-xl-current-count.json',UIDS[0],'14358bc6060b5c2988e0071d6c39b8b6a1cb0585d4fda88da3605ec903a1dc2d');assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
