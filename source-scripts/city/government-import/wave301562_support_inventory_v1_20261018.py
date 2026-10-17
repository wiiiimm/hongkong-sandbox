"""Read-only exact footprint and raw-sheet support nominations for Wave's remaining companion."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave301562-source-tin-check-v1-20261018';BATCH='government-xl-wave301562-support-inventory-v1-20261018';DOC=BASE/BATCH;KEY='44f644c3aa99e3a7514b69c04e0e4841aba7df414a29ed1474197a09884f1917'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  sha,data=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(KEY,)).fetchone();profiles={cell:c.execute('SELECT DISTINCT model_id,cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+cell+'%')).fetchall()for cell in ['1613726707','1617526690']}
 for e in receipt['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=next(r for r in read(BASE/'government-xl-wave-verdant-remaining-interfaces-v1-20261018/interfaces.json.gz')['rows']if r['mode']=='original'and r['uid']=='landsd/301562:0');faces={f['faceIndex']:f for x in row['unresolved']for f in x['sourceFaces']};polys=[Polygon(np.asarray(f['vertices'])[:,[0,2]])for f in faces.values()];area=unary_union([p for p in polys if p.area>1e-6]);near=[]
 for r in read(BASE/'government-xl-wave-verdant-multicore-neighbours-v4-20261017/neighbour-inputs.json.gz')['rows']:
  b=r['building'];poly=Polygon(b['rings'][0],b['rings'][1:]);distance=poly.distance(area)
  if distance<8:near.append(dict(building=b,footprintDistanceM=distance,overlapM2=poly.intersection(area).area))
 x0,z0,x1,z1=area.bounds;models=[];unknown=[]
 for m in data['models']:
  bounds=m.get('worldBounds')
  if not bounds:unknown.append(m['modelId']);continue
  lo,hi=bounds
  if hi[0]>=x0-.1 and lo[0]<=x1+.1 and hi[2]>=z0-.1 and lo[2]<=z1+.1 and lo[1]<=15.4:models.append(m)
 out=dict(uid='landsd/301562:0',projectionAreaM2=area.area,projectionBounds=list(area.bounds),nearbyForms=near,sameCellProfiles=profiles,rawSheet=dict(cacheKey=KEY,resultSHA256=sha,modelCount=len(data['models']),missingBounds=unknown,modelBoundsCandidates=models),fullAcceptance=False,qualification='Complete179-model indexed sheet broad-phase nomination plus prior complete48-form neighbourhood. Bounds hits require exact source geometry. Absence in this sheet is not global source absence or corruption; adjacent sheets and non-building source layers are not ruled out.')
 save(DOC/'lookup.json.gz',out);save(DOC/'summary.json',dict(nearbyForms=[r['building']['uid']for r in near],sheetModelCount=len(data['models']),boundsCandidates=[m['modelId']for m in models],unknownBounds=unknown,sameCellCounts={c:len(p)for c,p in profiles.items()},fullAcceptance=False));result=module('wave_inventory_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-original-companion-footprint-raw-sheet-support-nominations-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]],dict(uids=['landsd/301562:0'],fullAcceptance=False,newlyInstalled=0));print(read(DOC/'summary.json'),flush=True);print(result['jobId'],flush=True)
if __name__=='__main__':main()
