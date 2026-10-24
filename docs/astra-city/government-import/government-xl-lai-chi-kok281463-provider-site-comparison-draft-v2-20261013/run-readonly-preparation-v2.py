"""Authorised isolated import/preflight only; never model/DB/lease execution."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CALLER=HERE/'source-component-comparison-draft-v2.py'
CONTRACT=HERE/'comparison-input-contract-v2.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=HERE/'actual-readonly-preparation-v2';out.mkdir(exist_ok=False)
 contract=json.loads(CONTRACT.read_bytes());pins=dict(contract['allInputHashes'])
 for p in (CONTRACT,Path(__file__)):pins[str(p.relative_to(ROOT))]=sha(p)
 for rel,value in pins.items():assert sha(ROOT/rel)==value
 for rel in contract['staticLiteralLocalPythonClosure']:ast.parse((ROOT/rel).read_bytes(),filename=rel)
 import_code="import importlib.util,json,sys;from pathlib import Path;p=Path(sys.argv[1]);s=importlib.util.spec_from_file_location('lckp_readonly_v2',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);h=m.HERE;loaded=[str(Path(x.__file__).resolve()) for x in sys.modules.values() if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(h)];assert loaded==[],loaded;probe=m.summary('0'*64,1,1,0);assert probe['uids']==['landsd/281463:0'];assert probe['currentAcceptance'] is False;print(json.dumps({'imported':True,'projectGeometryOrDBModulesImported':loaded,'UIDsSummarySchemaPassed':True,'sourceDecode':False,'DB':False,'lease':False}))"
 commands=[('isolated-import',[sys.executable,'-I','-c',import_code,str(CALLER)]),('preflight',[sys.executable,'-I',str(CALLER),'--preflight-only'])]
 results=[]
 for name,command in commands:
  result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
  for suffix,value in (('stdout.log',result.stdout),('stderr.log',result.stderr)):
   with (out/(name+'.'+suffix)).open('x') as stream:stream.write(value)
  row={'name':name,'command':command,'exitCode':result.returncode,'stdoutSHA256':sha(out/(name+'.stdout.log')),'stderrSHA256':sha(out/(name+'.stderr.log'))}
  if result.returncode==0:row['actualResult']=json.loads(result.stdout)
  results.append(row)
  if result.returncode!=0:break
 after={rel:sha(ROOT/rel) for rel in pins};unchanged=after==pins
 passed=len(results)==2 and all(r['exitCode']==0 for r in results) and unchanged
 validation={'allPassed':passed,'commands':results,'allInputHashesBefore':pins,'allInputHashesAfter':after,'literalInputs':len(pins),'allStartEndPinsUnchanged':unchanged,'staticLiteralClosureFiles':len(contract['staticLiteralLocalPythonClosure']),'canonicalResourceCount':18,'actualOriginalModelTestsRun':0,'actualSourceDecodeOrCensusExecuted':False,'DBQueriesOrWrites':False,'reservationsClaimed':False,'normalExecutionByThisAgent':False,'priorExactSourceJobCheckedFromSavedBytesOnly':contract['priorExactSourceReceipt']}
 with (out/'validation.json').open('x') as stream:json.dump(validation,stream,indent=2);stream.write('\n')
 print(json.dumps({'allPassed':passed,'actualExits':[r['exitCode'] for r in results],'beforeEndLiteralInputs':len(pins),'callerSHA256':sha(CALLER),'contractSHA256':sha(CONTRACT),'validationSHA256':sha(out/'validation.json')}))
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
