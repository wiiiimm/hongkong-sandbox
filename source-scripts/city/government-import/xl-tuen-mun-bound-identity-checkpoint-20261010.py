"""Freeze replayed Special Block identity; every physical gate stays pending."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,digest
from tuen_mun_current_bound_identity_20261010 import DOC as INPUT,verify_files
BATCH='government-xl-tuen-mun-bound-current-identity-promotion-20261010';DOC=INPUT.parent/BATCH
def main():
 x=read(DOC/'identity-proof.json.gz');row=read(DOC/'selection.json.gz')['rows'][0];ctx=read(DOC/'context.json.gz')['rows'][0]
 assert verify_files(row,ctx,HERE/'local'/BATCH/'independent-frozen-replay')==x and x['passed'] and not x['physicalAccepted'] and not x['installationApproved']
 refs=read(INPUT/'result.json')['evidenceRefs']
 for r in refs:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 (DOC/'README.md').write_text('''# Tuen Mun Hospital Special Block exact source identity

The untouched18,759-face Special Block and exact13,121-face Main Block podium
have80positive original interfaces involving174original excess faces. The
unique Active primary stable identifiers, dated original sources and reviewed
official HA introduction/LegCo site plan corroborate this one named relation.
The not-to-scale plan is not used for coordinates, legal certification, geometry
modification or load-bearing proof. No common occupation permit is invented.

Current/primary own whole-source coverage, all original vertices, every other
foreign actor and both complete geographic-cell checks pass. Only the two
specific raw foreign-related-podium identity reasons are interpreted. Both
exact native-run members and source versions, all packed source streams/root/
world geometry, new primary response/request bytes, every current actor/tile,
current manifest and complete owner provenance/Neon receipt are replayed.
42meaningful actual source/input mutation tests pass (28named,14binding).

All130 Special Block source components remain. This identity grants no supporting
podium import, foundation, terrain, collision, runtime, browser or installation
credit. The raw podium-alone75%coverage remains; a separate original seven-actor
collection diagnostic explains most holes and reports99.3%combined coverage,
without filling holes or granting common-site acceptance. Current physical
support and every remaining source component must still be processed.
''')
 s=importlib.util.spec_from_file_location('hospital_identity_promotion_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'named-exact-original-hospital-owner-source-current-bound-identity-v1',[ROOT/r['path'] for r in refs]+[INPUT/'result.json',INPUT/'neon-sync.json',Path(__file__)],dict(uids=[row['uid']],identityAccepted=True,identityProof=x,sourceIdentityReviewUsedAI=True,scriptFullAcceptancePassed=False,actualSourceCounterexampleTests=42,requiresAIModelGeometry=False,requiresHumanDecision=False,remainingReason='complete-current-original-support-foundation-runtime-gates-pending',nextStep='Continue full source-local/current physical terrain/foundation/foreign/runtime and complete original component accounting. Supporting podium and other towers remain independently unaccepted; no source geometry edits.'))
 print(json.dumps(dict(identityAccepted=True,physicalAccepted=False,installationApproved=False)),flush=True)
if __name__=='__main__':main()
