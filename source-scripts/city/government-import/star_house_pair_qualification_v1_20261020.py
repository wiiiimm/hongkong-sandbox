"""Bind exact unchanged Star House pair reviews; preserve raw sampler failures."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-star-house-pair-qualification-v1-20261020';DOC=BASE/BATCH
SOURCES={'landsd/33396:0':('200b83da07a41f01a028815178d53f28cd73cba432ff29ccc9dd8ac74d07ec07',22741),'landsd/231484:0':('2d2b63f0aedd4e57971f295e6aecc51f1c23e7c4e7c739b5a1085d4a0712761a',3260)}
def folder(n):return BASE/('government-xl-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 names=['star-house-podium-identity-review-v1','star-house-pair-loader-v1','star-house-pair-neighbours-v1','star-house-pair-browser-review-v1','star-parkview-four-mode-foundations-v1','star-house-podium-source-relationship-review-v1','star-house-pair-support-review-v1']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in names:
   d=folder(n);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 identity=folder('star-house-podium-identity-review-v1')/'231484:0-review.json';ir=read(identity);assert ir['identityOnlyApproved'] and ir['sourceSHA256']==SOURCES['landsd/231484:0'][0]
 tower=folder('next-twenty-original-identity-v2')/'33396:0/identity.json';tr=read(tower);assert tr['passed'] and all(tr['proof'][k]for k in ['exactBuildingCSUID','exactObjectId','identityAccepted','uniqueViewerMatch']);assert str(tower.relative_to(ROOT))in pins
 v=read(folder('star-house-pair-loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==2 and v['exceptions']==0
 raw=read(folder('star-house-pair-loader-v1')/'summary.json')
 assert {r['uid']:r['reasons']for r in raw['rawPolicyReasons']}=={'landsd/33396:0':['ground-contact-unresolved'],'landsd/231484:0':['terrain-intersects-source-over-0.5m']}
 near=read(folder('star-house-pair-neighbours-v1')/'summary.json');assert not near['flagged'] and near['forms']==6 and near['maxGroundChange']==0 and near['terrainChanged'] is False
 supportPath=folder('star-house-pair-support-review-v1')/'ROOT-SUPPORT-REVIEW.json';support=read(supportPath)
 assert support['sourceSpecificSupportAccepted'] and support['rawCanonicalInterfacePassed'] is False and support['sourceSHA256ByUid']=={u:s for u,(s,n)in SOURCES.items()}
 assert support['sourceGeometryChanges']==support['sourcePoseChanges']==0
 groundPath=folder('star-house-podium-source-relationship-review-v1')/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json';ground=read(groundPath)
 assert ground['originalSurveyedRelationshipAccepted'] and ground['rawStrictTerrainIntersectionPassed'] is False and ground['rawStrictFoundationPassed'] and ground['sourceSHA256']==SOURCES['landsd/231484:0'][0] and not ground['buriedFaceIds']
 bindings=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  accounts=[r for r in support['sampleAccounts']if r['mode']==mode];assert len(accounts)==1;a=accounts[0]
  assert a['samples']==1105 and a['canonicalContacts']==1033 and a['canonicalResolvedWallContacts']==1 and a['directOriginalFaceContacts']==71 and a['stillUnresolved']==0
  for uid,(sha,count)in SOURCES.items():
   f=read(folder('star-parkview-four-mode-foundations-v1')/(uid.split('/')[1]+'-'+mode+'.json'));assert f['sourceSHA256']==sha and f['strictFoundationAccepted']
   assert f['worldSHA256']==a['sourceWorldSHA256' if uid=='landsd/33396:0'else 'supportWorldSHA256']
   if uid=='landsd/231484:0':assert any(g['mode']==mode and g['wholeWorldSHA256']==f['worldSHA256']and g['strictFoundationAccepted']for g in ground['checks'])
   bindings.append(dict(uid=uid,mode=mode,sourceSHA256=sha,wholeWorldSHA256=f['worldSHA256'],sourceFaces=count))
 images=read(folder('star-house-pair-browser-review-v1')/'ROOT-IMAGE-REVIEW.json');assert images['visualAcceptance'] and len(images['imagesActuallyViewed'])==8 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 save(DOC/'qualification.json',dict(uids=list(SOURCES),sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,rawPolicyReasons=raw['rawPolicyReasons'],remainingPhysicalReasons=[],strictTerrainIntersectionCheckPassed=False,rawCanonicalSupportInterfacePassed=False,sourceSpecificReviewsResolveApplicability=True,identityReviews=[ref(identity),ref(tower)],neighbourReview=ref(folder('star-house-pair-neighbours-v1')/'summary.json'),neighbourReviewScope='Unchanged terrain regression only; no blanket cross-building collision clearance.',supportReview=ref(supportPath),groundRelationshipReview=ref(groundPath),visualReview=ref(folder('star-house-pair-browser-review-v1')/'ROOT-IMAGE-REVIEW.json'),terrainCandidates=[],terrainReplacement=False,completeLoaderPickingCollisionPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,basicSuppressionApproved=False,publication=False,installationApproved=False,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('star_pair_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pair-qualified-source-specific-checks',list(set(refs)),dict(uids=list(SOURCES),sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
