"""Exact original Olympian pair applicability; preserve all raw numeric failures."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-one-functional-applicability-v1-20261018';DOC=BASE/BATCH
POD='landsd/72354:0';TOWER='landsd/256927:0'
EXPECTED={POD:('3441519852P20060804','38fd11ec0a1af842baa4cc274c4141bbc2c816468a44b8376c59d8fd2fc2f2b9',31046),TOWER:('3441719871T20050430','1a3a5716d69fbd2c7b5217213f06f4a58a374d85aff334b29e2f58c0f22de59a',4183)}
FACES=[2424,2425,2426,3014,3015,3016,3017,3018,3019,4177,4178,4179,4180,4181,4182]
NARROW={TOWER+':ground-contact-unresolved','validation:'+TOWER+':sampled-ground-gap-below-model-bottom','original-support-interface-unresolved'}
MODES={'original','literal','explicitLeftF32','explicitBalancedF32'}
def folder(s):return BASE/('government-xl-olympian-one-'+s+'-20261018')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def apply(decision,binding,foundations,raw):
 assert decision['reviewer']=='Codex ROOT' and decision['reviewType']=='exact-original-source-functional-interpretation'
 assert decision['sourceFunctionalInterpretationAccepted']is True
 assert decision['sourceFaceIds']==FACES and decision['all47FailuresRemainNumericallyFailed']is True
 assert decision['strictOriginalInterfacePassed']is False and decision['independentSupportFor47SamplesProved']is False
 assert decision['modelGeometryChanges']==0 and decision['aiGeometryModelling']is False
 assert not any(decision[k]for k in ['installationApproved','publicationApproved','physicalAccepted'])
 assert {r['uid']for r in decision['sourceBindings']}==set(EXPECTED)
 for r in decision['sourceBindings']:assert (r['buildingCSUID'],r['sourceSHA256'])==EXPECTED[r['uid']][:2]
 strict=decision['rawStrictInterfaceVerbatim']
 assert strict['passed']is False and strict['samples']==497 and strict['strictContacts']==450 and len(strict['unresolved'])==47
 assert len(strict['strictLowRim']['failed'])==47 and all(r['reason']=='support-above-rim'for r in strict['strictLowRim']['failed'])
 assert len(decision['imagesActuallyInspected'])==5
 assert binding['ROOTSourceReview']==ref(folder('source-review-v1')/'ROOT-SOURCE-INTERPRETATION.json')
 assert len(binding['bindings'])==len(foundations)==8
 tuples={(u,m)for u in EXPECTED for m in MODES}
 assert {(r['uid'],r['mode'])for r in binding['bindings']}==tuples=={(r['uid'],r['mode'])for r in foundations}
 for r in binding['bindings']:
  assert (r['buildingCSUID'],r['sourceSHA256'],r['completeFaces'])==EXPECTED[r['uid']]
  f=next(f for f in foundations if (f['uid'],f['mode'])==(r['uid'],r['mode']))
  assert f['worldSHA256']==r['wholeWorldSHA256'] and f['strictFoundationAccepted']is True
  assert f['foundation']['triangles']==r['completeFaces']==f['foundation']['completeTerrainTriangles']
  assert f['foundation']['fullyBuriedAreaFraction']==0 and f['foundation']['fullyBuriedUpwardTriangles']==0
 assert {r['mode']for r in binding['descriptors']}==MODES and len(binding['descriptors'])==4
 for r in binding['descriptors']:
  assert [f['originalFaceID']for f in r['faces']]==FACES
  assert r['wholeWorldSHA256']==next(b['wholeWorldSHA256']for b in binding['bindings']if b['uid']==TOWER and b['mode']==r['mode'])
 assert set(raw)==NARROW and len(raw)==3
 assert set(decision['proposedNarrowApplicability'])=={TOWER+':ground-contact-unresolved',TOWER+':sampled-ground-gap-below-model-bottom','original-support-interface-unresolved'}
 return dict(uids=list(EXPECTED),rawReasonsVerbatim=raw,rawStrictInterfaceVerbatim=strict,strictInterfacePassed=False,sourceScopedApplicabilityAccepted=True,resolvedByExactSourceFunctionalApplicability=sorted(NARROW),remainingPhysicalReasons=[],rawNumericalFailuresRemainFailed=True,independentSupportFor47SamplesProved=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,installationApproved=False,stagedLiveBrowserStillRequired=True)
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];physical=folder('pair-physical-v2');ground=folder('global-bottom-resolution-v1');review=folder('source-review-v1');bindings=folder('wall-binding-v1')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [physical,ground,review,bindings]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 decision=read(review/'ROOT-SOURCE-INTERPRETATION.json');b=read(bindings/'exact-source-face-bindings.json.gz');foundations=[read(p)for p in physical.glob('*-foundation.json')];raw=read(ground/'summary.json')['remainingReasons']
 result=apply(decision,b,foundations,raw)
 v=read(physical/'validation.json');assert v['loaderAccepted']==v['checksPassed']==v['models']==2 and v['exceptions']==0
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 neighbours=read(physical/'neighbour-checks.json');assert not any(r['reasons']for r in neighbours['rows'])
 native=read(physical/'native-neighbour-checks.json');assert not set(native['blocked'])-set(native['resolved'])
 identities=folder('identity-review-v1');identity=read(identities/'72354:0-review.json');assert identity['identityOnlyApproved']is True
 tower=read(folder('original-assembly-v1')/'256927:0-identity.json');assert tower['passed']is True
 result.update(ROOTReview=ref(review/'ROOT-SOURCE-INTERPRETATION.json'),completePhysical=ref(physical/'result.json'),sourceBindings=b['bindings'],globalBottomResolution=ref(ground/'result.json'),identityReview=ref(identities/'72354:0-review.json'),completeLoaderPickingCollisionPassed=True,completeNeighboursPassed=True)
 save(DOC/'qualification.json',result)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_functional_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-facade-functional-applicability',list(dict.fromkeys(refs)),dict(uids=list(EXPECTED),sourceScopedApplicabilityAccepted=True,strictInterfacePassed=False,installationApproved=False,sourceGeometryChanges=0))
 print('Exact original-pair applicability qualified; browser/publication still required.',flush=True)
if __name__=='__main__':main()
