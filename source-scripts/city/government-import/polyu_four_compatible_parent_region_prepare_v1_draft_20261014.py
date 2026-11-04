"""ROOT preparation only: static pins, seven synthetic fixtures, import/schema."""
from pathlib import Path
import ast,json,gzip,hashlib,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import'
P=BASE/'government-xl-polyu-four-gap-source-compatible-parent-regions-v1-20261014-proposal'
CALLER=HERE/'polyu_four_compatible_parent_region_nomination_v1_draft_20261014.py'
HELPER=HERE/'polyu_compatible_current_parent_regions_v1_draft_20261014.py';TEST=HERE/'test_polyu_compatible_current_parent_regions_v1_draft_20261014.py'
FEAS=BASE/'government-xl-polyu-nine-complete-parent-restoration-feasibility-v1-20261013';MAX=BASE/'government-xl-polyu-saved64-actual-max-reviewed-validator-v1-20261014'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):
 with p.open('x')as f:json.dump(v,f,sort_keys=True,separators=(',',':'),allow_nan=False);f.write('\n')
def distinct(qs):
 d={}
 for q in qs:
  if q['path']in d:assert d[q['path']]==q
  d[q['path']]=q
 return [d[p]for p in sorted(d)]
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
 todo=[CALLER,HELPER,TEST,Path(__file__),HERE/'polyu_four_gap_saved_columns_v1_draft_20261014.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'];seen=set()
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
 return sorted(seen)
def build_pins():
 feasibility=read(FEAS/'complete-nine-parent-restoration-feasibility.json.gz');outcome=read(MAX/'unchanged-validator-outcome.json')
 qs=[ref(FEAS/'result.json'),ref(FEAS/'complete-nine-parent-restoration-feasibility.json.gz'),ref(MAX/'result.json'),ref(MAX/'ROOT-VERIFIED.json'),ref(MAX/'unchanged-validator-outcome.json'),
     outcome['metadataOnlyCandidate'],outcome['audit'],feasibility['exactSourceContext'],ref(P/'complete-failed-saved-column-analysis.json'),ref(P/'complete-failed-actual-binary64-guard-boundaries.json')]
 local=read(P/'complete-failed-saved-column-analysis.json');qs+=local['inputRefs']
 for actor in feasibility['rows']:
  if actor['uid']not in ['landsd/72322:0','landsd/89540:0','landsd/258852:0','landsd/305600:0']:continue
  qs.append(actor['completeMask'])
  for mode in actor['sourceWorlds']:
   for chunk in sorted({i//64 for i in mode['conflictingSourceFaces']}):qs.append(mode['chunks'][chunk])
 inputs=distinct(qs)
 for q in inputs:assert ref(ROOT/q['path'])==q
 code=[ref(p)for p in code_paths()]+[ref(P/'METHOD.md'),ref(HERE/'polyu_four_gap_saved_boundary_v1_draft_20261014.mjs'),ref(HERE/'upton_six_basic_guard_samples_v1_20261012.mjs'),ref(ROOT/'3d-viewer/city/geo.js')]
 oldpins=read(MAX.parent/(MAX.name+'-proposal')/'draft-pins.json')
 save(P/'nomination-draft-pins.json',dict(caller=ref(CALLER),codeRefs=distinct(code),inputRefs=inputs,completeOldMeshBinding=oldpins['completeMeshBinding'],
  completedMAXJob=read(MAX/'result.json')['jobId'],completedFeasibilityJob=read(FEAS/'result.json')['jobId'],historicalSourceContext=True,currentAcceptance=False))
def prepare():
 pins=read(P/'nomination-draft-pins.json');assert pins['caller']==ref(CALLER);declared=distinct(pins['codeRefs']+pins['inputRefs'])
 def fence():
  for q in declared:assert ref(ROOT/q['path'])==q
 fence();commands=[];refs=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(name,cmd):
  log=P/(name+'.log')
  with log.open('xb')as out:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));refs.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode)
  return log
 log=run('actual-seven-region-fixtures',[sys.executable,str(TEST),'-v']);text=log.read_text();assert 'Ran 7 tests'in text and '\nOK\n'in text
 validation=P/'region-helper-validation.json';save(validation,dict(passedTests=7,failedTests=0,exitCode=0,executedCodeRefs=[ref(HELPER),ref(TEST)],evidenceRefs=[ref(HELPER),ref(TEST),ref(log)]));refs.append(ref(validation))
 run('actual-nomination-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-nomination-schema',[sys.executable,str(CALLER),'--schema-only']);fence()
 save(P/'actual-nomination-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),helperValidationRef=ref(validation),commands=commands,
  beforeEndAllDeclaredPinsVerified=True,completeTransitivePythonCodeRefs=pins['codeRefs'],evidenceRefs=distinct(refs+[ref(Path(__file__)),ref(P/'nomination-draft-pins.json')]),
  noPartitionPackingFiniteSourceDecodeDBLeaseOrWorker=True))
 print(json.dumps(dict(preparation=ref(P/'actual-nomination-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build_pins();print(json.dumps(dict(pins=ref(P/'nomination-draft-pins.json'))))
 else:assert '--prepare-only'in sys.argv;prepare()
