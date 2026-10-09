"""Production replay of the independently reviewed named relationship; identity only."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save
from southside_current_bound_identity_20261010 import verify_files,DOC as INPUT
DOC=ROOT/'docs/astra-city/government-import/government-xl-southside-current-bound-identity-promotion-20261010'
def main():
 assert not DOC.exists();row=read(INPUT/'selection.json.gz')['rows'][0];context=read(INPUT/'context.json.gz')['rows'][0];proof=verify_files(row,context,HERE/'local'/DOC.name)
 save(DOC/'identity-proof.json.gz',proof);save(DOC/'selection.json.gz',read(INPUT/'selection.json.gz'));save(DOC/'context.json.gz',read(INPUT/'context.json.gz'))
 (DOC/'README.md').write_text('Named mall-station identity-only production replay following independently reviewed kernel34 and bound-adapter21 actual-source tests. Preserves full11699/1191 originals,157 mall components, every34 raw overlap face and all current actors. MTR/owner corroborate direct connection; no common OP/legal ownership/per-face L1 attribution/support claim. Only the exact named station foreign-overlap reasons are replaced. Both current/provider95%coverage/10m extent/all other foreign bounds and raw whole-cell guards remain. No physical, terrain, runtime, browser, installation or AI geometry credit.\n')
 s=importlib.util.spec_from_file_location('southside_identity_promotion_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);paths=[Path(__file__),HERE/'southside_named_original_station_envelope_identity_20261010.py',HERE/'southside_current_bound_identity_20261010.py',HERE/'test_southside_named_original_station_envelope_identity_20261010.py',HERE/'test_southside_current_bound_identity_20261010.py',INPUT/'result.json',INPUT/'neon-sync.json'];m.freeze(DOC.name,'named-original-station-current-bound-identity-only-v1',paths,{'uids':['landsd/315025:0','landsd/300867:0'],'identityAccepted':proof['passed'],'physicalAccepted':False,'identityReasons':proof['reasons'],'completeOriginalFaces':[11699,1191],'rawRelatedStationOverlapRetained':proof['rawRelatedPodiumOverlapsRetained'],'allOtherCurrentActorsRetained':True,'remainingReason':'complete-original-source-current-terrain-support-runtime-and-browser-checks','sourceIdentityReviewUsedAI':True})
 print({'identityPassed':proof['passed'],'reasons':proof['reasons'],'physicalAccepted':False},flush=True)
if __name__=='__main__':main()
