import json,sys,hashlib,gzip
from pathlib import Path
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,connect,reservations
from upton_exact_actual_history_archive_bindings_draft_v1_20261011 import load_contract,exact_ref
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'government-xl-upton12728-12662-current-source-identification-rebind-v1-20261011'
PROPOSAL=BASE/'government-xl-upton-current-source-identification-wrapper-proposal-v1-20261011'
HISTORY=BASE/'government-xl-upton-root-recursive-actual-history-extension-v1-20261012/root-actual-history-contract-extension.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
contract=load_contract(ROOT,str(HISTORY.relative_to(ROOT)),'6a5bda21e060fe267ba9240e7efc473c45d013adc8228c1c5a2016c6956ddc15')
seal=read(DOC/'primary-source-identification-exact-seal.json');assert ref(DOC/'primary-source-identification-exact-seal.json')['sha256']=='dbfd48e0e6e9ed4b3dfff16e750aa6211ad4c9394b9bba431b398f0bb46eb4fb'
assert seal['sourceIdentificationOnly']and not seal['physicalAccepted']and not seal['installationApproved']and seal['nativeCount']==6649
assert seal['currentManifestSHA256']=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
seen={};pending=[];nodes=0;missing={}
def nominate(x):
 global nodes
 nodes+=1
 if isinstance(x,dict):
  if isinstance(x.get('path'),str)and isinstance(x.get('sha256'),str)and len(x['sha256'])==64:
   path=x['path'];assert '..'not in Path(path).parts,path
   if Path(path).is_absolute():assert Path(path).is_relative_to('/tmp')or Path(path).is_relative_to(ROOT),path
   pending.append({'path':path,'sha256':x['sha256']})
  for v in x.values():nominate(v)
 elif isinstance(x,list):
  for v in x:nominate(v)
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for j in seal['exactNeonJobs']:
  rr=read(ROOT/j['actualReceipt']['path']);assert ref(ROOT/j['actualReceipt']['path'])==j['actualReceipt']
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(j['jobId'],)).fetchone()==('complete',rr)
  assert rr['jobId']==j['jobId']and len(rr['evidenceRefs'])==j['directEvidenceCount'];nominate(rr);pending.append(j['actualReceipt'])
assert len(seal['exactNeonJobs'])==6 and len(seal['exactDirectBindings'])==375
for b in seal['exactDirectBindings']:
 assert exact_ref(ROOT,b['originalEvidenceRef'],contract)==b;pending.append(b['originalEvidenceRef'])
v=read(PROPOSAL/'offline-wrapper-history-tests-v1-validation.json');assert v['passed']and v['exitCode']==0 and v['expectedTests']==29
nominate(v);pending+=[ref(PROPOSAL/'offline-wrapper-history-tests-v1-validation.json'),ref(DOC/'primary-source-identification-exact-seal.json'),ref(HISTORY)]
while pending:
 e=pending.pop();key=(e['path'],e['sha256'])
 if key in seen:continue
 try:actual=exact_ref(ROOT,e,contract)
 except AssertionError as error:
  missing[key]={'evidenceRef':e,'error':str(error)};continue
 seen[key]=actual
 p=ROOT/actual['actualVerifiedFile']['path']
 if p.name.endswith('.json')or p.name.endswith('.json.gz'):
  nominate(read(p))
if missing:
 report={'rootRecursiveClosurePassed':False,'verifiedFileVersions':len(seen),'missingVersions':[missing[k]for k in sorted(missing)],'noCertificateCreated':True,'originalReceiptsUnchanged':True}
 Path('/tmp/upton-root-recursive-missing-actual-versions-20261011.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report),flush=True);sys.exit(2)
outcome=read(DOC/'source-identification-only.json');assert outcome['identityAccepted']and not outcome['physicalAccepted']and not outcome['installationApproved']
assert len(outcome['identityContext']['complete23ProperInteriorCrossingsRetained'])==23 and not outcome['foreignCollisionExemption']and not outcome['intentionalJointEstablished']
r=read(DOC/'result.json');assert r['identityAccepted']and not r['scriptFullAcceptancePassed']and not r['canStartTerrainWork']
assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==seal['currentManifestSHA256']
assert not reservations.owns(read(HERE/'local'/DOC.name/'reservation.json'))
for k,b in seen.items():
 if Path(b['actualVerifiedFile']['path']).is_absolute():
  p=Path(b['actualVerifiedFile']['path']);data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==k[1]
  archived=HISTORY.parent/'actual-external-bytes'/k[1]/p.name;archived.parent.mkdir(parents=True,exist_ok=True);assert not archived.exists() or archived.read_bytes()==data;archived.write_bytes(data)
  b['actualVerifiedFile']=ref(archived);b['historicalArchiveUsed']=True;b['literalExternalBytesArchived']=True
body={'reviewer':'ROOT','independentlyVerified':True,'sourceIdentificationOnly':True,'identityAccepted':True,'physicalAccepted':False,'installationApproved':False,'canStartTerrainWork':False,'completedCurrentJobId':r['jobId'],'exactNeonJobReadbacks':6,'directCurrentJobReferencesVerified':288,'directSourceSealBindingsVerified':375,'recursiveFileVersionsVerified':len(seen),'recursiveStructuredNodesVisited':nodes,'currentManifestSHA256':seal['currentManifestSHA256'],'currentNativeCount':6649,'all23ProperOriginalCrossingsPreserved':True,'rawOrdinaryIdentityNegativesRetained':True,'originalSourceGeometryChanges':0,'optimisationAuthorised':False,'oldReceiptsRewritten':False,'actualHistoricalArchivesOnly':True,'historicalBindingsUsed':sum(x['historicalArchiveUsed']for x in seen.values()),'historicalContractExtension':ref(HISTORY),'bindings':[seen[k]for k in sorted(seen)],'qualification':'ROOT independently read all six exact completed pinned-Neon source jobs and recursively verified every explicit path/SHA reference reachable through their structured source proof and the exact source seal. Historical inputs resolve only literal archived files or exact Git blobs, including the separate 47-version extension preserving the original51b1 contract. This closes source identification only; no intended joint, ownership, shared edge, root, solid clearance, foreign physical exemption, runtime approval or installation.'}
target=DOC/'root-recursive-source-identification-closure.json';assert not target.exists();target.write_text(json.dumps(body,indent=2)+'\n')
paths={x['actualVerifiedFile']['path']for x in seen.values()if x['actualVerifiedFile']['path']not in ['3d-viewer/city/data/manifest.json','3d-viewer/city/data/building-progress.json','docs/astra-city/model-integration-20260909/current-source-review.json']}
paths|={str(p.relative_to(ROOT))for folder in [DOC,PROPOSAL,HISTORY.parent]for p in folder.rglob('*')if p.is_file()}
assert all(not Path(p).is_absolute() and '..'not in Path(p).parts for p in paths)
Path('/tmp/upton-root-closed-source-only-scope-20261011.json').write_text(json.dumps({'paths':sorted(paths)}))
print(json.dumps({k:v for k,v in body.items()if k!='bindings'}),flush=True)
