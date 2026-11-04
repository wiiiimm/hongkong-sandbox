"""Test seven eligible existing roofs with the unchanged illustrative-post mechanism.

Each child claims/releases exact source/terrain leases; no publication or source edits.
"""
import sys,subprocess,json
from run import ROOT,HERE,read,save
P='government-xl-academic309823-after-carpark-'
BASE=ROOT/'docs/astra-city/government-import'
BATCH=P+'canopy-post-sequence-v1-20261101'
def main():
    local=HERE/'local'/BATCH;assert not local.exists();local.mkdir(parents=True)
    forms={f['uid']:f for f in read(BASE/(P+'patch-scope-v1-20261101')/'form-obligations.json.gz')}
    flags=read(BASE/(P+'native-neighbours-v1-20261101')/'summary.json')['basicFlags']
    wanted=sorted(r['uid']for r in flags if forms[r['uid']].get('kind')=='roof'and forms[r['uid']].get('structureType')=='Open-sided Structure')
    assert len(wanted)==7
    outcomes=[]
    for uid in wanted:
        suffix=uid.split('/')[1].replace(':','-');batch=P+'canopy-post-'+suffix+'-v1-20261101'
        command=[sys.executable,str(HERE/'estimated_canopy_foundation_proposal_v2_20261101.py'),'--batch',batch,'--runtime',P+'patch-runtime-v1-20261101','--scope',P+'patch-scope-v1-20261101','--ground-uid','landsd/309823:0','--uid',uid]
        with (local/(suffix+'.log')).open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=3600)
        outcomes.append(dict(uid=uid,batch=batch,exitCode=r.returncode))
        save(local/'progress.json',dict(rows=outcomes,installationApproved=False))
        print(json.dumps(outcomes[-1]),flush=True)
    save(local/'complete.json',dict(rows=outcomes,installationApproved=False,publication=False))
if __name__=='__main__':main()
