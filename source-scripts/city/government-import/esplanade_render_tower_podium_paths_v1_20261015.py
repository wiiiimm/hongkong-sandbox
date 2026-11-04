"""Exact positive-dimensional tower/podium contacts and same-source edge paths."""
from pathlib import Path
from collections import defaultdict,deque
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-esplanade-render-tower-podium-paths-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-esplanade-source-roles-v1-20261015';PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';LOCAL=HERE/'local'/PHYSICAL.name

def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 old=read(PRIOR/'tower-connectivity.json');rows=read(PHYSICAL/'selection.json.gz')['rows'];runtime=read(LOCAL/'runtime-geometry.json.gz')['rows'];original={};literal={};paths=[Path(__file__),PRIOR/'result.json',PRIOR/'tower-connectivity.json',PHYSICAL/'selection.json.gz',LOCAL/'runtime-geometry.json.gz']
 for row in rows:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];original[row['uid']]=decode_original_world_triangles(asset.read_bytes());r=next(r for r in runtime if r['uid']==row['uid']);literal[row['uid']]=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];assert original[row['uid']].shape==literal[row['uid']].shape;paths.append(asset)
 capture_doc=BASE/'government-xl-esplanade-render-finite-v2-20261015';capture_receipt=read(capture_doc/'result.json')
 for q in capture_receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 captured=read(capture_doc/'attributes.json.gz');worlds={}
 for mode,key in [('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
  worlds[mode]={r['uid']:np.asarray(r[key],float).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in captured['rows']}
 paths.extend([capture_doc/'result.json',capture_doc/'attributes.json.gz'])
 claim=reservations.claim('esplanade-exact-interface-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];summaries=[]
 try:
  for mode,world in worlds.items():
   tower=world['landsd/268828:0'];podium=world['landsd/309385:0'];contacts=exact_component_contacts(tower,old['sampledContactFaces'],podium,list(range(len(podium))));positive=[r for r in contacts['contacts']if r['dimension']>0];roots={r['sourceFaceA']for r in positive};assert reservations.heartbeat(lease)['ok'];valid=np.linalg.norm(np.cross(tower[:,1]-tower[:,0],tower[:,2]-tower[:,0]),axis=1)>0;edges=defaultdict(list)
   for i in np.flatnonzero(valid):
    for a,b in zip(tower[i],np.roll(tower[i],-1,axis=0)):
     if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(int(i))
   adjacency=defaultdict(set)
   for members in edges.values():
    for i in members:adjacency[i].update(set(members)-{i})
   roots={i for i in roots if valid[i]};parents={i:None for i in roots};queue=deque(sorted(roots))
   while queue:
    i=queue.popleft()
    for j in sorted(adjacency[i]):
     if j not in parents:parents[j]=i;queue.append(j)
   failures=[]
   for item in old['rows']:
    candidate=[]
    for i in item['incidentFaces']:
     if i in parents:
      path=[i]
      while parents[path[-1]]is not None:path.append(parents[path[-1]])
      candidate.append(path)
    failures.append(dict(position=item['position'],rawReason=item['reason'],incidentFaces=item['incidentFaces'],exactSharedEdgePathsToPositivePodiumContact=candidate))
   save(DOC/(mode+'.json.gz'),dict(mode=mode,towerWorldSHA256=digest(tower.tobytes()),podiumWorldSHA256=digest(podium.tobytes()),completeTowerFaces=len(tower),completePodiumFaces=len(podium),rawExactContacts=contacts,positiveContactRoots=sorted(roots),reachableFaces=len(parents),failures=failures,installationApproved=False,qualification='Exact rational contact dimensions and unchanged shared edges. Original failure labels retain literal sampled incident-face associations. Geometric continuity only, not load-bearing/engineering or whole-model acceptance.'))
   summary=dict(mode=mode,positiveContacts=len(positive),contactRootFaces=len(roots),failurePoints=len(failures),failurePointsWithExactPath=sum(bool(r['exactSharedEdgePathsToPositivePodiumContact'])for r in failures),trianglePairsTested=contacts['trianglePairsTested']);summaries.append(summary);print(summary,flush=True)
  for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
  paths.extend(HERE/n for n in ['exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py'])
  spec=importlib.util.spec_from_file_location('esplanade_exact_path_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'exact-explicit-f32-tower-podium-positive-contact-paths-v1',paths,dict(uids=['landsd/268828:0','landsd/309385:0'],rows=summaries,fullAcceptance=False,nextStep='Source-specific facade/support role reconciliation and actual render/staging checks. No automatic role or installation approval.'))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
