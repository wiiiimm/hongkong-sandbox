"""Validate reviewed Whampoa evidence; stage guarded assembly publication, never write live assets."""
import pathlib,json,hashlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/whampoa-special'
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
assert reservations.owns(read(pathlib.Path('/tmp/astra-whampoa-lease.json')))
cat=read(HERE/'candidates/catalogue.json');uids={m['uid']for m in cat['models']};assert uids=={'landsd/144948:0','landsd/225581:0'}
source=read(HERE/'staged/11-NE-21C/manifest.json');envelopes=read(DOC/'height-envelopes.json');observations=read(HERE/'visual-acceptance.json');assert observations['status']=='approved-native-assembly' and observations['verticalScale']==1
for m in source['models']:
 for p,h in m['sourceHashes'].items():assert sha(HERE/'staged/11-NE-21C'/p)==h
support=read(DOC/'support.json');assert support['rows'][0]['contacts']==56 and support['rows'][0]['total']==60 and support['rows'][0]['maxDistance']<.523
surface=read(DOC/'surfaces.json');assert all(r['stats']['patched']['whollyBuriedTriangles']==0 for r in surface['rows'])
terrain=read(DOC/'terrain-patches.json');assert len(terrain['checks'])==1;check=terrain['checks'][0];assert check['nativeCoveredNodes']==check['gridNodes'] and check['boundaryError']==0 and check['waterMaskChanges']==0
for folder in ['browser-terrain','browser-isolated']:
 report=read(DOC/folder/'report.json');assert not report['errors'] and len(report['views'])==6
 for v in report['views']:
  assert sha(DOC/folder/v['file'])==v['sha256']
  if v['phase']=='after':assert set(v['activeUIDs'])==uids and all(p['uid']==p['hitUid'] for p in v['picking'])
out=HERE/'approved';out.mkdir(exist_ok=True)
for m in cat['models']:
 src=HERE/'candidates'/m['asset'];assert sha(src)==m['sha256'];shutil.copyfile(src,out/m['asset'])
 m.update(priority='landmark',placementReviewed=True,identityReviewApproved=True,sourceIdentityReviewed=True,publicationApproved=True,reviewIssue='HKS-219',proceduralWindows=False,supportDependencies=[{'uid':'landsd/225581:0','state':'candidate'}]if m['uid']=='landsd/144948:0'else [],wholeLandmarkComplete=False,architectureReview=observations['models'][m['uid']],heightEnvelopeReview='Native mesh envelope and footprint base/top differ; both retained unchanged. See HKS-219 source height band evidence.')
cat['loadingPolicy']='Reviewed native assembly; both source parts and native terrain must publish together.';save(out/'catalogue.json',cat);save(out/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']})
p=terrain['bundles'][0]['patches'][0];plan={'areas':[{'area':'The Whampoa special landmark ship','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/whampoa-special/catalogue.json'}],'topLevelTerrainPatches':[{'area':'The Whampoa surveyed native terrain','source':p['path'],'sha256':p['sha256'],'destination':'city/data/terrain-whampoa-ship.json','resolution':1}]};save(HERE/'publication-plan.json',plan)
inputs=[HERE/'visual-acceptance.json',DOC/'support.json',DOC/'surfaces.json',DOC/'height-envelopes.json',DOC/'native-terrain.json',DOC/'terrain-patches.json',DOC/'browser-terrain/report.json',DOC/'browser-isolated/report.json',HERE/'candidates/catalogue.json']
guard={'issue':'HKS-219','uids':sorted(uids),'sourceParts':2,'triangles':sum(m['triangles']for m in cat['models']),'compressedBytes':sum(m['bytes']for m in cat['models']),'inputHashes':{str(p.relative_to(ROOT)):sha(p)for p in inputs},'planSHA256':sha(HERE/'publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'status':'approved-for-guarded-integration','published':False,'verticalScale':1,'remaining':['Root applies guarded publisher with live source receipt, then verifies installed picking/collision/streaming.','Photographic texture, signage and authentic decorative lighting are not included in this non-textured native geometry pass.','This special request is separate from the original 213-landmark baseline.']};save(DOC/'guard.json',guard);save(DOC/'publication-plan.json',plan);print(json.dumps({k:v for k,v in guard.items()if k!='inputHashes'}))
