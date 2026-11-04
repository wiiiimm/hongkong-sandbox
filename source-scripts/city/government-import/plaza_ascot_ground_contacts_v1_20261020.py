"""Strict contact diagnostics for the captured original against actual drawn terrain."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-ground-contacts-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020'
def main():
 assert not DOC.exists();receipt=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};path=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
 row=read(path)['rows'][0]
 import numpy as np
 ground=np.asarray(row['drawnGroundGeometry']).reshape(-1,3,3)
 save(DOC/'input.json.gz',dict(podium=ground.tolist(),rows=[dict(uid=row['uid'],position=row['position'],index=row['index'])]))
 tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'support.json.gz');proof=report['rows'][0]['proof']
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=dict(uids=[row['uid']],samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved']),passed=proof['passed'],installationApproved=False)
 save(DOC/'summary.json',summary)
 module('ascot_ground_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-captured-original-terrain-strict-contact',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
