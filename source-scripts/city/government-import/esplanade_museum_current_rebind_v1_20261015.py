"""Reconcile the exact Museum-only publication against Esplanade's saved evidence."""
import json,sys
from pathlib import Path
import numpy as np
import esplanade_guarded_publish_v1_20261015 as guard
from run import ROOT,HERE,read,save,digest,connect
BATCH='government-xl-esplanade-museum-current-rebind-v1-20261015'
DOC=guard.BASE/BATCH
ref=guard.stage.ref

def main():
 assert not DOC.exists()
 museum=guard.BASE/'government-xl-heritage165054-original-installed-v2-20261015'
 receipts=[read(d/'result.json')for d in [guard.stage.DOC,guard.BROWSER,guard.REVIEW,museum]]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in receipts[-1]['evidenceRefs']:guard.check(q)
 history=read(museum/'historical-input-context.json');historical={q['originalPath']:q for q in history['mutableCurrentByteSnapshots']}
 refs={}
 for r in receipts[:-1]:
  for q in r['evidenceRefs']:
   if q['path']in refs:assert refs[q['path']]==q
   refs[q['path']]=q
 changed=[];paths=[]
 for p,q in refs.items():
  if ref(ROOT/p)==q:paths.append(ROOT/p);continue
  h=historical[p];assert h['originalSHA256']==q['sha256'];guard.check(h['savedHistoricalBytes']);assert h['savedHistoricalBytes']['sha256']==q['sha256']
  changed.append(dict(historicalReference=q,historicalBytes=h['savedHistoricalBytes'],currentReference=ref(ROOT/p)))
  paths.extend([ROOT/h['savedHistoricalBytes']['path'],ROOT/p])
 assert {r['historicalReference']['path']for r in changed}=={'3d-viewer/city/data/manifest.json','3d-viewer/city/data/tiles/1_-6.json'}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';old=read(ROOT/historical[str(manifest.relative_to(ROOT))]['savedHistoricalBytes']['path']);current=read(manifest)
 assert {k for k in old.keys()|current.keys()if old.get(k)!=current.get(k)}=={'officialModelCatalogues','terrainPatches','tiles'}
 assert current['officialModelCatalogues'][:-1]==old['officialModelCatalogues']and current['terrainPatches'][:-1]==old['terrainPatches']
 assert len(current['tiles'])==len(old['tiles'])
 tilechanges=[(a,b)for a,b in zip(old['tiles'],current['tiles'])if a!=b];assert len(tilechanges)==1
 a,b=tilechanges[0];assert a['url']==b['url']=='city/data/tiles/1_-6.json';assert {k:v for k,v in a.items()if k!='bytes'}=={k:v for k,v in b.items()if k!='bytes'}
 tp='3d-viewer/'+a['url'];before=read(ROOT/historical[tp]['savedHistoricalBytes']['path']);after=read(ROOT/tp)
 assert {k:v for k,v in before.items()if k!='buildings'}=={k:v for k,v in after.items()if k!='buildings'}
 assert len(before['buildings'])==len(after['buildings']);changes=[(a,b)for a,b in zip(before['buildings'],after['buildings'])if a!=b]
 assert len(changes)==1 and changes[0][0]['uid']==changes[0][1]['uid']=='landsd/128971:0'
 domain=read(guard.BASE/guard.stage.NAMES['scope']/'scope.json.gz')['parentDomain']
 tilebounds=tilechanges[0][0]['bounds']
 def outside(bounds):return bounds[2]<domain[0]or bounds[0]>domain[2]or bounds[3]<domain[1]or bounds[1]>domain[3]
 assert outside(tilebounds)
 catpath=ROOT/'3d-viewer'/current['officialModelCatalogues'][-1];cat=read(catpath);assert len(cat['models'])==1 and cat['models'][0]['uid']=='landsd/165054:0'
 model=cat['models'][0];bounds=model['worldBounds'];assert outside([bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2]])
 patchpath=ROOT/'3d-viewer'/current['terrainPatches'][-1]['url'];patch=read(patchpath);vertices=np.asarray(patch['nativeMesh']['position']).reshape(-1,3);lo=vertices.min(axis=0);hi=vertices.max(axis=0);patchbounds=[float(lo[0]),float(lo[2]),float(hi[0]),float(hi[2])];assert outside(patchbounds)
 assert not model['suppressesBuildingUids']and not model['supportDependencies']
 # Existing local proof inputs remain byte-identical. Global changed files are
 # bound to their exact previous bytes and to the completed Museum transaction.
 paths += [museum/'result.json',museum/'ROOT-VERIFIED.json',museum/'historical-input-context.json',catpath,catpath.parent/model['asset'],patchpath,Path(__file__)]+[d/'result.json'for d in [guard.stage.DOC,guard.BROWSER,guard.REVIEW]]
 DOC.mkdir();save(DOC/'reconciliation.json',dict(currentManifest=ref(manifest),priorReceipts=[r['jobId']for r in receipts[:-1]],interveningInstalledJob=receipts[-1]['jobId'],changedReferences=changed,unchangedHistoricalReferences=[q for p,q in refs.items()if p not in {x['historicalReference']['path']for x in changed}],esplanadeParentDomain=domain,changedTileBounds=tilebounds,addedNativeWorldBounds=bounds,addedNativeTerrainBounds=patchbounds,allChangesOutsideEsplanadeParent=True,allOtherEvidenceUnchanged=True,sourceGeometryChanges=0,publication=False,fullAcceptance=False))
 guard.stage.module('rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-museum-only-current-map-reconciliation-v1',paths,dict(uids=list(guard.stage.SOURCES),fullAcceptance=False,currentMapReconciled=True))
 print('Exact current-map reconciliation complete.',flush=True)
if __name__=='__main__':main()
