"""Persist current original-model recovery evidence and unfinished work; zero acceptance credit."""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-four-original-recovery-';BATCH=P+'progress-v1-20261101';BASE=ROOT/'docs/astra-city/government-import';LOCAL=HERE/'local'/BATCH

def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'));out=BASE/BATCH;assert not out.exists();records=[];refs=[Path(__file__)]
    for folder in sorted({p for pattern in ['government-xl-peak-retained-*20261101*','government-xl-peak-source-bounds-retained-*20261101*','government-xl-peak-original-physical-context-*20261101*','government-xl-silvercord-lippo-*20261101*','government-xl-peak-harbourfront-*20261101*'] for p in BASE.glob(pattern)}):
        path=folder/'result.json'
        if folder.name==BATCH or not path.is_file():continue
        result=read(path);assert result['batch']==folder.name
        records.append(dict(batch=folder.name,jobId=result['jobId'],result=result));refs.append(path)
    assert records
    with connect()as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        rows={r[0]:(r[1],r[2])for r in db.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId']for r in records],)).fetchall()}
        for r in records:assert rows[r['jobId']]==('complete',r['result'])
    summaries=[dict(batch=r['batch'],jobId=r['jobId'],resultSHA256=digest((BASE/r['batch']/'result.json').read_bytes()),installationApproved=r['result'].get('installationApproved',False),sourceGeometryChanges=r['result'].get('sourceGeometryChanges',0))for r in records]
    assert not any(r['installationApproved']or r['sourceGeometryChanges']for r in summaries)
    save(out/'completed-proof-index.json',dict(rows=summaries,allNeonResultsReadBack=True))
    countpath=BASE/'government-xl-academic309823-after-kai-tak-carpark-original-installed-v1-20261101/full-xl-current-count.json';count=read(countpath);manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==count['manifestSHA256']and count['counts']==dict(total=521,installedVerified=414,remaining=107)
    refs.append(countpath)
    result=dict(uids=['landsd/167911:0','landsd/233227:0','landsd/233997:0','landsd/231645:0'],humanStatus='In process',requiredResource='Further code and compute under existing guards. No AI geometry modelling performed. No new human decision requested.',fixedXLCounts=dict(total=521,installed=414,existingTerminal=3,unfinished=104,notInstalledIncludingTerminal=107),installedDetailedActors=7067,newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,completedProofJobs=len(records),allProofJobsReadBack=True,remainingByUid={
      'landsd/167911:0':'Explicit248218 retention candidate39976faces; exact consolidation31313 still exceeds constructor25k. Source-bounds alternative41278 also fails that cap. Diagnostic production runtime preserves failed admission and reveals actual min gap-19.14047m/low gap-4.69669m, no missing terrain or sampler mismatch. Source/model mobile budget passes450k triangle profile, but physical clearance does not. Complete four-world foundation/low-face diagnostics are running; no budget change or source geometry edits.',
      'landsd/233997:0':'Bounded source association review recorded with fresh provider OBJECTID233626 versus cached233997 explicitly nonexact; stable CSUID/BuildingID/GeoRef and source bytes retained. Terrain domain crosses territory root and a regional grid boundary; disjoint-inside-parent candidate was correctly rejected. Requires coordinated local root/grid terrain, current source physical, neighbour, collision, runtime identity consumption and browser/publication checks.',
      'landsd/231645:0':'Bounded source association review recorded with provider OBJECTID231275 versus cached231645 explicitly nonexact. Local terrain domain intersects native leaf234188 but is not wholly inside it; needs coordinated native/grid terrain and complete retention, physical and all other checks. Four-world original pair contacts remain raw, including Float32 area contacts.',
      'landsd/233227:0':'Original-source extent and physical coverage remain unresolved. Private authentic terrain32901faces; existing budget adapter correctly refuses low parent facets. Proposed guard-removing adapter remains rejected/unwritten. No global guard or publication approval changed; further safe original-source/terrain work remains.'},qualification='Readback-verified evidence and exact actionable reasons only. No source newly corrupt/terminal, installed, approved for runtime or optimised. Whole104unfinished fixedXL scope and bothNULLkeys remain; supporting actors do not replace the objective.')
    save(out/'summary.json',result);refs.extend([out/'completed-proof-index.json',ROOT/'3d-viewer/city/data/manifest.json'])
    module('four_original_recovery_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-model-scripted-recovery-progress-no-acceptance',refs,result)
    print(dict(proofJobsReadBack=len(records),newlyInstalled=0),flush=True)
if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists();claim=reservations.claim('four-original-recovery-proof-checkpoint-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
