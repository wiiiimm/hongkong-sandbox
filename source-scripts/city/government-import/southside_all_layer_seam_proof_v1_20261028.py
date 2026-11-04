"""Compare every finite seam layer without changing any existing validator result."""
import argparse,sys,uuid,subprocess
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from finite_layered_seam_coverage_v1_20261028 import bidirectional_layer_coverage
sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
import coordinated_native_boundary as legacy
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-all-layer-seam-proof-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PRIOR='government-xl-southside-partition-existing-seams-v1-20261028';UID='landsd/315025:0'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json',HERE/'finite_layered_seam_coverage_v1_20261028.py',HERE/'test_finite_layered_seam_coverage_v1_20261028.py',HERE/'coordinated_native_boundary_v1_20261023.py',Path(legacy.__file__)]
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 old=take(BASE/PRIOR/'summary.json');assert len(old['pairs'])==5 and all(s['finitePairConstructionPassed']for r in old['pairs']for s in r['sides']);proc=subprocess.run([sys.executable,str(HERE/'test_finite_layered_seam_coverage_v1_20261028.py')],cwd=ROOT,capture_output=True,text=True);assert proc.returncode==0;save(DOC/'tests.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr));rows=[]
 for j in range(5):
  p=BASE/PRIOR/('pair-'+str(j)+'.json');pair=take(p);names=sorted(pair['members']);nodes={name:take(ROOT/pair['members'][name]['candidate']['path'])for name in names};boxes={name:legacy.bounds(node)for name,node in nodes.items()};x=boxes[names[0]][2];assert x==boxes[names[1]][0];edit=shapely.from_wkt(pair['editRegionWKT']);lo,hi=edit.bounds[1],edit.bounds[3];curves={name:legacy.seam_segments(legacy.triangles(node),0,x,lo,hi)for name,node in nodes.items()};report=bidirectional_layer_coverage(curves[names[0]],curves[names[1]]);rows.append(dict(pair=names,sharedX=x,finiteInterval=[lo,hi],allLayerCoverage=report,legacyUpperEnvelopeConstructionStillPassed=True,legacyFailedBandVertices=sum(s['failedVertices']for r in old['pairs']if r['pair']==names for s in r['sides'])));save(DOC/'progress.json',dict(completed=len(rows),rows=rows,installationApproved=False));assert reservations.owns(lease);print(dict(pair=names,allLayersPassed=report['passed']),flush=True)
 result=dict(uids=[UID],pairs=rows,allFiveBidirectionalLayerProofsPassed=all(r['allLayerCoverage']['passed']for r in rows),legacyNegativeResultsPreserved=True,productionGuardChanges=False,terrainValidatorPassed=False,physicalAccepted=False,identityAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact rational full finite-layer comparison at9.99mm, strictly below legacy1cm. Mathematical source-conservation evidence only; existing pair validator negatives remain preserved and no boundary adapter or publisher is changed. No old overlap approval transfer, current-neighbour approval, browser approval or installation credit.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('southside_all_layer_seam_proof_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-all-layer-seam-conservation-with-legacy-negatives-preserved',refs,result);print(dict(allFivePassed=result['allFiveBidirectionalLayerProofsPassed']),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-all-layer-exact-seams-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
