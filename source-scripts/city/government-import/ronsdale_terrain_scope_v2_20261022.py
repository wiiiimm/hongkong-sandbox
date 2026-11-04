"""Locate current terrain parents and nominate neighbours for an original-TIN repair."""
from pathlib import Path
import numpy as np
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-terrain-scope-v2-20261022';DOC=BASE/BATCH;SOURCE=BASE/'government-xl-ronsdale-podium-original-ground-v1-20261022'
def extent(p):
 g=p['meta']['georef'];return [g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
def main():
 assert not DOC.exists();_,pins=authenticate(SOURCE);sp=SOURCE/'selection.json.gz';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))];selection=read(sp);rows=selection['rows'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs=[Path(__file__),sp,SOURCE/'result.json',manifestpath]
 current_hash=digest(manifestpath.read_bytes())
 for row in rows:
  sourcepath=ROOT/'3d-viewer'/row['source']['tile'];assert digest(sourcepath.read_bytes())==row['source']['tileSHA256'];refs.append(sourcepath)
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 save(DOC/'manifest-reconciliation.json',dict(historicalManifestSHA256=selection['manifestSHA256'],currentManifestSHA256=current_hash,sourceBytesAndTilesUnchanged=True,installationApproved=False))
 lo=np.min([r['native']['model']['worldBounds'][0]for r in rows],axis=0);hi=np.max([r['native']['model']['worldBounds'][1]for r in rows],axis=0);bounds=[lo.tolist(),hi.tolist()];builder=module('ronsdale_cells',HERE/'resolve-pass-indexed-parent-clipping.py');basepath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(basepath);refs.append(basepath);cells=builder.rectangle_for(bounds,parent);domain=builder.extent(cells,parent);overlaps=[]
 for entry in manifest['terrainPatches']:
  path=ROOT/'3d-viewer'/entry['url'];patch=read(path);e=extent(patch)
  if box(*domain).intersection(box(*e)).area<=1e-8:continue
  refs.append(path);nestedcells=builder.rectangle_for(bounds,patch);nestedextent=builder.extent(nestedcells,patch);overlaps.append(dict(url=entry['url'],sha256=digest(path.read_bytes()),extent=e,nativeMesh=bool(patch.get('nativeMesh')),nestedReplacementCells=nestedcells,nestedReplacementExtent=nestedextent,nestedContainedByParent=box(*e).covers(box(*nestedextent)),children=[dict(id=c.get('id'),extent=extent(c))for c in patch.get('patches',[])]))
 actors=[]
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for e in read(path)['models']:
   low,high=e['worldBounds']
   if box(low[0],low[2],high[0],high[2]).intersects(box(*domain)):actors.append(dict(uid=e['uid'],catalogue=url,entry=e))
 scope=dict(uids=[r['uid']for r in rows],sourceWorldBounds=bounds,baseReplacementCells=cells,baseReplacementExtent=domain,overlappingTerrain=overlaps,preliminaryActors=actors,qualification='Catalogue worldBounds are preliminary nominations only. Full decoded runtime bounds and complete neighbour checks remain required before publication.',installationApproved=False)
 assert digest(manifestpath.read_bytes())==current_hash;save(DOC/'scope.json',scope);refs.append(HERE/'resolve-pass-indexed-parent-clipping.py');module('ronsdale_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-terrain-parent-discovery',refs,scope);print(dict(domain=domain,parents=[r['url']for r in overlaps],preliminaryActors=len(actors)),flush=True)
if __name__=='__main__':main()
