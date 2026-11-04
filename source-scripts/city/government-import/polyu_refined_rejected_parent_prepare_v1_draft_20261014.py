"""ROOT-only fixtures/import/pin/schema preparation; no source numerical worker."""
from pathlib import Path
import json,hashlib,gzip,sys,os,subprocess,ast
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import'
P=BASE/'government-xl-polyu-refined-rejected-parent-nomination-v1-20261014-proposal'
CALLER=HERE/'polyu_refined_rejected_parent_nomination_v1_draft_20261014.py';HELPER=HERE/'polyu_refine_rejected_parent_regions_v1_draft_20261014.py';TEST=HERE/'test_polyu_refine_rejected_parent_regions_v1_draft_20261014.py'
OLD=BASE/'government-xl-polyu-four-gap-source-compatible-parent-regions-v1-20261014-proposal'
NOM=BASE/'government-xl-polyu-four-compatible-parent-region-nomination-v1-20261014';CAP=BASE/'government-xl-polyu-four-compatible-parent-current-production-v2-20261014'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):
 with p.open('x')as f:json.dump(v,f,sort_keys=True,separators=(',',':'));f.write('\n')
def distinct(rows):
 d={}
 for q in rows:
  if q['path']in d:assert d[q['path']]==q
  d[q['path']]=q
 return [d[p]for p in sorted(d)]
def closure():
 seen=set();todo=[CALLER,HELPER,TEST,Path(__file__)]
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return [ref(p)for p in sorted(seen)]
def main():
 assert '--prepare-only'in sys.argv
 old=read(OLD/'nomination-draft-pins.json');inputs=old['inputRefs']+[ref(OLD/'nomination-draft-pins.json'),ref(NOM/'result.json'),ref(NOM/'ROOT-VERIFIED.json'),ref(NOM/'private-compatible-current-parent-append-nomination.json.gz'),ref(CAP/'result.json'),ref(CAP/'private-native-terrain-candidate.json.gz'),ref(BASE/'government-xl-polyu-five-residual-guard-sites-saved-attribution-v1-20261014-proposal/five-site-saved-membership.json')]
 code=distinct(old['codeRefs']+closure()+[ref(P/'METHOD.md')]);declared=distinct(code+inputs)
 def fence():
  for q in declared:assert ref(ROOT/q['path'])==q
 fence();commands=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(name,cmd):
  log=P/(name+'.log')
  with log.open('xb')as f:result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=result.returncode,log=ref(log)));fence();assert result.returncode==0,(name,result.returncode);return log
 log=run('actual-nine-refinement-fixtures',[sys.executable,str(TEST),'-v']);assert 'Ran 9 tests'in log.read_text()and '\nOK\n'in log.read_text()
 validation=P/'helper-validation.json';save(validation,dict(passedTests=9,failedTests=0,exitCode=0,executedCodeRefs=[ref(HELPER),ref(TEST)],evidenceRefs=[ref(HELPER),ref(TEST),ref(log)]))
 nom=read(NOM/'private-compatible-current-parent-append-nomination.json.gz')
 save(P/'draft-pins.json',dict(caller=ref(CALLER),codeRefs=code,inputRefs=distinct(inputs),validationRef=ref(validation),completePriorMeshBinding=nom['newCompleteMeshBinding']))
 run('actual-refinement-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-refinement-schema',[sys.executable,str(CALLER),'--schema-only']);fence()
 save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),beforeEndAllPinsVerified=True,transitivePythonCodeRefs=code,commands=commands,evidenceRefs=[ref(validation),ref(P/'draft-pins.json')]+[q['log']for q in commands],noSourceNumericalWorkerLeaseDB=True))
 print(json.dumps(dict(passed=True,preparation=ref(P/'actual-readonly-preparation.json'))))
if __name__=='__main__':main()
