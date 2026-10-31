"""Prepare guarded publication only from explicitly authored visual decisions; no live writes."""
import json,pathlib,hashlib,shutil,sys,argparse
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
read=lambda p:json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',action='append',type=pathlib.Path,required=True);args=p.parse_args();sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
 leases=[read(p)for p in args.lease_file];assert all(reservations.owns(l)for l in leases);resources={k for l in leases for k in l['resources']};review=read(HERE/'visual-acceptance.json');assert review['status']=='approved-native-source-components' and review['verticalScale']==1
 rows={r['uid']:r for r in review['rows']};uids={u for u,r in rows.items()if r['status']=='approved-native-source-component'};assert uids and {'building:'+u for u in uids}<=resources
 for path,digest in review['inputHashes'].items():assert sha(ROOT/path)==digest,'Reviewed input changed: '+path
 for row in rows.values():
  for image in row['images']:assert sha(ROOT/image['path'])==image['sha256'],'Reviewed image changed'
 framing=read(DOC/'bulk-framing/report.json');assert not framing['errors'];byuid={r['uid']:r for r in framing['rows']};support={r['uid']:r for r in read(DOC/'decisions.json')['rows']};catalogue=read(HERE/'review-candidates/catalogue.json');models={m['uid']:m for m in catalogue['models']};manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid']for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};assert not uids&installed
 for url in manifest['officialModelCatalogues']:
  for model in read(ROOT/'3d-viewer'/url)['models']:
   for dependency in model.get('supportDependencies',[]):
    d={'uid':dependency,'state':'fallback'}if isinstance(dependency,str)else dependency
    assert not(d['state']in ('fallback','surveyed-footprint-fallback')and d['uid']in uids),'Existing native dependent needs reviewed metadata migration: '+model['uid']+' -> '+d['uid']
 for uid in uids:
  assert support[uid]['placementApproved'];views=byuid[uid]['views'];assert len(views)==2
  for v in views:assert v['active'] and v['nativeGeometryUnchanged'] and v['final']['fullyFramed'] and v['final']['clear']
  for dependency in support[uid]['supportDependencies']:
   if dependency['state']=='candidate':assert dependency['uid']in uids|installed,'Missing native support dependency'
   if dependency['state']=='surveyed-footprint-fallback':assert dependency['uid']not in uids|installed,'Required fallback has been replaced'
 out=HERE/'approved';out.mkdir(exist_ok=True);approved=[]
 for uid in sorted(uids):
  m=dict(models[uid]);asset=HERE/'review-candidates'/m['asset'];assert sha(asset)==m['sha256'] and asset.stat().st_size==m['bytes'];shutil.copyfile(asset,out/m['asset']);m.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=support[uid]['landmarkMembershipApproved'],publicationApproved=True,supportDependencies=support[uid]['supportDependencies'],reviewIssue='HKS-214',architectureReview=rows[uid]['observation'],reviewScope=review['scope'],wholeLandmarkComplete=False);approved.append(m)
 catalogue['models']=approved;catalogue['counts']['packedModels']=len(approved);save(out/'catalogue.json',catalogue);save(out/'catalogue-index.json',{'models':len(approved),'catalogues':['catalogue.json']})
 patch=HERE/'roof-review-54170-0.json';terrain_url='city/data/terrain-lohas-club-galaxy.json';plan={'areas':[{'area':'Reviewed native support assemblies','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/native-support-review-20260909/catalogue.json'}],'topLevelTerrainPatches':[{'area':'LOHAS Club Galaxy source terrain','source':str(patch.relative_to(ROOT)),'destination':terrain_url,'sha256':sha(patch),'resolution':1}]};save(HERE/'publication-plan.json',plan)
 guard={'issue':'HKS-214','published':False,'uids':sorted(uids),'heldUids':sorted(set(rows)-uids),'reviewSHA256':sha(HERE/'visual-acceptance.json'),'inputHashes':review['inputHashes'],'planSHA256':sha(HERE/'publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'modelBytes':sum(m['bytes']for m in approved),'triangles':sum(m['triangles']for m in approved),'terrainSHA256':sha(patch),'requiredNextStep':'Root runs publisher and installed scene/picking/collision/streaming checks including simultaneous native support availability. Source geometry approval does not finish landmark membership, facades or regions.'};save(HERE/'guard.json',guard);save(DOC/'guard.json',guard);save(DOC/'approved-catalogue.json',catalogue);save(DOC/'publication-plan.json',plan);print(json.dumps({'approved':len(approved),'bytes':guard['modelBytes'],'triangles':guard['triangles'],'published':False}))
if __name__=='__main__':main()
