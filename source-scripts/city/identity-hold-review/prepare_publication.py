"""Validate explicit reviewed identities and physical decisions; stage, never publish."""
import hashlib, json, pathlib, shutil
ROOT=pathlib.Path(__file__).resolve().parents[3]
HERE=pathlib.Path(__file__).resolve().parent
DOC=ROOT/'docs/astra-city/identity-hold-review'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def main():
 review=read(HERE/'physical-acceptance.json')
 assert review['verticalScale']==1 and review['status']=='approved-native-geometry-subset'
 for p,d in review['inputHashes'].items():assert sha(ROOT/p)==d,'Reviewed evidence changed: '+p
 rows={r['uid']:r for r in review['rows']};assert len(rows)==5
 for r in rows.values():
  assert r['status']=='approved-for-integration'
  assert r['images'],'No inspected screenshot evidence'
  for im in r['images']:assert sha(ROOT/im['path'])==im['sha256'],'Inspected image changed'
 cpu=read(DOC/'cpu-validation.json');assert cpu['checksPassed']==5 and cpu['exceptions']==0
 browser=read(DOC/'browser-terrain/report.json');assert len(browser['views'])==20 and not browser['errors']
 for v in browser['views']:
  assert v['activeUIDs']==v['uids'] and v['boxInsideView'] and not v['cameraCollision'] and not v['uiOverflow']
  assert all(p['uid']==p['hitUid'] for p in v['picking'])
  assert sha(DOC/'browser-terrain'/v['file'])==v['sha256']
 for uid in rows:
  assert {(v['mobile'],v['time']) for v in browser['views'] if uid in v['uids']}=={(False,15),(False,22),(True,15),(True,22)}
 surface={r['uid']:r for r in read(DOC/'surfaces.json')['rows']}
 for uid,r in rows.items():
  stats=surface[uid]['stats']['patched'];assert stats['upwardWhollyBuriedTriangles']==0
  assert stats['whollyBuriedTriangles']==(6 if uid=='landsd/314191:0' else 0)
 k11=surface['landsd/205478:0']['k11'];assert len(k11['rim'])==66
 assert all(r['insideSurveyedPodium'] or r['actualRuntimeVolumeSurfaceDistance']<.15 for r in k11['rim'])
 terrain=read(DOC/'terrain-patches.json');patchuids=set()
 for b in terrain['bundles']:
  assert sha(ROOT/'3d-viewer'/b['parentTerrainURL'])==b['parentSha256'],'Parent terrain changed'
  for p in b['patches']:
   assert sha(ROOT/p['path'])==p['sha256'];patchuids.update(p['uids'])
 assert patchuids=={uid for uid,r in rows.items() if r['requiresTerrainPatch']}
 assert all(c['boundaryError']==0 and c['waterMaskChanges']==0 for c in terrain['checks'])
 terrain.update(publicationApproved=True,approvalEvidence=str((HERE/'physical-acceptance.json').relative_to(ROOT)),approvalSHA256=sha(HERE/'physical-acceptance.json'),approvalScope='Reviewed native part placement only; preserve recorded below-grade foundation geometry and original water mask. Install child terrain and models together, then run combined installed checks.')
 save(HERE/'approved-terrain.json',terrain)
 cat=read(HERE/'identity-approved/catalogue.json');assert set(rows)=={m['uid'] for m in cat['models']}
 existing=set();manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']:existing.update(m['uid'] for m in read(ROOT/'3d-viewer'/url)['models'])
 assert not set(rows)&existing,'UID already published; review current integration rather than duplicate it'
 out=HERE/'approved';out.mkdir(exist_ok=True)
 for m in cat['models']:
  r=rows[m['uid']];src=HERE/'identity-approved'/m['asset'];assert sha(src)==m['sha256'] and src.stat().st_size==m['bytes'];shutil.copyfile(src,out/m['asset'])
  m.update(priority='landmark',placementReviewed=True,identityReviewApproved=True,publicationApproved=True,wholeLandmarkAccepted=False,landmarkMembershipApproved=r['landmarkMembershipApproved'],placementReview=r['placementObservation'],architectureReview=r['architectureObservation'],facadeReview=r['facadeObservation'],supportDependencies=r.get('supportDependencies',[]),requiresTerrainPatch=r['requiresTerrainPatch'],reviewIssue='HKS-214',reviewScope=review['scope'])
  m.pop('remainingReview',None)
 cat['area']='Five source-identity and placement reviewed native parts';save(out/'catalogue.json',cat);save(out/'catalogue-index.json',{'models':5,'catalogues':['catalogue.json']})
 plan={'areas':[{'area':'Identity-resolved native landmark components','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/identity-hold-review/catalogue.json'}]};save(HERE/'publication-plan.json',plan)
 old=read(ROOT/'docs/astra-city/landmark-preflight/report.json');oldrows={p['uid']:p for p in old['parts']}
 pairs=sorted((m['uid'],m['sha256']) for m in cat['models']);snapshot=hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()[:16]
 parts=[]
 for m in cat['models']:
  p=oldrows[m['uid']];parts.append({'uid':m['uid'],'name':m['label'],'landmarkIds':p['landmarkIds'],'classification':['identity-resolved-native-part','placement-reviewed-with-explicit-dependencies'],'knownHold':None,'objectId':m['objectId'],'sourceProgress':'prepared-for-review','candidate':{'sha256':m['sha256'],'asset':str((out/m['asset']).relative_to(ROOT))},'landmarkMembershipApproved':rows[m['uid']]['landmarkMembershipApproved']})
 inventory={'snapshotId':snapshot,'issue':'HKS-214','parts':parts,'derivedFrom':'Sorted five UID/SHA256 pairs encoded as compact JSON','previousSnapshotUnmodified':old['snapshotId'],'publicationPerformed':False};save(DOC/'supplemental-source-inventory.json',inventory)
 guard={'issue':'HKS-214','published':False,'uids':sorted(rows),'reviewSHA256':sha(HERE/'physical-acceptance.json'),'inputHashes':review['inputHashes'],'capturedRuntimeHashes':browser['runtimeHashes'],'planSHA256':sha(HERE/'publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'terrainBundle':str((HERE/'approved-terrain.json').relative_to(ROOT)),'terrainBundleSHA256':sha(HERE/'approved-terrain.json'),'modelBytes':sum(m['bytes'] for m in cat['models']),'nativeTriangles':sum(m['triangles'] for m in cat['models']),'assets':[{'uid':m['uid'],'source':str((out/m['asset']).relative_to(ROOT)),'sha256':m['sha256'],'bytes':m['bytes']} for m in cat['models']],'requiredNextStep':'Root verifies guard, installs required terrain children and native models together using existing publisher, retains K11 fallback UID256535, then verifies actual installed runtime and neighbour terrain. No deployment or publication performed here.'}
 for name,value in [('guard.json',guard),('publication-plan.json',plan),('approved-catalogue.json',cat),('approved-terrain.json',terrain)]:save(DOC/name,value)
 save(HERE/'guard.json',guard);print(json.dumps({'approved':5,'terrainChildren':len(patchuids),'bytes':guard['modelBytes'],'triangles':guard['nativeTriangles'],'supplementalSnapshot':snapshot,'published':False}))
if __name__=='__main__':main()
