"""Apply tested sampler/publication repair between owned batches, then recover."""
import json, os, signal, subprocess, sys, time
from pathlib import Path
from run import ROOT, HERE, read, save, digest

BATCH='government-xl-safe-boundary-recovery-sequence-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
AFTER=ROOT/'docs/astra-city/government-import/government-xl-retained-compatibility-sequence-20261006/commands.json'
PID=351105
INSTALLERS=['xl-explicit-root-install.py','xl-explicit-cell-root-install.py',
            'xl-explicit-owned-retained-install.py','xl-explicit-cell-retained-install.py',
            'xl-explicit-cell-assembly-install.py','xl-explicit-cell-installed-support-install.py']

def main():
    assert not DOC.exists(),'Fresh boundary only'
    geo=ROOT/'3d-viewer/city/geo.js'
    frozen={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [geo,*[HERE/n for n in INSTALLERS]]}
    save(DOC/'plan.json',{'inputHashes':frozen,'after':str(AFTER.relative_to(ROOT)),
        'queuedSuccessorPid':PID,'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})
    LOCAL.mkdir(parents=True,exist_ok=True);phases=[]
    def phase(name,command):
        log=LOCAL/(name+'.log')
        with log.open('w') as out:status=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT).returncode
        phases.append({'name':name,'command':command,'returncode':status,'log':str(log.relative_to(ROOT))})
        save(DOC/'working-commands.json',{'phases':phases,'activeWorkers':0,'queuedFollowups':1})
        assert status==0, 'Explicit phase failed: '+str(log)
    while not AFTER.exists():time.sleep(10)
    prior=read(AFTER);assert prior['activeWorkers']==prior['queuedFollowups']==0
    args=Path(f'/proc/{PID}/cmdline').read_bytes().split(b'\0')
    assert args[:2]==[b'/tmp/astra-city-venv/bin/python',b'source-scripts/city/government-import/xl-basic-parent-complete-handoff-sequence-20261006.py']
    assert '\nState:\tT' in Path(f'/proc/{PID}/status').read_text(),'Queued successor must be stopped before source claims'
    for path,sha in frozen.items():assert digest((ROOT/path).read_bytes())==sha
    old='height:(x,z)=>waterAt(x,z)?.illustrativeBed??(patchAt(x,z)?.height(x,z)??(native?sample(x,z,true):Math.max(1.2,sample(x,z,true))))'
    new='height:(x,z)=>renderedPatchHeight(patchAt(x,z)?.height(x,z),waterAt(x,z)?.illustrativeBed,()=>native?sample(x,z,true):Math.max(1.2,sample(x,z,true)))'
    content=geo.read_text();assert content.count(old)==1
    geo.write_text("import {renderedPatchHeight} from './rendered-patch-height.js';\n"+content.replace(old,new))
    for name in INSTALLERS:
        path=HERE/name;content=path.read_text();old="if __name__=='__main__':owned() if args.owned else start()";assert content.count(old)==1
        content=content.replace(old,"if __name__=='__main__':\n    if args.owned:\n        from publication_lock import locked_publication\n        with locked_publication(ROOT):owned()\n    else:start()")
        path.write_text(content)
    path=HERE/'xl-reconcile-published-original.py';content=path.read_text();old="if __name__=='__main__':main()";assert content.count(old)==1
    path.write_text(content.replace(old,"if __name__=='__main__':\n    if '--owned' in sys.argv:\n        from publication_lock import locked_publication\n        with locked_publication(ROOT):main()\n    else:main()"))
    phase('publication-lock-tests',[sys.executable,'-m','unittest','discover','-s',str(HERE),' -p'.strip(),'test_publication_lock.py'])
    phase('rendered-height-tests',['node','--test',str(HERE/'rendered-patch-height.test.mjs')])
    phase('compile',['node','--check',str(geo)])
    phase('python-compile',[sys.executable,'-m','py_compile',*[str(HERE/n) for n in INSTALLERS],str(path)])
    save(DOC/'applied.json',{'modifiedFiles':[str(p.relative_to(ROOT)) for p in [geo,*[HERE/n for n in INSTALLERS],path]],
                           'inputHashes':frozen,'modelGeometryChanges':0,'scriptExternalAICalls':0})
    print(json.dumps({'safeBoundaryApplied':True,'next':'fresh current physical and browser recovery'}),flush=True)
    base='docs/astra-city/government-import/government-xl-uncovered-57-inputs-20261006'
    previous='docs/astra-city/government-import/government-xl-uncovered-qualified-sequence-20261006-270142-0'
    installed=previous+'-installed'
    current='government-xl-pumping-station-current-recovery-20261006'
    phase('physical-recovery',[sys.executable,str(HERE/'xl-published-original-current-recheck.py'),'--previous',previous,
          '--prior-installed',installed,'--batch',current,'--base',base])
    physical=ROOT/'docs/astra-city/government-import'/current
    assert read(physical/'result.json')['scriptChecksPassed'], 'Fresh physical checks remain held; no review recovered'
    recovered='government-xl-pumping-station-current-reconciled-20261006'
    phase('installed-recovery',[sys.executable,str(HERE/'xl-reconcile-published-original.py'),
                               '--source',str(physical.relative_to(ROOT)),'--batch',recovered])
    result=read(ROOT/'docs/astra-city/government-import'/recovered/'result.json')
    assert result['installedUids']==['landsd/270142:0'] and result['runtimeAssetsAdded']==0
    save(DOC/'inspection-required.json',{'installation':recovered,'jobId':result['jobId'],'resultSHA256':digest((ROOT/'docs/astra-city/government-import'/recovered/'result.json').read_bytes())})
    print(json.dumps({'currentReviewRecovered':True,'coordinatorInspectionAndCommitRequired':recovered}),flush=True)
    marker=DOC/'inspection-and-commit-complete.json'
    while not marker.exists():time.sleep(10)
    accepted=read(marker);assert accepted['jobId']==result['jobId'] and accepted['browserInspected'] and accepted['pushed']
    assert subprocess.check_output(['git','status','--porcelain','--',str((ROOT/'docs/astra-city/government-import'/recovered).relative_to(ROOT))],cwd=ROOT,text=True).strip()==''
    os.kill(PID,signal.SIGCONT)
    save(DOC/'commands.json',{'batch':BATCH,'phases':phases,'currentReviewRecovered':True,'resumedSuccessorPid':PID,
         'activeWorkers':0,'queuedFollowups':0,'scriptExternalAICalls':0,'modelGeometryChanges':0,
         'qualification':'Broader100-XL goal remains active; next complete-parent successor resumes after coordinator inspection and pushed receipt.'})

if __name__=='__main__':main()
