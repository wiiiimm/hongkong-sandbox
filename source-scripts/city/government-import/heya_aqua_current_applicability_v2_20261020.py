"""Rebind Heya evidence and nominate all current native neighbours; no terrain change."""
from pathlib import Path
import copy
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-current-applicability-v2-20261020';DOC=BASE/BATCH
SCOPE=BASE/'government-xl-mount-sterling-current-scope-v2-20261020';REN=BASE/'government-xl-heya-aqua-render-foundations-v1-20261020';SUP=BASE/'government-xl-heya-aqua-current-support-v3-20261020';UID='landsd/184287:0'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_bounds_v3_20261010.py'];receipts={};correction=BASE/'government-xl-lai-chi-kok-dependency-applied-v1-20261020'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [correction,SCOPE,REN,SUP,BASE/'government-xl-heya-aqua-identity-review-v1-20261020',BASE/'government-xl-heya-aqua-physical-review-v1-20261020']:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');receipts[folder.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==receipts[folder.name][str(p.relative_to(ROOT))],str(p);refs.append(p);return read(p)
 inventory=take(SCOPE,SCOPE/'complete-bounds.json.gz');manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(SCOPE,manifestpath);models={};assets={};catalogues={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;key=str(p.relative_to(ROOT));expected=receipts[SCOPE.name][key]
  if digest(p.read_bytes())!=expected:
   correction_result=read(correction/'result.json');aliases=[a for a in correction_result['aliases']if a['path']==key and a['sha256']==expected];assert len(aliases)==1
   archive=ROOT/aliases[0]['archivePath'];assert digest(archive.read_bytes())==expected;refs.append(archive);cat=take(correction,p);old=read(archive)
   def without_states(value):
    value=copy.deepcopy(value)
    for m in value['models']:
     for d in m.get('supportDependencies',[]):d.pop('state',None)
    return value
   assert without_states(cat)==without_states(old), 'Only verified dependency state labels may differ'
  else:cat=take(SCOPE,p)
  for e in cat['models']:
   assert e['uid']not in models;models[e['uid']]=e;assets[e['uid']]=p.parent/e['asset'];catalogues[e['uid']]=str(p.relative_to(ROOT))
 assert UID not in models and len(models)==len(inventory['rows'])==6781
 for r in inventory['rows']:
  p=assets[r['uid']];assert r['sourceSHA256']==models[r['uid']]['sha256']==digest(p.read_bytes());refs.append(p)
 for p,h in inventory['currentFormTileHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 cap=take(REN,REN/'attributes.json.gz');source=take(SUP,SUP/'support-inputs.json')['sources'];row=next(r for r in source if r['uid']==UID);a=next(r for r in cap['rows']if r['uid']==UID)
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 original=packed_world_bounds((ROOT/row['candidate']['path']).read_bytes());assert original['sourceSHA256']==row['sourceSHA256'];bounds=[original['originalWholeSourceBounds'],a['completeLiteralWorldBounds'],a['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],a['completeExplicitBalancedFloat32ModelMatrixWorldBounds']];lo=np.min([b[0]for b in bounds],0);hi=np.max([b[1]for b in bounds],0);near=[]
 for r in inventory['rows']:
  lower=np.min([b[0]for b in r['completeFourWorldBounds']],0);upper=np.max([b[1]for b in r['completeFourWorldBounds']],0)
  if np.all(lower<=hi)and np.all(upper>=lo):near.append(dict(**r,entry=models[r['uid']],catalogue=catalogues[r['uid']]))
 identityfolder=BASE/'government-xl-heya-aqua-identity-review-v1-20261020';identity=take(identityfolder,identityfolder/'review.json');assert identity['identityOnlyApproved']and identity['rawProof']['freshCurrentIdentity']['unrelatedIntersectingForms']==0
 for r in source:
  p=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(p)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(p)
 for name in ['terrain.json']:
  p=ROOT/'3d-viewer/city/data'/name;refs.append(p)
 for e in manifest['terrainPatches']:refs.append(ROOT/'3d-viewer'/e['url'])
 result=dict(uids=[UID],currentNativeActors=len(models),currentManifest=dict(path=str(manifestpath.relative_to(ROOT)),sha256=digest(manifestpath.read_bytes())),sourceBounds=[lo.tolist(),hi.tolist()],touchingNativeActors=near,terrainChanges=0,basicFormChanges=0,retainedModelChanges=0,unrelatedRecordedFormIntersections=0,installationApproved=False)
 save(DOC/'applicability.json',result)
 module('heya_current_applicability_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-entire-native-inventory-and-original-evidence-applicability',list(dict.fromkeys(refs)),result)
 print('TOUCHING',[r['uid']for r in near],flush=True)
if __name__=='__main__':main()
