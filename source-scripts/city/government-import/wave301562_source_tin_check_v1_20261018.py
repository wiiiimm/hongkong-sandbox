"""Compare the small unchanged Wave source with authenticated source TIN, without a new patch."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-seam-bounds-v1-20261018';TIN=BASE/'government-xl-wave-verdant-source-tin-support-v1-20261017';ASSEMBLY=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';BATCH='government-xl-wave301562-source-tin-check-v1-20261018';DOC=BASE/BATCH;UID='landsd/301562:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');tin=read(TIN/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for q in [r,tin]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 path=TIN/'input.json.gz';e=next(e for e in tin['evidenceRefs']if e['path']==str(path.relative_to(ROOT)));assert digest(path.read_bytes())==e['sha256']
 data=read(ASSEMBLY/'literal/input.json.gz');row=next(x for x in data['rows']if x['uid']==UID);original=read(path);save(DOC/'input.json.gz',dict(rows=[row],podium=original['podium']))
 tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
 with(DOC/'support.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 proof=read(DOC/'support.json.gz')['rows'][0]['proof'];old=next(x['proof']for x in read(ASSEMBLY/'literal/support.json.gz')['rows']if x['uid']==UID);oldpoints={tuple(f['position'])for f in old['unresolved']};newpoints={tuple(f['position'])for f in proof['unresolved']};summary=dict(uid=UID,mode='literal',candidateUnresolved=len(oldpoints),sourceTinUnresolved=len(newpoints),sameUnresolvedPositions=oldpoints==newpoints,sourceTinStrictContacts=proof['strictContacts'],sourceTinSamples=proof['samples'],fullAcceptance=False,qualification='Uses the complete authenticated original TIN and original Wave podium from the verified earlier source-TIN receipt; bypasses the private multicore transition. No new terrain or model geometry, no placement approval.');save(DOC/'summary.json',summary)
 refs=[Path(__file__),PRIOR/'result.json',TIN/'result.json',path,tool,*[ROOT/p for p in pins]];out=module('wave_small_tin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-small-original-source-tin-support-diagnostic-v1',refs,dict(uids=[UID],summary=summary,fullAcceptance=False,newlyInstalled=0));print(summary,flush=True);print(out['jobId'],flush=True)
if __name__=='__main__':main()
