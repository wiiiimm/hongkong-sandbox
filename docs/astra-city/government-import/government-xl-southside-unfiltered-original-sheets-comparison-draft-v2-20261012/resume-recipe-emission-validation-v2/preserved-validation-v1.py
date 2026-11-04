from pathlib import Path
import hashlib,json,subprocess
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');D=R/'docs/astra-city/government-import/government-xl-southside-unfiltered-original-sheets-comparison-draft-v2-20261012';H=R/'source-scripts/city/government-import'
p=H/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012.py';sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(p)=='3576a65a098812bca5a7821c60c48b896583f3ae6191fdbbc75163c3f34f5cdb'
out=D/'resume-recipe-emission-v1';out.mkdir(exist_ok=False);target=D/'root-issued-resume-recipe.json';assert not target.exists()
before=(R/'3d-viewer/city/data/manifest.json').read_bytes();assert hashlib.sha256(before).hexdigest()=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
run=subprocess.run(['/tmp/astra-city-venv/bin/python',str(p),'--resume-recipe-only'],cwd=R,capture_output=True)
(out/'stdout.log').write_bytes(run.stdout);(out/'stderr.log').write_bytes(run.stderr)
meta=dict(command=['/tmp/astra-city-venv/bin/python',str(p),'--resume-recipe-only'],exitCode=run.returncode,callerSHA256=sha(p),stdoutSHA256=sha(out/'stdout.log'),stderrSHA256=sha(out/'stderr.log'),workerStarted=False,descriptorCreated=False,retirementPerformed=False,currentAcceptance=False)
(out/'invocation.json').write_text(json.dumps(meta,sort_keys=True,indent=2)+'\n')
assert run.returncode==0,run.stderr.decode('utf-8',errors='replace');assert not run.stderr
row=json.loads(run.stdout)
assert set(row)=={'kind','inputPins','codePins','callerSHA256','currentManifestSHA256','completeFourSheetDeclaredFacets','resources','currentAcceptance','installationApproved'}
assert row['kind']=='southside-resume-source-recipe-v1'and row['callerSHA256']==sha(p)
assert row['currentManifestSHA256']=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'and row['completeFourSheetDeclaredFacets']==774477 and len(row['resources'])==52
assert row['resources']==sorted(set(row['resources']))and row['currentAcceptance']is False and row['installationApproved']is False
for key in ['inputPins','codePins']:
 assert row[key]and row[key]==sorted(row[key],key=lambda q:q['path'])and len({q['path']for q in row[key]})==len(row[key])
 for pin in row[key]:
  assert set(pin)=={'path','sha256'}and not pin['path'].startswith('/')and '..'not in pin['path'].split('/')and sha(R/pin['path'])==pin['sha256']
assert(R/'3d-viewer/city/data/manifest.json').read_bytes()==before
assert sha(p)=='3576a65a098812bca5a7821c60c48b896583f3ae6191fdbbc75163c3f34f5cdb'
with target.open('xb')as f:f.write(run.stdout)
result=dict(meta,recipePath=str(target.relative_to(R)),recipeSHA256=sha(target),recipeBytes=target.stat().st_size,inputPinCount=len(row['inputPins']),codePinCount=len(row['codePins']),resources=len(row['resources']),completeDeclaredGroundFacets=774477,allActualPinsVerified=True,currentManifestUnchanged=True,noLeaseClaim=True,noDB=True)
(out/'validation.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
