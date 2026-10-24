"""Bounded exact original tower/annex contact witness; no identity/support credit."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-source118003-adjacent-exact-interface-v1-20261022'
ACQUIRE='government-xl-source118003-adjacent-original-acquire-v1-20261022'
CAPTURE='government-xl-next-seventeen-current-capture-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)];pins={}
 for name in [ACQUIRE,CAPTURE]:
  _,p=authenticate(BASE/name);pins.update(p);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 acquire=take(BASE/ACQUIRE/'summary.json');assert acquire['sourceRecovered']
 row=next(r for r in take(BASE/CAPTURE/'selection.json.gz')['rows']if r['uid']=='landsd/118003:0')
 paths=[ROOT/row['candidate']['path'],ROOT/acquire['asset']['path']];expected=[row['sourceSHA256'],acquire['sourceSHA256']];tri=[]
 for p,sha in zip(paths,expected):
  raw=p.read_bytes();assert digest(raw)==sha;refs.append(p);tri.append(decode_original_world_triangles(raw))
 a,b=tri;assert len(a)==12969 and len(b)==550
 low,high=b.min(axis=(0,1)),b.max(axis=(0,1));ids=np.flatnonzero(np.all(a.max(1)>=low,axis=1)&np.all(a.min(1)<=high,axis=1))
 witness=None;tested=0;visited=[]
 for i in ids:
  q=exact_component_contacts(a,[int(i)],b,range(len(b)),maximum_pairs=10000);tested+=q['trianglePairsTested'];visited.append(int(i))
  positive=[c for c in q['contacts']if c['dimension']>0]
  if positive:witness=positive[0];break
 report=dict(uids=['landsd/118003:0'],relatedUID='landsd/118128:0',sourceSHA256ByRole=dict(tower=expected[0],annex=expected[1]),wholeSourceFaces=dict(tower=len(a),annex=len(b)),worldSHA256ByRole=dict(tower=digest(a.tobytes()),annex=digest(b.tobytes())),broadPhaseTowerFaces=len(ids),visitedTowerFaces=visited,trianglePairsTested=tested,firstPositiveDimensionalContact=witness,completePairEnumeration=False,identityAccepted=False,physicalSupportAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact rational original-source contact witness only. A crossing or shared line does not by itself prove identity, support or architectural intent. Stop after the first positive-dimensional witness; complete source/current-form/whole-neighbour and four-world physical obligations remain.')
 save(doc/'summary.json',report)
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py'])
 module('source118003_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-tower-annex-interface',refs,report)
 print(dict(witnessFound=witness is not None,trianglePairsTested=tested,visitedTowerFaces=len(visited)),flush=True)
if __name__=='__main__':main()
