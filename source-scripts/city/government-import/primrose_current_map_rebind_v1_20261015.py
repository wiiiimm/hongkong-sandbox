"""Exact current-map binding for unchanged Primrose local evidence."""
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-primrose-current-map-rebind-v1-20261015';DOC=BASE/BATCH
NAMES=['remaining-original-components-v2','current-identity-v1','private-terrain-floor-v5','join-runtime-capture-v5','join-basic-finite-v5','compound-foundation-v2','podium-current-finite-v2','podium-role-review-v2','towers-complete-finite-v1','shelter-source-review-v1','current-native-parent-scope-v1']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 folders=[BASE/('government-xl-primrose-'+n+'-20261015')for n in NAMES];installs=[BASE/('government-xl-'+n+'-original-installed-v2-20261015')for n in ['heritage165054','esplanade']]
 receipts=[read(d/'result.json')for d in folders+installs]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs={(q['path'],q['sha256']):q for r in receipts[:len(folders)]for q in r['evidenceRefs']};history=[read(d/'historical-input-context.json')for d in installs];backups={}
 for h in history:
  for q in h['mutableCurrentByteSnapshots']:backups[(q['originalPath'],q['originalSHA256'])]=q['savedHistoricalBytes']
 paths=[];changed=[]
 for key,q in refs.items():
  if ref(ROOT/q['path'])==q:paths.append(ROOT/q['path']);continue
  backup=backups[key];assert ref(ROOT/backup['path'])==backup and backup['sha256']==q['sha256'];paths.extend([ROOT/backup['path'],ROOT/q['path']]);changed.append(dict(previous=q,exactHistoricalBytes=backup,current=ref(ROOT/q['path'])))
 assert {q['previous']['path']for q in changed}=={'3d-viewer/city/data/manifest.json','3d-viewer/city/data/tiles/1_-6.json'}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';oldsha=next(q['previous']['sha256']for q in changed if q['previous']['path']==str(manifest.relative_to(ROOT)));old=read(ROOT/backups[(str(manifest.relative_to(ROOT)),oldsha)]['path']);new=read(manifest)
 assert {k for k in old.keys()|new.keys()if old.get(k)!=new.get(k)}=={'officialModelCatalogues','terrainPatches','tiles'}
 assert new['officialModelCatalogues'][:-2]==old['officialModelCatalogues']and new['terrainPatches'][:-2]==old['terrainPatches']
 assert len(old['tiles'])==len(new['tiles']);tilechanges=[(a,b)for a,b in zip(old['tiles'],new['tiles'])if a!=b];assert len(tilechanges)==1
 a,b=tilechanges[0];assert a['url']==b['url']=='city/data/tiles/1_-6.json';assert {k:v for k,v in a.items()if k!='bytes'}=={k:v for k,v in b.items()if k!='bytes'}
 tp='3d-viewer/'+a['url'];previous=next(q for q in changed if q['previous']['path']==tp);before=read(ROOT/previous['exactHistoricalBytes']['path']);after=read(ROOT/tp)
 assert {k:v for k,v in before.items()if k!='buildings'}=={k:v for k,v in after.items()if k!='buildings'}and len(before['buildings'])==len(after['buildings'])
 differences=[(a,b)for a,b in zip(before['buildings'],after['buildings'])if a!=b];assert len(differences)==1 and differences[0][0]['uid']==differences[0][1]['uid']=='landsd/128971:0'
 scope=read(folders[-1]/'scope.json.gz');domain=scope['parentDomain']
 def outside(b):return b[2]<domain[0]or b[0]>domain[2]or b[3]<domain[1]or b[1]>domain[3]
 assert outside(tilechanges[0][0]['bounds']);added=[]
 for url in new['officialModelCatalogues'][-2:]:
  p=ROOT/'3d-viewer'/url;paths.append(p)
  for m in read(p)['models']:
   lo,hi=m['worldBounds'];assert outside([lo[0],lo[2],hi[0],hi[2]])and not m.get('suppressesBuildingUids');asset=p.parent/m['asset'];assert ref(asset)['sha256']==m['sha256'];paths.append(asset);added.append(dict(uid=m['uid'],worldBounds=m['worldBounds'],sha256=m['sha256']))
 assert {r['uid']for r in added}=={'landsd/165054:0','landsd/268828:0','landsd/309385:0'}
 patches=[]
 for e in new['terrainPatches'][-2:]:
  p=ROOT/'3d-viewer'/e['url'];assert ref(p)['sha256']==e['sha256'];patch=read(p);v=np.asarray(patch['nativeMesh']['position']).reshape(-1,3);lo=v.min(axis=0);hi=v.max(axis=0);bounds=[float(lo[0]),float(lo[2]),float(hi[0]),float(hi[2])];assert outside(bounds);patches.append(dict(file=ref(p),bounds=bounds));paths.append(p)
 paths += [d/'result.json'for d in folders+installs]+[d/'historical-input-context.json'for d in installs]+[Path(__file__)]
 DOC.mkdir();save(DOC/'reconciliation.json',dict(currentManifest=ref(manifest),historicalJobs=[r['jobId']for r in receipts[:len(folders)]],interveningInstalledJobs=[r['jobId']for r in receipts[len(folders):]],changedReferences=changed,unchangedHistoricalReferences=[q for q in refs.values()if q not in [x['previous']for x in changed]],parentDomain=domain,addedModels=added,addedTerrain=patches,allChangesOutsidePrimroseParent=True,allOtherEvidenceUnchanged=True,fullAcceptance=False,publication=False))
 module('rebind_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-primrose-local-evidence-binding-v1',paths,dict(uids=['landsd/74568:0','landsd/74569:0','landsd/74570:0','landsd/74573:0'],fullAcceptance=False,currentMapReconciled=True))
if __name__=='__main__':main()
