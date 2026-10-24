"""Save completed original-source recovery evidence; no installation credit."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
 base=ROOT/'docs/astra-city/government-import';batch='government-xl-wah-shun-station-three-progress-v2-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];jobs={}
 for folder in sorted(base.glob('government-xl-wah-shun*20261024')):
  receipt=folder/'result.json'
  if not receipt.is_file():continue
  result,pins=authenticate(folder)
  # Receipts authenticate historical jobs; only their own frozen outputs are
  # rehashed here. This reporting checkpoint transfers no historical approval.
  for name,sha in pins.items():
   if (ROOT/name).is_relative_to(folder):assert digest((ROOT/name).read_bytes())==sha
  refs.append(receipt);jobs[folder.name]=result['jobId']
 assert 'government-xl-wah-shun-station-three-physical-review-v2-20261024' in jobs
 out.mkdir()
 for name,path in [('progress-v1-historical-mutable-context.log','/tmp/xl-wah-shun-three-progress-v1.log'),('unneeded-native-overlap-adapter.log','/tmp/xl-wah-shun-native-contacts-v1.log'),('ragged-matplotlib-v1.log','/tmp/xl-wah-shun-tower-negative-views.log'),('retained-only-browser-adapter-v1.log','/tmp/xl-wah-shun-three-private-browser-v1.log')]:
  p=Path(path)
  if p.exists():shutil.copyfile(p,out/name)
 refs.extend([HERE/n for n in ['original_compound_projection_diagnostic_v1_20261024.py','selected_original_local_inset_v8_20261024.py','original_complete_actual_ground_clearance_v1_20261024.py','original_exact_negative_face_views_v1_20261024.py','original_exact_negative_face_views_v2_20261024.py']])
 result=dict(uids=['landsd/237751:0','landsd/235644:0','landsd/84271:0'],status='original-physical-qualified-awaiting-private-browser-and-installation',newlyInstalled=0,installationApproved=False,publication=False,permanentRejection=False,requiresHumanDecision=False,requiresAIGeometryModelling=False,requiresCompute=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,completedJobs=jobs,currentFixedXL=dict(total=521,installed=353,unfinished=168),currentNativeActors=6899,
 completed=['Recovered unchanged821face QuarryBay original;12,248original faces total across3actors.','Exact shared original tower/podium source coverage98.33percent/wholeGeoRefcell and22finite support paths perworld; station has no actual original surfacecontact with either actor.','Bounded original-TIN union12353faces/7changedcoarseparentfaces passes unchanged validator;all25basicneighbours pass;full6899native scope has no touchingactors or terrainoverlap.','All3complete sources have zero whole/upward whole burial in all4worlds. Exact clearance identifies22tower/24station exposed walls with clear-cap paths and one specific provider-authored lower podium return1219. Original-TIN exact comparison reproduces that sole podium flag.','ROOT inspected complete/lower assembly, identity projection, all19two-angle negative-region exports; physicalreviewv2 remains source-case interpretation, preserves all raw failures and grants no installation.','12ground-context tests pass including all3real rank-cancellation facets and real below-limit negatives.'],
 correctedSetupFailures=['CheckpointV1stopped when an older acquisition pinned a prior mutable manifest; reportingV2authenticates historical jobs and rehashes each job own immutable outputs only, with no historical approval transfer. Native-overlap adapter correctly refuses zero pairs; complete native bounds already prove none overlap.','Prephysical continuousv1 stopped at real floating-point rank cancellation. V2uses exact finite arithmetic on those unchanged narrow projected faces.','Matplotlib mixed polygon lengths rejected plottingV1;V2onlydisables autoscaling and uses explicitly fixed complete plotbounds.','First browser adapter required retained-terrainreplacement, which this new patch does not have. It stopped before browser and released lease. SupportedbrowserV5preserves all checks and handles exact newterrain plus original support; separateV2started.'],
 nextActions=['Observe government-xl-wah-shun-station-three-private-browser-v2-20261024 and its existing process; do not restart a live or merely slow browser.','Inspect every resulting source export before final source review. Complete guarded staged/live installation and full521independent readback, then commit/push if installed.','Final source/physical envelope must bind complete25formterrain scope plus all3original source scopes; retain exact tower->235644dependency and independentstation.','Continue all168unfinishedfixedXL; this is one pendingXL source plus2support/neighbour originals, not3newXL credits.'])
 save(out/'remaining-work.json',result)
 module('wah_shun_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'unchanged-wah-shun-original-support-and-quarry-bay-recovery-progress',refs,result)

if __name__=='__main__':main()
