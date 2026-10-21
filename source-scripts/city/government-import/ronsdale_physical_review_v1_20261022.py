"""Record the bounded review of Ronsdale's unchanged original wall-ground relationship."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-physical-review-v1-20261022';DOC=BASE/BATCH
UID='landsd/233771:0';SOURCE='aede65daf536737fb2b8f8d9d3073647933ff54ee454bb8e6a0c5cc076ce0ff4'
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def doc(n,f):return take(n,BASE/n/f)
 runtime='government-xl-ronsdale-inset-runtime-v1-20261022';selection=doc(runtime,'selection.json.gz');metrics=doc(runtime,'metrics.json');assert len(selection['rows'])==len(metrics['rows'])==1
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 identity=doc('government-xl-remaining-forty-podium-identity-v1-20261021','233771:0/identity.json');assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256']==SOURCE
 for p,h in identity['exactRouteTileHashes'].items():assert digest((ROOT/'3d-viewer'/p).read_bytes())==h;refs.append(ROOT/'3d-viewer'/p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
 policy=module('ronsdale_review_policy',HERE/'acceptance-policy.py');metric=metrics['rows'][0];assert metric['uid']==UID and metric['sourceSHA256']==SOURCE
 raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),metric,metrics['profiles']['mobile']);assert raw==['terrain-intersects-source-over-0.5m'],raw
 sn='government-xl-ronsdale-clearance-attribution-v1-20261022';context=doc(sn,'context.json');assert context['failedSamples']==context['failedFaces']==context['failedCentroids']==1 and context['maximumAbsoluteRenderedOriginalGroundDeltaM']==0
 face=context['faces'][0];assert face['faceIndex']==1332 and face['normalisedVertical']==0 and face['vertices'][0][1]-face['vertices'][1][1]>17
 n='government-xl-ronsdale-four-world-foundations-v1-20261022';foundations=doc(n,'summary.json')['rows'];assert len(foundations)==4
 worlds=[doc(n,mode+'.json') for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']];assert len({r['sourceWorldSHA256']for r in worlds})==1
 for r in foundations:assert r['triangles']==r['completeTerrainTriangles']==2438 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0
 profile=doc('government-xl-ronsdale-wall-profile-v1-20261022','profile.json')['summary'];assert profile['sourceSHA256']==SOURCE and profile['faceIndex']==1332
 images=[];n='government-xl-ronsdale-wall-context-view-v2-20261022'
 for name in ['source-context.png','wall-profile.png']:
  p=BASE/n/name;take(n,p) if p.suffix=='.json' else None
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  h=cache[n][str(p.relative_to(ROOT))];assert digest(p.read_bytes())==h;refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=h))
 terrain=doc('government-xl-ronsdale-local-inset-v1-20261022','terrain-candidates.json');assert doc('government-xl-ronsdale-local-inset-v1-20261022','summary.json')['terrainValidationPassed']
 review=dict(uids=[UID],sourceSHA256ByUid={UID:SOURCE},reviewer='Codex ROOT',sourceSpecificPhysicalInterpretationAccepted=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,rawPolicyReasons=[dict(uid=UID,reasons=raw)],rawCanonicalFailuresPreserved=True,imagesActuallyViewed=images,terrainCandidates=terrain,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publicationApproved=False,basis='The one failing centroid belongs to the exact original vertical face1332, a 17.13m-tall, 12.63m2 triangular wall. Authenticated original government ground reproduces the failed centroid exactly; the private repair introduces zero height difference there. The full original and all three renderer representations are byte-identical world triangles, cover all2438faces and retain zero fully buried faces. The source-context and wall-profile exports were inspected: original terrain intersects a lower part of this vertical wall while its upper end remains exposed. This exact source-authored wall-ground relationship is accepted for viewer placement. The raw -2.387710m centroid and0.5m canonical threshold remain recorded.',scope='Only this exact original source, face1332 and validated private terrain. Complete form/native-neighbour, tower-support, browser, collision/picking/recovery and guarded publication are separate requirements.')
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review);refs.append(HERE/'acceptance-policy.py');module('ronsdale_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-specific-original-wall-ground-interpretation',refs,review)
if __name__=='__main__':main()
