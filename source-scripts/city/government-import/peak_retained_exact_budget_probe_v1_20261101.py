"""Record exact private consolidation counts after a failed runtime-budget gate.

Diagnostic only: no accepted candidate, guard edits, low-parent route or publication.
"""
import sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from constant_colour_terrain_consolidation_v1 import consolidate_patch
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peak-retained-exact-budget-probe-v1-20261101';LOCAL=HERE/'local'/BATCH;PRIOR='government-xl-peak-retained-original-terrain-v1-20261101-167911-0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 receipt,pins=authenticate(BASE/PRIOR);assert receipt['reason']=='terrain-runtime-budget'and not receipt['installationApproved']
 path=BASE/PRIOR/'unapproved-terrain.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];patch=read(path)
 low=BASE/PRIOR/'unchanged-low-parent-proof.json';assert digest(low.read_bytes())==pins[str(low.relative_to(ROOT))]and read(low)['unchangedLowParentFaces']==0
 output,proof=consolidate_patch(patch);assert np.isfinite(output).all()and output[:,:,1].min()>=1.2
 assert proof['allOriginalFacesAccounted']and proof['flatNormalsAndFinitePlaneSurfacesPreserved']and proof['mixedColourFacesRetainedUnchanged']
 doc=BASE/BATCH;save(doc/'exact-surface-proof.json.gz',proof)
 summary=dict(uids=receipt['uids'],sourceSHA256ByUid=receipt['sourceSHA256ByUid'],originalTerrainFaces=proof['originalFaces'],outputTerrainFaces=len(output),savedTerrainFaces=proof['savedFaces'],withinExisting25000FaceBudget=len(output)<=25000,existingTriangleBudget=25000,remainingExcessFaces=max(0,len(output)-25000),minimumTerrainHeightM=float(output[:,:,1].min()),minimumHeightGuardM=1.2,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,acceptedCandidateCreated=False,qualification='Exact count/surface diagnostic only. The existing 25k budget and 1.2m guard are unchanged. No candidate or physical approval is produced, regardless of count.')
 save(doc/'summary.json',summary);assert reservations.owns(lease)
 refs=[Path(__file__),BASE/PRIOR/'result.json',path,low,HERE/'constant_colour_terrain_consolidation_v1.py',HERE/'exact_runtime_coplanar_consolidation_20261010.py',HERE/'exact_coplanar_boundary_census_20261010.py',HERE/'exact_runtime_coplanar_groups_20261010.py']
 module('peak_retained_budget_probe_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-terrain-budget-count-diagnostic',refs,summary);print(summary,flush=True)
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()and not(BASE/BATCH).exists()
  c=reservations.claim('peak-retained-budget-probe-'+str(uuid.uuid4()),['building:landsd/167911:0','building:landsd/248218:0','terrain:city/data/terrain.json','terrain:city/data/support-exact-tin-248218-0.json','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
