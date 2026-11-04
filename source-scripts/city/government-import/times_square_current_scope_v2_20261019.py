"""Rebind the entire installed-source inventory to Times Square's changed terrain extent."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-current-scope-v2-20261019';DOC=BASE/BATCH
OLD=BASE/'government-xl-pacifica-current-scope-v1-20261018';ATTR=BASE/'government-xl-pacifica-actual-render-attributes-v1-20261019';INSTALL=BASE/'government-xl-pacifica-original-installed-v1-20261019';REVIEW=BASE/'government-xl-times-square-overlap-review-v1-20261019'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];installed=read(INSTALL/'result.json');history={(x['originalPath'],x['originalSHA256']):x['savedHistoricalBytes']for x in installed['historicalMutableByteSnapshots']};aliases=[]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [OLD,ATTR,INSTALL,REVIEW]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    p=ROOT/e['path']
    if digest(p.read_bytes())!=e['sha256']:
     saved=history[(e['path'],e['sha256'])];p=ROOT/saved['path'];assert digest(p.read_bytes())==e['sha256'];aliases.append(dict(original=e,historical=saved))
    key=str(p.relative_to(ROOT));assert key not in pins or pins[key]==e['sha256'];pins[key]=e['sha256']
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath)
 inventory=read(OLD/'complete-bounds.json.gz');rows=inventory['rows'];models={};assets={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cat=read(p);refs.append(p);assert cat['rootTranslation']==[-834500,0,816500]
  for e in cat['models']:
   assert e['uid']not in models;models[e['uid']]=e;assets[e['uid']]=p.parent/e['asset']
 oldids={r['uid']for r in rows};new=set(models)-oldids;assert new==set(installed['installedUids']) and oldids<=set(models)
 for r in rows:assert r['sourceSHA256']==models[r['uid']]['sha256']==digest(assets[r['uid']].read_bytes())
 for p,h in inventory['currentFormTileHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 captured=read(ATTR/'attributes.json.gz');assert captured['startEndAllInputsVerified'];assert {r['uid']for r in captured['rows']}==new
 for r in captured['rows']:
  uid=r['uid'];raw=assets[uid].read_bytes();assert digest(raw)==r['sourceSHA256']==models[uid]['sha256'];proof=packed_world_bounds(raw)
  rows.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],completeFourWorldBounds=[proof['originalWholeSourceBounds'],r['completeLiteralWorldBounds'],r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']],completeOriginalPOSITIONProof=proof))
 # All publication entries preserve source pose; source metadata and renderer closure are also authenticated by the installation receipt.
 domain=[2212.5,872.5,2422.5,1082.5];touch=[]
 for r in rows:
  r['disjoint']=closed_disjoint(r['completeFourWorldBounds'],domain)
  if not r['disjoint']:touch.append(r['uid'])
 overlaps=[]
 for e in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/e['url'];patch=read(p);refs.append(p);g=patch['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(patch['w']-1)*g['aE'],816500-g['bN']-(patch['h']-1)*g['aN']]
  if box(*domain).intersection(box(*bounds)).area>1e-8:overlaps.append(e['url'])
 assert len(rows)==len(models)==6724 and touch==[] and overlaps==[],(len(rows),touch,overlaps)
 summary=dict(uids=['landsd/233901:0','landsd/254824:0','landsd/266146:0'],currentNativeActors=len(rows),changedParentExtent=domain,touchingNativeUids=touch,overlappingTerrainURLs=overlaps,freshAddedBounds=sorted(new),allCurrentActorsNominated=True,historicalInputAliases=aliases,installationApproved=False)
 save(DOC/'scope.json',summary);save(DOC/'complete-bounds.json.gz',dict(rows=rows,currentFormTileHashes=inventory['currentFormTileHashes']))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend(assets.values());refs.extend([HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
 module('times_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-complete-current-installed-scope',list(dict.fromkeys(refs)),summary)
 print(dict(actors=len(rows),touching=touch,overlappingPatches=overlaps),flush=True)
if __name__=='__main__':main()
