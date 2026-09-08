"""Stage manually accepted native source parts; never modify runtime or review ledgers."""
import argparse, hashlib, json, pathlib, shutil, sys
ROOT=pathlib.Path(__file__).resolve().parents[3]; HERE=pathlib.Path(__file__).resolve().parent
DOC=ROOT/'docs/astra-city/grounded-framing-review'; SOURCE=ROOT/'source-scripts/city/grounded-model-review'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',type=pathlib.Path,required=True);args=parser.parse_args()
 sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
 lease=read(args.lease_file); assert reservations.owns(lease),'Reservation lost'
 review=read(HERE/'visual-acceptance.json'); rows={r['uid']:r for r in review['rows']}; assert review['verticalScale']==1
 assert set('building:'+u for u in rows)<=set(lease['resources'])
 for path,digest in review['inputHashes'].items(): assert sha(ROOT/path)==digest,'Reviewed input changed: '+path
 for row in rows.values():
  for image in row['images']: assert sha(ROOT/image['path'])==image['sha256'],'Inspected capture changed'
 verification=read(DOC/'verification.json');assert verification['verifiedParts']==24 and verification['verifiedScreenshots']==48
 assert all(r['sourceComponentInspectable'] and r['isolatedCameraClear'] and r['bothViewsContainWholeBounds'] for r in verification['rows'])
 before=read(ROOT/'docs/astra-city/grounded-model-review/browser/before/verification.json');after=read(ROOT/'docs/astra-city/grounded-model-review/browser/after/verification.json');assert before['result']==after['result']=='passed'
 checked={m['uid']:m for a in after['areas'] for m in a['models']}; assert set(checked)==set(rows)
 assert all(m['active'] and m['visible'] and m['pick']==u for u,m in checked.items())
 preflight=read(ROOT/'docs/astra-city/landmark-preflight/report.json');cpu={p['uid']:p for p in preflight['parts']}
 assert all('cpu-clear-awaiting-visual-review' in cpu[u]['classification'] and not cpu[u]['cpu']['concerns'] for u in rows)
 catalogue=read(SOURCE/'candidates/catalogue.json');catalogue['models']=[m for m in catalogue['models'] if rows[m['uid']]['status']=='approved-native-source-part']
 uids={m['uid'] for m in catalogue['models']};assert uids
 existing=set();manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']: existing.update(m['uid'] for m in read(ROOT/'3d-viewer'/url)['models'])
 assert not uids&existing,'Source UID already installed'
 assert reservations.owns(lease),'Reservation lost before staging'
 out=HERE/'approved';out.mkdir(exist_ok=True)
 for m in catalogue['models']:
  asset=SOURCE/'candidates'/m['asset'];assert sha(asset)==m['sha256'] and asset.stat().st_size==m['bytes'];shutil.copyfile(asset,out/m['asset']);r=rows[m['uid']]
  m.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=not r['proposedIdentity'],publicationApproved=True,reviewIssue='HKS-214',reviewScope=review['scope'],architectureReview=r['architectureObservation'],placementReview=r['placementObservation'],facadeReview='Existing procedural windows are illustrative; no surveyed facade or storey-count approval.',wholeLandmarkComplete=False)
 catalogue['counts']['packedModels']=len(uids);save(out/'catalogue.json',catalogue);save(out/'catalogue-index.json',{'models':len(uids),'catalogues':['catalogue.json']})
 destination='city/data/official-models/grounded-review-20260909/catalogue.json';assert not (ROOT/'3d-viewer'/destination).exists()
 plan={'areas':[{'area':'Grounded native source parts after camera-safe review','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':destination}]};save(HERE/'publication-plan.json',plan)
 guard={'issue':'HKS-214','published':False,'uids':sorted(uids),'held':[u for u,r in rows.items() if r['status']!='approved-native-source-part'],'reviewSHA256':sha(HERE/'visual-acceptance.json'),'inputHashes':review['inputHashes'],'planSHA256':sha(HERE/'publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'modelBytes':sum(m['bytes'] for m in catalogue['models']),'nativeTriangles':sum(m['triangles'] for m in catalogue['models']),'assets':[{'uid':m['uid'],'source':str((out/m['asset']).relative_to(ROOT)),'sha256':m['sha256'],'bytes':m['bytes']} for m in catalogue['models']],'requiredNextStep':'Root verifies guard, applies existing publisher and checks representative installed scene after road changes. This source-part approval does not approve proposed landmark membership or finish any whole landmark.'}
 save(HERE/'guard.json',guard);save(DOC/'approved-catalogue.json',catalogue);save(DOC/'guard.json',guard);save(DOC/'publication-plan.json',plan);print(json.dumps({'approved':len(uids),'held':guard['held'],'bytes':guard['modelBytes'],'triangles':guard['nativeTriangles'],'published':False}))
if __name__=='__main__': main()
