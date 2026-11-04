"""Finish passing explicit sources after frozen-input workers, without more prompts."""
import argparse,json,subprocess,sys,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('base','primary','followups','sequence','batch'):p.add_argument('--'+n,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and Path(a.batch).name==a.batch
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    assert not doc.exists(),'Fresh explicit installation continuation required'
    for path in (a.base,a.primary,a.followups,a.sequence):assert (ROOT/path).resolve().is_relative_to(ROOT)
    waiting=time.monotonic();done=ROOT/a.sequence/'commands.json'
    while not done.exists():
        assert time.monotonic()-waiting<10800, 'Known input workers did not complete in three hours'
        time.sleep(5)
    sequence=read(done);assert all(r['returncode']==0 for r in sequence['rows']), 'Input continuation command failed; resolve explicit failure first'
    sources=read(ROOT/a.primary/'commands.json')['rows'];latest={r['uid']:r for r in sources}
    for row in read(ROOT/a.followups/'commands.json')['rows']:
        if row['returncode']==0 and row['result']:latest[row['uid']]=row
    outcomes=[];local.mkdir(parents=True,exist_ok=True)
    for primary in sources:
        row=latest[primary['uid']];result=row['result']
        if not result or not result['scriptChecksPassed']:continue
        previous=ROOT/'docs/astra-city/government-import'/row['batch']
        candidates=read(previous/'terrain-candidates.json');assert len(candidates)==1
        patch=candidates[0];value=read(ROOT/patch['path']);assert digest((ROOT/patch['path']).read_bytes())==patch['sha256']
        if patch.get('replaces') or not value.get('nativeMesh') or value.get('patches'):
            outcomes.append({'uid':row['uid'],'name':row['name'],'result':None,'reason':'dedicated-retained-grid-or-native-publication-required','source':str(previous.relative_to(ROOT))})
            save(doc/'working-commands.json',{'rows':outcomes});continue
        uid=row['uid'];token=uid.split('/')[1].replace(':','-');recheck=a.batch+'-'+token+'-recheck';installation=a.batch+'-'+token+'-installed'
        steps=[]
        for phase,command in [('recheck',[sys.executable,str(HERE/'xl-recheck-candidate-evidence.py'),'--previous',str(previous.relative_to(ROOT)),'--batch',recheck]),
            ('installed',[sys.executable,str(HERE/'xl-explicit-root-install.py'),'--uid',uid,'--batch',installation,
                '--source','docs/astra-city/government-import/'+recheck,'--base',a.base])]:
            log=local/(token+'-'+phase+'.log');print(json.dumps({'starting':uid,'phase':phase}),flush=True)
            with log.open('w') as out:proc=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
            target=ROOT/'docs/astra-city/government-import'/(recheck if phase=='recheck' else installation)
            new=read(target/'result.json') if (target/'result.json').exists() else None
            steps.append({'phase':phase,'command':command,'returncode':proc.returncode,'batch':target.name,'result':new,'log':str(log.relative_to(ROOT))})
            if proc.returncode or new is None or (phase=='recheck' and not new['scriptChecksPassed']):break
        outcomes.append({'uid':uid,'name':primary['name'],'steps':steps,'result':steps[-1]['result']})
        save(doc/'working-commands.json',{'batch':a.batch,'rows':outcomes})
        print(json.dumps({'completed':uid,'installed':bool(steps[-1]['result'] and steps[-1]['result'].get('installedUids')),'returncode':steps[-1]['returncode']}),flush=True)
        if steps[-1]['result'] and steps[-1]['result'].get('installedUids'):
            # Publication is a meaningful checkpoint: commit/push promptly even
            # when independent held-source processing remains in this cohort.
            save(doc/'installation-ready-for-commit.json',{'uid':uid,'installation':steps[-1]['batch']})
            print(json.dumps({'commitRequired':uid,'installation':steps[-1]['batch']}),flush=True)
            # The coordinator keeps processing; the active agent stages exact
            # installation paths and pushes without another user prompt.
    save(doc/'commands.json',{'batch':a.batch,'rows':outcomes,'scriptExternalAICalls':0,'modelGeometryChanges':0,
        'qualification':'Only script-passing explicit source candidates. Fresh current recheck, staged/live browser, guarded publisher and exact installed ledger determine installation credit. Commit each actual installation promptly.'})

if __name__=='__main__':main()
