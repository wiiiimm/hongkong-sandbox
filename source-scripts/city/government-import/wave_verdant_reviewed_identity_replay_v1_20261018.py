"""Freshly replay two source-specific identities and reject changed evidence."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from wave_verdant_reviewed_identities_v1_20261018 import SOURCES,REVIEW,verify_files,apply_review
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-reviewed-identity-replay-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists();r=read(REVIEW/'result.json');pins={};refs=[Path(__file__),REVIEW/'result.json',HERE/'wave_verdant_reviewed_identities_v1_20261018.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sources={}
 for name in ['government-xl-wave-all-original-support-distance-v1-20261017','government-xl-wave-verdant-podium-support-v1-20261017']:
  sources.update({x['uid']:x for x in read(BASE/name/'support-inputs.json')['sources']})
 contexts=read(BASE/'government-xl-wave-verdant-current-identity-runtime-v1-20261018/identity-context.json');rows=[]
 for uid,sha in SOURCES.items():
  row=sources[uid];row.update(modelId=row['native']['model']['modelId'],triangles=row['native']['model']['triangles']);context=dict(sourceSHA256=sha,identity=next(x['identity']for x in contexts['rows']if x['uid']==uid),neighbourTileHashes=contexts['neighbourTileHashes']);proof=verify_files(row,context,LOCAL/uid.replace('/','-').replace(':','-'));assert proof['passed'] and not proof['physicalAccepted'] and not proof['installationApproved'];decision=proof['identityDecision'];raw=proof['rawIdentityVerbatim'];rejected=[]
  for key in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256','uid']:
   changed=deepcopy(raw);changed[key]='changed'
   try:apply_review(changed,decision)
   except (AssertionError,KeyError):rejected.append(key)
   else:raise AssertionError('Changed evidence accepted')
  changed=deepcopy(raw);changed['freshCurrentIdentity']['targetCoveredBySourceProjection']+=.001
  try:apply_review(changed,decision)
  except AssertionError:rejected.append('currentCoverage')
  else:raise AssertionError('Changed coverage accepted')
  save(DOC/(uid.replace('/','-').replace(':','-')+'-identity.json'),proof);rows.append(dict(uid=uid,freshReplayPassed=True,rejectedChanges=rejected));print(rows[-1],flush=True)
 save(DOC/'summary.json',dict(rows=rows,fullAcceptance=False));refs.extend([*[ROOT/p for p in pins],*[p for p in LOCAL.rglob('*')if p.is_file()]])
 out=module('wave_pair_replay_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-exact-reviewed-original-identities-fresh-replay-v1',list(set(refs)),dict(uids=list(SOURCES),identityAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
