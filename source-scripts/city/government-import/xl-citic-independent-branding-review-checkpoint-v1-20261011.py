"""Preserve bounded primary-source signage review; unit70 stays unresolved."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-citic-independent-branding-review-checkpoint-v1-20261011'
REVIEW=BASE/'government-xl-citic-independent-source-role-review-v1-20261011'
def main():
 assert not(BASE/BATCH).exists()
 r=read(REVIEW/'review.json')
 assert r['outcome']=='seven-source-only-signage-representation-roles-supported-unit70-unresolved'
 assert not r['visualRoleAccepted']and not r['installationApproved']and not r['publication']and not r['aiGeometryModelling']
 refs=r['evidenceRefs']
 for p in refs:assert digest((ROOT/p['path']).read_bytes())==p['sha256']
 files=[ROOT/p['path']for p in refs]+[Path(__file__),REVIEW/'REVIEW.md',REVIEW/'review.json']
 spec=importlib.util.spec_from_file_location('citic_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 q=m.freeze(BATCH,'independent-primary-source-seven-signage-role-review-v1',files,dict(uids=r['uids'],sourceRoleEvidenceSupported=True,proposedSignageComponents=[34,29,39,36,35,33,40],unresolvedComponents=[70],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,terrainGeometryChanges=0,visualRoleAccepted=False,installationApproved=False,publication=False,qualification='Independent owner/contractor photo and complete source-facet review corroborates only the six exact logo/letter render components and one-face second-I lower-serif fragment. All failed facade mounts/open topology preserved. Unit70 unidentified; no attachment/grounding/bridge/current-F32/native/runtime/install credit.'))
 print(dict(jobId=q['jobId'],sourceRoleEvidenceOnly=True,unresolved=[70]),flush=True)
if __name__=='__main__':main()
