"""Strict BASIC contacts against complete current terrain plus original podium."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-basic-combined-support-v1-20261020';DOC=BASE/BATCH
AFTER=BASE/'government-xl-plaza-ascot-basic-ground-v2-20261020';BASIC=BASE/'government-xl-plaza-ascot-basic-support-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [AFTER,BASIC]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cap=take(AFTER,AFTER/'ground.json.gz');basic=take(BASIC,BASIC/'input.json.gz');save(DOC/'input.json.gz',dict(podium=basic['podium'],rows=cap['rows']))
 tool=HERE/'plaza_ascot_basic_combined_support_v1_20261020.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'support.json.gz');rows=[dict(uid=r['uid'],samples=r['proof']['samples'],strictContacts=r['proof']['strictContacts'],wallIntersections=r['proof']['wallIntersections'],unresolved=len(r['proof']['unresolved']),passed=r['proof']['passed']) for r in report['rows']]
 for capture in [cap,report]:
  for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=[r['uid'] for r in rows],rows=rows,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',result);module('ascot_combined_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'strict-basic-complete-terrain-and-original-podium-contact',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
