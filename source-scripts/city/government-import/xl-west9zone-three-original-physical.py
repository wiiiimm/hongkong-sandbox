"""Fresh full physical proof for three unchanged original WEST9ZONE components.

No geometry edits, publication or general acceptance waiver. Actual original
support faces replace only terrain-only contact diagnostics for the two towers.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row,NATIVE_RUN
from government_georef_cell_identity import verify_files as individual_verify
from retained_component_geographic_identity import verify_files as group_verify
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BATCH='government-xl-west9zone-three-original-physical-20261008'
DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
BASE=ROOT/'docs/astra-city/government-import/government-xl-west9zone-three-original-identities-20261008'
OLD=ROOT/'docs/astra-city/government-import/government-xl-west9zone-current-retained-terrain-20261007'
SEAMS=ROOT/'docs/astra-city/government-import/government-xl-west9zone-original-contact-seams-20261008/interfaces.json'
PRIMARY='landsd/227099:0';UIDS={PRIMARY,'landsd/81972:0','landsd/83691:0'}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 selection=read(BASE/'selection.json.gz');rows=selection['rows'];manifest_path=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest_path.read_bytes())==selection['manifestSHA256'];manifest=read(manifest_path)
 contexts={c['uid']:c for c in read(BASE/'context.json.gz')['rows']};seams=read(SEAMS)
 for path,sha in seams['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 interfaces={r['uid']:r for r in seams['rows']};assert set(interfaces)==UIDS-{PRIMARY}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)',(sorted(UIDS),)).fetchall()
  for r in rows:assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
 identities=[]
 for row in rows:
  proof=(group_verify if row['uid']==PRIMARY else individual_verify)(row,contexts[row['uid']],LOCAL/'identity'/row['uid'].split('/')[1]);assert proof['passed'],proof['reasons'];identities.append(proof)
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT))
 save(DOC/'owned-source-identity.json',{'rows':identities});save(DOC/'selection.json.gz',selection)
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area=BATCH,models=[r['candidate']['entry'] for r in rows],counts={'packedModels':3});save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',{'models':3,'catalogues':['catalogue.json']});save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
 patches=read(OLD/'terrain-candidates.json');assert len(patches)==1;patch=patches[0]
 assert ref(ROOT/patch['path'])['sha256']==patch['sha256'];assert digest((ROOT/'3d-viewer'/patch['replaces']['url']).read_bytes())==patch['replaces']['sha256'];save(DOC/'terrain-candidates.json',patches);save(DOC/'terrain.json',{'patches':patches,'originalRetainedTerrainEvidence':ref(OLD/'terrain.json'),'modelGeometryChanges':0,'terrainReconstructionChangesSincePriorCandidate':0})
 final=module('west_three_final','xl-final-script-pass.py');forms=final.load_forms(patch['bounds']);native={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};assert not native&UIDS
 save(DOC/'neighbour-inputs.json.gz',{'rows':[{'building':b,'patchIndexes':[0],'existingNative':b['uid'] in native or bool(b.get('modelGeometry'))} for b,_,_ in forms],'inputHashes':{str((ROOT/'3d-viewer'/url).relative_to(ROOT)):digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms},'candidateIds':sorted(UIDS),'patches':patches})
 def call(args,allowed=(0,)):
  assert subprocess.run(args,cwd=ROOT).returncode in allowed;assert reservations.owns(lease)
 rel=lambda p:str(p.relative_to(ROOT))
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 geometry={g['uid']:g for g in read(LOCAL/'runtime-geometry.json.gz')['rows']};assert set(geometry)==UIDS
 triangles={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for u,g in geometry.items()}
 foundations=[];decisions=[];reasons=[];metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module('west_three_numeric','acceptance-policy.py')
 for row in rows:
  uid=row['uid'];ground=np.asarray(geometry[uid]['drawnGroundGeometry']).reshape(-1,3,3)
  if uid!=PRIMARY:ground=np.concatenate([ground,triangles[PRIMARY]])
  b=row['source']['building'];f=final.foundation_context(triangles[uid],ground,Polygon(b['rings'][0],b['rings'][1:]));foundation={'uid':uid,'sourceSHA256':row['sourceSHA256'],'foundation':f,'strictFoundationAccepted':f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0,'supportUid':PRIMARY if uid!=PRIMARY else None};foundations.append(foundation)
  m=next(r for r in metrics['rows'] if r['uid']==uid);v=next(r for r in validation['results'] if r['uid']==uid);positive=next(p for p in identities if p['uid']==uid)
  raw=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':positive['proof']},m,metrics['profiles']['mobile']);diagnostic=resolve_global_bottom_warning(v,m,foundation);remaining=list(raw);remaining_diagnostics=diagnostic['remaining'];contact=False
  if uid!=PRIMARY:
   interface=interfaces[uid];assert interface['sourceSHA256']==row['sourceSHA256'] and interface['supportSHA256']==next(r for r in rows if r['uid']==PRIMARY)['sourceSHA256']
   p=interface['interface'];raw_interface=p['rawInterface'];assert p['policy']=='exact-original-contact-seams-v1' and p['maximumEmbeddingM']==.5 and p['exactSeamToleranceM']==.001
   assert p['strictContacts']+p['wallIntersections']+p['seamCorrections']+len(p['unresolved'])==p['samples']
   contact=p['passed'] and p['samples']>0 and p['strictContacts']>0 and not p['unresolved'] and foundation['strictFoundationAccepted']
   # Only ground-gap diagnostics are replaced by exact real original support.
   # Source/terrain penetration, sampler agreement, identity, mobile budgets,
   # loader and every complete foundation gate remain unchanged.
   if contact:
    resolved={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom'};remaining=[r for r in remaining if r not in resolved];remaining_diagnostics=[r for r in remaining_diagnostics if r not in resolved]
   else:remaining.append('original-support-interface-or-compound-foundation')
  if not foundation['strictFoundationAccepted']:remaining.append('whole-source-foundation')
  decisions.append({'uid':uid,'rawNumericReasons':raw,'diagnosticResolution':diagnostic,'originalSupportContactAccepted':contact,'remainingNumericReasons':remaining,'remainingDiagnosticReasons':remaining_diagnostics})
  reasons.extend(uid+':'+r for r in [*remaining,*remaining_diagnostics]);print(json.dumps({'uid':uid,'foundation':foundation,'remaining':remaining+remaining_diagnostics}),flush=True)
 save(DOC/'foundation.json',{'rows':foundations});save(DOC/'physical-decisions.json',{'rows':decisions});save(DOC/'support-checks.json',seams)
 if validation['checksPassed']!=3 or validation['loaderAccepted']!=3 or validation['exceptions']:reasons.append('runtime-validation')
 native_check=read(DOC/'native-neighbour-checks.json');resolved=set(native_check['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native_check['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
 refs=[ref(p) for p in sorted(DOC.iterdir()) if p.is_file()]+[ref(p) for p in [Path(__file__),BASE/'selection.json.gz',BASE/'context.json.gz',SEAMS,LOCAL/'catalogue.json',LOCAL/'source-forms.json',LOCAL/'runtime-geometry.json.gz',HERE/'original-contact-seams.mjs',HERE/'test-original-contact-seams.mjs',HERE/'retained_component_geographic_identity.py',HERE/'government_georef_cell_identity.py',HERE/'xl-final-script-pass.py']]
 for report in [metrics,validation,read(DOC/'neighbour-inputs.json.gz'),native_check,seams]:refs.extend({'path':p,'sha256':h} for p,h in (report.get('inputHashes') or report.get('hashes') or {}).items())
 refs=list({r['path']:r for r in refs}.values());payload={'uids':sorted(UIDS),'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in rows},'manifestSHA256':selection['manifestSHA256'],'evidenceRefs':refs};stage='three-original-contact-seams-full-physical-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'reasons':sorted(set(reasons)),'scriptChecksPassed':not reasons,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'qualification':'Exact original support seam corrections retain all raw ray diagnostics. Three actual candidate originals require complete fresh terrain/compound-foundation/runtime checks; all other basic and native neighbours, including retained229310, are checked. No browser or publication credit.'}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for item in refs:assert ref(ROOT/item['path'])==item
  assert digest(manifest_path.read_bytes())==selection['manifestSHA256']
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'scriptChecksPassed':not reasons,'reasons':result['reasons'],'neonVerified':True}),flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();selection=read(BASE/'selection.json.gz');assert {r['uid'] for r in selection['rows']}==UIDS
 final=module('west_three_scope','xl-final-script-pass.py');patch=read(OLD/'terrain-candidates.json')[0];scope={b['uid'] for b,_,_ in final.load_forms(patch['bounds'])}|UIDS|set(patch['replaces']['retainedUids'])
 claim=reservations.claim('codex-west-three-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope)]+['terrain-patch:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
