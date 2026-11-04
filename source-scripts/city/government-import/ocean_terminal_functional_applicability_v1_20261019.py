"""Exact original Ocean Terminal applicability; raw failures remain recorded."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-functional-applicability-v1-20261019';DOC=BASE/BATCH
UID='landsd/205767:0';SHA='2fbf7665466f9cd015b00d263913002e3de6dc268d9c590f9815853d182eea89';MODES={'original','literal','explicitLeftF32','explicitBalancedF32'}
def folder(name):return BASE/('government-xl-ocean-terminal-'+name+'-20261019')
def inputs():
 cap=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018'
 return dict(decision=read(folder('source-relationship-review-v1')/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json'),identity=read(folder('identity-review-v1')/'205767:0-review.json'),foundations=[read(folder('four-mode-foundations-v1')/('205767:0-'+m+'.json'))for m in sorted(MODES)],scope=read(folder('current-scope-v1')/'scope.json'),equivalence=read(folder('retained-parent-equivalence-v1')/'equivalence.json'),sampler=read(folder('retained-sampler-v1')/'sampler.json'),neighbours=read(folder('current-neighbours-v1')/'summary.json'),validation=read(folder('ordinary-validation-v2')/'validation.json'),metric=read(cap/'metrics.json')['rows'][0],low=read(folder('low-rim-ground-attribution-v1')/'attribution.json'),burial=read(folder('original-ground-attribution-v1')/'attribution.json'))
def qualify(decision,identity,foundations,scope,equivalence,sampler,neighbours,validation,metric,low,burial):
 assert decision['uid']==identity['uid']==metric['uid']==UID
 assert decision['sourceSHA256']==identity['sourceSHA256']==metric['sourceSHA256']==SHA
 assert identity['identityOnlyApproved'] and identity['identityProof']['identityAccepted']
 assert decision['reviewer']=='Codex ROOT' and decision['originalSurveyedRelationshipAccepted'] and not decision['installationApproved'] and not decision['publicationApproved']
 assert decision['rawStrictGroundContactPassed'] is False and decision['rawStrictFoundationPassed'] is False and decision['geometryOrPoseChanges']==0
 assert len(foundations)==4 and {f['mode']for f in foundations}==MODES
 bindings=[]
 for f in foundations:
  assert f['uid']==UID and f['sourceSHA256']==SHA and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==40299
  assert not f['strictFoundationAccepted'] and f['foundation']['fullyBuriedTriangles']==4 and f['foundation']['fullyBuriedUpwardTriangles']==0
  assert [r['faceId']for r in f['buriedFaces']]==decision['buriedFaceIds']==[27545,27546,27547,27548]
  d=next(d for d in decision['checks']if d['mode']==f['mode']);assert d['wholeWorldSHA256']==f['wholeWorldSHA256']
  bindings.append(dict(uid=UID,mode=f['mode'],sourceSHA256=SHA,wholeWorldSHA256=f['wholeWorldSHA256']))
 assert low['summary']==decision['rawLowRimSummary'] and burial['summary']==decision['rawBurialSummary']
 assert low['summary']['sourceSHA256']==burial['summary']['sourceSHA256']==SHA
 assert low['summary']['flaggedFacesCompared']==len(low['faces'])==len(decision['lowRimFaceIds'])==106
 assert [f['faceId']for f in low['faces']]==decision['lowRimFaceIds'] and low['summary']['maximumTerrainDifferenceMetres']==0
 assert burial['summary']['originalTerrainFullyBuriedIds']==[27545,27546,27547,27548] and burial['summary']['maximumTerrainDifferenceMetres']<2e-7
 assert metric['sourcePreserved'] and metric['missingTerrain']==0 and metric['maxSamplerDelta']==0
 assert -.861<metric['minSurfaceGap']<-.860 and .366<metric['minLowGap']<.367 and .712<metric['maxLowGap']<.714
 assert scope['allCurrentActorsNominated'] and scope['currentNativeActors']==6727 and scope['touchingNativeUids']==[]
 assert equivalence['allCurrentSourceBoundsDisjoint'] and equivalence['unchangedParentExceptAddedChild'] and equivalence['allRetainedChildrenIdenticalExceptByteIdenticalEvidenceAliases']
 assert equivalence['currentNativeActors']==6727 and equivalence['retainedChildren']==13 and equivalence['changedChildExtent']==scope['changedParentExtent']
 assert sampler['passed'] and sampler['errors']==sampler['differences']==[] and sampler['currentActors']==6727 and sampler['checked']==sampler['uniqueProbePoints']==34042
 assert neighbours['currentNativeActors']==6727 and neighbours['touchingNativeUids']==[] and neighbours['currentBasicForms']==11 and neighbours['flagged']==[]
 assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
 assert len(validation['results'])==1 and validation['results'][0]['uid']==UID and validation['results'][0]['concerns']==['sampled-terrain-above-model-bottom']
 return dict(uids=[UID],sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawStrictGroundContactPassed=False,rawStrictFoundationPassed=False,rawNumericalFailuresRemainFailed=True,rawMetric=metric,rawDiagnosticConcerns=validation['results'][0]['concerns'],retainedTerrainRelationshipUnchanged=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,publicationApproved=False,installationApproved=False,stagedAndLiveBrowserStillRequired=True,qualification='Exact original Ocean Terminal model/TIN relationship only. Retain all106 low-rim faces and four buried escalator-base faces with unchanged source geometry and pose. Distant retained actors use exact unchanged parent/domain evidence plus runtime corroboration; no legacy support record is relabelled. No generic numeric threshold changes.')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['source-relationship-review-v1','current-neighbours-v1','retained-parent-equivalence-v1','retained-sampler-v1']:
   p=folder(name)/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 data=inputs();v=data['validation']
 for p,h in {**pins,**v['hashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 cap=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018';refs.extend([folder('ordinary-validation-v2')/'validation.json',cap/'metrics.json',cap/'selection.json.gz',folder('source-relationship-review-v1')/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json'])
 q=qualify(**data);policy=module('ocean_policy',HERE/'acceptance-policy.py');metrics=read(cap/'metrics.json');raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=data['identity']['identityProof']),data['metric'],metrics['profiles']['mobile']);assert set(raw)=={'terrain-intersects-source-over-0.5m','ground-contact-unresolved'};q['rawPolicyReasons']=raw
 save(DOC/'qualification.json',q);refs.append(HERE/'acceptance-policy.py')
 module('ocean_applicability_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-exact-original-functional-applicability',list(dict.fromkeys(refs)),dict(uids=[UID],sourceScopedApplicabilityAccepted=True,rawStrictGroundContactPassed=False,rawStrictFoundationPassed=False,installationApproved=False))
if __name__=='__main__':main()
