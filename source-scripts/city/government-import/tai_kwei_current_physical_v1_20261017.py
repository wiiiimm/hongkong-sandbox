"""Current full-original Tai Kwei physical capture; no identity override or publication."""
import sys,json,uuid,subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN,reservations
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
UID='landsd/106413:0';SHA='797e15e504a549f44c02b55fe11ab769dec45f27f5174c4dc6dc313a7562fe79'
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tai-kwei-current-physical-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OLD=BASE/'government-xl-sustained-131-inputs-20261006/check-selection.json.gz'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());m=read(manifest);refs=[Path(__file__),manifest,OLD];cats={}
 for url in m['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cats[p]=digest(p.read_bytes());assert not any(r['uid']==UID for r in read(p)['models'])
 row=next(r for r in read(OLD)['rows'] if r['uid']==UID);assert row['sourceSHA256']==SHA
 source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==SHA;tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];refs.append(source)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 final=module('tai_kwei_current_final',HERE/'xl-final-script-pass.py');lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);b,_,tile=next(x for x in forms if x[0]['uid']==UID);assert b['buildingCSUID']==row['source']['building']['buildingCSUID']
 row['source']=dict(building=b,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()));dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']=dict(row['candidate'],path=str(dest.relative_to(ROOT)));refs.append(dest)
 context=dict(uid=UID,sourceSHA256=SHA,identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});identity=verify_files(row,context,LOCAL/'identity');refs.extend(ROOT/'3d-viewer'/t for _,_,t in forms)
 save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=mh));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity-proof.json',identity)
 closure=DOC/'production-module-closure.json';js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root)));"
 subprocess.run(['node','--input-type=module','-e',js,str(closure)],cwd=ROOT,check=True);cl=read(closure);assert cl['completeAuditedLiteralImportClosure']and not cl['unsupportedDynamicImports']
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 rt=read(LOCAL/'runtime-geometry.json.gz');assert len(rt['rows'])==1;g=rt['rows'][0];actual=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert actual.shape==tri.shape and np.max(np.abs(actual-tri))<=1e-9
 ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 for p,h in {**cl['inputHashes'],**rt['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
 for p,h in cats.items():assert digest(p.read_bytes())==h
 refs.extend([LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 metrics=read(DOC/'metrics.json');assert not any(r.get('error')for r in metrics['rows'])
 strict=foundation['completeTerrainTriangles']==foundation['triangles']and foundation['fullyBuriedAreaFraction']==0 and not foundation['fullyBuriedUpwardTriangles']
 result=module('tai_kwei_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-current-complete-original-physical-diagnostic-v1',list(set(refs)),dict(uids=[UID],identityPassed=identity['passed'],identityReasons=identity['reasons'],foundation=foundation,strictFoundationAccepted=strict,fullAcceptance=False,nextStep='Resolve current Tai Kwei identity and physical failures against original source and adjacent forms; no source edits or threshold waiver.'))
 print(dict(jobId=result['jobId'],identityPassed=identity['passed'],identityReasons=identity['reasons'],strictFoundationAccepted=strict,foundation=foundation),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 require_remaining(BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json',UID,SHA);assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
