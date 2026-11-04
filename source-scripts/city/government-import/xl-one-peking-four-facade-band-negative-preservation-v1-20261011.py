"""Durably preserve a completed nonaccepting diagnostic and its receipt abort.

No recalculation or acceptance claim: original finite results and every input
remain explicitly reviewable, with the missing-uids checkpoint error retained.
"""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,digest
BATCH='government-xl-one-peking-four-facade-band-negative-preservation-v1-20261011'
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-one-peking-four-original-facade-strips-finite-band-diagnostic-v1-20261010'
def main():
 assert not (BASE/BATCH).exists() and not (OLD/'result.json').exists()
 raw=read(OLD/'diagnostic.json.gz');assert raw['coordinateBandM']==.1 and not raw['visualRoleAccepted'] and not raw['physicalAccepted']
 assert [r['component'] for r in raw['completeFourComponentProofs']]==[27,34,46,49]
 assert all(not r['allFacesAssociated'] for r in raw['completeFourComponentProofs'])
 phys=BASE/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010';graph=BASE/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010'
 assets=[ROOT/r['candidate']['path'] for r in read(phys/'selection.json.gz')['rows']]
 refs=[Path(__file__),OLD/'diagnostic.json.gz',HERE/'xl-one-peking-four-original-facade-strips-finite-band-diagnostic-v1-20261010.py',graph/'result.json',graph/'diagnostic.json.gz',phys/'result.json',phys/'selection.json.gz',*assets]
 refs += [HERE/p for p in ['exact_original_surface_coordinate_band_20261010.py','test_exact_original_surface_coordinate_band_20261010.py','exact_original_slab_projection_coverage_20261010.py','exact_original_projection_coverage_20261009.py','exact_packed_world_geometry_20261009.py']]
 sp=importlib.util.spec_from_file_location('peking_band_negative_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 result=m.freeze(BATCH,'nonaccepting-four-source-facade-finite-band-negative-and-checkpoint-abort-preservation-v1',refs,dict(uids=['landsd/233985:0','landsd/240487:0'],preservedCompletedUnfencedDiagnosticSHA256=digest((OLD/'diagnostic.json.gz').read_bytes()),priorCheckpointError="KeyError: 'uids'",completeFourComponentRawResults=raw['completeFourComponentProofs'],allFourComponentFiniteBandIncomplete=True,identityAccepted=False,visualRoleAccepted=False,supportAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,requiresRevisitEvidence='Independent exact source mounting/footing or authored-role evidence; unchanged .1m complete-facet association currently fails. Do not rerun the unchanged failed full-facet route or increase limits.',qualification='Transparent immutable preservation of existing nonaccepting source diagnostics after metadata-only checkpoint error. No numerical replay, positive provenance/role/support/current acceptance or installation is claimed. Complete original inputs/helper/runner/results are bound for independent review.'))
 print(json.dumps(dict(jobId=result['jobId'],allFourFiniteBandIncomplete=True,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
