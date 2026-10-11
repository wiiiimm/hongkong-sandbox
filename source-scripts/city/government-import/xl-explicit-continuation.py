"""Run a bounded frozen source list, retaining independent outcomes and process logs."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from run import ROOT,HERE,read,save


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);p.add_argument('--batch',required=True)
    args=p.parse_args();assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    base=(ROOT/args.base).resolve();assert base.is_relative_to(ROOT)
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    assert not (doc/'commands.json').exists(),'Completed commands are immutable'
    rows=read(base/'check-selection.json.gz')['rows'];assert 1<=len(rows)<=200
    assert len({r['uid'] for r in rows})==len(rows)
    local.mkdir(parents=True,exist_ok=True);outcomes=[]
    for row in rows:
        child=args.batch+'-'+row['uid'].split('/')[1].replace(':','-')
        target=ROOT/'docs/astra-city/government-import'/child
        # Never implicitly reuse a differently owned/completed child stage.
        assert not target.exists(),'Use explicit verified result reuse instead of overwriting a child'
        command=[sys.executable,str(HERE/'xl-indexed-terrain-continuation.py'),'--uid',row['uid'],
                 '--batch',child,'--base',args.base]
        log=local/(child+'.log');print(json.dumps({'starting':row['uid'],'name':row['name'],'completed':len(outcomes),'total':len(rows)}),flush=True)
        with log.open('w') as output:proc=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
        result=read(target/'result.json') if (target/'result.json').exists() else None
        outcomes.append({'uid':row['uid'],'name':row['name'],'batch':child,'command':command,
                         'returncode':proc.returncode,'log':str(log.relative_to(ROOT)),'result':result})
        save(doc/'working-commands.json',{'batch':args.batch,'rows':outcomes,'total':len(rows)})
        print(json.dumps({'completed':row['uid'],'returncode':proc.returncode,'checksPassed':result and result['scriptChecksPassed'],
                          'reasons':result and result['reasons']}),flush=True)
    save(doc/'commands.json',{'batch':args.batch,'rows':outcomes,'primarySources':len(rows),
        'newlyInstalled':0,'scriptExternalAICalls':0,'qualification':'Each child has separate fenced ownership and exact Neon result. Failed command outcomes remain explicit, never installation credit.'})


if __name__=='__main__':main()
