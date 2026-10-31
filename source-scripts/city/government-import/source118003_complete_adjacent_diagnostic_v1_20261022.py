"""Full unchanged-source pair contact and footprint evidence; no identity approval."""
from pathlib import Path
from collections import Counter
import numpy as np
import shapely
from shapely.geometry import Polygon,MultiPoint
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
B='government-xl-source118003-complete-adjacent-diagnostic-v1-20261022';BASE=ROOT/'docs/astra-city/government-import';D=BASE/B
CAP='government-xl-next-seventeen-current-capture-v1-20261022';ACQ='government-xl-source118003-adjacent-original-acquire-v1-20261022';LOOK='government-xl-source118003-adjacent-lookup-v1-20261022'
assert not D.exists();refs=[Path(__file__)];pins={}
for n in [CAP,ACQ,LOOK]:
 _,q=authenticate(BASE/n);pins.update(q);refs.append(BASE/n/'result.json')
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
r=next(x for x in take(BASE/CAP/'selection.json.gz')['rows']if x['uid']=='landsd/118003:0');a=take(BASE/ACQ/'summary.json');lookup=take(BASE/LOOK/'lookup.json');assert a['sourceRecovered']
tri=[]
for p,sha in [(ROOT/r['candidate']['path'],r['sourceSHA256']),(ROOT/a['asset']['path'],a['sourceSHA256'])]:
 raw=p.read_bytes();assert digest(raw)==sha;refs.append(p);tri.append(decode_original_world_triangles(raw))
assert [len(t)for t in tri]==[12969,550]
forms=[r['source']['building'],lookup['currentAdjacentForm']]
polys=[Polygon(f['rings'][0],f['rings'][1:])for f in forms]
projections=[shapely.union_all([MultiPoint(f[:,[0,2]]).convex_hull for f in t])for t in tri]
contacts=exact_component_contacts(tri[0],range(len(tri[0])),tri[1],range(len(tri[1])),maximum_pairs=1000000)
assert contacts['allPairsExamined'];save(D/'complete-contacts.json.gz',contacts)
rows=[]
for i in [0,1]:
 own=polys[i];p=projections[i];other=polys[1-i]
 rows.append(dict(uid=forms[i]['uid'],sourceFaces=len(tri[i]),sourceProjectionAreaM2=p.area,targetAreaM2=own.area,targetCoveredBySource=p.intersection(own).area/own.area,uncoveredCurrentFootprintM2=own.difference(p).area,sourceExcessM2=p.difference(own).area,sourceExcessInOtherCurrentFootprintM2=p.difference(own).intersection(other).area))
summary=dict(uids=['landsd/118003:0'],relatedUID='landsd/118128:0',sourceSHA256ByUid={'landsd/118003:0':r['sourceSHA256'],'landsd/118128:0':a['sourceSHA256']},rows=rows,completePairEnumeration=True,trianglePairsTested=contacts['trianglePairsTested'],contactDimensions=dict(Counter(str(c['dimension'])for c in contacts['contacts'])),sourceProjectedIntersectionM2=projections[0].intersection(projections[1]).area,identityAccepted=False,physicalSupportAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exhaustive unpadded-AABB/exact rational pair contacts and complete projected footprints. Projected overlap/contact dimension does not establish identity, ownership, support or collision acceptance; unchanged current full-scene checks remain required.')
save(D/'summary.json',summary)
refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py']);refs.extend([D/'summary.json',D/'complete-contacts.json.gz'])
module('complete_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'complete-original-adjacent-pair-diagnostic',refs,summary)
print({k:summary[k]for k in ['trianglePairsTested','contactDimensions','sourceProjectedIntersectionM2','rows']},flush=True)
