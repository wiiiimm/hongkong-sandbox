"""Run a prepared island terrain stage under renewing exact source leases."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid
from islands_direct_stage import ROOT,HERE,read,save,sha
from run import reservations


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--script',required=True);p.add_argument('--attempt',type=int,default=1);a=p.parse_args()
    assert a.batch.startswith('government-islands-') and '/' not in a.batch
    script=HERE/a.script;assert script.parent==HERE and script.name.startswith('islands_') and script.suffix=='.py' and script.is_file()
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    assert 1<=a.attempt<=9
    if a.attempt==1:assert not local.exists()
    receipt_path=local/('reservation.json' if a.attempt==1 else f'reservation-{a.attempt}.json')
    assert not receipt_path.exists()
    plan=read(doc/'nomination.json');assert 0<len(plan['uids'])==len(set(plan['uids']))<=50
    assert plan['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    resources=['building:'+u for u in plan['uids']]+['terrain:city/data/terrain.json']
    claim=reservations.claim('codex-islands-stage-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok'],'Existing owner; no takeover'
    receipt=json.loads(json.dumps(claim['reservation'],default=str));save(receipt_path,receipt);save(local/'reservations.json',[receipt])
    try:
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',receipt_path,'--ttl','3600','--',sys.executable,script],cwd=ROOT,check=True)
    finally:
        if reservations.owns(receipt):reservations.release(receipt)


if __name__=='__main__':main()
