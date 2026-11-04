"""UNEXECUTED ROOT-accepted source-identification-only interpretation, fresh ordinary replay."""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid,argparse
import upton_adjacent_original_roof_wall_identity_context_draft_v1_20261011 as adjacent
import upton_adjacent_roof_wall_identity_only_wrapper_v1_20261011 as identity_wrapper
from upton_exact_actual_history_archive_bindings_draft_v1_20261011 import load_contract,exact_ref
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify_files
from government_owned_identity import verify_files,POLICY
UID,SUPPORT='landsd/12728:0','landsd/12662:0'
PROTECTED=[UID,SUPPORT,'landsd/338946:0']
BATCH='government-xl-upton12728-12662-current-source-identification-rebind-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-upton-podium12728-12662-original-foreign-conflict-proposal-v1-20261011/source-inputs.json'
# Explicit root-provided current pins required on every future invocation; never
# inherit an old947f manifest/count after another publication.
MANIFEST_SHA=None;NATIVE_COUNT=None;HISTORY=None;HISTORY_REF=None
EXPECTED={u:(x[3],x[0],x[2],x[4],x[1])for u,x in adjacent.EXACT.items()}
VALIDATION=ROOT/'docs/astra-city/government-import/government-xl-upton-adjacent-original-roof-wall-identity-context-draft-v1-20261011/offline-23-tests-v1-validation.json'
MODULE_CAPTURE=HERE/'upton_source_identification_runtime_closures_draft_v1_20261011.mjs'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def native_rows():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  return c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[v[0]for v in EXPECTED.values()])).fetchall()
def review_state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(PROTECTED,)).fetchall()
def verify_completed_source_context():
 # Existing immutable complete jobs only; no current acceptance inherited.
 # Any changed historical path fails until a genuine exact archive is reviewed.
 for batch in ['government-xl-upton338946-podium12728-current-unchanged-owned-identity-v1-20261011','government-xl-upton-podium12728-12662-frozen-json-key-readback-recovery-v1-20261011','government-xl-upton-podium-boundary23-exact-roles-official-context-v1-20261011']:
  result=read(ROOT/'docs/astra-city/government-import'/batch/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  for e in result['evidenceRefs']:exact_ref(ROOT,e,HISTORY)
def main():
 global MANIFEST_SHA,NATIVE_COUNT,HISTORY,HISTORY_REF
 parser=argparse.ArgumentParser();parser.add_argument('--expected-manifest',required=True);parser.add_argument('--expected-native-count',required=True,type=int);parser.add_argument('--actual-history-contract',required=True);parser.add_argument('--expected-history-contract-sha',required=True);parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 MANIFEST_SHA=args.expected_manifest;NATIVE_COUNT=args.expected_native_count
 assert len(MANIFEST_SHA)==64 and NATIVE_COUNT==6649, 'Explicit post-Heya scene required; do not execute against old6648'
 HISTORY=load_contract(ROOT,args.actual_history_contract,args.expected_history_contract_sha)
 HISTORY_REF=ref(ROOT/args.actual_history_contract)
 # No test-code changes after the separately approved offline validation.
 validation=read(VALIDATION);assert validation['passed']and validation['exitCode']==0 and validation['expectedTests']==23
 for e in validation['codeRefs']+[validation['log']]:assert ref(ROOT/e['path'])==e
 if not args.owned:
  assert not DOC.exists()and not LOCAL.exists()
  claim=reservations.claim('upton-pair-current-owned-identity-'+str(uuid.uuid4()),['building:'+u for u in PROTECTED],batch=BATCH,ttl=1800);assert claim['ok'],claim
  lease=LOCAL/'reservation.json';save(lease,json.loads(json.dumps(claim['reservation'],default=str)))
  status=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease),'--ttl','1800','--',sys.executable,__file__,'--owned','--expected-manifest',MANIFEST_SHA,'--expected-native-count',str(NATIVE_COUNT),'--actual-history-contract',args.actual_history_contract,'--expected-history-contract-sha',args.expected_history_contract_sha],cwd=ROOT).returncode
  assert status==0,status;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_bytes=manifest_path.read_bytes();assert digest(manifest_bytes)==MANIFEST_SHA
 manifest=json.loads(manifest_bytes);catalogues=[ROOT/'3d-viewer'/p for p in manifest['officialModelCatalogues']];catalogue_refs=[ref(p)for p in catalogues]
 entries=[(p,m)for p in catalogues for m in read(p)['models']];assert len(entries)==NATIVE_COUNT and len({m['uid']for _,m in entries})==NATIVE_COUNT
 assert not any(m['uid']in EXPECTED for _,m in entries),'Actor membership changed; no silent installed-source reuse'
 verify_completed_source_context()
 protected_before=review_state();data=read(INPUT);sources=data['sources'];assert len(sources)==2 and {r['uid']for r in sources}==set(EXPECTED)
 provenance=data['evidenceRefs']
 for e in provenance:exact_ref(ROOT,e,HISTORY)
 native_before=native_rows();assert len(native_before)==2
 source_refs=[]
 for r in sources:
  model,sha,csuid,count,world_sha=EXPECTED[r['uid']]
  assert(r['modelId'],r['sourceSHA256'],r['source']['building']['buildingCSUID'],r['triangles'])==(model,sha,csuid,count)
  asset=ROOT/r['candidate']['path'];assert ref(asset)['sha256']==sha;source_refs.append(ref(asset))
  matches=[x for x in native_before if x[1]['modelId']==model];assert len(matches)==1
  assert matches[0]==(r['native']['cacheKey'],r['native']['model'],r['native']['sheet'],r['native']['resultSha'])
 walker=module('reviewed_source_closure',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');code_paths=set();walker.local_imports(Path(__file__),code_paths)
 for name in ['xl-final-script-pass.py','xl-second-pass.py','xl-popcorn-source-investigations-checkpoints-20261009.py']:walker.local_imports(HERE/name,code_paths)
 production=[ROOT/'3d-viewer/city'/p for p in ['app.js','world.js','geo.js','native-terrain.js']];assert all(p.is_file()for p in production)
 input_pins=[ref(p)for p in sorted(code_paths|set(production)|{INPUT,VALIDATION,MODULE_CAPTURE,HERE/'literal_production_module_dependency_closure_20261010.mjs',ROOT/HISTORY_REF['path']})]
 # Snapshot the literal production import closures now; reverify unchanged at end.
 DOC.mkdir(parents=True);subprocess.run(['node',str(MODULE_CAPTURE),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 runtime_paths=[DOC/('runtime-'+name+'-closure.json')for name in ['app','world','geo','native-terrain']]
 runtime_refs=[ref(p)for p in runtime_paths]
 save(DOC/'runtime-closure-bindings.json',dict(modules=runtime_refs,runtimeAccepted=False))
 final=module('fresh_current_identity_forms',HERE/'xl-final-script-pass.py');contexts=[];fresh_rows=[];results=[];forms_by_uid={};tiles=set()
 for original in sources:
  assert reservations.heartbeat(lease)['ok']
  row=dict(original);uid=row['uid'];model,sha,csuid,count,world_sha=EXPECTED[uid]
  tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert tri.shape==(count,3,3)and np.isfinite(tri).all()and digest(tri.astype('<f8').tobytes())==world_sha
  low,high=tri.min((0,1)),tri.max((0,1));forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2]);own=[x for x in forms if x[0]['uid']==uid];assert len(own)==1
  form,_,tile=own[0];assert form['buildingCSUID']==csuid
  row['source']=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
  context=dict(uid=uid,sourceSHA256=sha,identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms})
  raw=raw_verify_files(row,context,LOCAL/('raw-full-cell-identity-'+uid.split('/')[1].replace(':','-')))
  owned=verify_files(row,context,LOCAL/('original-owned-identity-'+uid.split('/')[1].replace(':','-')));assert owned['policy']==POLICY and owned['uid']==uid
  results.append(dict(uid=uid,completeOriginalFaces=count,completeWorldTrianglesSHA256=world_sha,rawFullCellIdentity=raw,ownedIdentity=owned));fresh_rows.append(row);contexts.append(context)
  for f,_,t in forms:
   if f['uid']in forms_by_uid:assert forms_by_uid[f['uid']]==f
   forms_by_uid[f['uid']]=f;tiles.add(t)
 # Keep independently recomputed raw/owned outcomes for BOTH podium actors.
 context,triangles=adjacent.frozen_context(ROOT)
 for path,h in adjacent.PINS.items():assert ref(ROOT/path)['sha256']==h
 save(DOC/'complete-current-catalogue-bindings.json',dict(nativeCount=NATIVE_COUNT,catalogues=catalogue_refs))
 save(DOC/'complete-current-original-source-bindings.json',dict(sourceRefs=source_refs,nativeRows=native_before,sourceInput=ref(INPUT)))
 complete_forms=[forms_by_uid[k]for k in sorted(forms_by_uid)]
 own_proof=next(r['rawFullCellIdentity']for r in results if r['uid']==UID)
 binding=dict(manifestSHA256=MANIFEST_SHA,ordinaryProofCanonicalSHA256=adjacent.digest(adjacent.canonical(own_proof)),completeFormsCanonicalSHA256=adjacent.digest(adjacent.canonical(complete_forms)),requiredFileRefs=dict(manifest=ref(manifest_path),runtimeClosure=ref(DOC/'runtime-closure-bindings.json'),nativeCatalogue=ref(DOC/'complete-current-catalogue-bindings.json'),buildingSourceCatalogue=ref(DOC/'complete-current-original-source-bindings.json')))
 draft=adjacent.assess_draft(ROOT,own_proof,complete_forms,binding,context,triangles)
 foreign=next(r for r in results if r['uid']==SUPPORT)
 identity_only=identity_wrapper.apply_identity_only(ROOT,own_proof,foreign['rawFullCellIdentity'],foreign['ownedIdentity'],complete_forms,binding,context,triangles)
 save(DOC/'source-identification-only.json',identity_only)
 assert draft['identityAccepted']is False and draft['installationApproved']is False and draft['physicalAccepted']is False
 save(DOC/'draft-adjacent-context-assessment.json',draft)
 subprocess.run(['node',str(MODULE_CAPTURE),str(DOC.relative_to(ROOT))+'/','--verify'],cwd=ROOT,check=True)
 for e in runtime_refs:assert ref(ROOT/e['path'])==e
 assert manifest_path.read_bytes()==manifest_bytes and reservations.owns(lease)
 for e in input_pins+catalogue_refs+source_refs:assert ref(ROOT/e['path'])==e
 for e in provenance:exact_ref(ROOT,e,HISTORY)
 for context in contexts:
  for path,sha in context['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==sha
 assert native_rows()==native_before and review_state()==protected_before
 save(DOC/'protected-review-state-before.json',dict(rows=protected_before,sourceOnly=True));save(DOC/'selection.json.gz',dict(rows=fresh_rows,manifestSHA256=MANIFEST_SHA));save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'complete-current-forms.json.gz',dict(rows=[forms_by_uid[k]for k in sorted(forms_by_uid)]));save(DOC/'identities.json',dict(rows=results))
 save(DOC/'complete-two-native-source-memberships.json',dict(nativeRun=NATIVE_RUN,rows=[dict(cacheKey=k,model=m,sheet=s,resultSHA256=h)for k,m,s,h in native_before],sourceInputs=ref(INPUT)))
 save(DOC/'current-input-bindings.json',dict(manifestSHA256=MANIFEST_SHA,nativeCount=NATIVE_COUNT,bothUninstalled=True,catalogues=catalogue_refs,inputPins=input_pins,sourcePins=source_refs,historicalSourceSelectionRefs=provenance,runtimeAcceptance=False))
 (DOC/'captured-manifest.json').write_bytes(manifest_bytes)
 freeze=module('identity_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 paths=list(code_paths|set(production)|{INPUT,VALIDATION,MODULE_CAPTURE,HERE/'literal_production_module_dependency_closure_20261010.mjs'});paths += [ROOT/p for p in adjacent.PINS]+[ROOT/e['path']for e in validation['codeRefs']+[validation['log']]];paths +=[ROOT/e['path']for e in source_refs]+[ROOT/exact_ref(ROOT,e,HISTORY)['actualVerifiedFile']['path']for e in provenance]+catalogues+[ROOT/'3d-viewer'/t for t in tiles]+[p for p in LOCAL.rglob('*')if p.is_file()]
 result=freeze.freeze(BATCH,'upton-fresh-source-identification-only-no-physical-or-installation',paths,dict(uids=[UID,SUPPORT],manifestSHA256=MANIFEST_SHA,completeOriginalFaces=2047,completeCurrentForms=len(forms_by_uid),identityOutcomes=[dict(uid=r['uid'],rawStrictPassed=r['rawFullCellIdentity']['passed'],rawReasons=r['rawFullCellIdentity']['reasons'],ownedPassed=r['ownedIdentity']['passed'],ownedReasons=r['ownedIdentity']['reasons'])for r in results],draftContextQualified=draft['draftContextQualified'],identityAccepted=identity_only['passed'],physicalAccepted=False,scriptFullAcceptancePassed=False,canStartTerrainWork=False,qualification='Fresh unchanged ordinary raw/owned proofs plus ROOT-accepted source-identification interpretation only. Historical selection provenance is not current runtime proof. Earlier podium1.910445m2 foreign overlap and tower737body obligations remain independent. No geometry/source pose edit, support/root/runtime/native approval, installation, terrain, threshold waiver or optimisation.'))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert review_state()==protected_before
 print(json.dumps(dict(jobId=result['jobId'],outcomes=result['identityOutcomes'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
