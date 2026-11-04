"""Resume exact historical assembly source analysis after Apex; never transfer old map approval."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';APEX=BASE/'government-xl-apex227942-original-installed-v1-20261018';BATCH='government-xl-wave-verdant-remaining-interfaces-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();old=read(PRIOR/'result.json');new=read(APEX/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json',APEX/'result.json'];historical=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [old,new]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 history={(r['originalPath'],r['originalSHA256']):r['savedHistoricalBytes']for r in new['historicalMutableByteSnapshots']}
 for e in old['evidenceRefs']:
  key=e['path'];assert key not in pins or pins[key]==e['sha256'];pins[key]=e['sha256']
 for p,h in pins.items():
  path=ROOT/p
  if digest(path.read_bytes())!=h:
   replacement=history[(p,h)];path=ROOT/replacement['path'];assert digest(path.read_bytes())==h==replacement['sha256'];historical.append(dict(originalPath=p,originalSHA256=h,savedHistoricalBytes=replacement))
  refs.append(path)
 save(DOC/'input-provenance.json',dict(priorReceipt=str((PRIOR/'result.json').relative_to(ROOT)),historicalInputs=historical,currentMapAcceptance=False,qualification='Prior immutable original geometry and private V4 ground remain source-analysis inputs. Apex historical snapshots authenticate changed mutable metadata; no old current-map acceptance is transferred.'))
 tool=HERE/'wave_verdant_remaining_interfaces_v1_20261018.mjs'
 with(DOC/'analysis.log').open('w')as log:subprocess.run(['node',str(tool),str(PRIOR.relative_to(ROOT)),str((DOC/'interfaces.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 data=read(DOC/'interfaces.json.gz');rows=[dict(mode=r['mode'],uid=r['uid'],unresolved=len(r['unresolved']),additionalActorContactCandidates=sum(bool(f['additionalWithinStrictInterval'])for f in r['unresolved']))for r in data['rows']];save(DOC/'summary.json',dict(rows=rows,fullAcceptance=False,newlyInstalled=0))
 refs.extend(HERE/n for n in ['wave_verdant_remaining_interfaces_v1_20261018.mjs','source-face-query.mjs','support-contact.mjs','triangle-point-index.mjs']);out=module('wave_remaining_interfaces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-verdant-exact-residual-source-contact-attribution-v1',list(set(refs)),dict(uids=sorted({r['uid']for r in rows}),fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True);print(rows,flush=True)
if __name__=='__main__':main()
