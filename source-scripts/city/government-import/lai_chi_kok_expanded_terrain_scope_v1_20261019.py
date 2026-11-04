"""Nominate complete merged terrain extent and all touching current actors."""
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-expanded-terrain-scope-v1-20261019';DOC=BASE/BATCH
SRC=BASE/'government-xl-lai-chi-kok-current-scope-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 scope=read(SRC/'scope.json')['rows'][0];bounds=read(SRC/'complete-bounds.json.gz')['rows'];assert len(bounds)==6743
 oldpath=ROOT/'3d-viewer/city/data/government-native-273000-0.json';old=read(oldpath);cells=scope['baseReplacementCells'];oc=old['coarseCells'];cells=[min(cells[0],oc[0]),min(cells[1],oc[1]),max(cells[2],oc[2]),max(cells[3],oc[3])]
 helper=module('lai_full_extent',HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';domain=helper.extent(cells,read(parentpath));touching=[x for x in bounds if not closed_disjoint(x['completeFourWorldBounds'],domain)]
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);overlaps=[]
 for e in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/e['url'];patch=read(p);g=patch['meta']['georef'];extent=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(patch['w']-1)*g['aE'],816500-g['bN']-(patch['h']-1)*g['aN']]
  area=shapely.box(*domain).intersection(shapely.box(*extent)).area
  if area>1e-8:overlaps.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),extent=extent,intersectionM2=area,contained=shapely.box(*domain).covers(shapely.box(*extent)),targetUids=patch['meta'].get('targetUids',[])));refs.append(p)
 save(DOC/'affected-actors.json.gz',dict(rows=touching,allCurrentActors=6743,completeFourWorldBoundsUsed=True))
 summary=dict(uid='landsd/281463:0',coarseCells=cells,expandedExtent=domain,touchingNativeUids=[x['uid']for x in touching],overlappingTerrain=overlaps,installationApproved=False,fullNeighbourRegressionRequired=True)
 save(DOC/'summary.json',summary);refs.extend([parentpath,manifestpath,HERE/'resolve-pass.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
 module('lai_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-expanded-complete-terrain-scope',refs,dict(uids=[summary['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
