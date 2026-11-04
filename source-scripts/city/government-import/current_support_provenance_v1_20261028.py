"""Trace current strict and finite-path contacts to exact support providers.

Actor reachability is a diagnostic, never proof of rooted source components or
architectural/structural acceptance. No successful support/path search is rerun.
"""
import argparse,sys,uuid,subprocess
from pathlib import Path
from collections import deque
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';CURRENT='government-xl-elegant-garden-final-sixteen-composed-support-v1-20261028'
PATHS=['government-xl-elegant-garden-fortune-and-main-podium-current-paths-v1-20261028','government-xl-elegant-garden-remaining-eight-current-paths-v1-20261028']
REBIND='government-xl-elegant-garden-current-four-wall-path-rebind-v1-20261028'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-') and '/' not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 resourcepath=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(resourcepath)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('current-support-provenance-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease) and resources<=set(lease['resources']);refs=[Path(__file__),resourcepath];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(CURRENT,'summary.json');take(CURRENT,'contacts.json.gz');uids=summary['uids']
 # Node reuses unchanged sampling/surface kernels and compares EVERY strict
 # measurement and warning to the completed receipt before attributing faces.
 take(CURRENT,'input.json.gz');tool=HERE/'current_support_provenance_v1_20261028.mjs';refs.append(tool);out.mkdir(parents=True)
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(BASE/CURRENT/'input.json.gz'),str(BASE/CURRENT/'summary.json'),str(BASE/CURRENT/'contacts.json.gz'),str(out/'strict-providers.json.gz')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 proof=read(out/'strict-providers.json.gz')
 for path,sha in proof['inputHashes'].items():
  p=Path(path) if Path(path).is_absolute() else ROOT/path;assert digest(p.read_bytes())==sha;refs.append(p)
 assert len(proof['rows'])==64
 def provider(uid,face):
  part=next(p for p in summary['supportRosters'][uid] if p['sourceFaceRange'][0]<=face<p['sourceFaceRange'][1]);return dict(kind=part.get('kind','other-original'),uid=part.get('uid'),supportFace=face,localFace=face-part['sourceFaceRange'][0])
 pathrows=[]
 for batch in PATHS:
  details=take(batch,'summary.json')
  for row in details['rows']:
   uid,mode=row['uid'],row['mode'];data=take(batch,uid.split('/')[1]+'-'+mode+'.json.gz')
   assert data['currentWarnings']==data['endpointBoundedPaths'] and data['unmappedWitnesses']==0
   for path in data['paths']:
    assert path['passesExistingEndpointHeight'];contact=path['terminal']['contact'];assert contact['dimension']>0
    pathrows.append(dict(uid=uid,mode=mode,witness=path['witness'],sourceFaces=path['faces'],provider=provider(uid,contact['sourceFaceB'])))
 rebound=take(REBIND,'summary.json');assert rebound['sourceWallRoleRebound'] and sum(r['verifiedExistingPaths'] for r in rebound['rows'])==28
 for mode in ['original','literal','leftF32','balancedF32']:
  for path in take(REBIND,mode+'.json.gz')['rows']:
   pathrows.append(dict(uid='landsd/173532:0',mode=mode,witness=path['witness'],sourceFaces=path['faces'],provider=dict(kind='other-original',uid='landsd/236170:0',basis='exact-current-source-podium-and-terminal-contact-rebind')))
 assert len(pathrows)==552
 edges=[];reachability=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  graph={u:set()for u in uids}
  def target(p):return 'drawn-terrain' if p['kind']=='actual-drawn-terrain' else p['uid']
  for row in proof['rows']:
   if row['mode']!=mode:continue
   assert row['uid'] in graph
   for sample in row['strictSamples']:
    for p in sample['providers']:graph[row['uid']].add(target(p))
  for row in pathrows:
   if row['mode']==mode:graph[row['uid']].add(target(row['provider']))
  for uid in uids:
   queue=deque([[uid]]);seen={uid};route=None
   while queue:
    chain=queue.popleft()
    if chain[-1]=='drawn-terrain':route=chain;break
    for to in sorted(graph.get(chain[-1],set())):
     if to not in seen:seen.add(to);queue.append(chain+[to])
   reachability.append(dict(uid=uid,mode=mode,actorLevelTerrainRoute=route,structuralRootAccepted=False))
   edges.append(dict(uid=uid,mode=mode,providers=sorted(graph[uid])))
 save(out/'path-providers.json.gz',pathrows);save(out/'actor-graph.json',dict(edges=edges,reachability=reachability))
 result=dict(uids=uids,strictSamplesAttributed=sum(len(r['strictSamples'])for r in proof['rows']),pathsAttributed=len(pathrows),rows=reachability,sourceGeometryChanges=0,structuralRootsAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Exact existing strict-height provider facets and authenticated path terminal providers. Actor-level reachability records possible directed terrain routes only. It does not prove that every disconnected source component or witness has a rooted accepted dependency, grant architectural roles or approve cycles, surveyed BASIC grounding, identity, collision or installation.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('support_provider_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-strict-and-path-support-provider-attribution',list(dict.fromkeys(refs)),result)
 print(dict(strict=result['strictSamplesAttributed'],paths=len(pathrows),actorTerrainRoutes=sum(r['actorLevelTerrainRoute']is not None for r in reachability),rows=len(reachability)),flush=True)
if __name__=='__main__':main()
