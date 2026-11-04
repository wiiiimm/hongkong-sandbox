"""DRAFT fresh exact current owned-policy identity replay; raw strict negatives independent."""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify_files
from government_owned_identity import verify_files,POLICY
UID,SUPPORT='landsd/173512:0','landsd/139415:0'
BATCH='government-xl-youth-square173512-current-unchanged-owned-identity-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-eight-new-original-closures-20261008/support-inputs.json'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-youth-square173512-original-body-extent-podium-contacts-v2-20261011'
MANIFEST_SHA='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
EXPECTED={UID:('B424281381401063C0','a3905a76856bc0c622d7f09139995fd2429d294771b68e2385317056987fcea1','4242813814T20100329',13100),SUPPORT:('B424091381802063C0','1edf63068d903718bec435d4c9426f38192a1e5f32da1c439867a3cd530375a9','4240913818P20080619',22)}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def native_rows():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  return c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[v[0]for v in EXPECTED.values()])).fetchall()
def review_state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',([UID,SUPPORT],)).fetchall()
def main():
 if '--owned'not in sys.argv:
  assert not DOC.exists()and not LOCAL.exists()
  claim=reservations.claim('youth-current-owned-identity-'+str(uuid.uuid4()),['building:'+UID,'building:'+SUPPORT],batch=BATCH,ttl=1800);assert claim['ok'],claim
  lease=LOCAL/'reservation.json';save(lease,json.loads(json.dumps(claim['reservation'],default=str)))
  status=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode
  assert status==0,status;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_bytes=manifest_path.read_bytes();assert digest(manifest_bytes)==MANIFEST_SHA
 manifest=json.loads(manifest_bytes);catalogues=[ROOT/'3d-viewer'/p for p in manifest['officialModelCatalogues']];catalogue_refs=[ref(p)for p in catalogues]
 entries=[(p,m)for p in catalogues for m in read(p)['models']];assert len(entries)==6648 and len({m['uid']for _,m in entries})==6648
 assert not any(m['uid']in EXPECTED for _,m in entries),'Changed owned/support membership; do not silently reuse an installed actor'
 protected_before=review_state();prior=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for e in prior['evidenceRefs']:assert ref(ROOT/e['path'])==e
 sources=[r for r in read(INPUT)['sources']if r['uid']in EXPECTED];assert len(sources)==2 and len({r['uid']for r in sources})==2
 source_refs=[]
 for r in sources:
  model,sha,csuid,count=EXPECTED[r['uid']]
  assert(r['modelId'],r['sourceSHA256'],r['source']['building']['buildingCSUID'],r['triangles'])==(model,sha,csuid,count)
  asset=ROOT/r['candidate']['path'];assert ref(asset)['sha256']==sha;source_refs.append(ref(asset))
 native_before=native_rows();assert len(native_before)==2
 for r in sources:
  matched=[x for x in native_before if x[1]['modelId']==r['modelId']];assert len(matched)==1
  k,m,s,h=matched[0];assert(k,m,s,h)==(r['native']['cacheKey'],r['native']['model'],r['native']['sheet'],r['native']['resultSha'])
 # Source-only identity math is current-file-bound. No browser/runtime acceptance.
 walker=module('reviewed_source_closure',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py')
 code_paths=set();walker.local_imports(Path(__file__),code_paths)
 for name in ['xl-final-script-pass.py','xl-second-pass.py','xl-popcorn-source-investigations-checkpoints-20261009.py']:
  walker.local_imports(HERE/name,code_paths)
 production=[ROOT/'3d-viewer/city'/p for p in ['app.js','world.js','geo.js','native-terrain.js']]
 assert all(p.is_file()for p in production)
 input_pins=[ref(p)for p in sorted(code_paths|set(production)|{INPUT})]
 row=next(r for r in sources if r['uid']==UID);row=dict(row);tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert tri.shape==(13100,3,3)and np.isfinite(tri).all()
 assert digest(tri.astype('<f8').tobytes())=='6119e583590a5940678bec0e52b45e463c563fa8441a2f5ebe92fce68f3f5fc5'
 low,high=tri.min((0,1)),tri.max((0,1));final=module('fresh_current_identity_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2]);own=[x for x in forms if x[0]['uid']==UID];assert len(own)==1
 form,_,tile=own[0];assert form['buildingCSUID']==EXPECTED[UID][2]
 row['source']=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
 context=dict(uid=UID,sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms})
 raw=raw_verify_files(row,context,LOCAL/'raw-full-cell-identity');owned=verify_files(row,context,LOCAL/'original-owned-identity');assert owned['policy']==POLICY and owned['uid']==UID
 assert manifest_path.read_bytes()==manifest_bytes and reservations.owns(lease)
 for e in input_pins+catalogue_refs+source_refs:assert ref(ROOT/e['path'])==e
 for path,sha in context['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==sha
 assert native_rows()==native_before
 save(DOC/'protected-review-state-before.json',dict(rows=protected_before,sourceOnly=True));save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=MANIFEST_SHA));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'complete-current-forms.json.gz',dict(rows=[f for f,_,_ in forms]));save(DOC/'identity.json',owned);save(DOC/'raw-full-cell-identity.json',raw)
 save(DOC/'complete-two-native-source-memberships.json',dict(nativeRun=NATIVE_RUN,rows=[dict(cacheKey=k,model=m,sheet=s,resultSHA256=h)for k,m,s,h in native_before],sourceInputs=ref(INPUT)))
 save(DOC/'current-input-bindings.json',dict(manifestSHA256=MANIFEST_SHA,nativeCount=6648,ownedAndPodiumBothUninstalled=True,catalogues=catalogue_refs,inputPins=input_pins,sourcePins=source_refs,neighbourTileHashes=context['neighbourTileHashes'],runtimeAcceptance=False))
 (DOC/'captured-manifest.json').write_bytes(manifest_bytes)
 freeze=module('identity_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 paths=list(code_paths|set(production)|{INPUT,PRIOR/'result.json',PRIOR/'diagnostic.json.gz'});paths +=[ROOT/e['path']for e in source_refs]+catalogues+[ROOT/'3d-viewer'/t for _,_,t in forms]+[p for p in LOCAL.rglob('*')if p.is_file()]
 result=freeze.freeze(BATCH,'youth-square-current-unchanged-owned-identity-no-physical-credit',paths,dict(uids=[UID,SUPPORT],manifestSHA256=MANIFEST_SHA,completeOriginalFaces=13100,completeCurrentForms=len(forms),rawFullCellIdentityPassed=raw['passed'],rawIdentityReasons=raw['reasons'],ownedIdentityPassed=owned['passed'],ownedIdentityReasons=owned['reasons'],identityAccepted=owned['passed'],physicalAccepted=False,scriptFullAcceptancePassed=False,canStartTerrainWork=False,qualification='Existing unchanged government_owned_identity policy replay only. Raw complete strict cell and cached spatial/current extent/foreign negatives preserved. Both original native memberships/source/catalogue/forms and actual current code bytes independently fenced. No architectural role, source support, runtime, ground/native reapproval, installation, terrain or threshold waiver. Fresh actual four-world capture remains independent.'))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert review_state()==protected_before
 print(json.dumps(dict(jobId=result['jobId'],rawStrictPassed=raw['passed'],ownedPassed=owned['passed'],ownedReasons=owned['reasons'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
