"""Compose exact four-original source acceptance; guarded publication remains separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nobhill-source-review-v1-20261018';DOC=BASE/BATCH
NAMES=['government-xl-nobhill-interface-grade-review-v1-20261018','government-xl-nobhill-source-identity-review-v1-20261018','government-xl-nobhill-tower-identity-v1-20261018','government-xl-nobhill-joint-validation-v2-20261018','government-xl-nobhill98845-native-scope-v1-20261018','government-xl-nobhill-browser-1280-v1-20261018','government-xl-nobhill-browser-390-v1-20261018','government-xl-nobhill-fallback-390-v1-20261018']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def checked(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 joint=BASE/NAMES[3];selection=checked(joint/'selection.json.gz');rows=selection['rows'];models={r['uid']:r for r in rows};assert len(models)==len(rows)==4
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest);roster=[]
 for row in rows:
  uid=row['uid'];sha=row['sourceSHA256'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset);tile=ROOT/'3d-viewer'/row['source']['tile'];assert row['source']['building']in checked(tile)['buildings']
  if uid=='landsd/98845:0':
   path=BASE/NAMES[1]/'ROOT-IDENTITY-REVIEW.json';identity=checked(path);assert identity['identityAccepted'] and identity['manifestSHA256']==selection['manifestSHA256']
  else:
   path=BASE/NAMES[2]/(uid.split('/')[1]+'.json');identity=checked(path)['identity'];assert identity['passed'] and not identity['reasons'];assert identity['exactRouteManifestSHA256']==selection['manifestSHA256']
  assert identity['uid']==uid and identity['sourceSHA256']==sha==row['candidate']['entry']['sha256'];key=row['native']['cacheKey']+'/'+row['modelId'];roster.append(dict(uid=uid,sourceSHA256=sha,sourceKey=key,modelId=row['modelId'],buildingCSUID=row['candidate']['entry']['buildingCSUID'],identityAccepted=True,identityEvidence=ref(path)))
 reviewpath=BASE/NAMES[0]/'ROOT-INTERFACE-GRADE-REVIEW.json';interface=checked(reviewpath);sources={u:r['sourceSHA256']for u,r in models.items()};assert interface['sourceSHA256ByUid']==sources and interface['sourceSpecificInterfaceInterpretationAccepted'] and interface['sourceSpecificGradeInterpretationAccepted'];deps=interface['supportDependencies'];assert deps=={u:['landsd/98845:0']for u in models if u!='landsd/98845:0'}
 v=checked(joint/'validation.json');assert v['loaderAccepted']==v['checksPassed']==4 and v['exceptions']==0;basic=checked(joint/'neighbour-checks.json')['rows'];assert len(basic)==37 and all(not r['reasons']for r in basic)
 scope=checked(BASE/NAMES[4]/'scope.json');assert scope['allCurrentActorsNominated'] and scope['touchingNativeUids']==[];candidate=checked(joint/'terrain-candidates.json')[0];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];refs.append(ROOT/candidate['path']);assert candidate['bounds']==scope['changedParentExtent']
 second=module('nob_final_terrain_contract',HERE/'xl-second-pass.py');parent=ROOT/'3d-viewer/city/data/terrain.json';patch=read(ROOT/candidate['path']);second.resolution.validate_patch(patch,checked(parent));save(DOC/'terrain-validation.json',dict(passed=True,validator='xl-second-pass.resolution.validate_patch',source=ref(ROOT/candidate['path']),currentParent=ref(parent),triangles=len(patch['nativeMesh']['index'])//3,publication=False));refs.append(HERE/'xl-second-pass.py')
 browsers=[]
 for name,width in zip(NAMES[5:7],[1280,390]):
  path=BASE/name/'staged-browser.json';report=checked(path);assert report['passed'] and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==8 and {(v['uid'],v['time'])for v in views}=={(u,t)for u in models for t in ['15:00','22:00']}
  assert len(report['jointViews'])==4
  for v in views:assert v['sourceSHA256']==sources[v['uid']] and v['active'] and v['visible'] and v['solidAppearance'] and v['fullyFramed'] and not v['fallbackFaces'] and v['pick']==v['collision']==v['uid']
  browsers.append(ref(path))
 fallbackpath=BASE/NAMES[7]/'staged-browser.json';fallback=checked(fallbackpath);failed=[v for v in fallback['views']if v.get('phase')=='failed-download'];assert fallback['passed'] and not fallback['errors'] and len(failed)==4 and {v['uid']for v in failed}==set(models) and all(v['fallbackRetained'] and v['fallbackFaces']>0 for v in failed)
 for e in interface['inspectedBrowserImages']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
 save(DOC/'roster.json',dict(models=roster));save(DOC/'ROOT-SOURCE-REVIEW.json',dict(uids=list(models),originalSourceReviewAccepted=True,sourceSHA256ByUid=sources,identityRoster=ref(DOC/'roster.json'),supportDependencies=deps,terrainCandidate=candidate,browserEvidence=browsers,fallbackEvidence=ref(fallbackpath),sourceSpecificReviewEvidence=[ref(reviewpath)],rawDiagnosticsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,reviewer='Codex ROOT',limitations=['Exact source-specific original acceptance only; raw generic foundation/interface failures remain in bound evidence. No global threshold change or engineering certification.','Guarded publication and live verification remain required.']))
 for p in refs:
  rel=str(p.relative_to(ROOT))
  if rel in pins:assert digest(p.read_bytes())==pins[rel]
 out=module('nob_source_accept_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nobhill-four-unchanged-original-source-acceptance-v1',list(dict.fromkeys(refs)),dict(uids=list(models),originalSourceReviewAccepted=True,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
