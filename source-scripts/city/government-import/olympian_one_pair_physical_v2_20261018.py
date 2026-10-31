"""Finish saved full-pair checks after correcting missing private catalogue sourceTile."""
from pathlib import Path
import subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import olympian_one_pair_physical_v1_20261018 as prior
BASE=prior.BASE;BATCH='government-xl-olympian-one-pair-physical-v2-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__),Path(prior.__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [prior.PAIR,prior.ATTR,prior.NEAR,prior.IDENTITY,prior.REVIEW,prior.BIND]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(prior.PAIR/'selection.json.gz')['rows'];shutil.copytree(prior.LOCAL,LOCAL);cat=read(LOCAL/'catalogue.json');before=digest((LOCAL/'catalogue.json').read_bytes());fixes=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for entry in cat['models']:
   if 'sourceTile'in entry:continue
   row=next(r for r in rows if r['uid']==entry['uid']);sha=c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()[0];assert sha==row['native']['resultSha'];sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()[0];entry['sourceTile']=sheet;fixes.append(dict(uid=entry['uid'],sourceTile=sheet,cacheKey=row['native']['cacheKey'],nativeResultSha=sha))
 save(LOCAL/'catalogue.json',cat);save(DOC/'metadata-fix.json',dict(originalCatalogueSHA256=before,fixes=fixes,geometryChanges=0))
 for name in ['terrain-candidates.json','neighbour-checks.json','native-neighbour-checks.json','neighbour-inputs.json.gz']:
  p=prior.DOC/name;raw=p.read_bytes();(DOC/name).write_bytes(raw);refs.append(p)
 foundations=[]
 for p in sorted(prior.DOC.glob('*-foundation.json')):
  f=read(p);foundations.append(f);shutil.copyfile(p,DOC/p.name);refs.append(p)
 assert len(foundations)==8 and {(r['uid'],r['mode'])for r in foundations}=={(u,m)for u in [prior.POD,prior.TOWER]for m in ['original','literal','explicitLeftF32','explicitBalancedF32']}
 bindings=read(prior.BIND/'exact-source-face-bindings.json.gz')['bindings']
 for f in foundations:assert f['worldSHA256']==next(b['wholeWorldSHA256']for b in bindings if b['uid']==f['uid']and b['mode']==f['mode'])
 tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'validation.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'validation-command.json',dict(command=cmd,exitCode=p.returncode));assert p.returncode in[0,1]and(DOC/'validation.json').exists()
 metrics=read(prior.PAIR/'metrics.json');identity=read(prior.IDENTITY/'72354:0-review.json');tower=read(prior.PAIR/'256927:0-identity.json');assert identity['identityOnlyApproved']and tower['passed'];policy=module('olympian_pair_policy',HERE/'acceptance-policy.py');raw=[]
 for row in rows:
  proof=identity['identityProof']if row['uid']==prior.POD else tower['proof'];m=next(m for m in metrics['rows']if m['uid']==row['uid']);raw.extend(row['uid']+':'+x for x in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=proof),m,metrics['profiles']['mobile']))
 validation=read(DOC/'validation.json');raw.extend('validation:'+r['uid']+':'+x for r in validation['results']for x in r.get('concerns',[]))
 if validation['loaderAccepted']!=2 or validation['checksPassed']!=2 or validation['exceptions']:raw.append('complete-current-loader-validation')
 for r in read(DOC/'neighbour-checks.json')['rows']:raw.extend('neighbour:'+r['uid']+':'+x for x in r['reasons'])
 native=read(DOC/'native-neighbour-checks.json');raw.extend('native:'+u for u in set(native['blocked'])-set(native['resolved']))
 raw.extend('foundation:'+r['uid']+':'+r['mode']for r in foundations if not r['strictFoundationAccepted']);raw.append('original-support-interface-unresolved')
 summary=dict(uids=[prior.POD,prior.TOWER],rawReasons=sorted(set(raw)),allCompoundFoundationsPassed=all(f['strictFoundationAccepted']for f in foundations),loaderChecksPassed=validation['checksPassed'],installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',summary);print(summary,flush=True)
 for report in [read(DOC/'neighbour-checks.json'),native,validation]:
  for p,h in report.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([tool,HERE/'xl-final-script-pass.py',HERE/'acceptance-policy.py',prior.DOC/'validation.log',prior.DOC/'validation-command.json']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 module('olympian_pair_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-pair-validation-finished',list(dict.fromkeys(refs)),summary)
if __name__=='__main__':main()
