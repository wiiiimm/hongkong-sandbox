"""Complete finite contacts of unchanged Sol City podium and unnamed neighbour."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-neighbour-contacts-v1-20261021';DOC=BASE/BATCH;REC=BASE/'government-xl-sol-city-neighbour-recovery-v1-20261021';OLD=BASE/'government-xl-sol-city-original-support-20261006'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for d in [REC,OLD]:
  r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
def take(d,p):
 assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
n=take(REC,REC/'recovery.json')['rows'][0];p=next(x for x in take(OLD,OLD/'support-inputs.json')['sources']if x['uid']=='landsd/273271:0');sources=[(n['uid'],ROOT/n['assetPath'],n['sourceSHA256']),(p['uid'],ROOT/p['candidate']['path'],p['candidate']['entry']['sha256'])];arrays=[]
for uid,path,sha in sources:assert digest(path.read_bytes())==sha;refs.append(path);arrays.append(decode_original_world_triangles(path.read_bytes()))
a,b=arrays;proof=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))));save(DOC/'contacts.json.gz',dict(neighbourUid=n['uid'],podiumUid=p['uid'],proof=proof,installationApproved=False));positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
result=dict(uids=[n['uid'],p['uid']],completeNeighbourFaces=len(a),completePodiumFaces=len(b),trianglePairsTested=proof['trianglePairsTested'],positiveFiniteContactPairs=len(positive),pointContactPairs=sum(c['dimension']==0 for c in proof['contacts']),sourceGeometryChanges=0,installationApproved=False,qualification='Exact original-source intersection evidence only; not a publication or clearance approval.')
save(DOC/'summary.json',result);refs.extend(HERE/x for x in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']);module('sol_neighbour_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-neighbour-podium-contacts',refs,result);print(result,flush=True)
