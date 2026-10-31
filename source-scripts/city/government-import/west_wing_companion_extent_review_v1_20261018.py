"""Review two exact low source extensions; preserve unrelated overlap failures."""
from copy import deepcopy
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-west-wing-other-original-identities-v1-20261018';CTX=BASE/'government-xl-west-wing-companion-extent-context-v1-20261018';PLAN=BASE/'government-xl-west-wing26195-architect-site-plan-v1-20261015';BATCH='government-xl-west-wing-companion-extent-review-v1-20261018';DOC=BASE/BATCH
SPEC={'landsd/322270:0':('b1ce8e22f43eb51bda3d6728c74b6e43fa0511e223fc42ed2fd078c8c89254ef',34,'Low bent site-access extension attached to the CGO perimeter, distinct from the main office tower.'),'landsd/315069:0':('60bb7de8a73b979d1a9cc3d337db904a1975c9da27c791e17ceae4550dcc6118',49,'Low eastern perimeter and approach structure alongside the Legislative Council complex, extending past the circular chamber footprint.')}
KEYS={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
def compose(raw,ctx,tri):
 uid=raw['uid'];sha,count,role=SPEC[uid];assert raw['sourceSHA256']==ctx['sourceSHA256']==sha and ctx['uid']==uid
 assert digest(tri.tobytes())==ctx['worldSHA256']==raw['worldTrianglesSHA256'];assert raw['originalOwnership']['sourceGraphVerified'] and raw['freshCurrentIdentity']['exactObjectAndCSUID'] and raw['exactWholeCellCoverage']['covered'] and raw['geographicCell']['targetCoversWholeCell']
 faces=ctx['completeOver10mFaceIds'];assert len(faces)==count and np.array_equal(tri[faces],ctx['farFaceTriangles']);assert raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==len(tri)==ctx['completeFaceCount']
 out=deepcopy(raw);out['rawIdentityRetained']=deepcopy(raw);out['reasons']=[x for x in raw['reasons']if x not in KEYS];out['passed']=not out['reasons'];out.update(narrowlyAccountedReasonKeys=sorted(KEYS),installationApproved=False,physicalAccepted=False,sourceGeometryChanges=0,sourceInterpretation=dict(reviewer='Codex ROOT',usesAISourceInterpretation=True,aiGeometryModelling=False,scope='Exact source extent only',role=role,sourceFaceIds=faces,worldSHA256=ctx['worldSHA256'],basis='ROOT inspected complete original plan/3D source diagrams and the retained architect site plan. These low authored site-edge structures belong to the complete government source rather than a second displaced tower. The plan supports the site approach/perimeter interpretation, not survey-precise alignment or legal ownership. No clipping, relocation, scale change or global extent allowance. All raw overlap and physical findings remain in force.'))
 return out
assert not DOC.exists();refs=[Path(__file__),PLAN/'site-plan.jpg',PLAN/'provenance.json'];rows=read(SRC/'selection.json.gz')['rows']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,CTX]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
summary=[]
for uid in SPEC:
 key=uid.split('/')[1];row=next(r for r in rows if r['uid']==uid);raw=read(SRC/key/'identity.json');ctx=read(CTX/(key+'.json'));asset=(ROOT/row['candidate']['path']).read_bytes();assert digest(asset)==SPEC[uid][0];tri=np.asarray(decode_original_world_triangles(asset),dtype='<f8');out=compose(raw,ctx,tri)
 checks=[]
 for field in ['sourceSHA256','worldTrianglesSHA256']:
  bad=deepcopy(raw);bad[field]='wrong'
  try:compose(bad,ctx,tri)
  except AssertionError:checks.append(dict(field=field,rejected=True))
  else:raise AssertionError(field)
 bad=deepcopy(ctx);bad['completeOver10mFaceIds'].pop()
 try:compose(raw,bad,tri)
 except AssertionError:checks.append(dict(omittedFaceRejected=True))
 else:raise AssertionError('omitted-face')
 bad=deepcopy(raw);bad['reasons'].append('independent-failure');assert 'independent-failure'in compose(bad,ctx,tri)['reasons'];checks.append(dict(independentFailureRetained=True))
 save(DOC/(key+'.json'),out);save(DOC/(key+'-checks.json'),checks);refs.extend([SRC/key/'identity.json',CTX/(key+'.json'),CTX/(key+'.png')]);summary.append(dict(uid=uid,identityAccepted=out['passed'],remainingReasons=out['reasons']))
assert summary[0]['remainingReasons']==['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'];assert summary[1]['identityAccepted']
save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
r=module('companion_extent_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-exact-original-site-extension-reviews',list(dict.fromkeys(refs)),dict(uids=list(SPEC),rows=summary,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
