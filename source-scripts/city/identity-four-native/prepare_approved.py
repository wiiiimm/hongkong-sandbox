"""Stage five reviewed native components and one atomic support migration; no live writes."""
import pathlib,json,hashlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-four-native';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
for path in ['/tmp/astra-identity-four-review-lease.json','/tmp/astra-identity-four-elements-lease.json','/tmp/astra-identity-four-dependent-lease.json']:assert reservations.owns(read(pathlib.Path(path)))
accept=read(HERE/'visual-acceptance.json');assert accept['status']=='approved-for-integration'
cat=read(HERE/'review-candidates/catalogue.json');uids={m['uid']for m in cat['models']};assert len(uids)==5;support=read(DOC/'support.json');rows={r['uid']:r for r in support['rows']}
for u,n in [('landsd/203728:0',499),('landsd/203724:0',566),('landsd/37369:0',42),('landsd/204153:0',41)]:assert rows[u]['contacts']==rows[u]['rimSamples']==n and rows[u]['maxDistance']<.5
assert all(e['supportedNativeComponent']for e in read(DOC/'oakhill-connectivity.json')['exceptions'])
surfaces=read(DOC/'surfaces.json');assert all(r['stats']['patched']['whollyBuriedTriangles']==0 for r in surfaces['rows'])
desktop=read(DOC/'browser-terrain/report.json');assert len(desktop['views'])==12 and not desktop['errors'] and all(not v['mobile']for v in desktop['views']);assert desktop['failureState']['stats']['errors']==[]
mobile=read(DOC/'browser-mobile-targeted/report.json');assert len(mobile['views'])==8 and not mobile['errors'] and not mobile.get('failureState')
for report,folder in [(desktop,'browser-terrain'),(mobile,'browser-mobile-targeted')]:
 for v in report['views']:
  assert sha(DOC/folder/v['file'])==v['sha256']
  if v['phase']=='after':assert set(v['activeUIDs'])==set(v['uids']) and all(p['uid']==p['hitUid']for p in v['picking'])
terrain=read(DOC/'terrain-patches.json');check=terrain['checks'][0];assert check['boundaryError']==check['waterMaskChanges']==0 and check['nativeCoveredNodes']==220473 and check['gridNodes']==236181
out=HERE/'approved';out.mkdir(exist_ok=True)
for m in cat['models']:
 src=HERE/'review-candidates'/m['asset'];assert sha(src)==m['sha256'];shutil.copyfile(src,out/m['asset']);m.update(priority='landmark',placementReviewed=True,identityReviewApproved=True,sourceIdentityReviewed=True,publicationApproved=True,reviewIssue='HKS-214',architectureReview=accept['models'][m['uid']],wholeLandmarkComplete=False)
cat['loadingPolicy']='Guarded coherent native assembly with actual support dependencies and adjacent native terrain patch.';save(out/'catalogue.json',cat);save(out/'catalogue-index.json',{'models':5,'catalogues':['catalogue.json']})
review=read(HERE/'dependency-replacements.json')
for c in review['catalogues']:assert sha(ROOT/c['source'])==c['oldSHA256'],'Existing catalogue changed; refresh migration sidecar'
assert review['contactReportSHA256']==sha(DOC/'support.json')
approval={'issue':'HKS-214','status':'approved-for-integration','observation':accept['existingDependencyMigration'],'sourceGeometryChanged':False,'supportEvidenceSHA256':sha(DOC/'support.json')};save(HERE/'migration-approval.json',approval)
p=terrain['bundles'][0]['patches'][0];plan={'areas':[{'area':'Four named tower source upgrades and Elements native support','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/identity-four-native/catalogue.json'}],'topLevelTerrainPatches':[{'area':'Elements native terrain adjacent to station','source':p['path'],'sha256':p['sha256'],'destination':'city/data/terrain-elements-native.json','resolution':1}],'dependencyReviews':[{'path':str((HERE/'dependency-replacements.json').relative_to(ROOT)),'sha256':sha(HERE/'dependency-replacements.json'),'visualApproval':{'path':str((HERE/'migration-approval.json').relative_to(ROOT)),'sha256':sha(HERE/'migration-approval.json')}}]};save(HERE/'publication-plan.json',plan)
inputs=[HERE/'visual-acceptance.json',DOC/'support.json',DOC/'surfaces.json',DOC/'identity-geometry.json',DOC/'oakhill-connectivity.json',DOC/'elements-native-terrain.json',DOC/'terrain-patches.json',DOC/'browser-terrain/report.json',DOC/'browser-mobile-targeted/report.json'];guard={'issue':'HKS-214','status':'approved-for-guarded-integration','newNativeUids':sorted(uids),'existingMetadataOnlyUids':['landsd/204153:0'],'sourceParts':5,'compressedBytes':sum(m['bytes']for m in cat['models']),'triangles':sum(m['triangles']for m in cat['models']),'inputHashes':{str(p.relative_to(ROOT)):sha(p)for p in inputs},'planSHA256':sha(HERE/'publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'published':False,'verticalScale':1,'remaining':'Root guarded publication and installed scene/collision/streaming checks; no whole-region completion claim.'};save(DOC/'guard.json',guard);save(DOC/'publication-plan.json',plan);print({k:v for k,v in guard.items()if k!='inputHashes'})
