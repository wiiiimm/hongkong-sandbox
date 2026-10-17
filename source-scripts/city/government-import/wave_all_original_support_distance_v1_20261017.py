"""Canonical original podium interfaces for five recovered Wave companions."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-all-original-support-distance-v1-20261017';DOC=BASE/BATCH
REC=BASE/'government-xl-wave-neighbours-terrain-capture-v1-20261017';PAIR=BASE/'government-xl-wave275510-pair-capture-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for d in [REC,PAIR]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=[r for r in read(REC/'selection.json.gz')['rows']if r['uid']!='landsd/195000:0'];podium=next(r for r in read(PAIR/'selection.json.gz')['rows']if r['uid']=='landsd/301560:0');assert len(rows)==5;rows.append(next(r for r in read(PAIR/'selection.json.gz')['rows']if r['uid']=='landsd/275510:0'))
 save(DOC/'support-inputs.json',dict(pairs=[dict(uid=r['uid'],supportUid=podium['uid'])for r in rows],sources=rows+[podium]))
 tool=HERE/'wave_original_support_distance_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);refs.append(tool)
 checks=read(DOC/'support-checks.json.gz');summary=[]
 for p,h in checks['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for r in checks['rows']:
  i=r.get('interface');summary.append(dict(uid=r['uid'],interface=None if i is None else {k:i.get(k)for k in ['passed','samples','strictContacts','wallIntersections']},unresolved=None if i is None else len(i['unresolved']),loadFailure=r.get('loadFailure'),failuresWithLowerContact=sum(any(-.1<=h['gap']<=1 for h in f['allOriginalPodiumLayers'])for f in r.get('unresolved',[]))))
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False));out=module('wave_companion_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-original-assembly-full-podium-nearest-face-diagnostic-v1',list(set(refs)),dict(uids=[r['uid']for r in rows]+[podium['uid']],summary=summary,fullAcceptance=False));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
