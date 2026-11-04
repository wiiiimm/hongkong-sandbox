"""Group exact flagged source faces for interpretation; no modelling or approval."""
from pathlib import Path
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-whole-components-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-sheung-shui-original-grade-context-v1-20261020'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=BASE/'government-xl-next-twenty-current-terrain-v2-20261020/selection.json.gz';assert str(selection.relative_to(ROOT)) in pins
 row=next(x for x in read(selection)['rows']if x['uid']=='landsd/56054:0');asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']
 tri=decode_original_world_triangles(raw);assert len(tri)==19911
 context=read(SRC/'56054:0-original.json.gz');assert context['sourceSHA256']==row['sourceSHA256']
 ids=context['continuousNegativeFaceIds'];assert len(ids)==68
 edges=defaultdict(set);adj=defaultdict(set)
 for i in range(len(tri)):
  pts=[tuple(v)for v in tri[i]]
  for a,b in [(0,1),(1,2),(2,0)]:
   if pts[a]!=pts[b]:edges[tuple(sorted((pts[a],pts[b])))].add(i)
 for group in edges.values():
  for i in group:adj[i].update(group-{i})
 unseen=set(range(len(tri)));groups=[];faces=context['faces'];assert all(f['sourceFace']==i for i,f in enumerate(faces))
 while unseen:
  todo=[min(unseen)];component=set()
  while todo:
   i=todo.pop()
   if i in component:continue
   component.add(i);todo.extend(adj[i]-component)
  unseen-=component
  flagged=component&set(ids)
  if not flagged:continue
  part=tri[sorted(component)];values=[faces[i]for i in sorted(flagged)]
  groups.append(dict(sourceFaceIds=sorted(component),flaggedSourceFaceIds=sorted(flagged),faces=len(component),worldBounds=[part.min((0,1)).tolist(),part.max((0,1)).tolist()],upwardFaceIds=sorted(component&set(context['negativeUpwardFaceIds'])),withoutExposedWitness=sorted(component&set(context['negativeWithoutExposedWitness'])),minimumGapM=min(v['minimum']['minimumGapM']for v in values),maximumObservedGapM=max(v['maximumObservedGapM']for v in values if v.get('maximumObservedGapM')is not None)))
 assert sorted(i for g in groups for i in g['flaggedSourceFaceIds'])==ids
 save(DOC/'groups.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],wholeSourceFaces=len(tri),flaggedFaces=len(ids),groups=groups,grouping='Exact Float64 world-vertex shared-edge adjacency across all19911 source faces, retaining every component touching a flagged face. Not architectural or structural component labels.',sourceOnly=True,installationApproved=False))
 refs=[Path(__file__),SRC/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('harbourfront_groups_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-whole-source-exact-edge-components',refs,dict(uids=[row['uid']],groups=len(groups),flaggedFaces=len(ids),installationApproved=False))
 print([(g['faces'],g['worldBounds'],len(g['upwardFaceIds']),len(g['withoutExposedWitness']))for g in groups],flush=True)
if __name__=='__main__':main()
