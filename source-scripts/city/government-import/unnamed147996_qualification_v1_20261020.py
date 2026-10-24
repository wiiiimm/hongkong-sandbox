"""Bind complete current checks for one unchanged original; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed147996-qualification-v1-20261020';DOC=BASE/BATCH
UID='landsd/147996:0';SHA='aa2f514855c60e67fdb9e1f2122f7615b2d9f9670afc745c13736c3d338c116a'
def folder(n):return BASE/('government-xl-unnamed147996-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for n in ['identity-review-v1','loader-v1','neighbours-v2','terrain-validation-v1','browser-review-v1','four-mode-foundations-v1','hoi-yu-prior-review-v1']:
   d=folder(n);r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 identity=read(folder('identity-review-v1')/'147996:0-review.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==SHA
 v=read(folder('loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==1 and not v['exceptions'];assert v['results'][0]['uid']==UID and not v['results'][0]['concerns']
 assert not read(folder('loader-v1')/'summary.json')['rawPolicyReasons']
 near=read(folder('neighbours-v2')/'summary.json');assert not near['flagged']and near['neighbourForms']==612 and len(near['requiredNativeUids'])==44
 hoi=read(folder('hoi-yu-prior-review-v1')/'review.json');assert hoi['existingExactSourceSupportReviewVerified']and hoi['currentSourcesAndDependencyUnchanged']
 for row in near['nativeChecks']:
  t=row['terrain'];assert t['newlyWhollyBuried']==t['newlyUpwardWhollyBuried']==0
  if not row['passed']:assert row['uid']=='landsd/177605:0'and row==hoi['currentCandidateTerrainRegression']
 foundations=read(folder('four-mode-foundations-v1')/'summary.json')['rows'];assert len(foundations)==4
 assert {r['mode']for r in foundations}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
 assert all(r['passed']and r['complete']==21776 and r['buried']==r['upwardBuried']==0 for r in foundations)
 bindings=[]
 for mode in ['original','explicitLeftF32','explicitBalancedF32']:
  f=read(folder('four-mode-foundations-v1')/('147996:0-'+mode+'.json'));assert f['sourceSHA256']==SHA and f['strictFoundationAccepted'];bindings.append(dict(mode=mode,sourceSHA256=SHA,wholeWorldSHA256=f['wholeWorldSHA256']))
 tv=read(folder('terrain-validation-v1')/'validation.json');assert tv['terrainValidatorPassed']and tv['positionsAndIndicesUnchanged']
 images=read(folder('browser-review-v1')/'ROOT-IMAGE-REVIEW.json');assert images['visualAcceptance']and len(images['imagesActuallyViewed'])==4 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 terrain=read(folder('loader-v1')/'terrain-candidates.json');assert len(terrain)==1;assert digest((ROOT/terrain[0]['path']).read_bytes())==terrain[0]['sha256']
 q=dict(uids=[UID],sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,rawPolicyReasons=[],remainingPhysicalReasons=[],strictTerrainIntersectionCheckPassed=True,identityReview=ref(folder('identity-review-v1')/'147996:0-review.json'),neighbourReview=ref(folder('neighbours-v2')/'summary.json'),inheritedSupportReview=ref(folder('hoi-yu-prior-review-v1')/'review.json'),visualReview=ref(folder('browser-review-v1')/'ROOT-IMAGE-REVIEW.json'),terrainCandidates=terrain,terrainReplacement=True,completeLoaderPickingCollisionPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,basicSuppressionApproved=False,publication=False,installationApproved=False,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'))
 save(DOC/'qualification.json',q)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('unnamed_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unnamed147996-original-qualified-checks',list(set(refs)),dict(uids=[UID],sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
