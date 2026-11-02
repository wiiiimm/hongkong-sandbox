"""Follow one concrete mobile worker with camera diagnostics and QA sheets.

No keepalive, predecessor restart, acceptance, publication or geometry work.
Waiting holds no lease; each concrete diagnostic claims/releases its own scope.
"""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import process_identity
from june_garden_publisher_hooks_v1_20261103 import SOURCES

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-june-garden-diagnostic-followthrough-v2-20261103'
PARENT='government-xl-june-garden-mobile-recovery-v1-20261103'
SUPPLEMENT='government-xl-june-garden-retained-camera-supplement-v2-20261103'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--after-pid',type=int,required=True);a=p.parse_args()
    inspection=BASE/'government-xl-june-garden-v4-export-sheets-v1-20261103/ROOT-DESKTOP-EXPORT-INSPECTION-20261103.json'
    decision=read(inspection)
    expected={'landsd/147505:0','landsd/147996:0','landsd/159422:0','landsd/160070:0','landsd/233970:0','landsd/309340:0'}
    assert decision['allListedExportsActuallyInspected'] and not decision['visualAcceptance']
    assert {r['uid'] for r in decision['unresolvedVisualFailures']}==expected
    inspection_hash=digest(inspection.read_bytes())
    out=BASE/BATCH;assert not out.exists();out.mkdir()
    phase='waiting-for-exact-mobile-worker'
    def state(status,**extra):
        save(out/'state.json',dict(status=status,phase=phase,sourceSHA256ByUid=SOURCES,
            predecessorPid=a.after_pid,publication=False,installationApproved=False,
            desktopInspection=dict(path=str(inspection.relative_to(ROOT)),sha256=inspection_hash),**extra))
    def call(name,command,timeout):
        state('running',command=command)
        with (out/(name+'.log')).open('w') as log:
            result=subprocess.run(command,cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
        assert result.returncode==0,name+' failed; preserve log and do not continue'
    try:
        ident=process_identity(a.after_pid)
        if ident is not None:
            argv=ident[1].split(b'\0')
            assert len(argv)>1 and Path(os.fsdecode(argv[1])).name=='june_garden_mobile_recovery_v1_20261103.py'
            assert b'--owned' not in argv
            state('waiting',predecessorStartTicks=ident[0])
            deadline=time.monotonic()+7800
            while process_identity(a.after_pid)==ident:
                if time.monotonic()>deadline:raise TimeoutError('Observation deadline only; predecessor is not stopped or restarted')
                time.sleep(2)
        phase='authenticate-completed-mobile'
        parent,_=authenticate(BASE/PARENT)
        assert parent['passed'] and parent['desktopDiagnosticsPassed'] and parent['mobileDiagnosticsPassed']
        assert parent['sourceSHA256ByUid']==SOURCES and parent['retainedNativeActors']==69
        assert digest(inspection.read_bytes())==inspection_hash
        phase='camera-only-supplement'
        command=[sys.executable,str(HERE/'june_garden_retained_camera_supplement_v1_20261103.py'),
            '--batch',SUPPLEMENT,'--parent',PARENT,'--resources-plan',
            'docs/astra-city/government-import/government-xl-tower3-june-garden-six-originals-current-v1-20261102-plan.json']
        for uid in sorted(expected):command.extend(['--uid',uid])
        call('camera-supplement',command,8100)
        supplemental,_=authenticate(BASE/SUPPLEMENT)
        assert supplemental['desktopMobileDiagnosticsPassed'] and supplemental['parentBrowserBatch']==PARENT
        assert supplemental['sourceSHA256ByUid']==SOURCES and not supplemental['visualAcceptance']
        phase='compose-pixel-preserving-export-sheets'
        tool=HERE/'original_browser_contact_sheets_v1_20261028.py'
        # Existing desktop sheets are reused only when the copied report and
        # all original bytes match. The utility enforces that exact condition.
        for batch,dest in [(PARENT,'government-xl-june-garden-v4-export-sheets-v1-20261103'),
                           (SUPPLEMENT,'government-xl-june-garden-supplement-export-sheets-v2-20261103')]:
            for width in [1280,390]:
                call(batch+'-'+str(width),[sys.executable,str(tool),'--source',str((BASE/batch/str(width)).relative_to(ROOT)),
                    '--out',str((BASE/dest).relative_to(ROOT)),'--width',str(width)],600)
        phase='ready-for-root-export-inspection'
        state('diagnostics-complete-review-pending',parentJob=parent['jobId'],supplementJob=supplemental['jobId'],
            parentReceiptSHA256=digest((BASE/PARENT/'result.json').read_bytes()),
            supplementReceiptSHA256=digest((BASE/SUPPLEMENT/'result.json').read_bytes()),
            next='Inspect authenticated original/supplemental exports and resolve every visual failure before qualified staging. No publisher was called.')
        print(json.dumps(dict(status='diagnostics-complete-review-pending',publication=False)),flush=True)
    except BaseException as error:
        state('stopped-with-error',errorClass=type(error).__name__)
        raise


if __name__=='__main__':main()
