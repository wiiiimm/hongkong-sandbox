"""Fresh full physical checks for one unchanged original tower/podium pair.

Neither part receives installed credit here. An exact strict original interface
can resolve only contact-gap diagnostics; every other existing gate remains.
"""
import argparse, importlib.util, json, subprocess, sys, uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
from pak_shing_compound_identity import verify_files as compound_verify, member_identity, POLICY, TOWER, PODIUM
from terrain_source_preflight import preflight, SourceSheetIndex
from terrain_diagnostic_resolution import resolve_global_bottom_warning
from installed_support_acceptance import resolve_contact


def module(name, filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def ref(path):
    path=Path(path);return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    base=ROOT/args.base;previous=ROOT/args.terrain_source;closure=ROOT/args.closure
    prior=read(previous/'result.json');assert prior['uid']==args.support
    assert read(previous/'neon-sync.json')=={'jobId':prior['jobId'],'resultVerified':True}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for evidence in prior['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
    old=read(closure/'support-inputs.json');pair={'uid':args.tower,'supportUid':args.support}
    assert pair in old['pairs']
    wanted={args.tower,args.support};assert len(wanted)==2
    frozen={r['uid']:r for r in read(base/'check-selection.json.gz')['rows']}
    contexts={r['uid']:r for r in read(base/'context.json.gz')['rows']}
    originals={r['uid']:r for r in old['sources']}
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_ref=ref(manifest_path);manifest=read(manifest_path)
    native={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not wanted&native,'Already installed source requires a dedicated recovery route'
    assert args.tower==TOWER and args.support==PODIUM, 'Exact Pak Shing assembly only'
    closure_result=read(closure/'result.json')
    assert read(closure/'neon-sync.json')=={'jobId':closure_result['jobId'],'resultVerified':True}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(closure_result['jobId'],)).fetchone()==('complete',closure_result)
    for evidence in closure_result['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
    interfaces=read(closure/'support-checks.json.gz')['rows']
    assert len(interfaces)==1
    compound=compound_verify([frozen[PODIUM],frozen[TOWER]],contexts,local,interfaces[0])
    save(doc/'compound-identity.json',compound)
    assert compound['passed'],compound['reasons']
    save(doc/'compound-route.json',{'scope':[PODIUM,TOWER],'policy':POLICY,
        'runner':ref(Path(__file__)),'compoundRunner':ref(HERE/'pak_shing_compound_identity.py'),
        'verifiedClosureJobId':closure_result['jobId'],'modelGeometryChanges':0,'publication':False})
    identities=[];rows=[]
    index_path=ROOT/'source-scripts/city/landmark-acquisition/index.json';index=SourceSheetIndex(read(index_path))
    for uid in [args.support,args.tower]:
        row=frozen[uid];assert row['sourceSHA256']==originals[uid]['sourceSHA256']
        raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
        assert ref(ROOT/'3d-viewer'/row['source']['tile'])['sha256']==row['source']['tileSHA256']
        for path,sha in contexts[uid]['neighbourTileHashes'].items():assert ref(ROOT/'3d-viewer'/path)['sha256']==sha
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
            assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',(uid,)).fetchone() is None
        positive=member_identity(compound,uid)
        assert positive['passed'],positive['reasons']
        route=preflight(row,contexts[uid],index);assert route['primarySheetIntersects']
        identities.append({'uid':uid,'sourceSHA256':row['sourceSHA256'],'method':POLICY,'positive':positive,'indexedPreflight':route})
        asset=local/'assets'/(row['sourceSHA256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
        row['candidate']['path']=str(asset.relative_to(ROOT));row['candidate']['entry']['asset']='assets/'+asset.name
        rows.append(row)
    save(doc/'identity-proofs.json',{'rows':identities,'modelGeometryChanges':0})
    patch=read(previous/'terrain-candidates.json')[0];assert ref(ROOT/patch['path'])['sha256']==patch['sha256']
    assert not patch.get('replaces'),'Joint retained-patch replacement requires complete separate handling'
    terrain=read(previous/'terrain.json')
    for source in terrain['sourceFiles']:assert ref(ROOT/source['path'])['sha256']==source['sha256']
    patch={**patch,'uids':[args.support,args.tower]}
    inputs=read(previous/'neighbour-inputs.json.gz')
    for path,sha in inputs['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
    assert wanted<={r['building']['uid'] for r in inputs['rows']}
    for row in inputs['rows']:row['existingNative']=row['building']['uid'] in native
    inputs.update(candidateIds=[args.support,args.tower],patches=[patch])
    save(doc/'terrain-candidates.json',[patch]);save(doc/'terrain.json',terrain);save(doc/'neighbour-inputs.json.gz',inputs)
    save(doc/'selection.json.gz',{'batch':args.batch,'rows':rows,'manifestSHA256':manifest_ref['sha256']})
    template=read(HERE/'local'/previous.name/'catalogue.json')
    save(local/'catalogue.json',{**template,'models':[r['candidate']['entry'] for r in rows],'counts':{**template.get('counts',{}),'packedModels':len(rows)}})
    save(local/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']})
    save(local/'source-forms.json',{r['uid']:r['source'] for r in rows})
    save(doc/'support-inputs.json',{'sources':rows,'pairs':[pair]})
    save(doc/'pinned-inputs.json',{'evidenceRefs':[ref(previous/n) for n in ['result.json','terrain.json','terrain-candidates.json','neighbour-inputs.json.gz']],
        'closure':ref(closure/'support-inputs.json'),'baseSelection':ref(base/'check-selection.json.gz'),'baseContext':ref(base/'context.json.gz'),
        'runner':ref(Path(__file__)),'identityRunner':ref(HERE/'government_georef_cell_identity.py'),'manifest':manifest_ref})
    rel=lambda p:str(p.relative_to(ROOT))
    def call(command,allowed=(0,)):
        assert subprocess.run(command,cwd=ROOT).returncode in allowed
        assert reservations.owns(lease)
    call(['node',str(HERE/'original-support-closure-interfaces.mjs'),rel(doc)+'/'])
    support=read(doc/'support-checks.json.gz');assert len(support['rows'])==1
    interface=support['rows'][0];assert interface['uid']==args.tower and interface['supportUid']==args.support
    assert interface['sourceSHA256']==frozen[args.tower]['sourceSHA256'] and interface['supportSHA256']==frozen[args.support]['sourceSHA256']
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(doc/'selection.json.gz'),'--candidates',rel(local),
          '--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'metrics.json'),'--geometry-out',rel(local/'runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(local),'--source-forms',rel(local/'source-forms.json'),
          '--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'validation.json')],(0,1))
    assert (doc/'validation.json').exists(),'Validator returned without a report; no physical acceptance or credit'
    call(['node',str(HERE/'check-neighbours.mjs'),rel(doc)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(doc)+'/'])
    geometries={r['uid']:r for r in read(local/'runtime-geometry.json.gz')['rows']}
    def body(geometry):return np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
    podium=body(geometries[args.support]);final=module('joint_original_foundation','xl-final-script-pass.py')
    policy=module('joint_original_policy','acceptance-policy.py');metrics=read(doc/'metrics.json');by_metric={r['uid']:r for r in metrics['rows']}
    validation=read(doc/'validation.json');by_validation={r['uid']:r for r in validation['results']};foundations=[];decisions=[];reasons=[]
    for row in rows:
        uid=row['uid'];geometry=geometries[uid];ground=np.asarray(geometry['drawnGroundGeometry']).reshape(-1,3,3)
        if uid==args.tower:ground=np.concatenate([ground,podium])
        building=row['source']['building'];foundation=final.foundation_context(body(geometry),ground,Polygon(building['rings'][0],building['rings'][1:]))
        strict=foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
        proof={'uid':uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,'strictFoundationAccepted':strict}
        foundations.append(proof);diagnostic=resolve_global_bottom_warning(by_validation[uid],by_metric[uid],proof)
        identity=next(v for v in identities if v['uid']==uid)['positive']['proof']
        raw_policy=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':identity},by_metric[uid],metrics['profiles']['mobile'])
        raw_diagnostics=diagnostic['remaining']
        remaining_policy=resolve_contact(raw_policy,interface['interface'],proof) if uid==args.tower else raw_policy
        remaining_diagnostics=resolve_contact(raw_diagnostics,interface['interface'],proof) if uid==args.tower else raw_diagnostics
        decisions.append({'uid':uid,'rawPolicyReasons':raw_policy,'rawDiagnosticReasons':raw_diagnostics,'remainingPolicyReasons':remaining_policy,'remainingDiagnosticReasons':remaining_diagnostics,'diagnosticResolution':diagnostic})
        reasons.extend(uid+':'+r for r in [*remaining_policy,*remaining_diagnostics])
        if not strict:reasons.append(uid+':whole-source-foundation')
    if not (interface['interface']['passed'] and interface['interface']['samples']>0 and interface['interface']['strictContacts']==interface['interface']['samples'] and not interface['interface']['wallIntersections'] and not interface['interface']['unresolved']):reasons.append('original-support-interface-unresolved')
    if validation['checksPassed']!=2 or validation['loaderAccepted']!=2 or validation['exceptions']:reasons.append('runtime-validation')
    native_checks=read(doc/'native-neighbour-checks.json');resolved=set(native_checks['resolved'])
    reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(doc/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    reasons.extend('native-neighbour-regression:'+u for u in set(native_checks['blocked'])-resolved)
    save(doc/'foundation.json',{'rows':foundations,'modelGeometryChanges':0});save(doc/'support-ground-resolution.json',{'rows':decisions,'strictInterface':interface['interface'],'modelGeometryChanges':0,'publication':False})
    if ref(manifest_path)!=manifest_ref:reasons.append('current-manifest-changed-recheck-required')
    refs=[ref(p) for p in sorted(doc.iterdir()) if p.is_file()];payload={'uids':[args.support,args.tower],'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in rows},'evidenceRefs':refs,'runner':ref(Path(__file__))}
    stage='joint-exact-original-support-full-physical-v1';jobid=jobs.enqueue(args.batch,stage,payload);job=jobs.claim(args.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**payload,'batch':args.batch,'jobId':jobid,'reasons':sorted(set(reasons)),'scriptChecksPassed':not reasons,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'requiresAI':False,'requiresHumanDecision':False,'activeWorkers':0,'queuedFollowups':0}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
    save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({'uids':result['uids'],'checksPassed':not reasons,'reasons':result['reasons'],'jobId':jobid,'neonVerified':True}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','base','terrain-source','closure','tower','support']:parser.add_argument('--'+key,required=True)
    parser.add_argument('--owned',action='store_true');args=parser.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    if args.owned:return owned(args,doc,local)
    assert not doc.exists(),'Fresh joint source check only'
    scope={r['building']['uid'] for r in read(ROOT/args.terrain_source/'neighbour-inputs.json.gz')['rows']}|{args.tower,args.support}
    claim=reservations.claim('codex-xl-joint-original-support-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-patch:'+args.support],batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
