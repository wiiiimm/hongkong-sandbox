"""UNEXECUTED ROOT-only saved one-face closed-projection coverage, hard60s.

No source decode, repartition, constructor, runtime import, DB, lease or live
state. Only a new controlled child group may be stopped; live V2 is untouched.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,signal,subprocess,sys,time,uuid

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-face891-saved-packed-closed-coverage-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');MAX_SECONDS=60.0


def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)


def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def check(pin):
    path=ROOT/pin['path'];assert ref(path)==pin;return path


def serial(value):
    from fractions import Fraction
    if isinstance(value,Fraction):return str(value)
    if isinstance(value,dict):return {k:serial(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serial(v)for v in value]
    return value


def save(path,value):
    raw=(json.dumps(serial(value),sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(raw);os.replace(temporary,path)


def schema(pins):
    for pin in pins['evidenceRefs']:check(pin)
    packet=read(check(pins['savedPacketRef']));terminal=read(check(pins['savedTerminalRef']))
    assert terminal['complete']and terminal['actualChildExitCode']==0
    for pin in terminal['evidenceRefs']:check(pin)
    assert packet['complete']and packet['face']==891 and packet['processedUniqueMasks']==539
    assert packet['completeFaceRelevantOccurrences']==2415 and packet['completeFaceRelevantUniqueMasks']==539
    assert packet['packedFacetCount']==3122 and packet['outputOutsidePolygons']==143 and packet['outputInsidePolygons']==1512
    assert len(packet['exactOwnPlanePackedPieces'])==3122
    assert len(packet['exactIdealPartition']['outside'])==143 and len(packet['exactIdealPartition']['inside'])==1512
    assert packet['idealCompleteSourceEdgesCovered']==[True]*3
    assert not packet['fullCandidateConstructed']and not packet['currentAcceptance']
    for pin in packet['inputRefs']:check(pin)
    return packet


def child(token):
    contract=read(DOC/'launch-contract.json')
    assert token==contract['token']and os.getppid()==contract['parentPID']and os.getpgid(0)==os.getpid()
    remaining=contract['deadlineMonotonic']-time.monotonic();assert 0<remaining<=MAX_SECONDS
    def expired(signum,frame):raise TimeoutError('Saved one-face60s deadline: incomplete coverage, not a deficit finding')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,remaining)
    started=time.monotonic();complete=False
    save(DOC/'child-process.json',dict(pid=os.getpid(),ppid=os.getppid(),pgid=os.getpgid(0)))
    try:
        pins=read(check(contract['draftPinsRef']));packet=schema(pins)
        import polyu_face891_saved_packed_closed_coverage_v1_draft_20261014 as helper
        with (DOC/'completed-region-progress.jsonl').open('w')as journal:
            def progress(summary,finding):
                journal.write(json.dumps(serial(finding),sort_keys=True,separators=(',',':'))+'\n');journal.flush()
                print(json.dumps({**summary,'elapsedSeconds':time.monotonic()-started}),flush=True)
            result=helper.inspect(packet,progress)
        for pin in pins['evidenceRefs']:check(pin)
        check(contract['draftPinsRef'])
        result['inputRefs']=pins['evidenceRefs'];result['elapsedSeconds']=time.monotonic()-started
        result['packedSourcePlaneEqualityNotClaimed']=True
        save(DOC/'saved-packed-closed-coverage.json.gz',result);complete=True
    except BaseException as error:
        save(DOC/'actual-child-error.json',dict(type=type(error).__name__,message=str(error),complete=False,
             elapsedSeconds=time.monotonic()-started,noAcceptance=True))
        raise
    finally:
        if not complete:signal.setitimer(signal.ITIMER_REAL,0)


def run_once():
    assert os.name=='posix'and not DOC.exists(),'Distinct immutable attempt; no timeout restart'
    pins=read(PROPOSAL/'draft-pins.json')
    for pin in pins['evidenceRefs']:check(pin)
    DOC.mkdir();token=str(uuid.uuid4());started=time.monotonic();deadline=started+MAX_SECONDS
    save(DOC/'launch-contract.json',dict(token=token,parentPID=os.getpid(),deadlineMonotonic=deadline,
        maximumSeconds=MAX_SECONDS,draftPinsRef=ref(PROPOSAL/'draft-pins.json')))
    proc=None;status=None;timed_out=False;error=None
    try:
        with (DOC/'closed-child-stdout.log').open('wb')as log:
            proc=subprocess.Popen([sys.executable,__file__,'--controlled-child-token',token],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            save(DOC/'parent-process.json',dict(parentPID=os.getpid(),controlledChildPID=proc.pid,liveV2NeverTargeted=True))
            while proc.poll()is None:
                if time.monotonic()>=deadline:
                    timed_out=True
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    break
                time.sleep(min(.05,max(0,deadline-time.monotonic())))
            status=proc.wait(timeout=5)
    except BaseException as failure:error=dict(type=type(failure).__name__,message=str(failure))
    finally:
        if proc is not None and proc.poll()is None:
            try:os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            status=proc.wait(timeout=5)
    assert proc is None or not Path('/proc',str(proc.pid)).exists()
    complete=error is None and not timed_out and status==0 and (DOC/'saved-packed-closed-coverage.json.gz').is_file()
    # End pins are checked even after a genuine geometry deficit or timeout.
    end_errors=[]
    for pin in pins['evidenceRefs']:
        try:check(pin)
        except (AssertionError,OSError)as failure:end_errors.append(dict(pin=pin,error=str(failure)))
    complete=complete and not end_errors
    if complete:assert read(DOC/'saved-packed-closed-coverage.json.gz')['complete']
    summary=dict(complete=complete,actualChildExitCode=status,hardDeadlineTriggered=timed_out,
        maximumSeconds=MAX_SECONDS,elapsedParentSeconds=time.monotonic()-started,parentError=error,
        endPinFailures=end_errors,controlledChildReapedAndDirectPIDAbsent=True,
        evidenceRefs=[ref(p)for p in sorted(DOC.iterdir())if p.is_file()],
        partialCompletedRegionsAreNotWholeCoverage=True,physicalAccepted=False,installationApproved=False,
        databaseCalls=0,reservationsClaimed=0,noConstructor=True,liveV2NeverStoppedOrEdited=True)
    save(DOC/'terminal-summary.json',summary);print(json.dumps(summary,sort_keys=True),flush=True)
    return 0 if complete else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--schema-only',action='store_true')
    modes.add_argument('--check-saved-face891-packed-coverage-only',action='store_true')
    modes.add_argument('--controlled-child-token');args=parser.parse_args()
    if args.schema_only:
        pins=read(PROPOSAL/'draft-pins.json');schema(pins)
        for pin in pins['evidenceRefs']:check(pin)
        print(json.dumps(dict(schemaOnly=True,packedFacets=3122,regions=1655,noCoverageMath=True)));return 0
    if args.controlled_child_token:return child(args.controlled_child_token)
    return run_once()


if __name__=='__main__':sys.exit(main())
