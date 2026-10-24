"""Exact boundary-edge fixed-band diagnostic for two residual original Tower 3A components."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-tower3a-connected-edge-band-v1-20261021';DOC=BASE/BATCH
FOUND=BASE/'government-xl-tko-complete-foundations-v2-20261021';JOIN=BASE/'government-xl-tko-residual-component-joins-v1-20261021'
CONTACT=BASE/'government-xl-tko-complete-contacts-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={};summary=[]
 for folder in [FOUND,JOIN,CONTACT]:
  _,bound=authenticate(folder);pins[folder]=bound;refs.append(folder/'result.json')
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 for mode in ['original','literal','leftF32','balancedF32']:
  inp=take(FOUND,FOUND/mode/'32024:0/input.json.gz');r=inp['rows'][0];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
  joins=take(JOIN,JOIN/mode/'32024:0-joins.json.gz');assert digest(t.tobytes())==joins['sourceWorldSHA256']
  excluded={i for c in joins['components']for i in c['componentFaces']}
  contact=take(CONTACT,CONTACT/mode/'32024:0.json.gz');assert contact['sourceWorldSHA256']==digest(t.tobytes());assert contact['podiumWorldSHA256']==digest(np.asarray(inp['podium']).reshape(-1,3,3).tobytes())
  from collections import defaultdict,deque
  valid=set(np.flatnonzero(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>0).tolist())-excluded
  seeds=sorted({c['sourceFaceA']for c in contact['proof']['contacts']if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0}&valid)
  shared=defaultdict(list)
  for f in sorted(valid):
   for a,b in [(0,1),(1,2),(2,0)]:
    edge=tuple(sorted((tuple(t[f,a]),tuple(t[f,b]))))
    if edge[0]!=edge[1]:shared[edge].append(f)
  adj=defaultdict(set)
  for ids in shared.values():
   for f in ids:adj[f].update(ids)
  previous={f:None for f in seeds};queue=deque(seeds)
  while queue:
   f=queue.popleft()
   for n in sorted(adj[f]):
    if n not in previous:previous[n]=f;queue.append(n)
  hosts=sorted(previous);assert hosts;rows=[]
  save(DOC/(mode+'-host-connectivity.json'),dict(sourceWorldSHA256=digest(t.tobytes()),sourceContactSeeds=seeds,parents=previous,hostFaces=hosts,excludedFaces=sorted(excluded),installationApproved=False))
  from collections import Counter
  edges=Counter(tuple(sorted((tuple(t[f,a]),tuple(t[f,b])))) for f in sorted(excluded) for a,b in [(0,1),(1,2),(2,0)])
  for edge,count in sorted(edges.items()):
   if count!=1 or edge[0]==edge[1]:continue
   proof=verify(np.asarray(edge),t[hosts]);rows.append(dict(sourceEdge=edge,proof=proof));print(mode,edge,proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'],flush=True)
  save(DOC/(mode+'.json.gz'),dict(sourceWorldSHA256=digest(t.tobytes()),hostFaceIds=hosts,excludedFaceIds=sorted(excluded),rows=rows,installationApproved=False))
  summary.append(dict(mode=mode,edges=len(rows),completeEdgesAssociated=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in rows)))
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['china_ferry_current_foundations_v1_20261020.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_slab_projection_coverage_20261010.py'])
 result=dict(uids=['landsd/32024:0'],rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Exact finite association only; excludes both residual components from hosts. Hosts have nondegenerate shared-edge paths to positive finite podium contacts. This records source connectivity only; role and installation remain unapproved, with no band changes.')
 save(DOC/'summary.json',result);module('tko_finite_band_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'residual-original-boundary-edge-finite-host-fixed-band',refs,result)
if __name__=='__main__':main()
