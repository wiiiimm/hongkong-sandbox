"""Continue explicit original-TIN compute after verified installation and release.

Never approves browser images or installs the next batch. Existing source,
terrain, runtime and lease guards run unchanged, in dependent order.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import time
from islands_direct_stage import ROOT, HERE, read, save, rel, sha
from run import connect


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('after-batch','batch','script','runtime-batch','clear-batch'):
        parser.add_argument('--'+key,required=True)
    parser.add_argument('--bounds',type=Path,required=True)
    args=parser.parse_args()
    assert all(v.startswith('government-islands-') and '/' not in v for v in (args.after_batch,args.batch,args.runtime_batch,args.clear_batch))
    script=HERE/args.script;assert script.parent==HERE and script.name.startswith('islands_') and script.suffix=='.py' and script.is_file()
    doc=ROOT/'docs/astra-city/government-import'/args.batch
    prior=ROOT/'docs/astra-city/government-import'/args.after_batch
    control=HERE/'local'/(args.batch+'-continuation')
    assert not control.exists();control.mkdir(parents=True)
    expected_manifest=read(doc/'nomination.json')['manifestSHA256']
    bounds=args.bounds.resolve();assert bounds.is_relative_to(ROOT)
    assert read(bounds)['currentManifest']['sha256']==expected_manifest
    deadline=time.monotonic()+14400
    while True:
        assert sha(ROOT/'3d-viewer/city/data/manifest.json')==expected_manifest,'Fresh context required after a manifest change'
        if (prior/'independent-installed-readback.json').exists():
            checked=read(prior/'independent-installed-readback.json');installed=read(prior/'integration.json')
            assert checked['passed'] and installed['neonVerified'] and checked['snapshotId']==installed['snapshotId']
            assert installed['manifestSHA256']==expected_manifest
            receipt=read(HERE/'local'/args.after_batch/'install-reservation.json')
            with connect() as db:
                db.execute('SET TRANSACTION READ ONLY')
                row=db.execute('SELECT released_at FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',(receipt['token'],receipt['owner'])).fetchone()
            assert row is not None
            if row[0] is not None:break
        assert time.monotonic()<deadline
        save(control/'state.json',{'state':'waiting-for-independent-installed-readback-and-release','publication':False})
        time.sleep(10)
    identity=doc/'identity-evidence.json.gz'
    steps=[('terrain-stage',[sys.executable,HERE/'islands_stage_owned.py','--batch',args.batch,'--script',args.script]),
           ('complete-current-scope',[sys.executable,HERE/'islands_tin_current_scope.py','--batch',args.batch,'--bounds',bounds,'--identity',identity]),
           ('complete-current-runtime',[sys.executable,HERE/'islands_tin_runtime.py','--source-batch',args.batch,'--batch',args.runtime_batch,'--wait'])]
    completed=[]
    for phase,command in steps:
        save(control/'state.json',{'state':phase,'completed':completed,'publication':False})
        log=control/(phase+'.log')
        with log.open('x') as stream:
            code=subprocess.run([str(x) for x in command],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT).returncode
        if code:
            save(control/'state.json',{'state':'script-error','phase':phase,'exitCode':code,'log':rel(log),'completed':completed,'publication':False})
            raise RuntimeError('Retain and inspect exact failed attempt; no next publication occurred')
        completed.append({'phase':phase,'log':rel(log),'sha256':sha(log)})
    result=read(doc/'runtime-current/summary.json')
    if result['clearScriptCandidates']:
        log=control/'clear-subset.log'
        with log.open('x') as stream:
            subprocess.run([sys.executable,HERE/'islands_tin_clear_subset.py','--source-batch',args.batch,'--batch',args.clear_batch,'--identity',identity],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
    save(control/'state.json',{'state':'checks-complete-awaiting-browser-review' if result['clearScriptCandidates'] else 'checks-complete-retained-negatives',
         'completed':completed,'models':result['models'],'clearScriptCandidates':result['clearScriptCandidates'],'publication':False,'newlyInstalled':0})


if __name__=='__main__':main()
