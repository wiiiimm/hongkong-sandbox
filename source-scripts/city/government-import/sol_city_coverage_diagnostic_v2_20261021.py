"""Locate actual packed terrain gaps without granting numerical exceptions."""
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,connect
from native_patch_resolution import projected_context
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-coverage-diagnostic-v2-20261021';DOC=BASE/BATCH
refs=[Path(__file__)];pins={}
for name in ['private-terrain-v1','shaped-ground-v1','regional-scope-v1']:
 d=BASE/('government-xl-sol-city-'+name+'-20261021');r=read(d/'result.json');refs.append(d/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
patch=read(HERE/'local/government-xl-sol-city-private-terrain-v1-20261021/candidate-terrain.json')
scope=read(BASE/'government-xl-sol-city-regional-scope-v1-20261021/scope.json')
_,polys,missing,_=projected_context(patch,scope['regionalParentExtent']);union=shapely.union_all(polys);extent=shapely.box(*scope['regionalParentExtent']);difference=union.symmetric_difference(extent)
protected=read(BASE/'government-xl-sol-city-shaped-ground-v1-20261021/protected.json');core=shapely.from_wkt(protected['coreWKT']);outer=shapely.from_wkt(protected['outerWKT'])
result=dict(uids=scope['uids'],symmetricDifferenceAreaM2=difference.area,missingAreaM2=missing.area,missingBeyond2mmM2=missing.difference(union.buffer(.002)).area,coreGapM2=difference.intersection(core).area,transitionGapM2=difference.intersection(outer.difference(core)).area,outsideGapM2=difference.difference(outer).area,installationApproved=False,qualification='Real transition coverage failure; no threshold waiver or source corruption finding.')
save(DOC/'difference.json',dict(wkt=difference.wkt));save(DOC/'summary.json',result)
refs.extend(ROOT/p for p in pins);refs.append(HERE/'native_patch_resolution.py')
module('sol_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-packed-transition-gap-diagnosis',refs,result)
print(result)
