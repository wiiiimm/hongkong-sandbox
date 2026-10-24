"""Independently revalidate saved local wall paths against all current coordinate modes."""
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_local_wall_paths_v1_20261017 import clip_segment
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-four-world-contacts-v2-20261017';DOC=BASE/BATCH

def bary(p,t):
 uv=np.linalg.lstsq(np.column_stack((t[1]-t[0],t[2]-t[0])),p-t[0],rcond=None)[0];return np.array([1-uv.sum(),*uv])
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'pool_local_wall_paths_v1_20261017.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={};names=['government-xl-sham-shui-po-pool-four-world-foundation-v1-20261017','government-xl-sham-shui-po-pool-local-wall-paths-v1-20261017']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 worldpath=BASE/names[0]/'world-triangles.json.gz';worlds={m:{u:np.array(t) for u,t in w.items()} for m,w in read(worldpath).items()};saved=read(BASE/names[1]/'paths.json')['rows'];DOC.mkdir();tool=HERE/'pool_four_world_interfaces_v1_20261017.mjs'
 prior_strict=BASE/'government-xl-sham-shui-po-pool-four-world-contacts-v1-20261017/strict-interfaces.json'
 old=read(prior_strict)
 for p,h in old['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 save(DOC/'strict-interfaces.json',old);refs += [prior_strict,HERE/'pool_four_world_contacts_v1_20261017.py',prior_strict.parent/'failed-worker.log']
 strict=read(DOC/'strict-interfaces.json');output=[]
 for state in strict['rows']:
  mode=state['mode'];source=worlds[mode]['landsd/271043:0'];support=worlds[mode]['landsd/265480:0'];rows=[]
  for failure in state['proof']['unresolved']:
   point=np.array(failure['position']);old=min(saved,key=lambda r:np.linalg.norm(np.array(r['position'])-point));w=old['witness'];distance=float(np.linalg.norm(np.array(old['position'])-point));checks=dict(matchedWithinExistingContactTolerance=distance<=.001,sourceStartOnFirstFace=False,sourceContactInsideLastFace=False,allSharedEdgesInsideLocalPrism=False,contactOnOriginalSupport=False)
   detail=dict(position=point.tolist(),matchedLiteralDistanceM=distance,checks=checks)
   if checks['matchedWithinExistingContactTolerance']:
    chain=w['faces'];contact=w['contact'];literal=worlds['literal']['landsd/271043:0'][contact['sourceFace']];weights=bary(np.array(contact['contact']),literal);q=weights@source[contact['sourceFace']];lo=point+[-.05,0,-.05];hi=point+[.05,np.sqrt(.5**2-2*.05**2),.05]
    checks['sourceStartOnFirstFace']=np.linalg.norm(closest(point,source[chain[0]])-point)<=.001
    checks['sourceContactInsideLastFace']=min(weights)>=-1e-8 and np.linalg.norm(closest(q,source[chain[-1]])-q)<=.001 and np.all(q>=lo-1e-9) and np.all(q<=hi+1e-9)
    edgeProof=[]
    for a,b in zip(chain,chain[1:]):
     shared=set(map(tuple,source[a]))&set(map(tuple,source[b]));clipped=clip_segment(*[np.array(v) for v in sorted(shared)],lo,hi) if len(shared)==2 else None;edgeProof.append(dict(faces=[a,b],clipped=None if clipped is None else clipped.tolist()))
    checks['allSharedEdgesInsideLocalPrism']=all(r['clipped'] is not None for r in edgeProof)
    hits=[]
    for h in contact['supportContacts']:
     t=support[h['faceIndex']];a,b,c=t;u=b-a;v=c-a;det=u[0]*v[2]-u[2]*v[0]
     if abs(det)<1e-10:continue
     d=q-a;s=(d[0]*v[2]-d[2]*v[0])/det;z=(u[0]*d[2]-u[2]*d[0])/det;y=a[1]+s*u[1]+z*v[1]
     if min(s,z)>=-1e-7 and s+z<=1+1e-7 and abs(q[1]-y)<=.001:hits.append(dict(faceIndex=h['faceIndex'],gapM=float(q[1]-y)))
    checks['contactOnOriginalSupport']=bool(hits);detail.update(contact=q.tolist(),sourceFaces=chain,sharedEdges=edgeProof,supportHits=hits)
   detail['checks']={k:bool(v) for k,v in checks.items()};detail['geometricWitnessVerified']=all(detail['checks'].values());rows.append(detail)
  output.append(dict(mode=mode,strictSamples=state['proof']['samples'],strictContacts=state['proof']['strictContacts'],strictWallContacts=state['proof']['wallIntersections'],remaining=len(rows),geometricWitnessesVerified=sum(r['geometricWitnessVerified'] for r in rows),rows=rows))
 save(DOC/'summary.json',dict(rows=output,allWitnessesVerified=all(r['remaining']==r['geometricWitnessesVerified'] for r in output),fullAcceptance=False,qualification='All canonical samples retained. Saved local source-wall paths independently revalidated in each world; this is evidence for scoped support review, not a global policy change.'))
 for p,h in strict['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 out=module('pool_four_contact_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-world-original-wall-contact-witnesses-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0','landsd/271043:0'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],worlds=[{k:r[k] for k in ['mode','strictSamples','remaining','geometricWitnessesVerified']} for r in output]),flush=True)
if __name__=='__main__':main()
