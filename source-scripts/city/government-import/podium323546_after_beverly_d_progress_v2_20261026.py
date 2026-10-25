"""Persist completed source work and exact remaining obligations; no acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 base=ROOT/'docs/astra-city/government-import';prefix='government-xl-podium323546-after-beverly-d-';batch=prefix+'progress-v2-20261026';out=base/batch;assert not out.exists();refs=[Path(__file__)];completed=[]
 for folder in sorted(base.glob(prefix+'*')):
  if (folder/'result.json').exists() and '-progress-' not in folder.name:
   receipt,_=authenticate(folder);refs.append(folder/'result.json');completed.append(dict(batch=folder.name,jobId=receipt['jobId']))
 assert len(completed)>=15
 roundoff=read(base/(prefix+'clamped-original-inset-v7-20261026')/'return-floor-roundoff.json');assert max(r['maximumCorrectionM']for r in roundoff['corrections'])==1.7462253865119237e-11 and len(roundoff['corrections'])==63
 remaining=[
  'Do not repeat unchanged additive terrain attempts: actual source-face558 centroid has originalTIN/private candidate4.571061135m, source4.689833323m, extra installed group fallback5.907827280m. Owner proof3aeaa688a412e14dc278bd32b408d867c4fd4d7fadc11619fc1d77ad415e9a13 proves exact Float32 rendered group grid triangle, not source corruption. Single witness is diagnostic only.',
  'Build explicitly pinned hierarchical replacement of city/data/government-native-central-piers-original-v1-20261021.json, preserving all13children and full old root surface/domain outside edit. Existing native child9/323703 bounds endX1607.5; original inset outer beginsX1610.909m, so source edit itself is disjoint. Candidate70m parent rectangle overlaps child9 and group root fallback; must reparent with correct5m group cells/full group extent, never just add top-level terrain or delete group. A narrower group-aligned child plus expanded group edge may avoid original native child overlap, but requires actual whole-domain proofs/current affected basics/native checks/terrain validation before any publication.',
  'V7 private candidate5707faces passes terrain validator. Raw actual additive runtime still799buried/381upward (before1577/759), minGap-4.971706m. Preserve these failures. Complete source10612faces covered; no geometry/pose edits. Newclamp helperV4 direct opposite level-set clips preserves tiny positive fragments, fixes GEOS subtraction sliver, keeps floor1.2m. Return roundoff maximum1.7462253865119237e-11m across63corrections, capped1e-10m; final strictfloor/globalvalidators unchanged. All10 tests passed, and actual660source upper fragments pass helper producing738pieces/66.07733m2floored projection. Do not edit any successful frozen producer; new versions only.',
  'Identity still fails maximum extent14.658229m; rawtarget coverage99.1745446%, source excess643.908m2, unrelatedoverlap0. Exact CSUID3616017496P20240826/sourceB361601749602063C0 confirmed, fresh official footprint exists but0structure relations. Needs bounded exact source/component role interpretation, not blanket identity approval. Source-only complete/base-clipped plots actually opened, no browser visual acceptance.',
  'Foreign BASIC210501/210742 have26/30positive original contacts(all4modes), beforeBASIC24each. Threeotherbasics0. Do not equate small projection overlap with no collision. Need source-role/support interpretation or exact original companions, with owncurrentchecks. Scope has6forms/0native; terrain scope13forms/one native323703 plusgroupfull-domain obligations.',
  'No source is permanently rejected. All diagnostic workers terminal, no publication/installation credit. Fixed521 remains382installed/139unfinished;6959actors. Dinstallation686c6eea2 alreadyPUSHED, neverreinstallD/A/F/E/K/UniversityHall. Preserve2nullUIDsourcekeys. NoAIgeometry/optimisation/shared4176restart/mainmerge/newagents.',
 ]
 failures=[dict(phase='initial-source-plot',reason='Selection receipt supplied to plot requiring actual runtime geometry; corrected V2uses completedruntime. No visual or installation credit from failed invocation.'),dict(phase='initial-inset-runtime',reason='Replacement-only V6 adapter rejected absent explicit replacement. Correct V2additive runtime completed; no guard weakened.')]
 result=dict(uids=['landsd/323546:0'],completed=completed,remainingWork=remaining,failedInvocationCauses=failures,tests=dict(clampHelper=10,passed=True,realFragmentRegression=True),fullXLCounts=dict(total=521,installedVerified=382,remaining=139),currentNativeActors=6959,newlyInstalled=0,installationApproved=False,publication=False,permanentRejection=False,sourceGeometryChanges=0,aiGeometryModelling=False,scriptExternalAICalls=0,heldForHumanDecision=False,heldForAIProcessing=False,heldForComputeAndCode=True,status='original-source-active-hierarchical-terrain-and-identity-work')
 result['supersedesProgressNote']=dict(batch=prefix+'progress-v1-20261026',correction='The earlier note quoted the first1.13e-14m return correction as if it were the maximum. Exact maximum is1.7462253865119237e-11m across63vertices, still below unchanged1e-10m construction roundoff bound. All frozen geometry and measured receipts are unchanged.')
 save(out/'remaining-work.json',result)
 for p in sorted(HERE.glob('*clamped*20261026.py')):refs.append(p)
 for p in sorted(HERE.glob('clamped_original_terrain_v*_20261026.py')):refs.append(p)
 refs.append(HERE/'selected_original_patch_runtime_v2.py')
 for log in ['podium323546-original-inset-v1.log',*[f'podium323546-clamped-original-inset-v{v}.log'for v in range(2,8)],'podium323546-inset-runtime-v1.log','podium323546-inset-runtime-v2.log']:
  p=Path('/tmp')/log
  if p.exists():dest=out/log;dest.write_bytes(p.read_bytes());refs.append(dest)
 module('podium_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'explicit-original-source-compute-progress-and-revisit-obligations',refs,result)
 print(dict(completed=len(completed),installedXL=382,unfinishedXL=139,publication=False),flush=True)
if __name__=='__main__':main()
