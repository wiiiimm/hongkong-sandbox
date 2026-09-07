"""Verify review hashes and stage the three approved source models. Never publishes.
Run immediately before the root task applies the existing guarded publisher.
"""
import hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
DOC=ROOT/'docs/astra-city/landmark-visual-review'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def main():
 review=read(HERE/'visual-acceptance.json');assert review['verticalScale']==1
 for path,digest in review['inputHashes'].items():assert sha(ROOT/path)==digest,'Review input changed: '+path
 for row in review['rows']:
  assert row['status']=='accept-native-geometry-with-local-terrain-followup'
  for image in row['images']:assert sha(ROOT/image['path'])==image['sha256'],'Review image changed'
 browser=read(DOC/'browser/after/verification.json');before=read(DOC/'browser/before/verification.json');assert browser['result']==before['result']=='passed' and not browser['errors']
 v=read(DOC/'hks209-validation.json');assert v['checksPassed']==3 and not v['concerns'] and not v['exceptions']
 source=ROOT/'source-scripts/city/architecture-followup/compact/catalogue.json';c=read(source);uids={r['uid']for r in review['rows']}
 assert uids=={m['uid']for m in c['models']}=={m['uid']for a in browser['areas']for m in a['models']}
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');existing=set()
 for url in manifest['officialModelCatalogues']:existing.update(m['uid']for m in read(ROOT/'3d-viewer'/url)['models'])
 assert not uids&existing,'Already published source UID'
 out=HERE/'approved';out.mkdir(exist_ok=True);observations={r['uid']:r for r in review['rows']}
 for m in c['models']:
  asset=source.parent/m['asset'];assert sha(asset)==m['sha256'] and asset.stat().st_size==m['bytes'];target=out/m['asset']
  if target.exists():assert sha(target)==m['sha256'],'Different existing staged asset'
  else:shutil.copyfile(asset,target)
  # Geometry/source bytes stay unchanged. Only explicit review metadata changes.
  m['placementReviewed']=True;m['priority']='landmark';m['placementReview']=observations[m['uid']]['observation'];m['terrainResidualReview']={k:observations[m['uid']][k]for k in ['sourceBottomHKPD','sampledGroundHKPD','maxSampledBaseGapM','maxSampledBaseBurialM']}
 save(out/'catalogue.json',c);save(out/'catalogue-index.json',{'models':3,'catalogues':['catalogue.json']})
 destination='city/data/official-models/asia-society-followup/catalogue.json';assert not (ROOT/'3d-viewer'/destination).exists(),'Publication destination already exists'
 plan={'areas':[{'area':'Asia Society HKS-209 follow-up','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':destination}]};save(HERE/'publication-plan.json',plan)
 guard={'issue':'HKS-209','published':False,'reviewSha256':sha(HERE/'visual-acceptance.json'),'inputHashes':review['inputHashes'],'planSha256':sha(HERE/'publication-plan.json'),'catalogueSha256':sha(out/'catalogue.json'),'uids':sorted(uids),'modelBytes':sum(m['bytes']for m in c['models']),'assets':[{'uid':m['uid'],'source':str((out/m['asset']).relative_to(ROOT)),'destination':str(pathlib.PurePosixPath(destination).parent/m['asset']),'sha256':m['sha256'],'bytes':m['bytes']}for m in c['models']],'requiredNextStep':'Root applies existing publisher then verifies installed route; no publication was performed by this script.'};save(HERE/'guard.json',guard);save(DOC/'guard.json',guard);save(DOC/'publication-plan.json',plan);save(DOC/'approved-catalogue.json',c);print(json.dumps({'staged':3,'bytes':guard['modelBytes'],'published':False,'hashesVerified':True}))
if __name__=='__main__':main()
