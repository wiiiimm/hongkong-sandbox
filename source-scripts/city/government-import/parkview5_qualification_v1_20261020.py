"""Qualify exact original towers; explicitly reconcile legacy installed-support evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview5-qualification-v1-20261020';DOC=BASE/BATCH
UIDS=['landsd/256113:0'];POD='landsd/254491:0'
def folder(n):return BASE/('government-xl-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
assert not DOC.exists();pins={};refs=[Path(__file__)]
names=['parkview5-loader-v1','parkview5-physical-review-v1','parkview5-browser-review-v1','parkview5-neighbours-v1','parkview-podium-flag-audit-v2']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for n in names:
  d=folder(n);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
supportPath=folder('parkview5-physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json';support=read(supportPath);assert support['sourceSpecificPhysicalInterpretationAccepted']and not support['rawCanonicalInterfacePassed'];assert support['sourceGeometryChanges']==support['sourcePoseChanges']==0
assert not support['rawStrictFoundationPassed'] and support['rawFailuresPreserved'];assert len(support['exactWholeBuriedFaceTerrainClearance'])==4 and all(x['minimumWholeFaceGroundClearanceM']>0 for x in support['exactWholeBuriedFaceTerrainClearance'])
sources={support['uid']:support['sourceSHA256']};assert set(sources)==set(UIDS);bindings=[]
for a in support['sampleAccounts']:
 assert a['unresolved']==0 and a['buriedSideFaceClearOfActualGround'] and a['rawBuriedUpwardFaces']==0 and a['samples']==a['canonicalStrictContacts']+a['priorBoundedWallPaths']+a['finiteBoundaryWallPaths']
 bindings.append(dict(uid=support['uid'],mode=a['mode'],sourceSHA256=sources[support['uid']],wholeWorldSHA256=a['sourceWorldSHA256'],supportWorldSHA256=a['supportWorldSHA256']))
assert len(bindings)==4 and len({(r['uid'],r['mode'])for r in bindings})==4
identityRefs=[]
for uid in UIDS:
 p=folder('next-twenty-original-identity-v2')/uid.split('/')[1]/'identity.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];r=read(p);assert r['sourceSHA256']==sources[uid]and r['passed']and not r['reasons']and all(r['proof'][k]for k in ['exactBuildingCSUID','exactObjectId','identityAccepted','uniqueViewerMatch']);identityRefs.append(ref(p))
v=read(folder('parkview5-loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0
raw=read(folder('parkview5-loader-v1')/'summary.json');assert {r['uid']:r['reasons']for r in raw['rawPolicyReasons']}=={u:['ground-contact-unresolved']for u in UIDS}
nearPath=folder('parkview5-neighbours-v1')/'summary.json';near=read(nearPath);assert not near['flagged']and near['forms']==3 and near['maxGroundChange']==0 and near['terrainChanged']is False
imagePath=folder('parkview5-browser-review-v1')/'ROOT-IMAGE-REVIEW.json';images=read(imagePath);assert images['visualAcceptance']and len(images['imagesActuallyViewed'])==8 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
auditPath=folder('parkview-podium-flag-audit-v2')/'audit.json';audit=read(auditPath);assert audit['uid']==POD and audit['reviewState']=='installed-verified'and audit['evidenceBackedOriginalApprovalReconciliation']and audit['sameCatalogueAsInstalledAcceptance']and audit['noLaterHoldOrRejection']
# Explicitly preserve the conflicting catalogue flag and the stronger exact-source
# installed review. This is not a generic flag bypass or variant approval transfer.
save(DOC/'qualification.json',dict(uids=UIDS,sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawPolicyReasons=raw['rawPolicyReasons'],rawCanonicalSupportInterfacePassed=False,sourceSpecificReviewsResolveApplicability=True,identityReviews=identityRefs,supportReview=ref(supportPath),neighbourReview=ref(nearPath),neighbourReviewScope='Unchanged terrain regression only; no blanket cross-building collision clearance.',visualReview=ref(imagePath),installedSupportApprovalReconciliation=ref(auditPath),requiredInstalledSupport=dict(uid=POD,sha256=audit['sourceSHA256'],catalogueFlag=False,authoritativeReviewState='installed-verified',approvalBasis='Exact byte-bound historical installed approval plus current source/runtime/browser checks; explicit legacy bookkeeping discrepancy retained.'),terrainCandidates=[],terrainReplacement=False,completeLoaderPickingCollisionPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,basicSuppressionApproved=False,publication=False,installationApproved=False,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('parkview5_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-towers-qualified-with-reviewed-installed-support',list(dict.fromkeys(refs)),dict(uids=UIDS,sourceScopedApplicabilityAccepted=True,installationApproved=False))
