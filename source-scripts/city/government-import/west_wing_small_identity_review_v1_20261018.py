"""Source-specific review of complete 34-face original; no geometry correction."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-small-identity-review-v1-20261018';DOC=BASE/BATCH
SRC=BASE/'government-xl-west-wing-other-original-identities-v1-20261018';CTX=BASE/'government-xl-west-wing-companion-extent-context-v1-20261018';UID='landsd/319534:0';SHA='6f085985d3ea19699c010d73d173d288107c3d3eea372bf5704a854bd2b1e2c1'
def compose(raw,context):
 assert raw['uid']==context['uid']==UID and raw['sourceSHA256']==context['sourceSHA256']==SHA
 assert raw['worldTrianglesSHA256']==context['worldSHA256']
 assert raw['originalOwnership']['sourceGraphVerified'] and raw['freshCurrentIdentity']['exactObjectAndCSUID']
 assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==34
 assert raw['geographicCell']['targetCoversWholeCell'] and context['completeFaceCount']==34
 assert context['completeOver10mFaceIds']==[]
 assert context['missingTargetAreaM2']==1.210920606910232 and context['excessSourceAreaM2']==0.5098385543592068
 assert raw['freshCurrentIdentity']['unrelatedIntersectingForms']==0
 accounted={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
 out=deepcopy(raw);out['rawIdentityRetained']=deepcopy(raw);out['reasons']=[r for r in raw['reasons']if r not in accounted];out['passed']=not out['reasons'];out.update(installationApproved=False,physicalAccepted=False,sourceGeometryChanges=0,narrowlyAccountedReasonKeys=sorted(accounted),sourceInterpretation=dict(reviewer='Codex ROOT',usesAISourceInterpretation=True,aiGeometryModelling=False,scope='Exact original 34-face source coverage only',basis='Inspected complete plan and 3D source diagnostic. The polygon residual is a narrow boundary strip around the same small rectangular vertical structure, not an absent building wing. Exact object/CSUID, source graph and shared full georeference cell independently agree. Keep the complete authored source at its original placement; no footprint stretching, inferred new geometry or landmark naming. This source-specific acceptance does not lower the general coverage threshold.',contextSHA256=digest((CTX/'319534:0.json').read_bytes()),imageSHA256=digest((CTX/'319534:0.png').read_bytes())))
 return out
assert not DOC.exists();refs=[Path(__file__)]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,CTX]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
raw=read(SRC/'319534:0/identity.json');context=read(CTX/'319534:0.json');out=compose(raw,context);assert out['passed']
checks=[]
for key,value in [('sourceSHA256','wrong'),('worldTrianglesSHA256','wrong'),('uid','landsd/other:0')]:
 bad=deepcopy(raw);bad[key]=value
 try:compose(bad,context)
 except AssertionError:checks.append(dict(field=key,rejected=True))
 else:raise AssertionError(key)
bad=deepcopy(raw);bad['reasons'].append('independent-failure');assert not compose(bad,context)['passed'];checks.append(dict(independentFailureRetained=True))
save(DOC/'ROOT-IDENTITY-REVIEW.json',out);save(DOC/'checks.json',checks)
refs.extend([SRC/'319534:0/identity.json',CTX/'319534:0.json',CTX/'319534:0.png'])
r=module('small_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-small-original-coverage-review',list(dict.fromkeys(refs)),dict(uids=[UID],identityAccepted=True,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
