"""Apply only the exact reviewed Verdant companion identity; never physical approval."""
from copy import deepcopy
from run import ROOT,read,digest,connect
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
UID='landsd/194544:0'
SHA='e3fafc04919ee3527766ad9c9b7b6abb11bc8866de3a1e9a89006fbea80d94c1'
REVIEW=ROOT/'docs/astra-city/government-import/government-xl-verdant194544-reviewed-identity-v1-20261018'
REASONS={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
def apply_review(raw,expected,decision):
 assert raw==expected,'Fresh identity evidence changed; repeat source-specific review'
 assert raw['uid']==decision['uid']==UID and raw['sourceSHA256']==decision['sourceSHA256']==SHA
 for key in ['sourceFormSHA256','worldTrianglesSHA256']:assert raw[key]==decision[key]
 assert decision['identityOnlyApproved']is True and decision['installationApproved']is False and decision['fullAcceptance']is False
 assert set(raw['reasons'])==REASONS
 assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']=='B161692660501062G0'
 assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid']==UID
 assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==42 and raw['geographicCell']['targetCoversWholeCell']
 out=deepcopy(raw);out.update(policy='exact-reviewed-verdant194544-boundary-identity-v1',passed=True,reasons=[],rawIdentityVerbatim=deepcopy(raw),identityDecision=deepcopy(decision),proof=deepcopy(decision['identityProof']),sourceIdentityReviewUsedAI=True,physicalAccepted=False,installationApproved=False,modelGeometryChanges=0,qualification='Exact source/form/world-specific identity only. Raw automatic coverage failures retained. All placement, support, collision, terrain, neighbours, runtime and publication gates remain. Changed current evidence requires a fresh review.')
 return out

def verify_files(row,context,local):
 r=read(REVIEW/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 return apply_review(raw_verify(row,context,local),read(REVIEW/'expected-raw-identity.json'),read(REVIEW/'identity-review.json'))
