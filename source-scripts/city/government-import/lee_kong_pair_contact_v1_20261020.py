"""Run established strict source support interface and retain all warnings."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from installed_support_acceptance import resolve_contact
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lee-kong-pair-contact-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-lee-kong-pair-runtime-v1-20261020';LOAD=BASE/'government-xl-lee-kong-pair-loader-v1-20261020';FOUND=BASE/'government-xl-lee-kong-pair-four-mode-foundations-v1-20261020'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [CAP,LOAD,FOUND]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
rows=read(CAP/'selection.json.gz')['rows'];save(DOC/'support-inputs.json',dict(pairs=[dict(uid='landsd/253697:0',supportUid='landsd/72296:0')],sources=rows))
subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
checks=read(DOC/'support-checks.json.gz');assert len(checks['rows'])==1;interface=checks['rows'][0]['interface'];foundation=dict(strictFoundationAccepted=all(x['passed'] for x in read(FOUND/'summary.json')['rows']))
raw=read(LOAD/'summary.json');policy=next(x['reasons'] for x in raw['rawPolicyReasons'] if x['uid']=='landsd/253697:0');diagnostic=next(x['concerns'] for x in raw['ordinaryConcerns'] if x['uid']=='landsd/253697:0')
summary=dict(uids=['landsd/72296:0','landsd/253697:0'],interfaceSummary={k:interface[k] for k in ['passed','samples','strictContacts','wallIntersections']},unresolved=len(interface['unresolved']),rawPolicyReasons=policy,rawDiagnosticReasons=diagnostic,remainingPolicyReasons=resolve_contact(policy,interface,foundation),remainingDiagnosticReasons=resolve_contact(diagnostic,interface,foundation),installationApproved=False)
save(DOC/'summary.json',summary)
for p,h in {**pins,**checks['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
refs.append(HERE/'installed_support_acceptance.py')
module('lee_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'strict-original-pair-contact-diagnostic',list(dict.fromkeys(refs)),summary)
print(summary,flush=True)
