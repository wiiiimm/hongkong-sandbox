"""Bind inspected original assembly, identity and physical evidence for private staging."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-qualification-v1-20261020';DOC=BASE/BATCH
NAMES=['four-original-browser-v2','four-original-browser-v1','physical-interpretation-v1','identity-review-v1','original-tower-identity-v1']
def folder(n):return BASE/('government-xl-victoria-mall-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];receipts={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);receipts[n]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(n,p):
  assert digest(p.read_bytes())==receipts[n][str(p.relative_to(ROOT))],str(p);refs.append(p);return read(p)
 # The latest complete browser receipt pins all current runtime inputs.
 for p,h in receipts['four-original-browser-v2'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 physical=take('physical-interpretation-v1',folder('physical-interpretation-v1')/'review.json');assert physical['physicalInterpretationAccepted'];sources=physical['sourceSHA256ByUid']
 identity=take('identity-review-v1',folder('identity-review-v1')/'227593:0-review.json');assert identity['identityReviewApproved']and identity['sourceSHA256']==sources['landsd/227593:0']
 ids=take('original-tower-identity-v1',folder('original-tower-identity-v1')/'summary.json')['rows'];assert len(ids)==2
 for row in ids:assert row['passed']and not row['reasons']and row['sourceSHA256']==sources[row['uid']]
 images=[];reports=[]
 for width in [390,1280]:
  f=folder('four-original-browser-v2')/str(width);r=take('four-original-browser-v2',f/'staged-browser.json');assert r['passed']and not r['errors'];reports.append(ref(f/'staged-browser.json'));views=[v for v in r['views']if 'time'in v];assert len(views)==8
  for v in views:
   assert v['fullyFramed']and v['active']and v['visible']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
   p=f/v['file'];assert ref(p)['sha256']==receipts['four-original-browser-v2'][str(p.relative_to(ROOT))];refs.append(p);images.append(ref(p))
  assert len(r['jointViews'])==4
  for joint in r['jointViews']:
   expect={'landsd/227593:0',joint['selectedUid']};assert {m['uid']for m in joint['models']}==expect
   for m in joint['models']:assert m['active']and m['visible']and not m['fallbackFaces']and m['sourceSHA256']==sources[m['uid']]
 failure=take('four-original-browser-v1',folder('four-original-browser-v1')/'390/staged-browser.json');failed=[v for v in failure['views']if v.get('phase')=='failed-download'];assert len(failed)==4 and {v['uid']for v in failed}==set(sources)and all(v['fallbackRetained']for v in failed)
 manifest=ref(ROOT/'3d-viewer/city/data/manifest.json');terrain=ref(folder('trimmed-overlap-validation-v1')/'candidate-terrain.json')
 review=dict(reviewer='Codex ROOT',uids=sorted(sources),sourceSHA256ByUid=sources,originalSourceReviewAccepted=True,sourceScopedApplicabilityAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=manifest,terrainCandidate=terrain,physicalReview=ref(folder('physical-interpretation-v1')/'review.json'),identityReviews=[ref(folder('identity-review-v1')/'227593:0-review.json'),ref(folder('original-tower-identity-v1')/'summary.json')],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,observations=['ROOT individually inspected all16 V2 exports. The selected tower tops and tower bodies are now visible; original podium terraces and street walls are visible across the mall and tower views.','All four originals are plain solid geometry, without invented procedural windows; the dark night appearance is retained. Adjacent sources can be in their existing blur transition; this is not a geometry defect in the selected source.','Mobile UI overlays part of the lower/right scene. The selected source is assessable across its own views, the mall overview, desktop whole assembly and the earlier nine exact joint closeups; no claim that every part is unobscured in every screenshot.','No broad floating or buried body is visible. Exact complete-foundation and finite original-contact proofs supply the physical evidence; these screenshots do not prove absence of temporal z-fighting or engineering soundness.','Previously installed Tower3 keeps exactly the same source bytes and pose. Its dependency must change atomically from surveyed fallback to exact native mall support so all originals can coexist.'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('victoria_qualification',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-reviewed-four-original-private-publication-qualification',list(dict.fromkeys(refs)),dict(uids=sorted(sources),originalSourceReviewAccepted=True,visualAcceptance=True,installationApproved=False))
 print('Victoria four-original assembly qualified for private publication planning',flush=True)
if __name__=='__main__':main()
