"""Bind complete paired checks; no publication and no source edits."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lee-kong-pair-qualification-v1-20261020';DOC=BASE/BATCH
SOURCES={'landsd/72296:0':('50f75b4c2d094f1da18b914601d0b78d2d93f2e1d96ff7ec894b397ac7b07f34',21662),'landsd/253697:0':('2db2214db4d26ac9711d4c16a145214d49121bf29432a6a21b182652f93625d4',372)}
def folder(n):return BASE/('government-xl-lee-kong-pair-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [folder(n) for n in ['identity-review-v1','loader-v1','neighbours-v1','browser-review-v1','four-mode-foundations-v1','contact-v1']]+[BASE/'government-xl-lee-kong72296-private-ground-v1-20261020']:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 identities=[]
 for uid,(sha,count) in SOURCES.items():
  p=folder('identity-review-v1')/(uid.split('/')[1]+'-review.json');r=read(p);assert r['identityOnlyApproved'] and r['sourceSHA256']==sha and r['sourceFaces']==count;identities.append(ref(p))
 v=read(folder('loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==2 and v['exceptions']==0
 contact=read(folder('contact-v1')/'summary.json');assert not contact['remainingPolicyReasons'] and not contact['remainingDiagnosticReasons'];assert contact['interfaceSummary']==dict(passed=True,samples=72,strictContacts=72,wallIntersections=0) and contact['unresolved']==0
 raw=read(folder('loader-v1')/'summary.json')
 for r in raw['rawPolicyReasons']:assert r['reasons']==(['ground-contact-unresolved'] if r['uid']=='landsd/253697:0' else [])
 for r in raw['ordinaryConcerns']:assert r['concerns']==(['sampled-ground-gap-below-model-bottom'] if r['uid']=='landsd/253697:0' else [])
 near=read(folder('neighbours-v1')/'summary.json');assert not near['flagged'] and near['neighbourForms']==80 and set(near['requiredNativeUids'])=={'landsd/186864:0','landsd/236490:0'};assert all(x['passed'] and x['terrain']['newlyWhollyBuried']==x['terrain']['newlyUpwardWhollyBuried']==0 for x in near['nativeChecks'])
 foundations=read(folder('four-mode-foundations-v1')/'summary.json')['rows'];assert len(foundations)==8;bindings=[]
 for uid,(sha,count) in SOURCES.items():
  rr=[x for x in foundations if x['uid']==uid];assert len(rr)==4 and {x['mode'] for x in rr}=={'original','literal','explicitLeftF32','explicitBalancedF32'};assert all(x['passed'] and x['complete']==count and x['buried']==x['upwardBuried']==0 for x in rr)
  for mode in ['original','explicitLeftF32','explicitBalancedF32']:
   f=read(folder('four-mode-foundations-v1')/(uid.split('/')[1]+'-'+mode+'.json'));assert f['sourceSHA256']==sha and f['strictFoundationAccepted'];bindings.append(dict(uid=uid,mode=mode,sourceSHA256=sha,wholeWorldSHA256=f['wholeWorldSHA256']))
 assert read(BASE/'government-xl-lee-kong72296-private-ground-v1-20261020/result.json')['guardFailure'] is None
 images=read(folder('browser-review-v1')/'ROOT-IMAGE-REVIEW.json');assert images['visualAcceptance'] and len(images['imagesActuallyViewed'])==8 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 terrain=read(folder('loader-v1')/'terrain-candidates.json');assert len(terrain)==1 and digest((ROOT/terrain[0]['path']).read_bytes())==terrain[0]['sha256']
 save(DOC/'qualification.json',dict(uids=list(SOURCES),sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,rawPolicyReasons=raw['rawPolicyReasons'],remainingPhysicalReasons=[],strictTerrainIntersectionCheckPassed=True,identityReviews=identities,neighbourReview=ref(folder('neighbours-v1')/'summary.json'),supportReview=ref(folder('contact-v1')/'summary.json'),visualReview=ref(folder('browser-review-v1')/'ROOT-IMAGE-REVIEW.json'),terrainCandidates=terrain,terrainReplacement=True,completeLoaderPickingCollisionPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,basicSuppressionApproved=False,publication=False,installationApproved=False,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('lee_pair_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pair-qualified-checks',list(set(refs)),dict(uids=list(SOURCES),sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
