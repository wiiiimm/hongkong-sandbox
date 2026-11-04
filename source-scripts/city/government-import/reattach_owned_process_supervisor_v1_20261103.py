"""Bounded Linux supervision of one orphaned, exact owned process; never restarts it.

Requires the existing current lease. No publication, approval or source changes.
PID start time, exact argv/cwd, process group and session are checked before signals.
"""
import argparse,json,os,signal,sys,time
from pathlib import Path
from run import ROOT,HERE,read,reservations
from observed_reserved_runner_v2_20261103 import observed_action


def process_identity(pid):
    p=Path('/proc')/str(pid)
    try:
        raw=(p/'stat').read_text();tail=raw[raw.rfind(')')+2:].split()
        if tail[0]=='Z':return None
        return dict(pid=pid,startTicks=int(tail[19]),ppid=int(tail[1]),
                    pgid=int(tail[2]),sid=int(tail[3]),cwd=str((p/'cwd').resolve(strict=True)),
                    argv=(p/'cmdline').read_bytes().rstrip(b'\0').decode().split('\0'))
    except (FileNotFoundError,ProcessLookupError):return None


def same_process(actual,expected):
    return actual is not None and all(actual[k]==expected[k]for k in ['pid','startTicks','pgid','sid','cwd','argv'])


def stop_exact(expected,grace=30):
    if not same_process(process_identity(expected['pid']),expected):return
    os.killpg(expected['pgid'],signal.SIGTERM)
    deadline=time.monotonic()+grace
    while time.monotonic()<deadline:
        if not same_process(process_identity(expected['pid']),expected):return
        time.sleep(.2)
    if same_process(process_identity(expected['pid']),expected):
        os.killpg(expected['pgid'],signal.SIGKILL)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--contract',type=Path,required=True);a=ap.parse_args();contract=read(a.contract)
    expected=contract['process'];lease_path=(ROOT/contract['leaseFile']).resolve();output=(ROOT/contract['resultFile']).resolve()
    assert lease_path.is_relative_to(ROOT)and output.is_relative_to(ROOT)and not output.exists()
    assert expected['cwd']==str(ROOT)and expected['ppid']==1
    assert expected['pid']==expected['pgid']==expected['sid']and expected['pid']>1
    assert same_process(process_identity(expected['pid']),expected),'Exact orphan process changed'
    assert expected['argv'][1]==str(HERE/'june_garden_live_install_v1_20261103.py')and '--owned'in expected['argv']
    assert 60<=contract['deadlineSeconds']<=21600
    lease=read(lease_path);assert lease['batch']==contract['batch']and reservations.owns(lease)
    # Renew the same owner/token; never claim, transfer or recreate a lease.
    assert observed_action('heartbeat',lease_path,3600),'Existing lease not renewable'
    prior={};interrupted=False;reason='target-exited';started=time.monotonic()
    def on_signal(signum,frame):
        nonlocal interrupted
        interrupted=True
    try:
        for s in [signal.SIGTERM,signal.SIGINT]:prior[s]=signal.signal(s,on_signal)
        next_heartbeat=time.monotonic()+300
        while same_process(process_identity(expected['pid']),expected):
            if interrupted:reason='supervisor-interrupted';break
            if time.monotonic()-started>=contract['deadlineSeconds']:reason='bounded-deadline';break
            if time.monotonic()>=next_heartbeat:
                if not observed_action('heartbeat',lease_path,3600):reason='lease-renewal-failed';break
                next_heartbeat=time.monotonic()+300
            time.sleep(1)
    except BaseException:
        reason='supervision-error';raise
    finally:
        if same_process(process_identity(expected['pid']),expected):stop_exact(expected)
        stopped=not same_process(process_identity(expected['pid']),expected)
        released=False
        if stopped and reservations.owns(lease):released=observed_action('release',lease_path,3600)
        result=dict(reason=reason,targetNoLongerLive=stopped,leaseReleased=released,
                    sameConcreteProcessOnly=True,restarted=False,installationAcceptance=False)
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
        for s,h in prior.items():signal.signal(s,h)
    return 0 if reason=='target-exited'and stopped else 2

if __name__=='__main__':raise SystemExit(main())
