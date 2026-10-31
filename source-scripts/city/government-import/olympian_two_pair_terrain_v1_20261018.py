"""Private two-podium terrain candidate; exact reviewed originals, no publication."""
from pathlib import Path
import json,sys,uuid,subprocess,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-olympian-two-pair-terrain-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/265851:0','landsd/239351:0']
INPUT=BASE/'government-xl-olympian-two-pair-terrain-inputs-v1-20261018'
MAIN=BASE/'government-xl-olympian-two-current-terrain-inputs-v1-20261018'
REVIEW=BASE/'government-xl-olympian-two-remaining-identity-review-v1-20261018'
PRIOR=BASE/'government-xl-olympian-two-current-retained-terrain-v1-20261018'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 pins={};refs=[Path(__file__)];sources=[INPUT,MAIN,REVIEW,PRIOR,BASE/'government-xl-olympian-two-current-native-scope-v1-20261018']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in sources:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[read(d/'check-selection.json.gz')['rows'][0]for d in [MAIN,INPUT]]
 contexts=[read(d/'context.json.gz')['rows'][0]for d in [MAIN,INPUT]]
 fresh=LOCAL/'inputs';save(fresh/'check-selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(fresh/'context.json.gz',dict(rows=contexts))
 # Keep the unmodified terrain algorithm; substitute only the previously reviewed, exact-source identity route.
 path=HERE/'xl-routed-source-local-contact-resolution.py';code=path.read_text()
 start=code.index('        from routed_original_cell_identity import verify_files, POLICY')
 end=code.index("        for path, pinned in context[r['uid']]['neighbourTileHashes'].items():",start)
 replacement="""        from exact_original_georef_cell_identity_20261009 import verify_files
        identity_base=ROOT/'docs/astra-city/government-import/government-xl-olympian-two-current-identity-runtime-v1-20261018'
        identity_context=read(identity_base/(r['uid'].split('/')[1]+'-identity.json'))['context']
        proof=verify_files(r,identity_context,LOCAL/'identity-recheck'/r['uid'].split('/')[1])
        if r['uid']=='landsd/239351:0':
            review=read(ROOT/'docs/astra-city/government-import/government-xl-olympian-two-remaining-identity-review-v1-20261018/239351:0-review.json')
            assert review['identityOnlyApproved'] and review['identityReviewApproved']
            for key in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:assert proof[key]==review[key],key
            assert proof['reasons']==review['rawReasonsRetained']
        else:
            assert proof['passed'],proof['reasons']
        save(DOC/(r['uid'].split('/')[1]+'-identity-recheck.json'),proof)
"""
 code=code[:start]+replacement+code[end:]
 # Inject complete previously nominated native scope into the existing generated checker input.
 old="    call(['node',str(HERE/'check-native-neighbours-multi-retained.mjs'),rel(DOC)+'/'])"
 new="""    ni=read(DOC/'neighbour-inputs.json.gz');ni['requiredNativeUids']=read(ROOT/'docs/astra-city/government-import/government-xl-olympian-two-current-native-scope-v1-20261018/scope.json')['touchingNativeUids'];save(DOC/'neighbour-inputs.json.gz',ni)
    call(['node',str(HERE/'check-native-neighbours-multi-retained-scoped-v3.mjs'),rel(DOC)+'/'])"""
 assert old in code;code=code.replace(old,new)
 generated=LOCAL/'pair-terrain-worker.py';generated.parent.mkdir(parents=True,exist_ok=True);generated.write_text(code);worker=module('olympian_pair_private_worker',generated)
 worker.BATCH=BATCH;worker.BASE=fresh;worker.DOC=DOC;worker.LOCAL=LOCAL;worker.UIDS=UIDS;worker.ALLOW_BASIC_TERRAIN_TARGETS=True
 worker.RETAIN_NATIVE_URLS=[x['url']for x in read(INPUT/'scope.json')['retainedParents']]
 recovery=read(PRIOR/'source-recovery.json')['sheets'];worker.SOURCE=ROOT/recovery[0]['cache'];worker.ADJACENT_SOURCES=[ROOT/r['cache']for r in recovery[1:]]
 error=None
 try:worker.owned()
 except AssertionError as exc:
  error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),publication=False,modelGeometryChanges=0))
 assert reservations.owns(lease)
 refs.extend(ROOT/p for p in pins);refs.extend([path,generated]);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 summary=dict(uids=UIDS,guardFailure=error,fullAcceptance=False,newlyInstalled=0,publication=False,modelGeometryChanges=0)
 out=module('olympian_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-original-pair-terrain-v1',list(set(refs)),summary);print(dict(jobId=out['jobId'],**summary),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope=read(INPUT/'scope.json');final=module('pair_scope_forms',HERE/'xl-final-script-pass.py');uids={b['uid']for b,_,_ in final.load_forms(scope['fullParentBounds'])}|set(UIDS)
 keys={('building:'if u.startswith('landsd/')else'source-form:')+u for u in uids}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['url']for r in scope['retainedParents']}
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
