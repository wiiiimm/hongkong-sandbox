"""Run an explicit original-source continuation outside an interactive exec session."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from run import ROOT,HERE,read,save,digest


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',required=True)
    ap.add_argument('--owned',action='store_true')
    a=ap.parse_args()
    path=(ROOT/a.config).resolve()
    assert path.is_relative_to(ROOT/'docs/astra-city/government-import')
    cfg=read(path);doc=path.parent;command=cfg['command']
    assert command[0]==sys.executable and Path(command[1]).resolve().parent==HERE
    assert Path(command[1]).name in {'selected_existing_runtime_followthrough_v1.py','xl_six_parent_coverage_followthrough_v1_20261022.py','xl_validated_parent_return_followthrough_v1_20261022.py'}
    assert digest(Path(command[1]).read_bytes())==cfg['workerScriptSHA256']
    assert not(doc/'terminal.json').exists()
    if not a.owned:
        assert not(doc/'runner.json').exists()
        with(doc/'controller.log').open('wb')as log:
            child=subprocess.Popen([sys.executable,__file__,'--config',str(path.relative_to(ROOT)),'--owned'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
        ticks=Path('/proc',str(child.pid),'stat').read_text().split()[21]
        save(doc/'runner.json',dict(pid=child.pid,processGroup=child.pid,startTicks=ticks,configSHA256=digest(path.read_bytes()),controllerSHA256=digest(Path(__file__).read_bytes()),startedUTC=datetime.now(timezone.utc).isoformat()))
        print(json.dumps(dict(detachedPID=child.pid,receipt=str((doc/'runner.json').relative_to(ROOT)))),flush=True)
        return
    exitcode=1;error=None
    try:
        with(doc/'worker.log').open('wb')as log:
            exitcode=subprocess.run(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT).returncode
    except BaseException as e:error=repr(e)
    save(doc/'terminal.json',dict(exitCode=exitcode,error=error,finishedUTC=datetime.now(timezone.utc).isoformat(),qualification='Process terminal status only; authenticate worker receipt independently.'))
    raise SystemExit(exitcode)


if __name__=='__main__':main()
