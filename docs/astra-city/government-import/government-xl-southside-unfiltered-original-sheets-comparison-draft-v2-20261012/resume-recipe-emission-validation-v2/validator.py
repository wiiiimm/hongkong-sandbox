from pathlib import Path
import hashlib,json,traceback
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');D=R/'docs/astra-city/government-import/government-xl-southside-unfiltered-original-sheets-comparison-draft-v2-20261012';E=D/'resume-recipe-emission-v1';O=D/'resume-recipe-emission-validation-v2';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();row=json.loads((E/'stdout.log').read_bytes());inv=json.loads((E/'invocation.json').read_text());target=D/'root-issued-resume-recipe.json'
assert inv['exitCode']==0 and (E/'stderr.log').read_bytes()==b''and sha(E/'stdout.log')==inv['stdoutSHA256']
assert not target.exists();assert set(row)=={'kind','inputPins','codePins','callerSHA256','currentManifestSHA256','completeFourSheetDeclaredFacets','resources','currentAcceptance','installationApproved'}
assert row['kind']=='southside-resume-source-recipe-v1'and row['callerSHA256']==inv['callerSHA256']=='3576a65a098812bca5a7821c60c48b896583f3ae6191fdbbc75163c3f34f5cdb'
assert row['currentManifestSHA256']=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'and row['completeFourSheetDeclaredFacets']==774477 and len(row['resources'])==52
assert row['resources']==sorted(set(row['resources']))and row['currentAcceptance']is False and row['installationApproved']is False
findings=[]
for key in ['inputPins','codePins']:
 assert row[key]and len({q['path']for q in row[key]})==len(row[key])
 # Preserve and verify the reviewed producer's sorted(Path) order exactly.
 assert row[key]==sorted(row[key],key=lambda q:Path(q['path']))
 findings.append(dict(key=key,count=len(row[key]),stringOrderEqualsPathOrder=row[key]==sorted(row[key],key=lambda q:q['path']),actualPathOrderVerified=True))
 for pin in row[key]:assert set(pin)=={'path','sha256'}and not pin['path'].startswith('/')and '..'not in pin['path'].split('/')and sha(R/pin['path'])==pin['sha256']
assert sha(R/'3d-viewer/city/data/manifest.json')==row['currentManifestSHA256']
with target.open('xb')as f:f.write((E/'stdout.log').read_bytes())
script=Path('/tmp/emit-southside-reviewed-resume-recipe-20261012.py');(O/'preserved-validation-v1.py').write_bytes(script.read_bytes())
failure=dict(kind='local-recipe-audit-ordering-failure',producerExitCode=0,producerSourceUnchanged=True,failedAudit='string-key lexical sorting versus producer sorted(Path)',numericalPredicatesRun=False,newWorkerStarted=False,recipeEmissionRepeated=False,rawOutputPin=dict(path=str((E/'stdout.log').relative_to(R)),sha256=sha(E/'stdout.log')),preservedAuditSHA256=sha(O/'preserved-validation-v1.py'),currentAcceptance=False)
(O/'preserved-audit-failure-v1.json').write_text(json.dumps(failure,sort_keys=True,indent=2)+'\n')
result=dict(kind='southside-isolated-resume-recipe-validation-v2',recipePath=str(target.relative_to(R)),recipeSHA256=sha(target),recipeBytes=target.stat().st_size,findings=findings,resourceCount=52,completeDeclaredGroundFacets=774477,callerSHA256=row['callerSHA256'],currentManifestSHA256=row['currentManifestSHA256'],allActualPinsVerified=True,noDB=True,noLeaseClaim=True,workerStarted=False,descriptorCreated=False,retirementPerformed=False,recipeEmissionRepeated=False,currentAcceptance=False)
(O/'validation.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');(O/'validator.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,sort_keys=True))
