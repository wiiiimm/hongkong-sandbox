"""Existing fail-closed runner with safe renewal exception classification only."""
import json,subprocess,sys,time
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
sys.path.insert(0,str(HERE.parent/'shared-modelling'))
import reservation_runner


def observed_action(action,lease_file,ttl):
    command=[sys.executable,str(HERE/'reservation_action_diagnostic_v1_20261103.py'),action,'--lease-file',str(lease_file),'--ttl',str(ttl)]
    started=time.monotonic();record=dict(reservationAction=action,ok=False)
    try:
        result=subprocess.run(command,capture_output=True,text=True,timeout=120)
        record['exitCode']=result.returncode
        try: safe=json.loads(result.stdout)
        except ValueError: safe={};record['failureClass']='invalid-action-json'
        record['ok']=result.returncode==0 and safe.get('ok') is True
        for key in ['errorClass','sqlstate','leaseLost']:
            if key in safe:record[key]=safe[key]
        if not record['ok']:record.setdefault('failureClass','subprocess-nonzero' if result.returncode else 'database-action-not-ok')
    except subprocess.TimeoutExpired:record['failureClass']='database-observation-timeout'
    except OSError:record['failureClass']='subprocess-launch-error'
    finally:
        record['elapsedSeconds']=round(time.monotonic()-started,3);print(json.dumps(record),flush=True)
    return record['ok']


def execute_reserved(lease,path,command):
    try:
        save(path,json.loads(json.dumps(lease,default=str)))
        result=subprocess.run([sys.executable,__file__,str(path),*command],cwd=ROOT)
        assert result.returncode==0,'Diagnostic failed; preserve evidence, no approval'
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']


def main():
    original=reservation_runner._lease_action;reservation_runner._lease_action=observed_action
    try:
        result=reservation_runner.run_reserved(sys.argv[1],sys.argv[2:],ttl=3600)
        print(json.dumps(result,indent=2),flush=True);return 0 if result['ok'] else result['exitCode']
    finally:reservation_runner._lease_action=original


if __name__=='__main__':raise SystemExit(main())
