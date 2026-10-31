"""Fresh fenced overlay reusing exact installed support identity; retain contact holds."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
from installed_source_identity import installed_identity

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--previous',required=True);p.add_argument('--batch',required=True)
p.add_argument('--owned',action='store_true',help=argparse.SUPPRESS);args=p.parse_args()
assert args.batch.startswith('government-xl-') and Path(args.batch).name==args.batch
PREVIOUS=(ROOT/args.previous).resolve();assert PREVIOUS.is_relative_to(ROOT)
DOC=ROOT/'docs/astra-city/government-import'/args.batch;LOCAL=HERE/'local'/args.batch


def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    previous=read(PREVIOUS/'result.json');sync=read(PREVIOUS/'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId']==previous['jobId']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()==('complete',previous)
    for ref in previous['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    selected={r['uid']:r for r in read(PREVIOUS/'selection.json.gz')['rows']};manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    outcomes=[];proofs=[]
    for pair in previous['rows']:
        proof=installed_identity(selected[pair['supportUid']],manifest)
        assert proof, 'Unchanged installed support evidence required'
        proofs.append(proof)
        reasons=[r for r in pair['reasons'] if r not in ('support-original-viewer-match-held','support-bounded-source-projection-held')]
        assert reasons, 'Identity reuse is not complete candidate acceptance'
        outcomes.append({**pair,'reasons':reasons,'installedSupportIdentityReused':proof,
            'nextStep':'Resolve actual tower/support contact samples and candidate terrain/foundation/runtime. Reuse the unchanged installed support identity; no repeated architectural review.'})
    save(DOC/'identity-reuse.json',{'proofs':proofs,'previousJobId':previous['jobId']})
    paths=[PREVIOUS/'result.json',PREVIOUS/'neon-sync.json',DOC/'identity-reuse.json',HERE/'accepted_source_identity.py',HERE/'installed_source_identity.py']
    refs=[{'path':str(x.relative_to(ROOT)),'sha256':digest(x.read_bytes())} for x in paths]
    payload={'evidenceRefs':refs,'runnerSHA256':digest(Path(__file__).read_bytes())};stage='exact-installed-support-identity-reuse-v1'
    jobid=jobs.enqueue(args.batch,stage,payload);job=jobs.claim(args.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**payload,'batch':args.batch,'jobId':jobid,'rows':outcomes,'newlyInstalled':0,'publication':False,
        'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'qualification':'Identity-only reuse of current installed acceptance with identical source/form/transforms/catalogue. Existing contacts and remaining candidate gates stay unresolved.'}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({'jobId':jobid,'identityReused':len(proofs),'newlyInstalled':0}),flush=True)


def start():
    assert not DOC.exists(),'Completed evidence is immutable'
    pairs=read(PREVIOUS/'result.json')['rows'];scope={u for r in pairs for u in (r['uid'],r['supportUid'])}
    claim=reservations.claim('codex-xl-support-reuse-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope)],batch=args.batch);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':owned() if args.owned else start()
