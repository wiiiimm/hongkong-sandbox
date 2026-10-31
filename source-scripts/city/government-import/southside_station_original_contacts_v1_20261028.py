"""Complete original podium/station finite-face contacts; no semantic acceptance."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-station-original-contacts-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';CAP='government-xl-la-marina-three-original-assembly-v1-20261028';STATION='government-xl-southside-station-original-recovery-v1-20261028';UIDS={'landsd/315025:0','landsd/300867:0'}
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and{'building:'+u for u in UIDS}<=set(lease['resources'])and not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py'];pins={}
 for name in [CAP,STATION]:
  _,bound=authenticate(BASE/name);pins.update(bound);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 row=next(r for r in take(BASE/CAP/'selection.json.gz')['rows']if r['uid']=='landsd/315025:0');station=take(BASE/STATION/'summary.json');assert station['recoveredCount']==1 and not station['errors'];specs=[dict(uid=row['uid'],path=row['candidate']['path'],sha256=row['sourceSHA256'],faces=11699),dict(uid='landsd/300867:0',path=station['sourceAsset']['path'],sha256=station['sourceAsset']['sha256'],faces=1191)];values=[]
 for s in specs:
  p=ROOT/s['path'];assert digest(p.read_bytes())==s['sha256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());assert len(tri)==s['faces'];values.append(tri);s['worldSHA256']=digest(tri.astype('<f8').tobytes())
 report=exact_finite_contacts(values[0],range(len(values[0])),values[1],range(len(values[1])),maximum_pairs=200000);assert report['allPairsExamined']and report['sourceFacesOmitted']==0
 save(DOC/'all-original-finite-contacts.json.gz',report);positive=[r for r in report['contacts']if r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2 and r['dimension']>=1];result=dict(uids=sorted(UIDS),sources=specs,completeFinitePairsAccounted=True,exactCandidatePairsTested=report['trianglePairsTested'],contacts=len(report['contacts']),positiveDimensionalSurfaceContacts=len(positive),sourceContactFaces=len({r['sourceFaceA']for r in report['contacts']}),stationContactFaces=len({r['sourceFaceB']for r in report['contacts']}),sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='All unchanged original faces supplied, including finite degenerate primitives. Exact rational contact geometry only; shared sites, footprint overlap and nonzero contacts do not automatically approve source identity, model penetration, support, placement or publication.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('southside_station_exact_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-podium-station-finite-face-contact-context',refs,result);print({k:result[k]for k in ['exactCandidatePairsTested','contacts','positiveDimensionalSurfaceContacts']},flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-station-exact-original-contacts-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
