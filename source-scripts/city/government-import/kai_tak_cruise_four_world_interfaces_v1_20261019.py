"""Bound exact source paths and recheck actual four-world interfaces; no publication."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-kai-tak-cruise-component-four-mode-foundations-v1-20261019';PATHS=BASE/'government-xl-kai-tak-cruise-lower-paths-v1-20261019';BATCH='government-xl-kai-tak-cruise-four-world-interfaces-v1-20261019';DOC=BASE/BATCH
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,PATHS]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 worlds=read(SRC/'worlds.json.gz');paths=[]
 for r in read(PATHS/'paths.json.gz')['rows']:
  for d in r['details']:
   if d['witness']:
    w=d['witness'];paths.append(dict(uid=r['uid'],position=d['position'],faces=w['faces'],path=w['continuousLowPath'],contact=w['contact'],ceiling=w['contactRegionCeiling']))
 assert len(paths)==837
 save(DOC/'inputs.json.gz',dict(worlds=worlds,paths=paths));tool=HERE/'kai_tak_cruise_four_world_interfaces_v1_20261019.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True)
 interfaces=read(DOC/'interfaces.json.gz')['rows'];contacts=read(DOC/'contacts.json.gz')['rows'];bounds=[]
 for mode,world in worlds.items():
  for uid in sorted({p['uid']for p in paths}):
   original=np.asarray(worlds['original'][uid]);actual=np.asarray(world[uid]);assert original.shape==actual.shape;delta=np.linalg.norm(actual-original,axis=2).max(1);checks=[]
   originalproof=next(r['proof']for r in interfaces if r['uid']==uid and r['mode']=='original');actualproof=next(r['proof']for r in interfaces if r['uid']==uid and r['mode']==mode)
   a=originalproof['strictLowRim']['failed'];b=actualproof['strictLowRim']['failed'];assert len(a)==len(b),(uid,mode,'failure count changed')
   for start,now in zip(a,b):
    matches=[p for p in paths if p['uid']==uid and p['position']==start['position']];assert len(matches)==1;w=matches[0];shift=float(np.linalg.norm(np.asarray(start['position'])-now['position']));bound=1e-8+float(delta[w['faces']].max())+shift;checks.append(dict(position=start['position'],actualPosition=now['position'],maximumFaceDistanceBoundM=bound,withinExistingMembershipTolerance=bound<=.001));assert max(p[1]for p in w['path'])<=w['ceiling']+1e-9
   bounds.append(dict(uid=uid,mode=mode,checks=checks,passed=all(x['withinExistingMembershipTolerance']for x in checks),maximumBoundM=max(x['maximumFaceDistanceBoundM']for x in checks)))
 save(DOC/'path-bounds.json.gz',dict(rows=bounds,installationApproved=False));summary=dict(pathContacts=len(contacts),pathContactsPassed=sum(r['contactPassed']for r in contacts),pathBoundsPassed=all(r['passed']for r in bounds),interfaces=[dict(uid=r['uid'],mode=r['mode'],passed=r['proof']['passed'],samples=r['proof']['samples'],strict=r['proof']['strictContacts'],walls=r['proof']['wallIntersections'],unresolved=len(r['proof']['unresolved']))for r in interfaces],installationApproved=False);save(DOC/'summary.json',summary);print(summary,flush=True)
 refs.extend([tool,HERE/'support-contact.mjs',HERE/'support-interface.mjs',HERE/'triangle-point-index.mjs'])
 module('kai_four_interfaces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-complete-four-world-interface-path-bounds',list(dict.fromkeys(refs)),dict(uids=sorted(worlds['original']),summary=summary,installationApproved=False))
if __name__=='__main__':main()
