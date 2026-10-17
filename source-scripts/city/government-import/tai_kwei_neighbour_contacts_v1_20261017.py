"""Full original Tai Kwei/Tai Fu/Tai Wing contact evidence, never acceptance."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tai-kwei-neighbour-contacts-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-tai-kwei-current-physical-v1-20261017';NEIGH=BASE/'government-xl-tai-kwei-neighbour-originals-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in [PRIOR,NEIGH]:
   r=read(p/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(PRIOR/'selection.json.gz')['rows']+read(NEIGH/'selection.json.gz')['rows'];tri=[]
 for r in rows:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];t=decode_original_world_triangles(p.read_bytes());assert len(t)==r['triangles'];tri.append(t);refs.append(p)
 a=tri[0];out=[]
 for r,b in zip(rows[1:],tri[1:]):
  low,high=b.min(1),b.max(1);pairs=sum(int(np.all(high>=f.min(0),1).__and__(np.all(low<=f.max(0),1)).sum())for f in a);print(dict(neighbour=r['uid'],broadPhasePairs=pairs),flush=True)
  contacts=exact_component_contacts(a,list(range(len(a))),b,list(range(len(b))),maximum_pairs=1000000)
  ap=shapely.union_all(shapely.polygons(a[:,:,[0,2]]));bp=shapely.union_all(shapely.polygons(b[:,:,[0,2]]));out.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],sourceTriangles=len(b),completeSourceProjectionOverlapM2=float(ap.intersection(bp).area),contacts=contacts))
 save(DOC/'contacts.json',dict(uid=rows[0]['uid'],sourceSHA256=rows[0]['sourceSHA256'],sourceTriangles=len(a),neighbours=out,identityApproved=False,installationApproved=False))
 refs +=[ROOT/p for p in pins]+[PRIOR/'selection.json.gz',NEIGH/'selection.json.gz']
 result=module('tai_kwei_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-complete-original-neighbour-contact-v1',list(set(refs)),dict(uids=[r['uid']for r in rows],summary=[dict(uid=r['uid'],sourceProjectionOverlapM2=r['completeSourceProjectionOverlapM2'],contacts=len(r['contacts']['contacts']),allPairsExamined=r['contacts']['allPairsExamined'])for r in out],nextStep='Interpret exact original source contacts against identity warnings; no collision or publication approval follows from this diagnostic.',fullAcceptance=False));print(result['jobId'],flush=True)
if __name__=='__main__':main()
