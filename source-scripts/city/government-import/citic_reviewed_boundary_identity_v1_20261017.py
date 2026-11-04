"""Exact CITIC source-identity decision; all physical/publication checks remain separate."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
UID='landsd/232579:0'
SOURCE='a8058e18e0fbdfa4a38b10b9b58a5dea5d62ddf0debf76df1e39198a07969b74'
WORLD='7677711e4f9790a28e590fd718516436e5d08ba32e3158942d1235c03fb57078'
BASE=ROOT/'docs/astra-city/government-import'
REVIEW=BASE/'government-xl-citic-reviewed-boundary-identity-v1-20261017'
RAW_REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
POLICY='exact-citic-authored-rear-boundary-source-identity-v1'
def apply_review(raw,expected,decision):
 assert decision['identityOnlyApproved'] is True and decision['installationApproved'] is False
 assert decision['uid']==UID and decision['sourceSHA256']==SOURCE and decision['worldTrianglesSHA256']==WORLD
 assert raw==expected,'Fresh complete identity evidence changed; repeat source review'
 assert raw['uid']==UID and raw['sourceSHA256']==SOURCE and raw['worldTrianglesSHA256']==WORLD
 assert set(raw['reasons'])==RAW_REASONS
 assert raw['originalOwnership']['sourceGraphVerified']
 assert raw['originalOwnership']['originalRootName']=='B352651574402063C0'
 assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==1762
 fresh=raw['freshCurrentIdentity'];assert fresh['exactObjectAndCSUID']
 assert fresh['targetCoveredBySourceProjection']>=.95 and fresh['sourceExcessMaximumDistanceFromTargetM']<=10
 assert {x['uid'] for x in fresh['intersectingForms'] if not x['sameParent']}==set(decision['foreignUIDs'])
 out=deepcopy(raw)
 out.update(policy=POLICY,passed=True,reasons=[],rawIdentityVerbatim=deepcopy(raw),rawUnrelatedOverlapReasonsRetained=sorted(RAW_REASONS),sourceIdentityReviewUsedAI=True,identityDecision=deepcopy(decision),proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,modelGeometryChanges=0,qualification='Identity only for this exact unchanged complete source and captured current/provider neighbourhood. Authored rear roof/wall boundary overlap is retained, not removed or treated as common ownership. Original finite contacts remain explicit. No clearance, support, collision, terrain, runtime, browser or publication exemption; changed evidence requires a fresh review.')
 return out

def verify_files(row,context,local):
 result=read(REVIEW/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
 raw=raw_verify(row,context,local)
 return apply_review(raw,read(REVIEW/'expected-raw-identity.json'),read(REVIEW/'decision.json'))
