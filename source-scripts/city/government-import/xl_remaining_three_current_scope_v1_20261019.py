"""Refresh all installed actors and terrain hierarchy for three unfinished XL sources."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-remaining-three-current-scope-v1-20261019';DOC=BASE/BATCH
OLD=BASE/'government-xl-ocean-terminal-current-scope-v1-20261019';ATTR=BASE/'government-xl-ocean-terminal-actual-render-attributes-v1-20261019';INSTALL=BASE/'government-xl-ocean-terminal-original-installed-v1-20261019'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];installed=read(INSTALL/'result.json');history={(x['originalPath'],x['originalSHA256']):x['savedHistoricalBytes']for x in installed['historicalMutableByteSnapshots']};aliases=[]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [OLD,ATTR,INSTALL]:
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
 # Recompute every candidate extent against the current terrain hierarchy.
 basepath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(basepath);refs.append(basepath)
 builder=module('three_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py');selectionpath=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz';selection=read(selectionpath)['rows'];refs.append(selectionpath)
 def extent(p):
  g=p['meta']['georef'];return[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
 summaries=[];uids=['landsd/263423:0','landsd/210032:0','landsd/281463:0']
 for uid in uids:
  row=next(r for r in selection if r['uid']==uid);cells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],parent);domain=builder.extent(cells,parent);overlaps=[]
  for entry in manifest['terrainPatches']:
   path=ROOT/'3d-viewer'/entry['url'];patch=read(path);e=extent(patch)
   if box(*domain).intersection(box(*e)).area<=1e-8:continue
   refs.append(path);nestedcells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],patch);nestedextent=builder.extent(nestedcells,patch)
   children=[dict(id=child.get('id'),extent=extent(child),intersectsNewChild=box(*nestedextent).intersection(box(*extent(child))).area>1e-8)for child in patch.get('patches',[])]
   overlaps.append(dict(url=entry['url'],sha256=digest(path.read_bytes()),extent=e,nativeMesh=bool(patch.get('nativeMesh')),nestedReplacementCells=nestedcells,nestedReplacementExtent=nestedextent,nestedContainedByParent=box(*e).covers(box(*nestedextent)),existingChildren=children,touchingNativeUids=[r['uid']for r in rows if not closed_disjoint(r['completeFourWorldBounds'],nestedextent)],parentNativeUids=[r['uid']for r in rows if not closed_disjoint(r['completeFourWorldBounds'],e)]))
  summaries.append(dict(uid=uid,baseReplacementCells=cells,baseReplacementExtent=domain,touchingBaseDomainNativeUids=[r['uid']for r in rows if not closed_disjoint(r['completeFourWorldBounds'],domain)],overlappingInstalledTerrain=overlaps,installationApproved=False))
 assert len(rows)==len(models)==6728
 summary=dict(uids=uids,rows=summaries,currentNativeActors=len(rows),freshAddedBounds=sorted(new),allCurrentActorsNominated=True,historicalInputAliases=aliases,installationApproved=False)
 for r in rows:r.pop('disjoint',None)
 save(DOC/'scope.json',summary);save(DOC/'complete-bounds.json.gz',dict(rows=rows,currentFormTileHashes=inventory['currentFormTileHashes']))
 refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend(assets.values());refs.extend([HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
 module('times_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-three-complete-current-installed-scope',list(dict.fromkeys(refs)),summary)
 print(dict(actors=len(rows),candidates=[dict(uid=r['uid'],touchingBaseDomain=len(r['touchingBaseDomainNativeUids']),parents=len(r['overlappingInstalledTerrain']))for r in summaries]),flush=True)
if __name__=='__main__':main()
