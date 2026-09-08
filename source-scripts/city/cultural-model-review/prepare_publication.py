"""Stage the explicitly reviewed five-part subset and a guarded plan. Never publish."""
import hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/cultural-model-review'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 review=read(HERE/'visual-acceptance.json');assert review['verticalScale']==1 and review['status']=='approved-native-geometry-subset'
 for p,d in review['inputHashes'].items():assert sha(ROOT/p)==d,'Reviewed input changed: '+p
 for row in review['rows']:
  assert row['status']=='approved-native-geometry';assert row['proceduralWindows'] is False
  for image in row['images']:assert sha(ROOT/image['path'])==image['sha256'],'Inspected image changed'
 cpu=read(DOC/'cpu-validation.json');assert cpu['checksPassed']==5 and cpu['exceptions']==0
 assert cpu['concerns']=={'sampled-ground-gap-below-model-bottom':1}
 context=read(DOC/'context.json');assert context['support']['samples']==context['support']['actualTriangleHits']==context['support']['within05m']==1314
 reports=[read(DOC/'browser/report.json'),read(DOC/'browser/foundations.json')]
 assert [len(r['views'])for r in reports]==[24,4] and not any(r['errors']for r in reports)
 for r in reports:
  for view in r['views']:
   assert not view['cameraCollision'] and not view['uiOverflow']
   assert set(view['activeUIDs'])==(set(view['uids']) if view['phase']=='after' else set())
 catalogue=read(HERE/'candidates/catalogue.json');uids={r['uid']for r in review['rows']};assert uids=={m['uid']for m in catalogue['models']}
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');existing=set()
 for url in manifest['officialModelCatalogues']:existing.update(m['uid']for m in read(ROOT/'3d-viewer'/url)['models'])
 assert not uids&existing,'Already published source UID'
 rows={r['uid']:r for r in review['rows']};out=HERE/'approved';out.mkdir(exist_ok=True)
 for m in catalogue['models']:
  asset=HERE/'candidates'/m['asset'];assert sha(asset)==m['sha256'] and asset.stat().st_size==m['bytes'];shutil.copyfile(asset,out/m['asset'])
  r=rows[m['uid']];m.update(priority='landmark',placementReviewed=True,identityReviewApproved=True,publicationApproved=True,proceduralWindows=False,placementReview=r['placementObservation'],facadeReview=r['facadeObservation'],architectureReview=r['architectureObservation'],reviewIssue='HKS-214',reviewScope='Native exterior geometry and source placement, not photoreal materials or complete interior/campus acceptance')
 save(out/'catalogue.json',catalogue);save(out/'catalogue-index.json',{'models':len(uids),'catalogues':['catalogue.json']})
 destination='city/data/official-models/west-kowloon-cultural-review/catalogue.json';assert not (ROOT/'3d-viewer'/destination).exists()
 plan={'areas':[{'area':'West Kowloon cultural native model upgrades','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':destination}]};save(HERE/'publication-plan.json',plan)
 guard={'issue':'HKS-214','published':False,'uids':sorted(uids),'reviewSHA256':sha(HERE/'visual-acceptance.json'),'inputHashes':review['inputHashes'],'planSHA256':sha(HERE/'publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'modelBytes':sum(m['bytes']for m in catalogue['models']),'nativeTriangles':sum(m['triangles']for m in catalogue['models']),'assets':[{'uid':m['uid'],'source':str((out/m['asset']).relative_to(ROOT)),'sha256':m['sha256'],'bytes':m['bytes']}for m in catalogue['models']],'requiredNextStep':'Root verifies guard and applies existing island-detail-integration publisher, then verifies installed routes. No publication performed here.'}
 save(HERE/'guard.json',guard);save(DOC/'approved-catalogue.json',catalogue);save(DOC/'publication-plan.json',plan);save(DOC/'guard.json',guard);print(json.dumps({'approved':len(uids),'bytes':guard['modelBytes'],'triangles':guard['nativeTriangles'],'published':False}))
if __name__=='__main__':main()
