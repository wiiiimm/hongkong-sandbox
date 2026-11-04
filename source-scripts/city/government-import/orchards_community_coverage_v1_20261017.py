"""Measure unchanged community and podium source coverage; no acceptance or publication."""
from pathlib import Path
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-orchards-community-coverage-v1-20261017'
def main():
 base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not (doc/'result.json').exists();rows=[];refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];projections=[]
 for name in ['government-xl-orchards-podium-original-recovery-v1-20261017','government-xl-orchards-community-original-recovery-v1-20261017']:
  d=base/name;result=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  pins={}
  for e in result['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  row=read(d/'selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==row['native']['model']['triangles'];projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));rows.append(row);projections.append(projection);refs.extend([d/'result.json',d/'selection.json.gz',ROOT/row['candidate']['path']])
 target=Polygon(rows[0]['source']['building']['rings'][0],rows[0]['source']['building']['rings'][1:]);missing=target.difference(projections[0]);combined=shapely.union_all(projections)
 summary=dict(uids=[r['uid']for r in rows],sourceSHA256=[r['sourceSHA256']for r in rows],sourceTriangles=[r['native']['model']['triangles']for r in rows],podiumFootprintM2=target.area,podiumOnlyCoverage=projections[0].intersection(target).area/target.area,communityCoversMissingM2=projections[1].intersection(missing).area,combinedCoverage=combined.intersection(target).area/target.area,remainingMissingM2=target.difference(combined).area,sourceGeometryChanges=0,installationApproved=False,identityApproved=False)
 save(doc/'coverage.json',summary);save(doc/'selection.json.gz',dict(rows=rows));out=module('orchards_community_coverage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-community-podium-full-projection-coverage-diagnostic-v1',refs,dict(uids=summary['uids'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
