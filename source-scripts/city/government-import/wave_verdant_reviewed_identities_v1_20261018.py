"""Exact two-source identity review adapter; physical/publication gates are independent."""
from copy import deepcopy
from run import ROOT,read,digest,connect
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
REVIEW=ROOT/'docs/astra-city/government-import/government-xl-wave-verdant-remaining-reviewed-identities-v1-20261018'
SOURCES={'landsd/304885:0':'448a02ec87fa8e83212a654f9734de7e2681b5ab90747fc1d0129664c411eed1','landsd/301562:0':'8326b663b61047b8728c2fa49550b0ab26b48868a05b8b2588db33004acf1959'}
def apply_review(raw,decision):
 uid=raw['uid'];assert uid in SOURCES and decision['uid']==uid and raw==decision['rawProof'],'Fresh identity differs from reviewed evidence'
 assert raw['sourceSHA256']==decision['sourceSHA256']==SOURCES[uid]
 for key in ['sourceFormSHA256','worldTrianglesSHA256']:assert raw[key]==decision[key]
 assert decision['identityOnlyApproved']is True and decision['installationApproved']is False and decision['fullAcceptance']is False
 assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']==decision['modelId']
 assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid']==uid
 assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==decision['sourceFaces'] and raw['geographicCell']['targetCoversWholeCell']
 out=deepcopy(raw);out.update(policy='exact-reviewed-wave-verdant-source-identity-v1',passed=True,reasons=[],rawIdentityVerbatim=deepcopy(raw),identityDecision=deepcopy(decision),proof=deepcopy(decision['identityProof']),sourceIdentityReviewUsedAI=True,physicalAccepted=False,installationApproved=False,modelGeometryChanges=0)
 return out

def verify_files(row,context,local):
 r=read(REVIEW/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 decision=read(REVIEW/(row['uid'].replace('/','-').replace(':','-')+'-review.json'))
 return apply_review(raw_verify(row,context,local),decision)
