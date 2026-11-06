"""Run current renderer and full affected-scope checks for private island patches.

Every result remains unapproved. Raw diagnostic warnings and patch-wide blockers
are persisted to the pinned job ledger under complete renewing source leases.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import uuid
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module,policy
from run import reservations,jobs,connect,dict_row,Jsonb

BATCH='government-islands-peng-chau-disjoint-runtime-20261106-v1'
BASE=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-disjoint-terrain-20261106-v1'
DOC=BASE/'runtime-current'
STAGE=HERE/'accepted/government-islands-peng-chau-disjoint-terrain-20261106-v1'
LOCAL=HERE/'local'/BATCH


def call(args, allowed=(0,)):
    result=subprocess.run([str(x)for x in args],cwd=ROOT)
    assert result.returncode in allowed,(args,result.returncode)


def owned():
    receipts=read(LOCAL/'reservations.json');assert all(reservations.owns(r)for r in receipts)
    sources=read(DOC/'selection.json.gz');by_uid={r['uid']:r for r in sources['rows']}
    neighbours=read(DOC/'neighbour-inputs.json.gz')
    for p,h in neighbours['inputHashes'].items():assert sha(ROOT/p)==h,p
    save(DOC/'source-forms.json',{r['uid']:r['source']for r in sources['rows']})
    call([sys.executable,HERE/'dependency_preflight.py','--catalogue',STAGE/'catalogue.json','--out',DOC/'dependency-preflight.json'])
    call(['node',HERE/'original_private_catalogue_preflight_v1_20261103.mjs',rel(STAGE/'catalogue.json')])
    call(['node',HERE.parent/'building-batch/validate_candidates.mjs','--candidates',rel(STAGE),'--source-forms',rel(DOC/'source-forms.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1))
    call(['node',HERE/'acceptance-metrics.mjs','--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),
          '--terrain-candidates',rel(BASE/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
    call(['node',HERE/'check-neighbours.mjs',rel(DOC)+'/'])
    raw=read(DOC/'neighbour-checks.json');save(DOC/'neighbour-checks.raw.json',raw)
    # Require full-mesh checks for every whole-source native nomination, even if
    # its GIS footprint samples happened to show no changed terrain.
    for row in raw['rows']:
        if row['uid']in neighbours['fullSourceNativeNominations']:
            row['reasons']=sorted(set(row['reasons']+['existing-native-neighbour-requires-full-mesh-check']))
    save(DOC/'neighbour-checks.json',raw)
    call(['node',HERE/'check-native-neighbours.mjs',rel(DOC)+'/'])
    native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved'])
    assert set(native['blocked'])==set(neighbours['fullSourceNativeNominations'])
    for row in raw['rows']:
        if row['uid']in resolved:
            row['reasons']=[x for x in row['reasons']if x!='existing-native-neighbour-requires-full-mesh-check']
    for i,patch in enumerate(raw['patches']):patch['blockedBy']=[r['uid']for r in raw['rows']if i in r['patchIndexes']and r['reasons']]
    save(DOC/'neighbour-checks.final.json',raw)
    metrics=read(DOC/'metrics.json');validation={r['uid']:r for r in read(DOC/'validation.json')['results']}
    deps={r['uid']:r for r in read(DOC/'dependency-preflight.json')['rows']}
    outcomes=[]
    for metric in metrics['rows']:
        uid=metric['uid'];row=by_uid[uid]
        reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['candidate']['entry']['sha256'],
            'identityProof':row.get('identityProof')},metric,metrics['profiles']['mobile'])
        if validation[uid]['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
        if deps[uid]['requiresAssemblyInvestigation']:reasons.append('dependency-investigation')
        patches=[p for p in raw['patches']if uid in p['uids']]
        assert len(patches)==1
        if patches[0]['blockedBy']:reasons.append('affected-neighbour-regression')
        outcomes.append({'uid':uid,'sourceSHA256':row['candidate']['entry']['sha256'],'reasons':sorted(set(reasons)),
            'metrics':metric,'rawValidation':validation[uid],'patchBlockedBy':patches[0]['blockedBy'],
            'humanStatus':'in-process','next':'Staged/browser/guarded installation'if not reasons else'Grouped resolution of exact recorded source/contact/neighbour negatives',
            'requiresAI':False,'requiresUserDecision':False,'publication':False})
    assert len(outcomes)==len(by_uid) and 0<len(outcomes)<=31
    for report in (metrics,native):
        for p,h in report['inputHashes'].items():assert sha(ROOT/p)==h,p
    report={'batch':BATCH,'models':len(outcomes),'rows':outcomes,'clearScriptCandidates':sum(not r['reasons']for r in outcomes),
        'reasonCounts':dict(Counter(x for r in outcomes for x in r['reasons'])),'affectedForms':len(raw['rows']),
        'nominatedNatives':len(native['blocked']),'nativePassed':len(resolved),'publication':False,'newlyInstalled':0,'aiCalls':0,'modelGeometryChanges':0}
    save(DOC/'results.json.gz',report);payload={'path':rel(DOC/'results.json.gz'),'sha256':sha(DOC/'results.json.gz')}
    stage='islands-original-terrain-current-runtime-v1';jobid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,receipts[0]['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**report,'jobId':jobid,'evidence':payload}
    with connect()as db:
        db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));groups=[reservations._current(db,r)for r in receipts];assert all(groups)
        resources={'building:'+r['building']['uid']for r in neighbours['rows']}|{'building:'+u for u in by_uid}
        assert resources<=set().union(*(set(g['resources'])for g in groups))
        assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(outcomes)})
    save(DOC/'summary.json',{k:v for k,v in report.items()if k!='rows'})
    print(json.dumps({k:v for k,v in report.items()if k!='rows'}),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    if a.owned:return owned()
    assert not LOCAL.exists();LOCAL.mkdir(parents=True)
    n=read(DOC/'neighbour-inputs.json.gz');s=read(DOC/'selection.json.gz')
    resources=sorted({'building:'+r['building']['uid']for r in n['rows']}|{'building:'+r['uid']for r in s['rows']}|{'terrain:city/data/terrain.json'})
    receipts=[];owner='codex-islands-runtime-'+str(uuid.uuid4())
    try:
        for start in range(0,len(resources),1000):
            claim=reservations.claim(owner,resources[start:start+1000],batch=BATCH,ttl=3600);assert claim['ok'],'Existing owner; no takeover'
            receipts.append(json.loads(json.dumps(claim['reservation'],default=str)));save(LOCAL/f'reservation-{len(receipts)}.json',receipts[-1])
        save(LOCAL/'reservations.json',receipts);cmd=[sys.executable,__file__,'--owned']
        for i in range(len(receipts),0,-1):cmd=[sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',LOCAL/f'reservation-{i}.json','--ttl','3600','--',*cmd]
        call(cmd)
    finally:
        for r in receipts:
            if reservations.owns(r):reservations.release(r)


if __name__=='__main__':main()
