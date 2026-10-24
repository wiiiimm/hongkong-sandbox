"""Nominate all installed actors across complete current terrain replacement domains."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-current-scope-v1-20261020';DOC=BASE/BATCH
OLD=BASE/'government-xl-mount-sterling-current-scope-v2-20261020';CURRENT=BASE/'government-xl-mount-sterling-neighbours-v2-20261020';SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';UID='landsd/258411:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [OLD,CURRENT,SRC]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 bounds=take(OLD,OLD/'complete-bounds.json.gz');rows=bounds['rows'];models={};manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(CURRENT,manifestpath)
 for name in ['official-models.js','official-model-assets.js','geo.js']:take(OLD,ROOT/'3d-viewer/city'/name) if name.endswith('.json')else None
 for name in ['official-models.js','official-model-assets.js','geo.js']:
  p=ROOT/'3d-viewer/city'/name;assert digest(p.read_bytes())==pins[OLD][str(p.relative_to(ROOT))];refs.append(p)
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cat=take(CURRENT,p);assert cat['rootTranslation']==[-834500,0,816500]
  for m in cat['models']:
   assert m['uid']not in models;models[m['uid']]=m;asset=p.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256'];refs.append(asset)
 assert len(rows)==len(models)==6781 and {r['uid']for r in rows}==set(models)
 for r in rows:assert r['sourceSHA256']==models[r['uid']]['sha256']
 for p,h in bounds['currentFormTileHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 selection=take(SRC,SRC/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID);tile=ROOT/'3d-viewer'/source['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==UID)==source['source']['building'];refs.append(tile)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath);builder=module('ascot_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 def extent(p):
  g=p['meta']['georef'];return[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
 cells=builder.rectangle_for(source['candidate']['entry']['worldBounds'],parent);domain=builder.extent(cells,parent);overlaps=[]
 for entry in manifest['terrainPatches']:
  path=ROOT/'3d-viewer'/entry['url'];patch=read(path);e=extent(patch)
  if box(*domain).intersection(box(*e)).area<=1e-8:continue
  refs.append(path);nested=builder.rectangle_for(source['candidate']['entry']['worldBounds'],patch);nd=builder.extent(nested,patch)
  overlaps.append(dict(url=entry['url'],sha256=digest(path.read_bytes()),extent=e,nativeMesh=bool(patch.get('nativeMesh')),nestedReplacementCells=nested,nestedReplacementExtent=nd,nestedContainedByParent=box(*e).covers(box(*nd)),existingChildren=[dict(id=p.get('id'),extent=extent(p),intersectsNewChild=box(*nd).intersection(box(*extent(p))).area>1e-8)for p in patch.get('patches',[])],touchingNativeUids=[r['uid']for r in rows if not closed_disjoint(r['completeFourWorldBounds'],nd)],parentNativeUids=[r['uid']for r in rows if not closed_disjoint(r['completeFourWorldBounds'],e)]))
 summary=dict(uids=[UID],currentNativeActors=len(rows),allCurrentActorsNominated=True,baseReplacementCells=cells,baseReplacementExtent=domain,touchingBaseDomainNativeUids=[r['uid']for r in rows if not closed_disjoint(r['completeFourWorldBounds'],domain)],overlappingInstalledTerrain=overlaps,installationApproved=False)
 save(DOC/'scope.json',summary);refs.append(HERE/'heritage_saved_native_bounds_binding_v1_20261014.py')
 module('ascot_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-terrain-and-installed-actor-scope',list(dict.fromkeys(refs)),summary)
 print(dict(actors=len(rows),baseTouching=len(summary['touchingBaseDomainNativeUids']),parents=[dict(url=r['url'],native=r['nativeMesh'],retained=len(r['parentNativeUids']))for r in overlaps]),flush=True)
if __name__=='__main__':main()
