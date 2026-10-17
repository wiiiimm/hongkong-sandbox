"""Bind actual inspected desktop/mobile exports and unchanged loader/mobile policy; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tai-kwei-browser-policy-review-v1-20261017';DOC=BASE/BATCH
PHYS=BASE/'government-xl-tai-kwei-candidate-physical-v2-20261017';IDENTITY=BASE/'government-xl-tai-kwei-reviewed-identity-v1-20261017';BROWSER=BASE/'government-xl-tai-kwei-private-browser-v2-20261017';LOADER=BASE/'government-xl-tai-kwei-loader-validation-v1-20261017'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__),HERE/'acceptance-policy.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PHYS,IDENTITY,BROWSER,LOADER]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(PHYS/'selection.json.gz')['rows'][0];identity=read(IDENTITY/'identity-review.json');assert identity['identityReviewApproved']and identity['sourceSHA256']==row['sourceSHA256']
 validation=read(LOADER/'validation.json');v=validation['results'][0];assert len(validation['results'])==1 and v['uid']==row['uid']and v['outcome']=='runtime-accepted-placement-unreviewed'and not v['concerns']
 metric=read(PHYS/'metrics.json');policy=module('tai_kwei_mobile_policy',HERE/'acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['identityProof']),metric['rows'][0],metric['profiles']['mobile']);assert not reasons,reasons
 report=read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert {(v['width'],v['time'])for v in views}=={(w,t)for w in [1280,390]for t in ['15:00','22:00']}and len(views)==4
 for v in views:assert v['sourceSHA256']==row['sourceSHA256']and v['originalTriangles']==row['triangles']and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and v['fallbackFaces']==0 and v['pick']==v['collision']==row['uid']and not v['overflow']
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained']
 cat=read(HERE/'local'/BROWSER.name/'catalogue.json');assert cat['models'][0]['proceduralWindows']is False
 def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 review=dict(reviewer='Codex ROOT',imagesActuallyViewed=[ref(BROWSER/v['file'])for v in views],sourceGeometryAppearanceAccepted=True,observation='All four exported desktop/mobile day/night images inspected. Complete source framed and solid; nearby buildings naturally occlude parts of its base. Plain original facade retained with procedural windows disabled; night view remains dark under scene lighting. No model geometry edits. This image review is not full numerical/publication acceptance.',proceduralWindows=False)
 save(DOC/'ROOT-IMAGE-INSPECTION.json',review);save(DOC/'policy.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],loaderOutcome=v['outcome']if 'outcome'in v else validation['results'][0]['outcome'],loaderConcerns=[],remainingMobilePolicyReasons=reasons,identityReview=ref(IDENTITY/'identity-review.json'),browserReport=ref(BROWSER/'staged-browser.json'),fullFiniteAcceptanceStillRequired=True,publicationApproved=False))
 out=module('tai_kwei_browser_policy_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-inspected-browser-and-current-mobile-policy-v1',list(set(refs)),dict(uids=[row['uid']],remainingMobilePolicyReasons=reasons,desktopMobileImagesAccepted=True,pickAndCollisionSelectionPassed=True,failedDownloadFallbackPassed=True,fullAcceptance=False,nextStep='Await complete all-world finite clearance and neighbour results before staging final publication. No live changes yet.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
