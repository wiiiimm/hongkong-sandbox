"""UNEXECUTED ROOT-only one-face V3 viability diagnostic; child wall bound60s.

No V2 oracle/whole constructor/source decode/DB/reservation/publisher. The
controlled child has its own process group; only that group may be terminated.
All building/source poses remain immutable and all packed acceptance is pending.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,signal,subprocess,sys,time,uuid

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-face891-all539-timed-v3-diagnostic-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal')
MAX_CHILD_SECONDS=60.0


def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)


def ref(path):
    return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def check(pin):
    path=ROOT/pin['path'];assert ref(path)==pin;return path


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(raw);os.replace(temporary,path)


def child(token):
    contract=read(DOC/'launch-contract.json')
    assert token==contract['token']and os.getppid()==contract['parentPID']and os.getpgid(0)==os.getpid()
    deadline=contract['deadlineMonotonic'];remaining=deadline-time.monotonic();assert 0<remaining<=MAX_CHILD_SECONDS
    def expired(signum,frame):raise TimeoutError('Controlled one-face60s deadline; no complete proof')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,remaining)
    started=time.monotonic();completed=False
    save(DOC/'child-process.json',dict(pid=os.getpid(),ppid=os.getppid(),pgid=os.getpgid(0),maximumSeconds=MAX_CHILD_SECONDS))
    progress_file=None
    try:
        pins=read(check(contract['inputPinsRef']))
        for pin in pins['evidenceRefs']:check(pin)
        # Imports, input checks, whole mask metadata and all one-face work are
        # inside the same60s child deadline, not separately unbounded phases.
        import numpy as np
        from fractions import Fraction as F
        import polyu_five_mask_source_plane_partition_fast_v1_20261014 as prior
        import polyu_five_mask_positive_hit_partition_v3_draft_20261014 as proposed
        from test_polyu_five_mask_positive_hit_partition_v3_draft_20261014 import closed_segment_covered
        source=read(check(pins['sourceAccountRef']));feasibility=read(check(pins['feasibilityRef']))
        assert source['candidateSHA256']=='b033b8f2e451d7ce73a6c409d0b855686a7a1b604454a04a8b6a56db118ed647'
        records=[]
        for row in feasibility['rows']:
            if row['eligibleCurrentParentMaskNominationOnly']:
                mask=read(check(row['completeMask']))
                records.extend({**mask['rows'][i],'uid':row['uid'],'maskEvidence':row['completeMask']}
                               for i in mask['positiveMaskIDs'])
        prepared=prior.PreparedMasks(records)
        assert len(prepared.masks)==5553 and len(prepared.first_ids)==1234
        lineage=source['account']['completeOutputFacetLineage'];assert len(lineage)==3214
        original=lineage[891];assert original['outputFacet']==891
        ideal=original['exactProposedPoints'];face=prior.oracle.points(ideal)
        first,relevant=prepared.relevant(prior.oracle.bb(face));assert len(first)==539 and len(relevant)==2415
        save(DOC/'exact-input-summary.json',dict(face=891,completeGlobalMaskOccurrences=5553,
             uniqueGlobalMasks=1234,faceRelevantUniqueMasks=539,faceRelevantOccurrences=2415,
             firstOccurrenceMaskIDs=first,allRelevantOccurrenceIDs=relevant,
             sourceFaceLineageVerbatim=original,all25AffectedActorsStillPending=feasibility['all25AffectedActors'],
             noV2PartitionOracle=True,currentAcceptance=False))
        progress_file=(DOC/'mask-progress.jsonl').open('w')
        def progress(value):
            row=prior.oracle.serial({**value,'elapsedChildSeconds':time.monotonic()-started})
            progress_file.write(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n');progress_file.flush()
            print(json.dumps(row,sort_keys=True),flush=True)
        result=proposed.partition(ideal,prepared,progress=progress)
        progress_file.close();progress_file=None
        # Full ideal source edge intervals, not actual rendered/collision coverage.
        polygons=result['outside']+[row['polygon']for row in result['inside']]
        boundaries=[closed_segment_covered(a,b,polygons)for a,b in zip(face,face[1:]+face[:1])]
        assert all(boundaries)
        # Same unchanged packer, one face only. No production import or sampler.
        pieces=prior.oracle.packed_pieces(polygons,ideal)
        n=prior.oracle.normal(face);assert n[1]
        packed_digest=hashlib.sha256();excluded=0;collapsed=0;residuals=[]
        for piece in pieces:
            t=piece['packedPieceTriplet'];packed_digest.update(np.asarray(t,dtype='<f8').tobytes())
            (ax,_,az),(bx,_,bz),(cx,_,cz)=t
            determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz)
            excluded+=abs(determinant)<1e-10
            collapsed+=not any(prior.oracle.normal(prior.oracle.points(t)))
            residuals.extend(abs(v/n[1])for v in piece['exactPackedSourcePlaneResiduals'])
        for pin in pins['evidenceRefs']:check(pin)
        check(contract['inputPinsRef'])
        packet=dict(scope='ONE source-private face891 V3 only, not a constructor or full physical proof',
             face=891,completeFaceRelevantUniqueMasks=539,completeFaceRelevantOccurrences=2415,
             processedUniqueMasks=len(result['maskDecisionAccounting']),
             masksUnvisitedOnlyAfterCompleteInsideAssignment=result['masksNotVisitedAfterCompleteInsideAssignment'],
             elapsedChildSeconds=time.monotonic()-started,complete=True,
             exactIdealPartition=prior.oracle.serial(result),idealCompleteSourceEdgesCovered=boundaries,
             outputInsidePolygons=len(result['inside']),outputOutsidePolygons=len(result['outside']),
             packedFacetCount=len(pieces),orderedOneFacePackedSHA256=packed_digest.hexdigest(),
             rendererExcludedProjectedFacetsAtExistingAbsDetLessThan1eMinus10=excluded,
             exact3DAreaZeroPackedFacets=collapsed,
             maxExactOwnPlaneVerticalPackingResidualM=str(max(residuals,default=F(0))),
             exactOwnPlanePackedPieces=prior.oracle.serial(pieces),
             currentAcceptance=False,physicalAccepted=False,installationApproved=False,
             fullCandidateConstructed=False,V2OracleOrFullActorReplay=False,
             actualPackedClosedMaskCoverageHeightMAXOrdinaryRuntimeAndOverlapQualificationPending=True,
             sourceBytesPoseOrGeometryEdited=False,sourceFaceLineageVerbatim=original,
             inputRefs=pins['evidenceRefs'])
        save(DOC/'one-face-result.json.gz',packet)
        completed=True
        print(json.dumps(dict(oneFaceComplete=True,elapsedChildSeconds=packet['elapsedChildSeconds'],
             insidePolygons=packet['outputInsidePolygons'],outsidePolygons=packet['outputOutsidePolygons'],
             packedFacets=packet['packedFacetCount'],currentAcceptance=False)),flush=True)
    except BaseException as error:
        # Partial mask journal is preserved and never advertised as completion.
        save(DOC/'child-error.json',dict(type=type(error).__name__,message=str(error),
             elapsedChildSeconds=time.monotonic()-started,complete=False,currentAcceptance=False))
        raise
    finally:
        if progress_file is not None:progress_file.close()
        # On success leave deadline protection active through process exit.
        if not completed:signal.setitimer(signal.ITIMER_REAL,0)


def run_once():
    assert os.name=='posix'and not DOC.exists(),'Distinct immutable attempt only; no timeout restart'
    pins=read(PROPOSAL/'draft-pins.json')
    for pin in pins['evidenceRefs']:check(pin)
    DOC.mkdir();token=str(uuid.uuid4());started=time.monotonic();deadline=started+MAX_CHILD_SECONDS
    save(DOC/'launch-contract.json',dict(token=token,parentPID=os.getpid(),deadlineMonotonic=deadline,
         maxChildSeconds=MAX_CHILD_SECONDS,face=891,runOnceOnly=True,inputPinsRef=ref(PROPOSAL/'draft-pins.json')))
    child_process=None;timed_out=False;status=None;parent_error=None
    try:
        with (DOC/'closed-child-stdout.log').open('wb')as log:
            child_process=subprocess.Popen([sys.executable,__file__,'--private-child-token',token],cwd=ROOT,
                 stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            save(DOC/'parent-process.json',dict(parentPID=os.getpid(),childPID=child_process.pid,
                 controlledChildPGID=child_process.pid,originalV2ProcessesNeverTargeted=True))
            while child_process.poll()is None:
                if time.monotonic()>=deadline:
                    timed_out=True
                    # No grace extension: stop only this newly-owned process group.
                    try:os.killpg(child_process.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    break
                time.sleep(min(.05,max(0,deadline-time.monotonic())))
            status=child_process.wait(timeout=5)
    except BaseException as error:
        parent_error=dict(type=type(error).__name__,message=str(error))
        save(DOC/'parent-error.json',dict(**parent_error,complete=False,currentAcceptance=False))
    finally:
        if child_process is not None and child_process.poll()is None:
            try:os.killpg(child_process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            status=child_process.wait(timeout=5)
    complete=parent_error is None and not timed_out and status==0 and (DOC/'one-face-result.json.gz').is_file()
    if complete:
        try:
            packet=read(DOC/'one-face-result.json.gz')
            assert packet['complete']and packet['face']==891 and not packet['currentAcceptance']
            assert packet['elapsedChildSeconds']<=MAX_CHILD_SECONDS
            for pin in packet['inputRefs']:check(pin)
        except BaseException as error:
            complete=False;parent_error=dict(type=type(error).__name__,message=str(error))
            save(DOC/'parent-verification-error.json',dict(**parent_error,complete=False,currentAcceptance=False))
    direct_absent=child_process is None or not Path('/proc',str(child_process.pid)).exists()
    assert direct_absent
    outputs=[ref(path)for path in sorted(DOC.iterdir())if path.is_file()]
    summary=dict(complete=complete,oneFaceOnly=True,actualChildExitCode=status,hardDeadlineTriggered=timed_out,
         elapsedParentSeconds=time.monotonic()-started,maxChildSeconds=MAX_CHILD_SECONDS,
         childPID=child_process.pid if child_process is not None else None,
         controlledChildCreated=child_process is not None,parentError=parent_error,
         controlledChildReapedAndDirectPIDAbsent=True,
         partialProgressIsNotCompletion=True,evidenceRefs=outputs,
         currentAcceptance=False,physicalAccepted=False,fullCandidateConstructed=False,
         databaseCalls=0,reservationsClaimed=0,originalV2NeverStoppedOrEdited=True)
    save(DOC/'terminal-summary.json',summary);print(json.dumps(summary,sort_keys=True),flush=True)
    return 0 if complete else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-one-face891-v3-only',action='store_true')
    modes.add_argument('--private-child-token')
    args=parser.parse_args()
    if args.private_child_token:return child(args.private_child_token)
    return run_once()

if __name__=='__main__':sys.exit(main())
