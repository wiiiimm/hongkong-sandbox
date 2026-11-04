"""Fence reviewed exact Yoho identity promotion; physical gates stay pending."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
from yoho_eight_current_bound_identity_20261009 import DOC as INPUT,verify_files
BATCH='government-xl-yoho-eight-current-bound-identity-promotion-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 x=read(DOC/'identity-proof.json.gz');row=read(DOC/'selection.json.gz')['rows'][0];ctx=read(DOC/'context.json.gz')['rows'][0]
 assert verify_files(row,ctx,HERE/'local'/BATCH/'independent-frozen-replay')==x and x['passed'] and not x['physicalAccepted'] and not x['installationApproved']
 refs=read(INPUT/'result.json')['evidenceRefs'];paths=[ROOT/r['path'] for r in refs]+[INPUT/'result.json',INPUT/'neon-sync.json',Path(__file__),HERE/'test_yoho_eight_current_bound_identity_20261009.py']
 for r in refs:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 (DOC/'README.md').write_text('''# Yoho Town Block8 exact related-podium identity promotion

Fresh bound production identity passes on unchanged14792-face Tower8 and its
7731-face original podium. The unique Active primary stable identifiers, dated
source models, distinct Tower5285253/Podium5285219 under NT21/2004(OP), and42
positive exact source line interfaces establish this narrowly named relationship.
Both whole1m GeoRef-cell checks remain intact. Complete current and primary
target coverage are95.1674%/95.1695%, maximum full original extent2.14107/2.14045m;
all other current actors contribute zero excess overlap. Raw8.87749m² related
podium overlap and353.98239m² primary footprint outside the carved podium remain
recorded; the podium hole is never filled. Current/provider OBJECTID revisions
are recorded without changing viewer metadata.

Every frozen input SHA and completed Neon receipt is replayed, both native cache
versions are checked, complete source compressed/decompressed/BIN/all-buffer-view
root/world pins remain exact, all current forms/tiles are reloaded, three exact
government query receipts are checked, and the ordinary raw full-cell identity
check is recomputed. Only the two specifically named foreign-podium overlap
reasons are interpreted.49 actual-source/input positive/counterexample tests
pass (30 named kernel,19 adapter); parent independently passed the30 kernel tests.

All953 original components and143 detached parts remain. Identity does not grant
support through the absent original podium, functional labels for detached parts,
collision/terrain exemptions for the current podium, runtime/browser approval,
source or current actor edits, suppression, or installation. Next work checks
actual current drawn podium/ground and complete original source physical roles.
''')
 s=importlib.util.spec_from_file_location('yoho_identity_promotion_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'named-exact-original-tower-related-primary-op-podium-bound-identity-v1',paths,{'uids':[row['uid']],'identityAccepted':True,'sourceIdentityReviewUsedAI':True,'identityProof':x,'scriptFullAcceptancePassed':False,'actualSourceCounterexampleTests':49,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'complete-current-supported-podium-and-detached-source-surface-physical-runtime-gates-pending','nextStep':'Resolve actual current drawn-ground support and complete original source component roles; retain actual related podium collision/runtime and every foreign actor. No absent original support credit.'})
if __name__=='__main__':main()
