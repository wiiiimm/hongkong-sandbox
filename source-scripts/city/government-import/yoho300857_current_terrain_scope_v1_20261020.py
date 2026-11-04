"""Refresh every installed actor for the Lee Kong 72296 terrain proposal."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-current-terrain-scope-v1-20261020';DOC=BASE/BATCH
OLD=BASE/'government-xl-tower6803-current-terrain-scope-v1-20261020';ATTR=BASE/'government-xl-tower6803-private-terrain-capture-v1-20261020';INSTALL=BASE/'government-xl-tower6803-original-installed-v1-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];installed=read(INSTALL/'result.json');aliases=[];receipts={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [OLD,ATTR,INSTALL]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');receipts[folder.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
 # Reuse exact immutable bounds/capture files. Historical runtime manifests are
 # not current evidence; fresh catalogues/assets/terrain are verified below.
 for folder,name in [(OLD,'complete-bounds.json.gz'),(ATTR,'attributes.json.gz')]:
  p=folder/name;h=receipts[folder.name][str(p.relative_to(ROOT))];assert digest(p.read_bytes())==h;pins[str(p.relative_to(ROOT))]=h
 for name in ['official-models.js','official-model-assets.js','geo.js']:
  path='3d-viewer/city/'+name;h=receipts[OLD.name][path];assert digest((ROOT/path).read_bytes())==h;pins[path]=h
 pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointerpath)['snapshotId']==installed['snapshotId'];refs.append(pointerpath)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath)
 inventory=read(OLD/'complete-bounds.json.gz');rows=inventory['rows'];models={};assets={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cat=read(p);refs.append(p);catalogueKey=str(p.relative_to(ROOT));expected=receipts[OLD.name].get(catalogueKey,receipts[INSTALL.name].get(catalogueKey));assert expected and digest(p.read_bytes())==expected;assert cat['rootTranslation']==[-834500,0,816500]
  for e in cat['models']:
   assert e['uid']not in models;models[e['uid']]=e;assets[e['uid']]=p.parent/e['asset']
 oldids={r['uid']for r in rows};new=set(models)-oldids;assert new==set(installed['installedUids']) and oldids<=set(models)
 for r in rows:assert r['sourceSHA256']==models[r['uid']]['sha256']==digest(assets[r['uid']].read_bytes())
 for p,h in inventory['currentFormTileHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 captured=read(ATTR/'attributes.json.gz');assert captured['startEndAllInputsVerified'];assert new<={r['uid']for r in captured['rows']}
 for r in [r for r in captured['rows']if r['uid']in new]:
  uid=r['uid'];raw=assets[uid].read_bytes();assert digest(raw)==r['sourceSHA256']==models[uid]['sha256'];proof=packed_world_bounds(raw)
  rows.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],completeFourWorldBounds=[proof['originalWholeSourceBounds'],r['completeLiteralWorldBounds'],r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']],completeOriginalPOSITIONProof=proof))
 # Exact coarse-cell domain plus all packed positions (including unused ones).
 import numpy as np
 basepath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(basepath);refs.append(basepath)
 terrainDoc=BASE/'government-xl-yoho300857-pair-terrain-candidate-v1-20261020'
 tr=read(terrainDoc/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(tr['jobId'],)).fetchone()==('complete',tr)
 tpins={e['path']:e['sha256'] for e in tr['evidenceRefs']}
 cp=terrainDoc/'terrain-candidates.json';assert digest(cp.read_bytes())==tpins[str(cp.relative_to(ROOT))];refs.extend([cp,terrainDoc/'result.json'])
 candidate=read(cp)[0];patchpath=ROOT/candidate['path'];assert digest(patchpath.read_bytes())==candidate['sha256'];refs.append(patchpath);patch=read(patchpath)
 builder=module('yoho300857_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py')
 domain=builder.extent(patch['coarseCells'],parent);assert domain==candidate['bounds']
 packed=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3)
 # Native positions are already world coordinates; union Float64 and Float32.
 allp=np.concatenate([packed,packed.astype('float32').astype('float64')]);lo=allp.min(0);hi=allp.max(0)
 affected=[min(domain[0],float(lo[0])),min(domain[1],float(lo[2])),max(domain[2],float(hi[0])),max(domain[3],float(hi[2]))]
 touch=sorted(r['uid'] for r in rows if not closed_disjoint(r['completeFourWorldBounds'],affected))
 assert len(rows)==len(models)==6764 and ref(manifestpath)==installed['manifest']
 summary=dict(uids=['landsd/300857:0','landsd/301636:0'],currentNativeActors=len(rows),freshAddedBounds=sorted(new),allCurrentActorsNominated=True,changedParentExtent=domain,allPackedAffectedExtent=affected,packedVertexCount=len(packed),touchingNativeUids=touch,fullMeshRegressionStillRequired=True,installationApproved=False)
 for r in rows:r.pop('disjoint',None)
 save(DOC/'scope.json',summary);save(DOC/'complete-bounds.json.gz',dict(rows=rows,currentFormTileHashes=inventory['currentFormTileHashes']))
 refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend(assets.values());refs.extend([HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
 module('times_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'yoho300857-whole-private-terrain-current-installed-scope',list(dict.fromkeys(refs)),summary)
 print(dict(actors=len(rows),touching=touch,affectedExtent=affected),flush=True)
if __name__=='__main__':main()
