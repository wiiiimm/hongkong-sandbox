"""Resolve original pair diagnostic context without geometry edits or acceptance."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-interface-distances-v1-20261018';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-times-square-original-assembly-v1-20261018';UID='landsd/233901:0'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(PRIOR/'selection.json.gz')['rows'];save(DOC/'support-inputs.json',dict(sources=rows,pairs=[dict(uid=r['uid'],supportUid=UID)for r in rows if r['uid']!=UID]));tool=HERE/'wave_original_support_distance_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);checks=read(DOC/'support-checks.json.gz');summary=[]
 for r in checks['rows']:
  assert not r.get('loadFailure');dist=[f['nearestPodiumFace']['distanceM']for f in r['unresolved']];summary.append(dict(uid=r['uid'],unresolved=len(dist),nearestFaceDistanceRangeM=[min(dist),max(dist)],within1mm=sum(x<=.001 for x in dist),within1cm=sum(x<=.01 for x in dist),within10cm=sum(x<=.1 for x in dist),over1m=sum(x>1 for x in dist),rawSupportPassed=r['interface']['passed']))
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False));print(summary,flush=True)
 for p,h in {**pins,**checks['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(tool);module('times_distances_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-original-interface-nearest-source-faces',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=summary,installationApproved=False))
if __name__=='__main__':main()
