"""Fresh original root/ownership/full-georef-cell identity; no placement approval."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from government_georef_cell_identity import verify_files
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-wave-verdant-private-browser-v5-20261018';VALID=BASE/'government-xl-wave-verdant-current-identity-runtime-v1-20261018';BATCH='government-xl-wave-verdant-authoritative-identity-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 for folder in [CAP,VALID]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 sources={}
 for name,file,key in [('government-xl-wave-all-original-support-distance-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-podium-support-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-block2-original-recovery-v1-20261017','selection.json.gz','rows'),('government-xl-wave-verdant-194544-original-recovery-v1-20261017','selection.json.gz','rows')]:
  p=BASE/name/file;refs.append(p);sources.update({x['uid']:x for x in read(p)[key]})
 contexts=read(VALID/'identity-context.json');proofs=[]
 for identityrow in contexts['rows']:
  uid=identityrow['uid'];row=dict(sources[uid]);row.update(modelId=row['native']['model']['modelId'],triangles=row['native']['model']['triangles']);context=dict(sourceSHA256=row['sourceSHA256'],identity=identityrow['identity'],neighbourTileHashes=contexts['neighbourTileHashes']);proof=verify_files(row,context,LOCAL/uid.replace('/','-').replace(':','-'));proofs.append(dict(uid=uid,proof=proof));save(DOC/(uid.replace('/','-').replace(':','-')+'-identity.json'),proof);print(dict(uid=uid,passed=proof['passed'],reasons=proof['reasons']),flush=True)
 save(DOC/'summary.json',dict(rows=proofs,fullAcceptance=False,newlyInstalled=0))
 refs.extend(HERE/p for p in ['government_georef_cell_identity.py','original_source_ownership.py','georef_projection_coverage.py','xl-second-pass.py','xl-final-script-pass.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());out=module('apex_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-fresh-current-whole-georef-identity-v1',list(set(refs)),dict(uids=[p['uid'] for p in proofs],identityPassed=sum(p['proof']['passed'] for p in proofs),fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
