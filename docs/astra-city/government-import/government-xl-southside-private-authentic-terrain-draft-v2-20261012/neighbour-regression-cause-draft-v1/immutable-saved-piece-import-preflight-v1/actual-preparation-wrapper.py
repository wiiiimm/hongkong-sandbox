import sys,subprocess,json,hashlib,re,datetime
from pathlib import Path
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';D=R/'docs/astra-city/government-import/government-xl-southside-private-authentic-terrain-draft-v2-20261012/neighbour-regression-cause-draft-v1';O=D/'immutable-saved-piece-import-preflight-v1';O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'southside_saved_finite_piece_guard_domain_v1_20261012.py':'d55dfeaed503b1a0ed64dbf848612d3096cfd41c03147932084bfd1db169b66a','test_southside_saved_finite_piece_guard_domain_v1_20261012.py':'4a14aac3b098a5a069754190cb3377d8cce8ea615776b20019a5a534bfd3a363','xl-southside-saved-piece-whole-form-compatibility-draft-v1-20261012.py':'b09fdeaff243fcdf85cd8910c899b10f9868e1d24497da669b164252461f82e6'}
for n,h in expected.items():assert sha(H/n)==h
assert sha(D/'SAVED-PIECE-COMPATIBILITY-METHOD.md')=='45e2f6389e10fe465262f1923c75c4c91badfb20b9a91f49bed15f50548fc019'
steps=[]
def call(args,name,cwd):
 p=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);log=O/(name+'.log');log.open('x').write(p.stdout);steps.append(dict(name=name,argv=args,exitCode=p.returncode,logPath=str(log.relative_to(R)),logSHA256=sha(log)));print(name,p.returncode,p.stdout,flush=True);return p
p=call([sys.executable,'-m','unittest','-v','test_southside_saved_finite_piece_guard_domain_v1_20261012'],'tests',H);m=re.search(r'Ran (\d+) tests?',p.stdout);count=int(m.group(1))if m else None
validation=dict(expectedTests=10,actualTests=count,exitCode=p.returncode,codePins=[dict(path=str((H/n).relative_to(R)),sha256=h)for n,h in expected.items()],methodPin=dict(path=str((D/'SAVED-PIECE-COMPATIBILITY-METHOD.md').relative_to(R)),sha256=sha(D/'SAVED-PIECE-COMPATIBILITY-METHOD.md')),testLogPin=steps[-1],noDB=True,noLease=True,noCalculation=True)
(O/'test-validation.json').open('x').write(json.dumps(validation,indent=2)+'\n')
if p.returncode or count!=10:sys.exit(1)
caller=H/'xl-southside-saved-piece-whole-form-compatibility-draft-v1-20261012.py'
code="import sys,importlib.util;from pathlib import Path;p=Path(sys.argv[1]);sys.path.insert(0,str(p.parent));s=importlib.util.spec_from_file_location('southside_saved_piece_readonly_preparation',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print('reviewed-caller-import PASS; main not executed')"
p=call([sys.executable,'-c',code,str(caller)],'import',R)
if p.returncode:sys.exit(p.returncode)
p=call([sys.executable,str(caller),'--preflight-only'],'preflight',R)
for n,h in expected.items():assert sha(H/n)==h
(O/'preparation-validation.json').open('x').write(json.dumps(dict(steps=steps,allStepsExitZero=all(q['exitCode']==0 for q in steps),exact10FocusedTestsPass=True,originalReviewedCodeUnchanged=True,noDB=True,noLease=True,noBoundedCalculation=True,validationSHA256=sha(O/'test-validation.json')),indent=2)+'\n')
print(json.dumps(dict(folder=str(O.relative_to(R)),testValidationSHA256=sha(O/'test-validation.json'),preparationValidationSHA256=sha(O/'preparation-validation.json'),exitCode=p.returncode)),flush=True)
sys.exit(p.returncode)
