"""Prepare separate browser stage for two physically accepted unchanged originals."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from miami_two_related_podium_identity_20261009 import verify_collection,UIDS
BATCH='government-xl-miami-two-original-staged-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-miami-two-complete-original-physical-20261009'
LOCAL=HERE/'local/government-xl-miami-two-complete-original-physical-20261009'
def sha(p):return digest(Path(p).read_bytes())
def rel(p):return str(Path(p).relative_to(ROOT))
def main():
 assert not DOC.exists() and not STAGE.exists(),'Use a new stage after any completed checkpoint'
 result=read(PHYSICAL/'result.json');assert result['jobId']=='d75a4c0ec6d0bf7641f963d41e4a761cc32eded1eab84b99dca37a76b0ec67bb' and result['scriptFullAcceptancePassed'] and not result['reasons']
 for r in result['evidenceRefs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
 proof=verify_collection();assert proof['identityAccepted'];manifest=sha(ROOT/'3d-viewer/city/data/manifest.json');assert manifest==proof['currentManifestSHA256']
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');scope={r['building']['uid'] for r in neighbours['rows']}|UIDS
 claim=reservations.claim('miami-two-stage-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope)],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation']
 try:
  selection=read(LOCAL/'frozen-inputs/check-selection.json.gz');assert selection['manifestSHA256']==manifest
  catalogue=read(LOCAL/'catalogue.json');sources=read(LOCAL/'source-forms.json');assert {m['uid'] for m in catalogue['models']}==UIDS
  forms=[]
  for m in catalogue['models']:
   assert not m.get('suppressesBuildingUids')
   m.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=False,proceduralWindows=False,placementReview='Complete exact original bytes and authored horizontal yaw; source-specific explicit original podium identity; all current actors retained and independently checked. Complete current terrain/foundation/runtime and 18 neighbours passed. No source geometry edits.')
   p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(LOCAL/m['asset'],p);assert sha(p)==m['sha256']
   b=dict(sources[m['uid']]['building']);b['tile']=Path(sources[m['uid']]['tile']).stem;forms.append(b)
  catalogue.update(area='Miami Beach Towers 2 and 5 unchanged complete government originals',loadingPolicy='Full original source detail, no simplification or modelling')
  save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',forms)
  patch=read(PHYSICAL/'terrain-candidates.json');assert len(patch)==1
  p=patch[0];target=STAGE/Path(p['path']).name;shutil.copyfile(ROOT/p['path'],target);assert sha(target)==p['sha256'];terrain=read(target)
  destination='city/data/official-models/'+BATCH+'/catalogue.json';terrainrow={'source':rel(target),'destination':'city/data/'+target.name,'sha256':p['sha256'],'resolution':terrain['cell'],'area':catalogue['area']+' indexed unchanged government terrain'}
  assert not (ROOT/'3d-viewer'/terrainrow['destination']).exists()
  plan={'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':[terrainrow]};save(STAGE/'plan.json',plan)
  save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/', 'doc':rel(DOC)+'/', 'catalogueURL':destination,'terrain':[terrainrow],'fitBox':True,'browserUids':sorted(UIDS),'failureTestUids':sorted(UIDS),'retainedBuildingUidsByModel':{u:['landsd/232089:0'] for u in sorted(UIDS)}})
  save(DOC/'stage-inputs.json',{'physicalReceipt':rel(PHYSICAL/'result.json'),'physicalJobId':result['jobId'],'identityProof':proof,'currentManifestSHA256':manifest,'sourceSHA256s':{m['uid']:m['sha256'] for m in catalogue['models']},'sourceGeometryChanges':0,'publication':False,'allCurrentNeighboursRetained':sorted(scope-UIDS),'planSHA256':sha(STAGE/'plan.json'),'catalogueSHA256':sha(STAGE/'catalogue.json')})
  assert sha(ROOT/'3d-viewer/city/data/manifest.json')==manifest
  print(json.dumps({'stage':rel(STAGE),'sources':sorted(UIDS),'neighbours':len(scope-UIDS),'publication':False}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
