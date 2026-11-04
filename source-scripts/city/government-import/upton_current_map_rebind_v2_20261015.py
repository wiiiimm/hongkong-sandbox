"""Rebind completed Upton staged acceptance to current disjoint installations."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from complete_actual_native_position_bounds_separation_20261011 import NATIVE_MODES
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-current-map-rebind-v2-20261015';DOC=BASE/BATCH
STAGE=BASE/'government-xl-upton-joint-original-dimension-private-stage-v2-20261014';BROWSER=BASE/'government-xl-upton-joint-original-dimension-staged-browser-v2-20261014';CENSUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipts=[read(p/'result.json')for p in [STAGE,BROWSER,CENSUS]]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 historical={};mp=ROOT/'3d-viewer/city/data/manifest.json';oldmp=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/captured-manifest.json';historical[(str(mp.relative_to(ROOT)),ref(oldmp)['sha256'])]=oldmp
 backup=BASE/'government-xl-heritage165054-original-installed-v2-20261015/historical-input-context.json'
 for q in read(backup)['mutableCurrentByteSnapshots']:historical[(q['originalPath'],q['originalSHA256'])]=ROOT/q['savedHistoricalBytes']['path']
 refs={};paths=[Path(__file__),backup]+[p/'result.json'for p in [STAGE,BROWSER,CENSUS]];changed=[]
 for r in receipts[:2]:
  for q in r['evidenceRefs']:
   assert q['path']not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
 for p,h in refs.items():
  file=ROOT/p;paths.append(file)
  if ref(file)['sha256']!=h:
   saved=historical[(p,h)];assert ref(saved)['sha256']==h;paths.append(saved);changed.append(dict(path=p,previousSHA256=h,exactHistoricalBytes=ref(saved),current=ref(file)))
 assert {q['path']for q in changed}=={'3d-viewer/city/data/manifest.json','3d-viewer/city/data/tiles/1_-6.json'}
 for q in receipts[2]['evidenceRefs']:assert ref(ROOT/q['path'])==q;paths.append(ROOT/q['path'])
 old,new=read(oldmp),read(mp);assert {k for k in old.keys()|new.keys()if old.get(k)!=new.get(k)}=={'officialModelCatalogues','terrainPatches','tiles'}
 assert new['officialModelCatalogues'][:len(old['officialModelCatalogues'])]==old['officialModelCatalogues'];commonold=[e for e in old['terrainPatches']if e in new['terrainPatches']];commonnew=[e for e in new['terrainPatches']if e in old['terrainPatches']];assert commonold==commonnew
 plan=read(HERE/'accepted'/STAGE.name/'plan.json');terrain=read(ROOT/plan['topLevelTerrainPatches'][0]['source']);parent=read(ROOT/'3d-viewer/city/data/terrain.json');g=parent['meta']['georef'];o=parent['meta']['origin'];i0,j0,i1,j1=terrain['coarseCells'];roi=[g['bE']+i0*g['aE']-o[0],o[1]-g['bN']-j0*g['aN'],g['bE']+i1*g['aE']-o[0],o[1]-g['bN']-j1*g['aN']]
 v=np.asarray(terrain['nativeMesh']['position']).reshape(-1,3);roi=[min(roi[0],v[:,0].min()),min(roi[1],v[:,2].min()),max(roi[2],v[:,0].max()),max(roi[3],v[:,2].max())];roi=list(map(float,roi))
 def outside(b):return b[2]<roi[0]or b[0]>roi[2]or b[3]<roi[1]or b[1]>roi[3]
 inv={r['uid']:r for r in read(CENSUS/'inventory.json.gz')['rows']};added=[]
 for url in new['officialModelCatalogues'][len(old['officialModelCatalogues']):]:
  p=ROOT/'3d-viewer'/url;paths.append(p)
  for e in read(p)['models']:
   r=inv[e['uid']];assert r['sourceSHA256']==e['sha256'];bounds={}
   for k in NATIVE_MODES.values():b=r[k];assert outside([b[0][0],b[0][2],b[1][0],b[1][2]]);bounds[k]=b
   added.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeBounds=bounds))
 patches=[]
 for e in [x for x in old['terrainPatches']if x not in new['terrainPatches']]+[x for x in new['terrainPatches']if x not in old['terrainPatches']]:
  p=ROOT/'3d-viewer'/e['url'];paths.append(p);assert ref(p)['sha256']==e['sha256'];t=read(p);i,j,k,l=t['coarseCells'];b=[g['bE']+i*g['aE']-o[0],o[1]-g['bN']-j*g['aN'],g['bE']+k*g['aE']-o[0],o[1]-g['bN']-l*g['aN']];assert outside(b)
  
  def checkpacked(t):
   if 'nativeMesh'in t:
    a=np.asarray(t['nativeMesh']['position']).reshape(-1,3);assert outside([float(a[:,0].min()),float(a[:,2].min()),float(a[:,0].max()),float(a[:,2].max())])
   for child in t.get('patches',[]):checkpacked(child)
  checkpacked(t);patches.append(ref(p))
 tc=[(a,b)for a,b in zip(old['tiles'],new['tiles'])if a!=b];assert len(old['tiles'])==len(new['tiles'])and len(tc)==1;a,b=tc[0];assert a['url']==b['url']=='city/data/tiles/1_-6.json'and outside(a['bounds']);assert {k:v for k,v in a.items()if k!='bytes'}=={k:v for k,v in b.items()if k!='bytes'}
 DOC.mkdir();save(DOC/'reconciliation.json',dict(currentManifest=ref(mp),historicalManifest=ref(oldmp),changedReferences=changed,completeReplacementROI=roi,addedModels=added,addedTerrain=patches,unchangedPriorEvidenceRefs=len(refs)-len(changed),localStagedEvidenceStillApplicable=True,fullAcceptance=False,publication=False))
 module('upton_current_rebind_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-map-disjoint-additions-upton-staged-binding-v1',paths,dict(uids=['landsd/12728:0','landsd/338946:0'],currentMapReconciled=True,addedModelsOutsideDomain=len(added),fullAcceptance=False))
 print(dict(addedModels=len(added),addedTerrain=len(patches),roi=roi),flush=True)
if __name__=='__main__':main()
