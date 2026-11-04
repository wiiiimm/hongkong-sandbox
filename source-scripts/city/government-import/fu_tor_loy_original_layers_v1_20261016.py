"""Exact original tower/podium interfaces, with current dependency bindings."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-fu-tor-loy-original-layers-v1-20261016';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRIOR=DOC.parent/'government-xl-fu-tor-loy-original-group-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 rows=read(PRIOR/'selection.json.gz')['rows'];DOC.mkdir();save(DOC/'support-inputs.json',dict(sources=rows,pairs=[dict(uid=row['uid'],supportUid='landsd/228219:0') for row in rows if row['uid']!='landsd/228219:0']))
 tool=HERE/'fu_tor_loy_original_layers_v1_20261016.mjs'
 with (DOC/'worker.log').open('w') as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
 proof=read(DOC/'support-layers.json.gz')
 for p,h in proof['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=[dict(uid=q['uid'],samples=q['interface']['conservative']['samples'],classes={key:sum(f['classification']==key for f in q['interface']['rows']) for key in sorted({f['classification'] for f in q['interface']['rows']})}) for q in proof['rows']];save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,newlyInstalled=0))
 out=module('fu_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-four-tower-podium-surface-layer-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=[q['uid'] for q in rows],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],rows=summary),flush=True)
if __name__=='__main__':main()
