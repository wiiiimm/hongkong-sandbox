"""Trace exact renderable edge-components through existing support evidence.

No component welding, geometry edits or structural acceptance. Disconnected
parts and sampled witness components remain separate, including absent roots.
"""
import argparse,sys,uuid
from pathlib import Path
from collections import deque
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from source_closed_components import components
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
CURRENT='government-xl-elegant-garden-final-sixteen-composed-support-v1-20261028'
PROVIDERS='government-xl-elegant-garden-current-support-provenance-v1-20261028'
OLDPATH='government-xl-elegant-garden-seven-witness-paths-v1-20261027'
REBIND='government-xl-elegant-garden-current-four-wall-path-rebind-v1-20261028'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-') and '/' not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 resourcepath=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(resourcepath)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('current-component-support-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease) and resources<=set(lease['resources']);refs=[Path(__file__),resourcepath];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(CURRENT,'summary.json');inputs=take(CURRENT,'input.json.gz');prior=take(CURRENT,'contacts.json.gz')
 strict=take(PROVIDERS,'strict-providers.json.gz');paths=take(PROVIDERS,'path-providers.json.gz');uids=summary['uids']
 assert len(paths)==552 and len(strict['rows'])==64
 def tri(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 output=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  assert reservations.owns(lease);geometries={};maps={};metadata={};graph={};bearing=set();unmapped=[]
  for uid in uids:
   data=next(r for r in inputs['rows'] if r['uid']==uid and r['mode']==mode);t=tri(data['source'])
   assert digest(t.tobytes())==data['sourceWorldSHA256'];geometries[uid]=t
   good=np.flatnonzero(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>0)
   partition=components(t[good]);mapping={}
   for k,c in enumerate(partition['components']):
    ids=[int(good[i]) for i in c['faceIndices']];key=uid+'#'+str(k);graph[key]=set()
    metadata[key]=dict(uid=uid,component=k,sourceFaces=ids,topology={x:v for x,v in c.items() if x!='faceIndices'})
    for i in ids:assert i not in mapping;mapping[i]=key
   assert set(mapping)==set(good.tolist());maps[uid]=mapping
  def component(uid,face):return maps[uid][face]
  def provider(p):
   if p['kind']=='actual-drawn-terrain':return 'drawn-terrain'
   if p['kind']=='surveyed-basic-podium':return 'unqualified-basic:'+p['uid']
   return component(p['uid'],p['localFace'])
  def support_provider(uid,face):
   part=next(p for p in summary['supportRosters'][uid] if p['sourceFaceRange'][0]<=face<p['sourceFaceRange'][1])
   return provider(dict(kind=part.get('kind','other-original'),uid=part.get('uid'),localFace=face-part['sourceFaceRange'][0]))
  for row in strict['rows']:
   if row['mode']!=mode:continue
   uid=row['uid'];t=geometries[uid];lo,hi=t.min(1),t.max(1)
   for sample in row['strictSamples']:
    point=np.asarray(sample['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
    ids=[int(i) for i in broad if i in maps[uid] and np.linalg.norm(closest(point,t[i])-point)<=.001]
    if not ids:unmapped.append(dict(uid=uid,sample=sample));continue
    for i in ids:
     key=component(uid,i);bearing.add(key)
     graph[key].update(provider(p) for p in sample['providers'])
  for path in paths:
   if path['mode']!=mode:continue
   uid=path['uid'];sourcekeys={component(uid,i)for i in path['sourceFaces']};assert len(sourcekeys)==1
   key=sourcekeys.pop();bearing.add(key)
   if uid=='landsd/173532:0':
    # The new rebound receipt proves exact warning/geometry/contact equality.
    rebound=take(REBIND,mode+'.json.gz');old=take(OLDPATH,mode+'.json.gz')
    assert [p['witness']for p in rebound['rows']]==[p['witness']for p in old['rows']]
    record=next(p for p in old['rows'] if p['witness']==path['witness']);assert record['faces']==path['sourceFaces']
    to=component('landsd/236170:0',record['terminal']['contact']['sourceFaceB'])
   else:to=provider(path['provider'])
   graph[key].add(to)
  for raw in prior['rows']:
   if raw['mode']!=mode:continue
   for wall in raw['rawInterface']['resolved']:
    for face in wall['sourceWallFaces']:
     key=component(raw['uid'],face['faceIndex']);bearing.add(key)
     graph[key].update(support_provider(raw['uid'],p['faceIndex'])for p in wall['supportFaces'])
  rows=[]
  for key,meta in metadata.items():
   queue=deque([[key]]);seen={key};route=None
   while queue:
    chain=queue.popleft()
    if chain[-1]=='drawn-terrain':route=chain;break
    for to in sorted(graph.get(chain[-1],set())):
     if to not in seen:seen.add(to);queue.append(chain+[to])
   rows.append(dict(key=key,**meta,providers=sorted(graph[key]),hasExistingSupportWitness=key in bearing,componentTerrainRoute=route,structuralRootAccepted=False))
  save(out/(mode+'.json.gz'),dict(rows=rows,unmappedStrictSamples=unmapped))
  for uid in uids:
   selected=[r for r in rows if r['uid']==uid]
   record=dict(uid=uid,mode=mode,renderableComponents=len(selected),witnessComponents=sum(r['hasExistingSupportWitness']for r in selected),
    componentsWithTerrainRoute=sum(r['componentTerrainRoute']is not None for r in selected),
    witnessComponentsWithoutTerrainRoute=[r['component']for r in selected if r['hasExistingSupportWitness'] and r['componentTerrainRoute']is None],
    componentsWithoutExistingSupportWitness=[r['component']for r in selected if not r['hasExistingSupportWitness']],
    unmappedStrictSamples=sum(r['uid']==uid for r in unmapped),structuralRootsAccepted=False)
   output.append(record);print(record,flush=True)
 result=dict(uids=uids,rows=output,sourceGeometryChanges=0,sourcePoseChanges=0,structuralRootsAccepted=False,physicalAccepted=False,installationApproved=False,
  qualification='Exact nondegenerate shared-edge topology, without rounded/welded vertices or zero-edge bridges. Existing strict sample incidences and finite path terminals provide directed component edges; no new contact/path search. Routes remain diagnostic: positive point/height incidence alone does not establish architectural roles, filled volumes, accepted terrain/BASIC root or complete disconnected-part support. Unwitnessed components and missing routes stay explicit.')
 save(out/'summary.json',result);refs.extend(HERE/n for n in ['source_closed_components.py','pool_incident_wall_contacts_v1_20261017.py'])
 assert reservations.owns(lease)
 module('component_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-source-component-support-provenance',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
