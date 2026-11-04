"""Bind optional BASIC fallback ownership to exact reviewed source/compound pairs."""
import re

KEYS={'uid','buildingCSUID','sourceSHA256','suppressorUid','suppressorSourceSHA256'}
HASH=re.compile(r'[0-9a-f]{64}')


def validated(rows):
 assert isinstance(rows,list),'BASIC protections must be an array'
 seen=set()
 for row in rows:
  assert isinstance(row,dict) and set(row)==KEYS,'Unexpected BASIC protection fields'
  assert all(isinstance(row[k],str) and 0<len(row[k])<=200 for k in ['uid','buildingCSUID','suppressorUid']),'Invalid BASIC protection identity'
  assert row['uid']!=row['suppressorUid'],'A source cannot protect BASIC against itself'
  assert all(isinstance(row[k],str) and HASH.fullmatch(row[k]) for k in ['sourceSHA256','suppressorSourceSHA256']),'Invalid BASIC protection source SHA'
  pair=(row['uid'],row['suppressorUid']);assert pair not in seen,'Duplicate BASIC protection pair';seen.add(pair)
 return rows


def stage_basic_fallback_protections(root,plan,original,manifest,edits,new_models,report,load,sha):
 proposed=validated(plan.get('basicFallbackProtections',[]))
 previous=validated(original.get('basicFallbackProtections',[]))
 if not proposed and not previous:return
 current={};paths={}
 for url in original.get('officialModelCatalogues',[]):
  path=root/'3d-viewer'/url
  for model in load(path)['models']:
   assert model['uid'] not in current,'Ambiguous installed source identity'
   current[model['uid']]=model;paths[model['uid']]=path
 all_models={**current,**new_models}
 combined=validated([*previous,*proposed])
 for row in combined:
  target=all_models.get(row['uid']);owner=current.get(row['suppressorUid'])
  assert target and owner,'BASIC protection requires exact target and installed compound'
  assert target['sha256']==row['sourceSHA256'] and target['buildingCSUID']==row['buildingCSUID'],'Stale BASIC target source identity'
  assert owner['sha256']==row['suppressorSourceSHA256'],'Stale BASIC compound source identity'
  assert row['uid'] in owner.get('suppressesBuildingUids',[]),'Compound does not suppress target BASIC'
  path=paths[owner['uid']]
  assert sha(path.parent/owner['asset'])==row['suppressorSourceSHA256'],'Installed compound bytes changed'
  if path in edits:
   import json
   staged=json.loads(edits[path]);matches=[m for m in staged['models']if m['uid']==owner['uid']]
   assert matches==[owner],'BASIC protection cannot rewrite retained compound metadata'
 for row in proposed:
  assert row['uid'] in new_models,'New BASIC protection must accompany its new original installation'
  target=new_models[row['uid']]
  assert target.get('publicationApproved')is True and target.get('placementReviewed')is True and target.get('identityReviewApproved')is True,'BASIC protection requires accepted new original'
 manifest['basicFallbackProtections']=combined
 report['basicFallbackProtections']={'retained':len(previous),'added':proposed}
