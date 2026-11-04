"""Complete exact CGO source identity after reviewing two ancillary boundary interfaces."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-cgo-identity-review-v1-20261018';DOC=BASE/BATCH;EXT=BASE/'government-xl-west-wing-companion-extent-review-v1-20261018';CTX=BASE/'government-xl-west-wing-cgo-overlap-context-v1-20261018'
assert not DOC.exists();refs=[Path(__file__)]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [EXT,CTX]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
raw=read(EXT/'322270:0.json');ctx=read(CTX/'context.json');keys={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def compose(raw,ctx):
 assert raw['uid']==ctx['uid']=='landsd/322270:0' and raw['sourceSHA256']==ctx['sourceSHA256']=='b1ce8e22f43eb51bda3d6728c74b6e43fa0511e223fc42ed2fd078c8c89254ef' and raw['worldTrianglesSHA256']==ctx['worldSHA256']
 assert [r['uid']for r in ctx['rows']]==['landsd/315069:0','landsd/320038:0'];assert [len(r['sourceFaceIds'])for r in ctx['rows']]==[8,33]
 assert raw['freshCurrentIdentity']['unrelatedIntersectingForms']==2
 for row in ctx['rows']:
  expected=next(r for r in raw['freshCurrentIdentity']['intersectingForms']if r['uid']==row['uid']);assert expected['sourceFaceCount']==len(row['sourceFaceIds']);assert abs(expected['intersectionAreaM2']-row['intersectionAreaM2'])<1e-8
 out=deepcopy(raw);out['extentReviewedIdentityRetained']=deepcopy(raw);out['reasons']=[r for r in raw['reasons']if r not in keys];out['passed']=not out['reasons'];out.update(identityAccepted=out['passed'],physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,overlapSourceInterpretation=dict(reviewer='Codex ROOT',usesAISourceInterpretation=True,aiGeometryModelling=False,exactContextSHA256=digest((CTX/'context.json').read_bytes()),rows=ctx['rows'],accountedReasonKeys=sorted(keys),basis='ROOT inspected both exact complete-face diagrams against current neighbour footprints. The eight LegCo-intersecting faces are ends of low perimeter/access structures; the 33 Chief Executive Office-intersecting faces form the low connecting approach at its footprint edge. These are authored site interfaces, not a second misplaced tower. Complete original graph ownership, exact object/CSUID and georeference-cell proofs remain bound by the raw review. Retain all measured intersections. No physical collision exemption, geometric tolerance change, ownership claim or geometry edit.'))
 return out
out=compose(raw,ctx);assert out['passed'];checks=[]
for key in ['sourceSHA256','worldTrianglesSHA256']:
 bad=deepcopy(raw);bad[key]='wrong'
 try:compose(bad,ctx)
 except AssertionError:checks.append(dict(field=key,rejected=True))
 else:raise AssertionError(key)
bad=deepcopy(ctx);bad['rows'][0]['sourceFaceIds'].pop()
try:compose(raw,bad)
except AssertionError:checks.append(dict(omittedFaceRejected=True))
else:raise AssertionError('face')
bad=deepcopy(raw);bad['reasons'].append('independent-failure');assert not compose(bad,ctx)['passed'];checks.append(dict(independentFailureRetained=True))
save(DOC/'ROOT-IDENTITY-REVIEW.json',out);save(DOC/'checks.json',checks);refs.extend([EXT/'322270:0.json',CTX/'context.json',CTX/'315069:0.png',CTX/'320038:0.png'])
r=module('cgo_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-cgo-ancillary-interface-identity-review',list(dict.fromkeys(refs)),dict(uids=['landsd/322270:0'],identityAccepted=True,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
