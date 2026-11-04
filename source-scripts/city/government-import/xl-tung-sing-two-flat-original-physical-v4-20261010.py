"""Complete bounded five-original physical/renderer/neighbour pass; never publish."""
import importlib.util,sys,subprocess,uuid,json,traceback
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,NATIVE_RUN
from terrain_source_preflight import SourceSheetIndex
from publication_lock import locked_publication
from tung_sing_flat_two_original_collection_identity_v3_20261010 import verify_files,UIDS,POLICY
BATCH='government-xl-tung-sing-two-flat-original-physical-v4-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;BASE=LOCAL/'frozen-inputs';INPUT=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-interior-current-identity-inputs-v2-20261010'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare():
 selection=read(INPUT/'selection.json.gz');assert {r['uid'] for r in selection['rows']}==UIDS
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');second=module('miami_phys_prepare_decode','xl-second-pass.py');second.LOCAL=LOCAL;final=module('miami_phys_current_context','xl-final-script-pass.py');(LOCAL/'assets').mkdir(parents=True,exist_ok=True)
 native_parent=read(ROOT/'3d-viewer/city/data/government-native-163705-0.json');g=native_parent['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(native_parent['w']-1)*g['aE'],816500-g['bN']-(native_parent['h']-1)*g['aN']];scope={b['uid'] for b,_,_ in final.load_forms(bounds)}|set(read(ROOT/'3d-viewer/city/data/government-native-163705-0.json')['meta']['targetUids']);contexts=[]
 for row in selection['rows']:
  row.setdefault('currentReview',None);row['triangles']=row['native']['model']['triangles'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw)
  lo,hi=row['native']['model']['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tri=second.glb_triangles(row);contexts.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}})
 return {**selection,'batch':BATCH,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'nativeRun':NATIVE_RUN},{'rows':contexts},scope
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);selection=read(BASE/'check-selection.json.gz');contexts=read(BASE/'context.json.gz');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256'];identities=[];identity_paths={}
 for row in selection['rows']:
  context=next(c for c in contexts['rows'] if c['uid']==row['uid']);proof=verify_files(row,context,LOCAL/'identity-precheck');assert proof['passed'];path=DOC/('owned-identity-'+row['uid'].split('/')[1].replace(':','-')+'.json');save(path,proof);identities.append(proof);identity_paths[row['uid']]=path
 save(DOC/'owned-source-identity.json',{'rows':identities});terrain=module('miami_phys_original_tin','xl-routed-cell-indexed-terrain-continuation.py');index=SourceSheetIndex(read(ROOT/'source-scripts/city/landmark-acquisition/index.json'));sheets=sorted({s['sheet'] for r in selection['rows'] for s in index.covering_sheets(r['native']['model']['worldBounds'])});recovered=[terrain.terrain_sheet(s,LOCAL) for s in sheets];save(DOC/'source-recovery.json',{'sheets':[p for _,p in recovered],'sourceGeometryChanges':0,'publication':False})
 resolution=module('miami_phys_all_current_gates','xl-tung-sing-two-flat-original-contact-resolution-v3-20261010.py');resolution.BATCH=BATCH;resolution.BASE=BASE;resolution.DOC=DOC;resolution.LOCAL=LOCAL;resolution.UIDS=[r['uid'] for r in selection['rows']];resolution.OWNED_IDENTITY_PATHS=identity_paths;resolution.NESTED_PARENT=False;resolution.PARENT_URL='city/data/government-native-163705-0.json';resolution.SOURCE=recovered[0][0];resolution.ADJACENT_SOURCES=[f for f,_ in recovered[1:]];reasons=[]
 try:resolution.owned()
 except (AssertionError,KeyError) as e:save(DOC/'guard-failure.json',{'error':str(e),'traceback':traceback.format_exc(),'publication':False});reasons.append('complete-five-original-physical-guard:'+str(e))
 if not reasons:
  metrics=read(DOC/'metrics.json');foundation=read(DOC/'foundation.json');validation=read(DOC/'validation.json');policy=module('miami_phys_unchanged_policy','acceptance-policy.py');decisions=[]
  from terrain_diagnostic_resolution import resolve_global_bottom_warning
  for row in selection['rows']:
   uid=row['uid'];m=next(r for r in metrics['rows'] if r['uid']==uid);f=next(r for r in foundation['rows'] if r['uid']==uid);positive=next(p for p in identities if p['uid']==uid);raw=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':positive['proof']},m,metrics['profiles']['mobile']);diagnostic=resolve_global_bottom_warning(next(v for v in validation['results'] if v['uid']==uid),m,f);reasons.extend(uid+':'+r for r in raw+diagnostic['remaining']);
   if not f['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
   decisions.append({'uid':uid,'rawNumericReasons':raw,'diagnosticResolution':diagnostic})
  save(DOC/'physical-decisions.json',{'rows':decisions});
  if validation['checksPassed']!=len(UIDS) or validation['loaderAccepted']!=len(UIDS) or validation['exceptions']:reasons.append('runtime-validation')
  native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
 reasons.append('complete-component-role:original-tower-detached-parts-343-344-unresolved');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256'],'Current manifest changed during candidate; no acceptance'
 freezer=module('miami_phys_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');paths=[Path(__file__),BASE/'check-selection.json.gz',BASE/'context.json.gz',HERE/'tung_sing_flat_two_original_collection_identity_v3_20261010.py',HERE/'tung_sing_interior_current_bound_identity_v2_20261010.py',HERE/'tung_sing_adjacent_original_envelope_identity_20261010.py',HERE/'xl-tung-sing-two-flat-original-contact-resolution-v3-20261010.py',HERE/'xl-routed-cell-contact-resolution.py']
 for name in ['metrics.json','validation.json','neighbour-inputs.json.gz','native-neighbour-checks.json']:
  if (DOC/name).exists():paths.extend(ROOT/p for p in (read(DOC/name).get('inputHashes') or read(DOC/name).get('hashes') or {}).keys())
 freezer.freeze(BATCH,'five-independent-complete-original-physical-runtime-neighbours-v1',paths,{'uids':sorted(UIDS),'scriptChecksPassed':not reasons,'reasons':sorted(set(reasons)),'sourceIdentityPolicy':POLICY,'identityAccepted':True,'scriptFullAcceptancePassed':not reasons,'remainingReason':'staged-and-live-browser-guarded-publication' if not reasons else 'complete-exact-physical-gate-recovery','nextStep':'Stage only if every recorded physical/runtime/neighbour gate passes; parent serializes publication, no browser or installed credit yet.'})
def main():
 if '--owned' in sys.argv:
  return owned()
 assert not DOC.exists() and not LOCAL.exists(),'Fresh named stage required';selected,contexts,scope=prepare();resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope|UIDS)]+['terrain-patch:'+u for u in sorted(UIDS)]+['terrain-surface:city/data/government-native-163705-0.json'];claim=reservations.claim('tung-sing-two-physical-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));save(BASE/'check-selection.json.gz',selected);save(BASE/'context.json.gz',contexts);subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
