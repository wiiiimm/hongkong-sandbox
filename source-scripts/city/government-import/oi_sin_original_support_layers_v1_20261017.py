"""Freeze existing original support-layer diagnostic without overriding acceptance."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-four-originals-physical-v1-20261017';BATCH='government-xl-oi-sin-original-support-layers-v1-20261017';DOC=BASE/BATCH
if __name__=='__main__':
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 tool=HERE/'oi_sin_original_support_layers_v1_20261017.mjs';subprocess.run(['node',str(tool)],cwd=ROOT,check=True);out=read(DOC/'layers.json');refs=[Path(__file__),PRIOR/'result.json',tool]
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=[dict(uid=x['uid'],failed=len(x['proof']['rows']),lowerContact=sum(p['classification']=='contact-layer-with-higher-overlap'for p in x['proof']['rows']))for x in out['rows']]
 result=module('oi_sin_layers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-original-podium-multiple-layer-diagnostic-v1',refs,dict(uids=[r['uid']for r in out['rows']],summary=summary,fullAcceptance=False,nextStep='Interpret exact original lower-floor and overlapping-wall evidence; all canonical support/identity/foundation failures remain until independently resolved.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
