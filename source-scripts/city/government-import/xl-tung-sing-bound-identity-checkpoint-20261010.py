"""Durable narrowly named current identity promotion; physical gates remain."""
import importlib.util
from run import ROOT,HERE,read,digest
BATCH='government-xl-tung-sing-current-bound-identity-promotion-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-lei-tung-original-source-relationship-20261010'
def main():
 proof=read(DOC/'identity-proof.json.gz');assert proof['passed'] and not proof['physicalAccepted'] and not proof['installationApproved']
 (DOC/'README.md').write_text('Named complete unchanged Tung Sing / Lei Tung original adjacent-envelope identity passes fresh full current replay. Housing Authority named Block E estate/key plans corroborate the mainbody relationship; no OP, legal ownership or load-bearing interpretation. All 65 raw overlap faces, all 365 source components, full 20.583241 m² overlap and every other actor remain. Original/root/BIN/all streams, current manifest/complete tiles/forms, native versions and primary raw/decoded responses independently replay. All 28 actual-source kernel and 19 current/provenance mutation tests pass. Identity only: complete paired terrain/support/foundation/neighbour/native/runtime/browser checks remain required. No geometry edits or installation credit.')
 s=importlib.util.spec_from_file_location('tung_sing_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 paths=[INPUT/'result.json']+[ROOT/r['path'] for r in read(INPUT/'result.json')['evidenceRefs']]+[Path(__file__)]+[HERE/q for q in ['tung_sing_current_bound_identity_20261010.py','test_tung_sing_current_bound_identity_20261010.py','xl-tung-sing-bound-current-identity-20261010.py']]
 m.freeze(BATCH,'named-complete-original-current-envelope-identity-v1',paths,{'uids':['landsd/53800:0','landsd/126434:0'],'identityAccepted':True,'physicalAccepted':False,'identityProof':proof,'kernelActualSourceTestsPassed':28,'adapterCounterexampleTestsPassed':19,'sourceIdentityReviewUsedAI':True,'remainingReason':'complete-original-pair-physical-support-foundation-neighbour-runtime-browser-gates-required'})
if __name__=='__main__':
 from pathlib import Path
 main()
