"""Exact-source qualification with unchanged numeric failures retained."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-functional-applicability-v1-20261020';DOC=BASE/BATCH
UID='landsd/56054:0';SHA='76ee08f0c71b97728e943666840654123f2efa7856b66bec551eed15496b8867'
def folder(n):return BASE/('government-xl-sheung-shui-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for n in ['original-grade-review-v1','identity-review-v1','loader-v1','neighbours-v2','candidate-terrain-v5','browser-review-v1','four-mode-foundations-v1']:
   d=folder(n);r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 grade=read(folder('original-grade-review-v1')/'ROOT-GRADE-REVIEW.json');assert grade['sourceSpecificGradeInterpretationAccepted']and grade['sourceSHA256']==SHA and not grade['strictTerrainIntersectionCheckPassed']and len(grade['sourceFaces'])==68
 identity=read(folder('identity-review-v1')/'56054:0-review.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==SHA
 v=read(folder('loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==1 and not v['exceptions'];assert v['results'][0]['uid']==UID and not v['results'][0]['concerns']
 near=read(folder('neighbours-v2')/'summary.json');assert not near['flagged']and not near['requiredNativeUids']and near['neighbourForms']==60
 for b in grade['sourceBindings']:
  f=read(folder('four-mode-foundations-v1')/('56054:0-'+b['mode']+'.json'));assert f['sourceSHA256']==SHA and f['wholeWorldSHA256']==b['wholeWorldSHA256']and f['strictFoundationAccepted']and f['foundation']['fullyBuriedTriangles']==0
 images=read(folder('browser-review-v1')/'ROOT-IMAGE-REVIEW.json');assert images['visualAcceptance']and len(images['imagesActuallyViewed'])==4 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 terrain=read(folder('loader-v1')/'terrain-candidates.json');assert len(terrain)==1;assert digest((ROOT/terrain[0]['path']).read_bytes())==terrain[0]['sha256']
 q=dict(uids=[UID],sourceBindings=grade['sourceBindings'],sourceScopedApplicabilityAccepted=True,rawPolicyReasons=grade['rawPolicyReasons'],resolvedByExactSourceFunctionalApplicability=grade['rawPolicyReasons'],remainingPhysicalReasons=[],strictTerrainIntersectionCheckPassed=False,gradeReview=ref(folder('original-grade-review-v1')/'ROOT-GRADE-REVIEW.json'),identityReview=ref(folder('identity-review-v1')/'56054:0-review.json'),neighbourReview=ref(folder('neighbours-v2')/'summary.json'),visualReview=ref(folder('browser-review-v1')/'ROOT-IMAGE-REVIEW.json'),terrainCandidates=terrain,terrainReplacement=True,completeLoaderPickingCollisionPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,basicSuppressionApproved=False,publication=False,installationApproved=False,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'))
 save(DOC/'qualification.json',q)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('sheung_shui_functional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'sheung-shui-exact-original-functional-applicability',list(set(refs)),dict(uids=[UID],sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
