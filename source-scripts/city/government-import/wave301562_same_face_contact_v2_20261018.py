"""Verify complete finite same-face paths to existing strict source contacts; no gate waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave301562-same-face-contact-v2-20261018';DOC=BASE/BATCH
NAMES=['government-xl-wave-verdant-remaining-reviewed-identities-v1-20261018','government-xl-wave301562-focused-context-v3-20261018','government-xl-wave301562-surface-connectivity-v1-20261017']
UID='landsd/301562:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];apexpath=BASE/'government-xl-apex227942-original-installed-v1-20261018/result.json';apex=read(apexpath);history={(x['originalPath'],x['originalSHA256']):x['savedHistoricalBytes']for x in apex['historicalMutableByteSnapshots']};refs.append(apexpath);resolved=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(apex['jobId'],)).fetchone()==('complete',apex)
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    path=e['path'];sha=e['sha256']
    if digest((ROOT/path).read_bytes())!=sha:
     assert name==NAMES[-1];replacement=history[(path,sha)];assert digest((ROOT/replacement['path']).read_bytes())==sha==replacement['sha256'];resolved.append(dict(originalPath=path,originalSHA256=sha,savedHistoricalBytes=replacement));path=replacement['path']
    assert path not in pins or pins[path]==sha;pins[path]=sha
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 connectivity=read(BASE/NAMES[-1]/'connectivity.json.gz')['rows'];worlds=read(BASE/'government-xl-wave-four-world-paths-v1-20261017/worlds.json.gz');residual=read(BASE/'government-xl-wave-verdant-remaining-interfaces-v1-20261018/interfaces.json.gz')['rows'];assembly=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';foundations=read(assembly/'summary.json')['rows'];results=[]
 for row in connectivity:
  mode=row['mode'];tri=np.array(worlds[mode][UID]);assert tri.shape==(144,3,3);q=next(x for x in residual if x['mode']==mode and x['uid']==UID);proof=next(x['proof']for x in read(assembly/mode/'support.json.gz')['rows']if x['uid']==UID);foundation=next(x for x in foundations if x['mode']==mode and x['uid']==UID)
  assert proof['samples']==90 and proof['strictContacts']==73 and proof['wallIntersections']==0 and not proof['passed'];assert foundation['strictFoundationAccepted']and foundation['buried']==foundation['upwardBuried']==0
  expected={tuple(x['position'])for x in proof['unresolved']};assert expected=={tuple(x['position'])for x in row['details']}=={tuple(x['position'])for x in q['unresolved']};checks=[]
  for failure in row['details']:
   w=failure['witness'];assert len(w['sourceFaces'])==1;face=w['sourceFaces'][0];a=np.array(failure['position']);b=np.array(w['strictContact']['position']);triangle=tri[face];assert face in failure['faces'] and face in w['strictContact']['faces'];assert -.1<=w['strictContact']['gap']<=1
   da=np.linalg.norm(closest(a,triangle)-a);db=np.linalg.norm(closest(b,triangle)-b);assert da<=1e-8 and db<=1e-8
   # A triangle is convex: both endpoints on this same finite original face
   # establish the entire segment; no sampled mesh-chain or infinite plane.
   n=np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0]);n=n/np.linalg.norm(n);assert n[1]<=1e-6
   checks.append(dict(position=a.tolist(),strictContact=b.tolist(),strictContactGapM=w['strictContact']['gap'],sourceFace=face,sourceFaceTriangle=triangle.tolist(),normal=n.tolist(),endpointResidualM=[da,db],segmentLengthM=float(np.linalg.norm(a-b)),entireSegmentOnSameFiniteFace=True))
  assert len(checks)==17;results.append(dict(mode=mode,uid=UID,sourceFaces=144,samples=90,strictContacts=73,rawUnresolved=17,verifiedSameFiniteFaceConnections=17,maximumConnectionM=max(x['segmentLengthM']for x in checks),wholeFoundationBuried=0,wallIntersections=0,checks=checks));print({k:v for k,v in results[-1].items()if k!='checks'},flush=True)
 assert {x['mode']for x in results}=={'original','literal','left','balanced'}
 save(DOC/'historical-inputs.json',resolved)
 save(DOC/'finite-face-connections.json',dict(rows=results,fullAcceptance=False,sourceSpecificSupportApproved=False,qualification='Every raw failed point and an existing strict-contact point lie on the same finite original triangle, so their joining segment stays on that unchanged original face. Distances are reported, not a new contact allowance. This does not prove architectural intent, structural engineering or automatically clear the original strict contact rule. All17 raw failures retained.'))
 refs.extend([HERE/'pool_incident_wall_contacts_v1_20261017.py',*[ROOT/p for p in pins]])
 out=module('wave_same_face_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-same-finite-face-contact-evidence-v1',list(set(refs)),dict(uids=[UID],verifiedConnectionsPerMode=17,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
