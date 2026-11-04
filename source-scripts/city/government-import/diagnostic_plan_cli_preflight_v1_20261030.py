"""Check diagnostic plan CLI contracts before any leased model work starts.

Only invokes the explicitly selected Python diagnostic tools with --help. It
never runs phase arguments, claims leases, queues work or grants model credit.
"""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def check(path):
 path=path.resolve();assert path.is_relative_to(ROOT/'docs/astra-city/government-import')
 plan=json.loads(path.read_text());assert len(plan['uids'])==len(set(plan['uids'])),'Duplicate report UIDs in plan'
 assert len({p['batch']for p in plan['phases']})==len(plan['phases']),'Duplicate output batches'
 cache={};checked=[]
 for phase in plan['phases']:
  name=phase['script'];assert Path(name).name==name and name.endswith('.py')
  tool=HERE/name;assert tool.is_file()
  if name not in cache:
   proc=subprocess.run([sys.executable,str(tool),'--help'],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True,timeout=30)
   assert proc.returncode==0,'Help preflight failed for '+name
   cache[name]=set(re.findall(r'--[a-zA-Z][a-zA-Z0-9-]*',proc.stdout))
  flags={v.split('=',1)[0]for v in phase['args']if isinstance(v,str)and v.startswith('--')}
  bad=flags-cache[name];assert not bad,name+' unsupported arguments: '+', '.join(sorted(bad))
  assert not flags&{'--apply','--install'},'Diagnostic plan cannot publish or install'
  checked.append(dict(script=name,batch=phase['batch'],argumentFlags=sorted(flags)))
 return dict(plan=str(path.relative_to(ROOT)),checkedPhases=len(checked),distinctHelpCalls=len(cache),phaseCommandsExecuted=0,leasesClaimed=0,modelAcceptanceGranted=False,phases=checked)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True);a=p.parse_args();result=check(ROOT/a.plan);print(json.dumps({k:v for k,v in result.items()if k!='phases'}))
if __name__=='__main__':main()
