"""Complete saved lower-path bounds in actual captured worlds, no source edits."""
from pathlib import Path
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-four-world-path-bounds-v1-20261018';DOC=BASE/BATCH
NAMES=['government-xl-olympian-two-residual-existing-tolerance-paths-v1-20261018','government-xl-olympian-two-four-world-interfaces-v1-20261018','government-xl-olympian-two-four-world-foundations-v1-20261018']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 paths={}
 for name in ['government-xl-olympian-two-source-face-paths-v4-20261018','government-xl-olympian-two-residual-surface-paths-v1-20261018']:
  for r in read(BASE/name/'paths.json.gz')['rows']:
   for d in r['details']:
    w=d['witness']
    if w:paths[r['uid'],tuple(d['position'])]=dict(uid=r['uid'],position=d['position'],faces=w['faces'],path=w.get('continuousLowPath',w.get('path')),contact=w['contact'],ceiling=w.get('contactRegionCeiling',w.get('ceiling')),originalResidualBoundM=1e-8)
 for r in read(BASE/NAMES[0]/'paths.json.gz')['rows']:
  assert r['pathContextVerified'];paths[r['uid'],tuple(r['position'])]=dict(uid=r['uid'],position=r['position'],faces=r['faces'],path=r['path'],contact=r['contact'],ceiling=r['ceiling'],originalResidualBoundM=r['maximumFiniteFaceResidualM'])
 assert len(paths)==1953
 worlds=read(BASE/'government-xl-olympian-two-six-original-four-world-v1-20261018/world-triangles.json.gz');original=worlds['original'];inputs=read(BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018/geometry-inputs.json.gz')
 for s in inputs['rows']:
  t=np.asarray(s['position']).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)];assert np.array_equal(t,np.asarray(original[s['uid']]))
 results=[]
 for r in read(BASE/NAMES[1]/'interfaces.json.gz')['rows']:
  uid=r['uid'];mode=r['mode'];source=np.asarray(original[uid]);actual=np.asarray(worlds[mode][uid]);delta=np.linalg.norm(actual-source,axis=2).max(1);proof=r['proof'];orig=next(x['proof']for x in read(BASE/NAMES[1]/'interfaces.json.gz')['rows']if x['mode']=='original'and x['uid']==uid);assert len(proof['unresolved'])==len(orig['unresolved']);checks=[]
  for a,b in zip(orig['unresolved'],proof['unresolved']):
   w=paths[uid,tuple(a['position'])];sampleShift=float(np.linalg.norm(np.asarray(a['position'])-b['position']));bound=w['originalResidualBoundM']+float(delta[w['faces']].max())+sampleShift;assert bound<=.001;assert max(p[1]for p in w['path'])<=w['ceiling']+1e-9
   checks.append(dict(position=a['position'],actualPosition=b['position'],maximumFaceDistanceBoundM=bound,sampleShiftM=sampleShift))
  results.append(dict(uid=uid,mode=mode,verifiedPathBounds=len(checks),maximumFaceDistanceBoundM=max(x['maximumFaceDistanceBoundM']for x in checks),checks=checks));print({k:v for k,v in results[-1].items()if k!='checks'},flush=True)
 save(DOC/'inputs.json.gz',dict(worlds=worlds,paths=list(paths.values())));tool=HERE/'olympian-two-four-world-path-contacts-v1-20261018.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True);contacts=read(DOC/'contacts.json.gz')['rows'];assert len(contacts)==1953*4 and all(x['contactPassed']for x in contacts)
 save(DOC/'bounds.json.gz',dict(rows=results,qualification='A triangle moves no more than its maximum corresponding-vertex displacement for identical barycentric coordinates. Original verified finite-face distance plus that bound plus actual start-sample displacement remains below existing .001m membership tolerance. No paths are geometry edits; no generic support waiver. Contact endpoint maximum-surface gaps independently rechecked in each captured world.',fullAcceptance=False))
 refs.extend(ROOT/p for p in pins);refs.extend([tool,HERE/'support-contact.mjs'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('olympian_four_path_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-all1953-lower-path-four-world-bounds-and-contacts-v1',list(set(refs)),dict(uids=sorted({r['uid']for r in results}),verifiedPathChecks=len(contacts),fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
