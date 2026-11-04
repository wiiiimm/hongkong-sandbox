"""Gate six unchanged originals on complete identity, physical and browser evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-source-review-v1-20261018';DOC=BASE/BATCH
P='government-xl-park-avenue239350-'
def folder(n):return BASE/(P+n+'-20261018')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();names=['identity-roster-v1','interface-review-v1','six-foundations-contacts-v1','joint-validation-v1','native-regression-v1','hoi-yu-prior-review-v2','native-scope-v1','joint-scope-v1','browser-1280-v3','browser-390-v2','fallback-390-v1'];pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in names:
   path=folder(name)/'result.json';r=read(path);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(path)
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 roster=read(folder('identity-roster-v1')/'roster.json')['models'];models={r['uid']:r for r in roster};assert len(models)==len(roster)==6 and all(r['identityAccepted'] for r in roster)
 interface=read(folder('interface-review-v1')/'ROOT-INTERFACE-REVIEW.json');assert interface['sourceSpecificInterfaceInterpretationAccepted']
 deps=read(folder('interface-review-v1')/'dependencies.json')['dependencies'];assert len(deps)==3 and all(v==['landsd/227455:0'] for v in deps.values())
 f=read(folder('six-foundations-contacts-v1')/'summary.json');assert f['allModesPassed'] and len(f['rows'])==24
 assert {(r['uid'],r['mode']) for r in f['rows']}=={(u,m) for u in models for m in ['original','literal','left','balanced']}
 assert all(r['passed'] and r['faces']==r['covered'] and r['buried']==r['upwardBuried']==0 for r in f['rows'])
 candidate=read(folder('joint-validation-v1')/'terrain-candidates.json')[0];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];assert read(folder('joint-validation-v1')/'final-terrain-budget.json')['passed']
 native=read(folder('native-regression-v1')/'native-neighbour-checks.json')['rows'];scope=read(folder('native-scope-v1')/'scope.json')['touchingNativeUids'];assert len(native)==len(set(scope))==38 and {r['uid'] for r in native}==set(scope)
 assert all(r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native)
 failed=[r for r in native if not r['passed']];assert len(failed)==1 and failed[0]['uid']=='landsd/177605:0'
 hoi=read(folder('hoi-yu-prior-review-v2')/'result.json');assert hoi['existingExactSourceSupportReviewVerified'] and hoi['currentSourcesAndDependencyUnchanged'] and hoi['threePodiumCandidateTerrainRegression']==failed[0]
 joint=read(folder('joint-scope-v1')/'scope.json')['jointReviewRequired'];assert all(next(r for r in native if r['uid']==j['uid'])['passed'] for j in joint)
 basic=read(folder('joint-validation-v1')/'neighbour-checks.json')['rows'];raw_basic=[r for r in basic if r['reasons'] and not r['existingNative']];assert {r['uid'] for r in raw_basic}==set(deps)
 browser=[]
 for width in [1280,390]:
  d=folder(f'browser-{width}-v{3 if width==1280 else 2}');report=read(d/'staged-browser.json');assert report['passed'] and not report['errors'];views=[v for v in report['views'] if 'time' in v]
  assert len(views)==12 and {(v['uid'],v['time']) for v in views}=={(u,t) for u in models for t in ['15:00','22:00']}
  for v in views:assert v['sourceSHA256']==models[v['uid']]['sourceSHA256'] and v['active'] and v['visible'] and v['solidAppearance'] and v['fullyFramed'] and not v['fallbackFaces'] and v['pick']==v['collision']==v['uid']
  retained=report['retainedNativeOwnViews'];assert len(retained)==76 and {(v['uid'],v['time']) for v in retained}=={(u,t) for u in scope for t in ['15:00','22:00']}
  assert len(report['jointViews'])==6;browser.append(ref(d/'staged-browser.json'))
 fallback=read(folder('fallback-390-v1')/'staged-browser.json');assert fallback['passed'] and not fallback['errors'];failed=[v for v in fallback['views'] if v.get('phase')=='failed-download'];assert len(failed)==6 and {v['uid'] for v in failed}==set(models) and all(v['fallbackRetained'] and v['fallbackFaces']>0 for v in failed)
 # Require a separately recorded ROOT visual review; automated checks cannot stand in for it.
 image_review=read(folder('browser-image-review-v1')/'review.json');assert image_review['reviewed'] and image_review['sourceSHA256ByUid']=={u:r['sourceSHA256'] for u,r in models.items()}
 assert len(image_review['images'])==12
 for e in image_review['images']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 refs.append(folder('browser-image-review-v1')/'review.json')
 decision=dict(uids=list(models),originalSourceReviewAccepted=True,sourceSHA256ByUid={u:r['sourceSHA256'] for u,r in models.items()},identityRoster=ref(folder('identity-roster-v1')/'roster.json'),supportDependencies=deps,terrainCandidate=candidate,browserEvidence=browser,sourceSpecificReviewEvidence=[ref(folder('interface-review-v1')/'ROOT-INTERFACE-REVIEW.json'),ref(folder('hoi-yu-prior-review-v2')/'result.json')],jointRetainedActorsReviewed=[r['uid'] for r in joint],baseNeighboursReplacedByReviewedOriginals=sorted(deps),rawDiagnosticsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,reviewer='Codex ROOT',limitations=['Exact original-source acceptance only. No global threshold waiver or engineering certification. Guarded publication and live verification remain.'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',decision)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('park_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-six-original-source-acceptance-v1',list(set(refs+[ROOT/p for p in pins])),dict(uids=list(models),originalSourceReviewAccepted=True,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
