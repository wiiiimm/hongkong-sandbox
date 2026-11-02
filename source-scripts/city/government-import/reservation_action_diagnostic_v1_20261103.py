"""Credential-free action result: no retries, timeout or ownership changes."""
import argparse, json, sys
from pathlib import Path
SHARED=Path(__file__).resolve().parent.parent/'shared-modelling'
sys.path.insert(0,str(SHARED))
import reservations


def action_result(action,lease,ttl):
    try:
        result=reservations.heartbeat(lease,ttl) if action=='heartbeat' else reservations.release(lease)
        return dict(ok=result.get('ok') is True,action=action,leaseLost=result.get('error')=='lease-lost')
    except Exception as error:
        # Never include exception text, query, config, environment or lease IDs.
        return dict(ok=False,action=action,errorClass=type(error).__name__,sqlstate=getattr(error,'sqlstate',None))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['heartbeat','release'])
    p.add_argument('--lease-file',type=Path,required=True);p.add_argument('--ttl',type=int,default=3600);a=p.parse_args()
    result=action_result(a.action,json.loads(a.lease_file.read_text()),a.ttl)
    print(json.dumps(result),flush=True);return 0 if result['ok'] else 1


if __name__=='__main__':raise SystemExit(main())
