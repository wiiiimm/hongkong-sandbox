"""Exact unchanged Royal Green original grade-wall review; no geometry waiver for other sources."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-royal-green3-retained-terrain-v1-20261017';BATCH='government-xl-royal-green3-source-review-v1-20261018';DOC=BASE/BATCH;UID='landsd/11093:0';SHA='99a6f4988219a941b614c8575a4d8fcc8746ce717a99a102e76ffcd80d1b5975'
def folder(n):return BASE/('government-xl-royal-green3-'+n+'-20261018')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__),HERE/'acceptance-policy.py'];names=[CAP]+[folder(n)for n in ['current-native-scope-v1','current-neighbours-v1','grade-face-context-v1','grade-views-v1','four-world-v1','four-foundations-v1','full-grade-context-v1','full-terrain-validation-v1','private-browser-v1','private-browser-v2']]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in names:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SHA
 identity=read(CAP/'identity-proof.json');assert identity['sourceSHA256']==SHA and all(identity['proof'][k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
 metric=read(CAP/'metrics.json');raw=module('royal_review_policy',HERE/'acceptance-policy.py').reasons(dict(row,state='runtime-validated-awaiting-acceptance',identityProof=identity['proof']),metric['rows'][0],metric['profiles']['mobile']);assert raw==['terrain-intersects-source-over-0.5m']
 grade=read(folder('full-grade-context-v1')/'summary.json')['rows'];assert len(grade)==4 and {x['mode']for x in grade}=={'original','literal','left','balanced'}
 for r in grade:
  assert r['continuousNegativeFaceIds']==[8310]and not r['negativeUpwardFaceIds']and not r['negativeWithoutExposedWitness']and not r['uncoveredFaces']and r['wholeSourceFaces']==16685
 foundation=read(folder('four-foundations-v1')/'summary.json');assert foundation['allModesPassed']and len(foundation['rows'])==4 and all(r['buried']==0 for r in foundation['rows'])
 context=read(folder('grade-face-context-v1')/'summary.json');assert all(r['adjacentFaces']==[6631,8311]and abs(r['flagged']['normalYRatio'])<.0001 and r['flagged']['context']['maximumObservedGapM']>3.9 for r in context['contexts'])
 neighbours=read(folder('current-neighbours-v1')/'summary.json');scope=read(folder('current-native-scope-v1')/'scope.json');assert neighbours['forms']==47 and not neighbours['basicFlags']and set(neighbours['nativeResolved'])==set(scope['touchingNativeUids'])and len(scope['touchingNativeUids'])==10
 terrain=read(folder('full-terrain-validation-v1')/'validation.json');assert terrain['passed'];candidate=read(CAP/'terrain-candidates.json')[0];assert terrain['candidateSHA256']==candidate['sha256']
 validation=read(CAP/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
 for n in ['private-browser-v1','private-browser-v2']:
  b=read(folder(n)/'staged-browser.json');assert b['passed']and not b['errors']and len([v for v in b['views']if 'time'in v])==4 and len(b['retainedNativeOwnViews'])==40 and any(v.get('phase')=='failed-download'and v['fallbackRetained']for v in b['views'])
 images=[folder('grade-views-v1')/'source.png',folder('grade-views-v1')/'ground.png']+sorted(folder('private-browser-v2').glob('staged-landsd-11093-0-*.png'));assert len(images)==6
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 decision=dict(uid=UID,sourceSHA256=SHA,reviewer='Codex ROOT',originalSourceReviewAccepted=True,identityAccepted=True,placementAccepted=True,rawPolicyReasons=raw,policyReasons=[],sourceSpecificResolutions=['original-lower-wall-sloping-ground-interface'],gradeEvidence=grade,terrainCandidate=candidate,inspectedImages=[ref(p)for p in images],observations=['Complete 16685-face ground check across original, literal and two explicit Float32 coordinate evaluations isolates face8310 as the sole crossing below the unchanged -0.5m diagnostic gate. It retains an exposed portion; no upward-facing affected surface or uncovered source face. All four whole-source foundations pass with zero wholly buried triangles.','Source close-ups show face8310 forming a lower wall with exact shared-edge wall neighbours6631 and8311. The original-government TIN and candidate reproduce approximately0.595m continuous crossing, while the upper wall retains approximately3.99m exposure. This is an original lower wall entering sloping grade, not a translated model or a buried upper floor. Source coordinates, triangles, source pose and raw numerical warnings remain unchanged.','Current complete native inventory nominates10 actors over the full coarse replacement extent, including12663 previously omitted. All10 pass complete retained neighbour regression;47nearby forms produce no BASIC flags. Both replaced terrain sources retain their documented preservation evidence.','Desktop/mobile day/night, original-byte loading, picking/collision and failed-download fallback pass. Forty retained-original own views pass. Padded v2 exported own views inspected; camera margin was increased for inspection only.'],sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,newlyInstalled=0,limitations=['Exact-source original acceptance only; not optimisation or engineering approval. No global threshold change.','Guarded staging, publication and live verification remain required. Explicit Float32 evaluations do not certify every GPU implementation.'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',decision);refs.extend([*[ROOT/p for p in pins],*images]);out=module('royal_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'royal-green3-exact-original-source-review-v1',refs,dict(uids=[UID],originalSourceReviewAccepted=True,rawPolicyReasons=raw,publication=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
