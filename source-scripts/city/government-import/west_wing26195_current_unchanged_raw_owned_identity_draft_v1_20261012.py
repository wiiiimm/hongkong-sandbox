"""DRAFT existing legacy entry: fresh unchanged raw and owned identity only."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
import west_wing26195_complete_current_runtime_capture_draft_v2_20261012 as W
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
from government_owned_identity import verify_files as owned_verify,POLICY
BATCH='government-xl-west-wing26195-current-unchanged-raw-owned-identity-v1-20261012'
DOC=W.B/BATCH;LOCAL=HERE/'local'/BATCH
PROPOSAL=W.B/'government-xl-west-wing26195-fresh-raw-owned-identity-proposal-v1-20261012'
CACHE='828133bbea286a52de1484a5163766bfab7ee42b0b4c07a8be3e756f0cabe7e6'
NATIVE_SHA='9ef4f709c01591edac1bb64be27c347726ea68c401c0fc1f2806dc297994a2b9'
CAP_RESULT_SHA='f0d258f68002b03a010e6d3f8e99f8c18d6e5e6aff6a826806e379a619fb66bb'
WORLD_SHA='32969c0eb6a4ea9d4fbfab447ad4e374809399b88ecf82fd52534a1d2d1c712b'
ref=W.ref

def native_row():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  rows=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND r.cache_key=%s AND m->>'modelId'=%s",(NATIVE_RUN,CACHE,W.MODEL)).fetchall()
 assert len(rows)==1 and rows[0][0]==CACHE and rows[0][3]==NATIVE_SHA
 model=rows[0][1];assert model['modelId']==W.MODEL and model['triangles']==W.FACES and model['asset']['sha256']==W.SOURCE_SHA
 return rows[0]

def inputs():
 for e in read(PROPOSAL/'draft-code-pins.json')['refs']:assert ref(ROOT/e['path'])==e
 p=W.preflight();scope=read(W.DOC/'capture-scope.json');assert p['manifest']==scope['currentManifest']and scope['nativeCount']==6649
 assert ref(W.DOC/'result.json')['sha256']==CAP_RESULT_SHA;r=read(W.DOC/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 captured=read(W.DOC/'selection.json.gz')['rows'];assert len(captured)==1;old=captured[0]
 assert old['rawInstalledEntry']==p['entry']and old['actualCatalogue']==ref(p['catalogue'])
 catalogue=read(p['catalogue']);entry={**p['entry'],'rootTranslation':catalogue['rootTranslation'],'coordinatePolicy':catalogue.get('coordinatePolicy'),'datasetId':catalogue.get('datasetId')}
 assert entry==old['candidate']['entry']and entry['rootTranslation']==[-834500,0,816500]
 before=read(W.DOC/'protected-state-before.json');assert json.loads(json.dumps(W.state(before['uids']),default=str))==before['rows']
 assert sorted('building:'+u for u in before['uids'])==scope['canonicalReservationResources']and len(before['uids'])==15
 native=native_row()
 row=dict(old,triangles=W.FACES,native=dict(cacheKey=native[0],model=native[1],sheet=native[2],resultSha=native[3]))
 row['candidate']=dict(entry=entry,path=str(p['asset'].relative_to(ROOT)))
 return p,scope,before,native,row,r

def main():
 a=argparse.ArgumentParser();a.add_argument('--preflight-only',action='store_true');a.add_argument('--owned',action='store_true');args=a.parse_args()
 p,scope,before,native,row,capture=inputs()
 if args.preflight_only:
  print(json.dumps(dict(uid=W.UID,currentManifest=p['manifest'],nativeCount=6649,canonicalResources=scope['canonicalReservationResources'],cacheKey=native[0],nativeResultSHA=native[3],sourceSHA=W.SOURCE_SHA,metadataAdapterPreservesRawEntry=True,noNumericIdentityRun=True,noReservations=True)),flush=True);return
 if not args.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('westwing-current-identity-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 walker=W.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_identity_closure');codes=set();walker.local_imports(Path(__file__),codes)
 final=W.module(HERE/'xl-final-script-pass.py','westwing_fresh_identity_forms');walker.local_imports(HERE/'xl-final-script-pass.py',codes)
 freezer=W.module(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py','westwing_identity_freezer');walker.local_imports(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',codes)
 evidence=[ref(x)for x in sorted(codes)]+[ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'draft-code-pins.json'),ref(W.DOC/'result.json'),ref(W.DOC/'capture-scope.json'),ref(W.DOC/'selection.json.gz')]
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
  for e in evidence:assert ref(ROOT/e['path'])==e
  assert native_row()==native and json.loads(json.dumps(W.state(before['uids']),default=str))==before['rows']
 fence();assert reservations.heartbeat(lease)['ok']
 tri=decode_original_world_triangles(p['asset'].read_bytes());assert tri.shape==(W.FACES,3,3)and np.isfinite(tri).all()and digest(tri.astype('<f8').tobytes())==WORLD_SHA==scope['completeOriginalWorldSHA256']
 low,high=tri.min((0,1)),tri.max((0,1));forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2]);assert {f['uid']for f,_,_ in forms}<=set(before['uids'])
 own=[x for x in forms if x[0]['uid']==W.UID];assert len(own)==1;form,_,tile=own[0];assert form['buildingCSUID']==W.CSUID and form['objectId']==26195
 row['source']=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
 context=dict(uid=W.UID,sourceSHA256=W.SOURCE_SHA,identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms})
 raw=raw_verify(row,context,LOCAL/'raw-full-cell-identity');fence();assert reservations.heartbeat(lease)['ok']
 owned=owned_verify(row,context,LOCAL/'original-owned-identity');assert owned['policy']==POLICY;fence()
 for path,h in context['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==h
 save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=W.MANIFEST_SHA));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identities.json',dict(uid=W.UID,completeOriginalFaces=W.FACES,completeOriginalWorldSHA256=WORLD_SHA,rawFullCellIdentity=raw,ownedIdentity=owned,sourceOnly=True,physicalAccepted=False))
 save(DOC/'current-input-bindings.json',dict(currentManifest=scope['currentManifest'],nativeCount=6649,inputHashes=scope['inputHashes'],rawInstalledEntry=row['rawInstalledEntry'],cataloguePreparedEntry=row['candidate']['entry'],actualNativeSource=dict(cacheKey=native[0],model=native[1],sheet=native[2],resultSHA=native[3]),protectedState=before,sourceOnly=True,legacyAcceptanceBackfillAllowed=False))
 paths=sorted(codes)+[ROOT/e['path']for e in evidence+capture['evidenceRefs']]+[ROOT/'3d-viewer'/t for _,_,t in forms]+[x for x in LOCAL.rglob('*')if x.is_file()]+[PROPOSAL/'METHOD.md',PROPOSAL/'draft-code-pins.json'];fence()
 result=freezer.freeze(BATCH,'west-wing-fresh-unchanged-raw-owned-identity-no-physical-credit',paths,dict(uid=W.UID,sourceSHA256=W.SOURCE_SHA,currentManifestSHA256=W.MANIFEST_SHA,nativeCount=6649,completeOriginalFaces=W.FACES,rawStrictPassed=raw['passed'],rawReasons=raw['reasons'],ownedPassed=owned['passed'],ownedReasons=owned['reasons'],physicalAccepted=False,installationApproved=False,legacyAcceptanceBackfillAllowed=False,modelReviewWrites=0,qualification='Fresh unchanged raw and owned identity only; genuine cached native matching retained verbatim. Legacy metadata adapter does not invent shape matches or grant source/root/physical acceptance. All42 ordinary failures/443 strict flags/118 body obligations remain independent.'))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 fence();print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),rawStrictPassed=raw['passed'],rawReasons=raw['reasons'],ownedPassed=owned['passed'],ownedReasons=owned['reasons'],physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
