"""Read-only canonical interface diagnostic of unchanged government originals."""
import subprocess,sys
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-olympian-two-canonical-contacts-v1-20261018'
DOC=BASE/BATCH

def main():
 assert not DOC.exists() or ('--resume-checkpoint' in sys.argv and not (DOC/'result.json').exists())
 prior=BASE/'government-xl-olympian-two-compound-tower-contacts-v1-20261018/result.json'
 result=read(prior);pins={e['path']:e['sha256'] for e in result['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 towers=read(BASE/'government-xl-olympian-two-restored-components-v2-20261018/restored.json')['rows']
 support=read(BASE/'government-xl-olympian-two-restored-support-v1-20261018/restored.json')['rows'][0]
 podium=read(BASE/'government-xl-olympian-two-source-local-terrain-20261008/selection.json.gz')['rows'][0]
 sources=towers+[support,dict(uid=podium['uid'],assetPath=podium['candidate']['path'],sourceSHA256=podium['sourceSHA256'])]
 rows=[];refs=[Path(__file__),prior,*[ROOT/p for p in pins],HERE/'exact_packed_world_geometry_20261009.py']
 for s in sources:
  p=ROOT/s['assetPath'];raw=p.read_bytes();assert digest(raw)==s['sourceSHA256'];t=decode_original_world_triangles(raw)
  rows.append(dict(uid=s['uid'],sourceSHA256=s['sourceSHA256'],bottom=float(t[:,:,1].min()),position=t.reshape(-1).tolist(),index=list(range(t.size//3))))
  refs.append(p)
 inputs=dict(towerUIDs=[s['uid'] for s in towers],rows=rows,modelGeometryChanges=0)
 if '--resume-checkpoint' in sys.argv:
  assert read(DOC/'geometry-inputs.json.gz')==inputs
 else:save(DOC/'geometry-inputs.json.gz',inputs)
 if '--resume-checkpoint' not in sys.argv:subprocess.run(['node',str(HERE/'olympian-two-canonical-contacts-v1-20261018.mjs'),str(DOC)],cwd=ROOT,check=True)
 refs.extend(HERE/x for x in ['olympian-two-canonical-contacts-v1-20261018.mjs','support-interface.mjs','support-contact.mjs','triangle-point-index.mjs','source-face-query.mjs'])
 out=module('olympian_canonical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-canonical-original-support-diagnostic-v1',refs,dict(uids=[s['uid'] for s in sources],fullAcceptance=False,newlyInstalled=0,currentHeldReason='original-tower-podium-interface-unresolved',nextStep='Resolve original support coverage and source component roles; separate podium terrain rim and full acceptance checks remain.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
