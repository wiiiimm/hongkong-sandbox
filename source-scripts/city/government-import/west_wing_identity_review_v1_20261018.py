"""Compose exact source interpretations over a fresh identity; physical gates remain."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-identity-review-v1-20261018';DOC=BASE/BATCH
NAMES={'current':'government-xl-west-wing-current-identity-v1-20261018','coverage':'government-xl-west-wing-park-coverage-review-v1-20261018','overlap':'government-xl-west-wing-overlap-role-review-v2-20261018','capture':'government-xl-west-wing-group-four-world-v1-20261018','pair':'government-xl-west-wing26195-neighbour319534-original-context-v1-20261015'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   folder=BASE/n;r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[k]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def checked(k,name):
  p=BASE/NAMES[k]/name;assert digest(p.read_bytes())==pins[k][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 raw=checked('current','identity.json');selection=checked('capture','selection.json.gz')['rows'];worlds=checked('capture','worlds.json.gz');coverage=checked('coverage','ROOT-COVERAGE-REVIEW.json');overlap=checked('overlap','ROOT-OVERLAP-REVIEW.json');pair=checked('pair','source-context.json')
 uid='landsd/26195:0';row=next(r for r in selection if r['uid']==uid);form=row['source']['building'];assert form==pair['currentForms'][uid]
 for proof in [coverage,overlap]:assert proof['uid']==uid and proof['sourceSHA256']==raw['sourceSHA256']==row['sourceSHA256']
 assert raw['sourceFormSHA256']==read(BASE/'government-xl-west-wing26195-typed-extent-review-v1-20261015/identity-extent-only.json')['sourceFormSHA256']
 extent=BASE/'government-xl-west-wing26195-typed-extent-review-v1-20261015';ctx=BASE/'government-xl-west-wing26195-extent-face-context-v1-20261015/context.json'
 # Re-execute the existing narrow extent interpretation against today's full source.
 code=HERE/'west_wing26195_typed_extent_review_v1_20261015.py';inter=read(extent/'interpretation.json');context=read(ctx)
 result=module('west_recompose_extent',code).compose(raw,np.asarray(worlds['original'][uid],dtype='<f8'),form,context,inter)
 expected={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','full-source-unrelated-overlap'}
 assert set(result['reasons'])==expected
 assert coverage['coverageInterpretationAccepted'] and coverage['accounting']['buildingScopeCoverage']>=.95 and overlap['overlapSourceScopeAccepted']
 fresh=raw['freshCurrentIdentity']['intersectingForms'];actual={f['uid'] for f in fresh if not f['sameParent'] and f['uid']!=uid};assert actual=={r['uid'] for r in overlap['rows']}
 for r in overlap['rows']:
  source=next(s for s in selection if s['uid']==r['uid']);assert source['sourceSHA256']==r['sourceSHA256']
  f=next(f for f in fresh if f['uid']==r['uid']);assert abs(f['intersectionAreaM2']-r['originalWestWingProjectedOverlap']['sourceIntersectionArea'])<1e-9
 assert coverage['rawCoverageRetained']['sourceSHA256']==raw['sourceSHA256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==raw['exactRouteManifestSHA256'];refs.append(manifest)
 for tile,h in raw['exactRouteTileHashes'].items():
  p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==h;refs.append(p)
 sources={r['uid']:r['sourceSHA256'] for r in selection}
 # All four original sources used for the saved residual remain byte-identical.
 assembly=BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015/projection.json'
 for r in read(assembly)['rows']:assert sources[r['uid']]==r['sourceSHA256']
 review=dict(uid=uid,sourceSHA256=raw['sourceSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],manifestSHA256=raw['exactRouteManifestSHA256'],tileHashes=raw['exactRouteTileHashes'],identityAccepted=True,installationApproved=False,physicalAccepted=False,rawAutomaticReasons=raw['reasons'],rawIdentity=raw,extentReview=inter,coverageReview=coverage,overlapReview=overlap,requiredAssemblyOriginals={'landsd/322270:0':sources['landsd/322270:0']},sourceSHA256ByUid=sources,sourceGeometryChanges=0,usesAISourceInterpretation=True,aiGeometryModelling=False,qualification='Exact current source-specific identity scope only. Coverage depends on the unchanged CGO original in the assembly and the reviewed park-space exclusion. All original physical, support, terrain, neighbour, runtime and browser checks remain mandatory. No general threshold changed.')
 save(DOC/'ROOT-IDENTITY-REVIEW.json',review);refs.extend([code,ctx,extent/'interpretation.json',extent/'identity-extent-only.json',assembly])
 out=module('west_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-exact-current-source-specific-identity-review-v1',refs,dict(uids=[uid],identityAccepted=True,publication=False,physicalAccepted=False,requiredAssemblyOriginals=review['requiredAssemblyOriginals'],sourceGeometryChanges=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
