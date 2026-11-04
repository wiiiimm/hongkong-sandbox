"""Fresh original root/ownership/full-georef-cell identity; no placement approval."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from government_georef_cell_identity import verify_files
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018';VALID=BASE/'government-xl-apex227942-current-identity-runtime-v1-20261018';BATCH='government-xl-apex227942-authoritative-identity-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

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
 row=read(CAP/'selection.json.gz')['rows'][0];row.update(modelId=row['native']['model']['modelId'],triangles=row['native']['model']['triangles']);lo,hi=row['native']['model']['worldBounds'];final=module('apex_identity_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(sourceSHA256=row['sourceSHA256'],identity=read(VALID/'identity-context.json'),neighbourTileHashes={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms});proof=verify_files(row,context,LOCAL);save(DOC/'identity.json',proof);save(DOC/'context.json',context)
 refs.extend(HERE/p for p in ['government_georef_cell_identity.py','original_source_ownership.py','georef_projection_coverage.py','xl-second-pass.py','xl-final-script-pass.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());out=module('apex_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-fresh-current-whole-georef-original-identity-v1',list(set(refs)),dict(uids=[row['uid']],passed=proof['passed'],reasons=proof['reasons'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],passed=proof['passed'],reasons=proof['reasons']),flush=True)
if __name__=='__main__':main()
