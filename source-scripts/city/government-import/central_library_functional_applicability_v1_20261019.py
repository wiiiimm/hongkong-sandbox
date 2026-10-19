"""Exact original-library column termination interpretation; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-library-functional-applicability-v1-20261019';DOC=BASE/BATCH;UID='landsd/232240:0'
def folder(s):return BASE/('government-xl-central-library-'+s+'-20261019')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();names=['private-ground-v1','neighbours-v1','four-mode-foundations-v2','loader-identity-v1','podium-identity-review-v1','full-grade-context-v1','original-grade-comparison-v1','grade-views-v2'];pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   d=folder(name);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(folder('private-ground-v1')/'selection.json.gz')['rows'][0];sha=row['sourceSHA256'];assert row['uid']==UID and sha=='d33beb18ab1ecd41bf45e2c0d36424173d0b2f6e4cf4e5f48ca563f8837b95da'
 identity=read(folder('podium-identity-review-v1')/'232240:0-review.json');assert identity['identityOnlyApproved'] and identity['sourceSHA256']==sha
 ids=list(range(23745,23785))+list(range(24432,24436))+list(range(26765,26805))+list(range(27111,27115));assert len(ids)==88
 bindings=[]
 for mode,fmode in [('original','original'),('literal','literal'),('left','explicitLeftF32'),('balanced','explicitBalancedF32')]:
  g=read(folder('full-grade-context-v1')/('232240:0-'+mode+'.json.gz'));cmp=read(folder('original-grade-comparison-v1')/(mode+'.json.gz'));f=read(folder('four-mode-foundations-v2')/('232240:0-'+fmode+'.json'))
  assert g['wholeSourceFaces']==cmp['wholeSourceFaces']==f['foundation']['completeTerrainTriangles']==33081
  assert g['continuousNegativeFaceIds']==ids and not g['negativeUpwardFaceIds'] and not g['negativeWithoutExposedWitness'] and not g['uncoveredFaces']
  assert cmp['allVertical'] and cmp['allOriginalCovered'] and cmp['allOriginalHaveExposedWitness'] and cmp['failedFaces']==88
  assert cmp['maximumMinimumGapDifferenceM']<.000001
  assert cmp['wholeWorldSHA256']==g['completeWorldSHA256']==f['wholeWorldSHA256']
  assert f['strictFoundationAccepted'] and f['foundation']['fullyBuriedTriangles']==0
  bindings.append(dict(uid=UID,mode=fmode,sourceSHA256=sha,wholeWorldSHA256=f['wholeWorldSHA256'],completeFaces=33081))
 validation=read(folder('loader-identity-v1')/'validation.json');assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0;assert not any(r.get('concerns')for r in validation['results'])
 metrics=read(folder('private-ground-v1')/'metrics.json');m=metrics['rows'][0];assert m['sourcePreserved']and not m['missingTerrain']and m['maxSamplerDelta']==0
 policy=module('central_library_functional_policy',HERE/'acceptance-policy.py');raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sha,identityProof=identity['identityProof']),m,metrics['profiles']['mobile']);assert raw==['terrain-intersects-source-over-0.5m']
 native=read(folder('neighbours-v1')/'native-neighbour-checks.json');assert not set(native['blocked'])-set(native['resolved']);assert len(native['rows'])==1 and native['rows'][0]['uid']=='landsd/227428:0' and native['rows'][0]['passed'];assert native['rows'][0]['terrain']['newlyWhollyBuried']==0
 near=read(folder('neighbours-v1')/'neighbour-checks.json');flagged=[r for r in near['rows']if r['reasons']];assert len(flagged)==1 and flagged[0]['uid']=='landsd/227428:0' and flagged[0]['existingNative'];assert set(flagged[0]['reasons'])=={'existing-native-neighbour-requires-full-mesh-check','increased-neighbour-ground-gap'}
 images=[folder('grade-views-v2')/(n+'.png')for n in ['grade-side','grade-reverse']]+[folder('original-grade-comparison-v1')/(n+'.png')for n in ['podium-grade','grade-close']]
 review=dict(reviewer='Codex ROOT',uid=UID,sourceSHA256=sha,sourceSpecificGradeInterpretationAccepted=True,sourceFaces=ids,sourceBindings=bindings,imagesActuallyInspected=[ref(p)for p in images],rawPolicyReasons=raw,rawNumericMetrics=m,strictTerrainIntersectionCheckPassed=False,observations=[
 'ROOT inspected the four exported source-grade views. The reverse side view highlights the exact88vertical faces in red: two round columns descending below the original side walkway. The side view is partly occluded and is not sole evidence; the reverse exposes both column sides.',
 'Complete33081face continuous ground analysis in allfour coordinate modes finds precisely these88negative faces, no negative upward faces, no uncovered face, and exposed portions on every flagged face. Allfour complete foundation checks have zero wholly buried triangles.',
 'The negative clearance already exists against the complete authentic government terrain. The candidate reproduces its minima within0.000001m. Interpret this exact source-authored lower column termination as retained original geometry, not a newly displaced floor or missing terrain. The raw approximately0.570064m penetration remains failed under the0.5m numeric check; this decision is restricted to these88faces and exact source/terrain/world bindings.',
 'The only BASIC neighbour flags concern the already installed main library227428, whose coarse footprint uses base12.1m instead of its full original geometry. The complete145359face native before/after test passes with no newly wholly buried face. Its full native result supersedes the coarse proxy ground-gap flags; all other38forms have no flags.'
 ],modelGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,installationApproved=False)
 save(DOC/'ROOT-GRADE-REVIEW.json',review)
 qualification=dict(uids=[UID],sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,rawPolicyReasons=raw,resolvedByExactSourceFunctionalApplicability=raw,remainingPhysicalReasons=[],identityReview=ref(folder('podium-identity-review-v1')/'232240:0-review.json'),gradeReview=ref(DOC/'ROOT-GRADE-REVIEW.json'),rawNativeProxyFlags=flagged,completeNativeCheck=native['rows'][0],completeLoaderPickingCollisionPassed=True,completeNeighboursPassed=True,sourceGeometryChanges=0,publication=False,installationApproved=False,stagedLiveBrowserStillRequired=True)
 save(DOC/'qualification.json',qualification)
 refs.append(HERE/'acceptance-policy.py')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('central_library_functional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'central-library-exact-original-column-termination-applicability',list(dict.fromkeys(refs)),dict(uids=[UID],sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
