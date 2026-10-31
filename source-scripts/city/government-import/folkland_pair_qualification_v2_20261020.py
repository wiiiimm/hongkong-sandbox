"""ROOT-reviewed exact original Folkland pair; final live installation remains separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-pair-qualification-v2-20261020';DOC=BASE/BATCH
NAMES=['assembly-identity-review-v1','pair-current-identity-v1','pair-loader-v1','pair-candidate-foundations-v2','neighbours-v2','hoi-yu-prior-review-v1','four-mode-support-v1','original-finite-path-verification-v1','runtime-finite-path-verification-v1','pair-browser-desktop-v2','pair-browser-mobile-v2']
def folder(n):return BASE/('government-xl-folkland-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   f=folder(n);r=read(f/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=read(folder('pair-candidate-foundations-v2')/'selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in selection};assert len(sources)==2
 assembly=read(folder('assembly-identity-review-v1')/'review.json');assert assembly['identityOnlyApproved'] and assembly['sourceSHA256ByUid']==sources
 for r in selection:
  proof=read(folder('pair-current-identity-v1')/(r['uid'].split('/')[1])/'identity.json');assert proof['sourceSHA256']==r['sourceSHA256'] and proof['reasons']==assembly['rawIndividualIdentityReasons'][r['uid']]
  assert proof['passed'] or r['uid']=='landsd/264677:0' and set(proof['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
 loader=read(folder('pair-loader-v1')/'validation.json');assert loader['models']==loader['loaderAccepted']==loader['checksPassed']==2 and loader['exceptions']==0
 foundations=read(folder('pair-candidate-foundations-v2')/'summary.json')['rows'];assert len(foundations)==10
 for f in foundations:assert f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0 and f['completeTerrainTriangles']==f['triangles']
 strict=read(folder('four-mode-support-v1')/'summary.json')['rows'];assert len(strict)==4
 accounts=[]
 for r in strict:
  mode=r['mode'];assert r['samples']==86 and r['strictContacts']==54 and r['unresolved']==31
  f=folder('original-finite-path-verification-v1' if mode=='original'else'runtime-finite-path-verification-v1');proof=read(f/(mode+'.json'));assert len(proof['rows'])==31
  assert all(x['finitePathVerified']and x['withinEndpointHeight']and x['allSteepWallFaces'] for x in proof['rows'])
  s=read(folder('four-mode-support-v1')/mode/'support.json.gz')['rows'][0]['proof'];assert s['wallIntersections']==1
  accounts.append(dict(mode=mode,strictContacts=54,ordinaryWallIntersections=1,sourceSpecificFiniteWallContacts=31,rawStrictPassed=False,sourceWorldSHA256=proof['sourceWorldSHA256'],supportWorldSHA256=proof['supportWorldSHA256']))
 neighbours=read(folder('neighbours-v2')/'summary.json');assert not neighbours['flagged'] and neighbours['neighbourForms']==612 and len(neighbours['requiredNativeUids'])==45
 hoi=read(folder('hoi-yu-prior-review-v1')/'review.json');assert hoi['existingExactSourceSupportReviewVerified']and hoi['currentSourcesAndDependencyUnchanged']
 native=read(folder('neighbours-v2')/'native-neighbour-checks.json')['rows'];assert len(native)==45
 for r in native:
  assert r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0
  if not r['passed']:assert r['uid']=='landsd/177605:0' and r==hoi['currentCandidateTerrainRegression']
 images=[];reports=[];failures=[]
 for name,width in [('pair-browser-desktop-v2',1280),('pair-browser-mobile-v2',390)]:
  f=folder(name);p=f/'staged-browser.json';r=read(p);assert r['passed']and not r['errors'];reports.append(ref(p));views=[v for v in r['views']if 'time'in v];assert len(views)==4
  for v in views:
   assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']];images.append(ref(f/v['file']))
  for j in r['jointViews']:
   expected={u:s for u,s in sources.items()if u=='landsd/225387:0' or j['selectedUid']=='landsd/264677:0'};assert {m['uid']:m['sourceSHA256']for m in j['models']}==expected
   assert all(m['active']and m['visible']and not m['fallbackFaces']and all(m['meshVisibility'])and not any(m['wireframeFlags'])for m in j['models'])
  failures.extend(v for v in r['views']if v.get('phase')=='failed-download')
 assert len(images)==8 and len(failures)==2 and {v['uid']for v in failures}==set(sources)and all(v['fallbackRetained']for v in failures)
 # All eight exact exported PNGs were actually viewed by ROOT using view_image.
 save(DOC/'ROOT-IMAGE-REVIEW.json',dict(reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),observations=['The grey original podium shows its lower facade, terrace and parapets at street level.','When selected, the unchanged tower replaces its basic representation and sits on the original podium; stepped roof recesses and vertical facade relief are visible.','Desktop and mobile day/night exports retain the original shape without procedural windows. The podium-only selection retains the basic tower until its own source loads.','No floating separate tower body or broad burial is visible. Numeric complete-foundation and finite-contact proofs support this visual interpretation; screenshots alone are not structural proof.'],installationApproved=False))
 review=dict(reviewer='Codex ROOT',uids=sorted(sources),sourceBindings=[dict(uid=u,sourceSHA256=s)for u,s in sorted(sources.items())],sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],terrainReplacement=True,sourceGeometryChanges=0,sourcePoseChanges=0,identityReview=ref(folder('assembly-identity-review-v1')/'review.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawStrictFailuresRetained=True,accounts=accounts,neighbourForms=612,retainedNativeActors=45,existingHoiYuSupportReview=ref(folder('hoi-yu-prior-review-v1')/'review.json'),basis='Exact unique government source identities and unchanged 1x placement. The original tower lower vertical walls enter the authored podium roof:54 strict rim contacts and1 ordinary wall contact remain accepted by the unchanged policy; the31 remaining rim samples each have independently verified finite steep-wall paths to positive-dimensional original podium contacts within their own endpoint heights in four coordinate representations. Thirty original/literal contacts are boundary contacts; the remaining interior contact is retained explicitly. This is a source-specific interpretation of the original embedded wall interface, not proof of engineering soundness or clearance at every point. Full source foundations have zero buried faces after restoring original terrain. The four initially affected BASIC neighbours retain their previous ground outside the source projection; all612 checks pass. All45 retained native actors have zero new burial; unchanged Hoi Yu support is bound to its existing exact-source review. No global threshold, source clipping, shifting, rescaling, suppression or model remodelling is approved.',installationApproved=False,publication=False)
 save(DOC/'qualification.json',review)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('folkland_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-reviewed-exact-original-pair-qualification',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceScopedApplicabilityAccepted=True,visualAcceptance=True,installationApproved=False));print('Folkland pair qualified for private publisher staging',flush=True)
if __name__=='__main__':main()
