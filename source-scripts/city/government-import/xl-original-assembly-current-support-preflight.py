"""Full current-terrain checks for one verified complete original assembly member.

No terrain is replaced. Historical provisional decisions are retained. Existing
strict interface/compound foundation, all physical/runtime and neighbour gates
remain mandatory; this runner never installs or grants progress credit.
"""
import argparse,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row,NATIVE_RUN
from provisional_original_review import verify
from original_source_assembly_diagnostic import verify_files,POLICY
from original_assembly_member_identity import member_identity
from terrain_source_preflight import preflight,SourceSheetIndex
from terrain_diagnostic_resolution import resolve_global_bottom_warning
from current_installed_support_acceptance import compound_foundation,record_resolution
BASE=ROOT/'docs/astra-city/government-import/government-xl-twelve-provisional-original-inputs-20261007'


def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def owned(a,doc,local):
 CLOSURE=(ROOT/a.closure).resolve();assembly=(ROOT/a.assembly).resolve()
 assert CLOSURE.is_relative_to(ROOT/'docs/astra-city/government-import') and assembly.is_relative_to(ROOT/'docs/astra-city/government-import')
 lease=read(local/'reservation.json');assert reservations.owns(lease)
 prior_identity=read(assembly/'result.json');assert prior_identity['identityPassed'] and not prior_identity['reasons'] and a.uid in prior_identity['uids']
 for ref in prior_identity['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 prior=read(CLOSURE/'result.json');pairs=read(CLOSURE/'support-inputs.json')['pairs'];assert a.uid in {p['uid'] for p in pairs}
 inputs=read(CLOSURE/'support-inputs.json');pair=next(p for p in inputs['pairs'] if p['uid']==a.uid)
 rows=[r for r in inputs['sources'] if r['uid'] in {a.uid,pair['supportUid']}]
 contexts={r['uid']:r for r in read(CLOSURE/'context.json.gz')['rows']}
 row=next(r for r in rows if r['uid']==a.uid);context=contexts[a.uid]
 pinned=next(r for r in read(BASE/'check-selection.json.gz')['rows'] if r['uid']==a.uid)
 assert pinned['sourceSHA256']==row['sourceSHA256']
 row['currentReview']=pinned['currentReview']
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
  assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior_identity['jobId'],)).fetchone()==('complete',prior_identity)
  retained=verify(con,a.uid,row['sourceSHA256'],row['currentReview'])
 save(doc/'provisional-review-continuation.json',{'current':retained,'pinned':row['currentReview'],'publication':False})
 for name in ('support-inputs.json','support-checks.json.gz'):
  ref=next(x for x in prior['evidenceRefs'] if x['path']==str((CLOSURE/name).relative_to(ROOT)))
  assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
 for tile,sha in context['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
 interface=next(r for r in read(CLOSURE/'support-checks.json.gz')['rows'] if r['uid']==a.uid)
 compound=verify_files(rows,contexts,local/'identity-current',interface);assert compound['passed'],compound['reasons']
 assert compound==read(assembly/'assembly-identity.json')
 save(doc/'assembly-identity.json',compound)
 save(doc/'assembly-inputs.json',{'closure':a.closure,'assembly':a.assembly,'tower':a.uid,'supportUid':pair['supportUid']})
 positive=member_identity(compound,a.uid)
 save(doc/'owned-source-identity.json',positive);save(doc/'owned-source-identity-contact.json',positive)
 index=ROOT/'source-scripts/city/landmark-acquisition/index.json';routing=preflight(row,context,SourceSheetIndex(read(index)))
 routing['legacyProjectionIdentity']=routing['identity'];routing['identity']={'passed':True,'proof':positive['proof'],'reasons':[],'method':POLICY}
 routing['canStartTerrainWork']=routing['primarySheetIntersects'];assert routing['canStartTerrainWork']
 routing['inputHashes']={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [index,BASE/'context.json.gz',Path(__file__),HERE/'provisional_original_review.py',HERE/'test_provisional_original_review.py',HERE/'current_installed_support_acceptance.py',HERE/'government_georef_cell_identity.py',HERE/'original_source_assembly_diagnostic.py',HERE/'original_assembly_member_identity.py',CLOSURE/'support-inputs.json',assembly/'result.json']}
 save(doc/'indexed-preflight.json',routing)
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
 dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT))
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);manifest_sha=digest(manifest_path.read_bytes())
 assert not any(m['uid']==a.uid for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'])
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area=a.batch,models=[row['candidate']['entry']],counts={'packedModels':1})
 save(local/'catalogue.json',catalogue);save(local/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']});save(local/'source-forms.json',{a.uid:row['source']})
 save(doc/'selection.json.gz',{'rows':[row],'batch':a.batch,'manifestSHA256':manifest_sha})
 save(doc/'terrain-candidates.json',[]);save(doc/'terrain.json',{'patches':[],'sourceFiles':[],'modelGeometryChanges':0,'terrainGeometryChanges':0})
 save(doc/'existing-terrain-only.json',{'manifestSHA256':manifest_sha,'closureResult':{'path':str((CLOSURE/'result.json').relative_to(ROOT)),'sha256':digest((CLOSURE/'result.json').read_bytes())},'qualification':'No terrain replacement; fresh exact currently installed source support interfaces and whole compound foundation required.'})
 final=module('current_support_foundation','xl-final-script-pass.py');lo,hi=row['native']['model']['worldBounds'];neighbours=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);native={e['uid'] for u in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/u)['models']}
 save(doc/'neighbour-inputs.json.gz',{'rows':[{'building':b,'patchIndexes':[],'existingNative':b['uid'] in native or bool(b.get('modelGeometry'))} for b,_,_ in neighbours],
  'inputHashes':{str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in neighbours},'candidateIds':[a.uid],'patches':[]})
 rel=lambda p:str(p.relative_to(ROOT))
 def call(command,allowed=(0,)):
  assert subprocess.run(command,cwd=ROOT).returncode in allowed;assert reservations.owns(lease)
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(doc/'selection.json.gz'),'--candidates',rel(local),'--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'metrics.json'),'--geometry-out',rel(local/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(local),'--source-forms',rel(local/'source-forms.json'),'--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(doc)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(doc)+'/'])
 geom=read(local/'runtime-geometry.json.gz')['rows'][0];triangles=np.asarray(geom['position']).reshape(-1,3)[np.asarray(geom['index']).reshape(-1,3)];ground=np.asarray(geom['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building']
 foundation,support=compound_foundation(doc,local,row,triangles,ground,Polygon(b['rings'][0],b['rings'][1:]),CLOSURE)
 f={'uid':a.uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,'strictFoundationAccepted':foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0};save(doc/'foundation.json',{'rows':[f],'modelGeometryChanges':0})
 save(doc/'identity-proof.json',{'uid':a.uid,'sourceSHA256':row['sourceSHA256'],'proof':positive['proof'],'method':POLICY,'ownedSourceProofSHA256':digest((doc/'owned-source-identity.json').read_bytes()),'preflightSHA256':digest((doc/'indexed-preflight.json').read_bytes())})
 metrics=read(doc/'metrics.json');diagnostic=resolve_global_bottom_warning(read(doc/'validation.json')['results'][0],metrics['rows'][0],f);save(doc/'diagnostic-resolution.json',diagnostic)
 reasons=module('current_support_policy','acceptance-policy.py').reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':positive['proof']},metrics['rows'][0],metrics['profiles']['mobile'])
 reasons,remaining=record_resolution(doc,reasons,diagnostic['remaining'],support);reasons+=remaining
 if not f['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 for path,sha in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 assert digest(manifest_path.read_bytes())==manifest_sha
 native_checks=read(doc/'native-neighbour-checks.json');resolved=set(native_checks['resolved'])
 assert all(x['maxGroundChange']==0 for x in read(doc/'neighbour-checks.json')['rows'])
 reasons.extend('terrain-regresses-neighbour:'+x['uid'] for x in read(doc/'neighbour-checks.json')['rows'] if x['reasons'] and x['uid'] not in resolved)
 reasons.extend('native-neighbour-regression:'+u for u in set(native_checks['blocked'])-resolved)
 finish(a,row,doc,local,reasons)

def finish(args, row, doc, local, reasons):
    receipt = read(local / 'reservation.json')
    assert reservations.owns(receipt)
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in sorted(doc.iterdir()) if p.is_file() and p.name not in ('result.json', 'neon-sync.json', 'README.md')]
    payload = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'evidenceRefs': refs,
               'runnerSHA256': digest(Path(__file__).read_bytes()),
               'installedSupportPolicySHA256': digest((HERE/'current_installed_support_acceptance.py').read_bytes()), 'identityPolicy': POLICY}
    stage = 'complete-original-assembly-current-support-continuation-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'reasons': sorted(set(reasons)),
              'humanStatus': 'held-unknown' if reasons else 'in-process',
              'scriptChecksPassed': not reasons, 'newlyInstalled': 0, 'publication': False,
              'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'activeWorkers': 0,
              'queuedFollowups': 0, 'requiresAI': False, 'requiresHumanDecision': False,
              'nextStep': 'Resolve exact recorded original terrain/source/support blockers with unchanged physical acceptance limits.' if reasons else 'Complete staged and live browser checks, guarded publication and installed ledger.'}
    with connect() as con:
        from provisional_original_review import verify
        from psycopg.rows import tuple_row
        con.row_factory = tuple_row
        verify(con, row['uid'], row['sourceSHA256'], row['currentReview'])
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, receipt)
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha'] == row['native']['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'uid': row['uid'], 'checksPassed': not reasons, 'reasons': result['reasons'], 'jobId': jobid, 'neonVerified': True}), flush=True)


def main():
 p=argparse.ArgumentParser();p.add_argument('--closure',required=True);p.add_argument('--assembly',required=True);p.add_argument('--uid',required=True);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned(a,doc,local)
  return
 assert not doc.exists(),'Fresh full current support proof only'
 CLOSURE=(ROOT/a.closure).resolve();assert CLOSURE.is_relative_to(ROOT/'docs/astra-city/government-import')
 pair=next(x for x in read(CLOSURE/'support-inputs.json')['pairs'] if x['uid']==a.uid)
 claim=reservations.claim('codex-xl-current-provisional-support-'+str(uuid.uuid4()),['building:'+a.uid,'building:'+pair['supportUid']],batch=a.batch);assert claim['ok'],claim
 save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
