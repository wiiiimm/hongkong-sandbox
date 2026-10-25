"""Save completed XL compute evidence and explicit remaining work; no acceptance."""
from pathlib import Path
import re
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-caribbean-tuen-mun-compute-checkpoint-v1-20261025'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];completed=[]
 rx=re.compile(r'government-xl-(?:caribbean-(?:two-after-high-court|upward|seams|minimal|companion-seams|two-private-browser|two-compound|two-foreign|two-current|two-final-source|two-original-final|290981-source|95518-source)|tuen-mun-(?:five-|private-seams|minimal-seams|town-hall-basic|290804-basic|small-34417-podium|podium-historical-exact))')
 for p in sorted(BASE.iterdir()):
  if not p.is_dir()or not rx.match(p.name)or not p.name.endswith('20261025')or not(p/'result.json').exists():continue
  result,_=authenticate(p);completed.append(dict(batch=p.name,jobId=result['jobId']));refs.append(p/'result.json')
 assert len(completed)>=57
 archive=HERE/'selected_original_minimal_seam_terrain_draft_v1_20261025.py';oldkey=str((HERE/'selected_original_seam_terrain_v2_20261025.py').relative_to(ROOT));archived=[]
 for name in ['government-xl-caribbean-upward-return-seams-v2-20261025','government-xl-tuen-mun-private-seams-v1-20261025']:
  r,pins=authenticate(BASE/name);assert pins[oldkey]==digest(archive.read_bytes());archived.append(dict(batch=name,historicalExecutedPath=oldkey,archivedExecutionPath=str(archive.relative_to(ROOT)),sha256=pins[oldkey],currentPublicationAuthority=False))
 refs.extend([archive,HERE/'selected_original_seam_terrain_v2_20261025.py',HERE/'selected_original_minimal_seam_terrain_v1_20261025.py',HERE/'float32_native_seam_cover_v2_20261025.py',HERE/'bounded_original_ramp_return_v2_20261025.py'])
 result=dict(uids=['landsd/290981:0','landsd/95518:0','landsd/290803:0','landsd/34417:0','landsd/196123:0','landsd/200057:0','landsd/200059:0'],installedXL=376,unfinishedXL=145,totalFixedXL=521,currentNativeActors=6947,newlyInstalled=0,completed=completed,historicalExecutionArchives=archived,caribbeanState='privately-qualified-awaiting-guarded-live-installation',tuenMunState='held-for-compute',humanDecisionRequired=False,aiGeometryModellingRequired=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,remainingCaribbean=['Run guarded prepare-only and inspect result','Commit/push qualification before publication','Guarded install; inspect all8freshliveexports','Independent all6947oldassets/full521/globalBASIC/terrain readback','Refresh inventories; commit/push installation'],remainingTuenMun=['Preserve current ground under BASIC290801/290804; direct original-podium support probes failed','Verify new6074face seam candidate against all5sources with exactcoverage/continuous/foundation checks','Full unchanged native229481mesh regression, complete current identity and neighbour checks','Fresh source-role/browser review before guarded installation'],qualification='Checkpoint only. Exactsource original acquisition/derivedterrain computation; no optimisation, model geometry changes, permanent rejection or publication credit. Historical trial seam producer is archived and restored; final guarded recipes remain separate.')
 save(out/'remaining-work.json',result);module('caribbean_tuen_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-caribbean-tuen-mun-compute-progress-and-execution-archive-checkpoint',refs,result)
 print(dict(completed=len(completed),installedXL=376,unfinishedXL=145),flush=True)
if __name__=='__main__':main()
