"""Complete unchanged eight-original assembly footprint accounting; diagnostic."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-assembly-footprints-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019'
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];pins[p]=e['sha256'];refs.append(p)
 rows=read(SRC/'selection.json.gz')['rows'];projections={}
 for row in rows:
  p=ROOT/row['candidate']['path'];raw=p.read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw);assert len(t)==row['triangles'];polys=shapely.polygons(t[:,:,[0,2]]);projections[row['uid']]=shapely.union_all(polys[shapely.area(polys)>1e-10])
 union=shapely.union_all(list(projections.values()));out=[]
 for row in rows[1:]:
  b=row['source']['building'];target=Polygon(b['rings'][0],b['rings'][1:]);own=projections[row['uid']];missing=target.difference(own);left=target.difference(union);r=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],ownCoverage=target.intersection(own).area/target.area,assemblyCoverage=target.intersection(union).area/target.area,missingOwnArea=missing.area,missingAssemblyArea=left.area,missingOwnCoveredByPlatformArea=missing.intersection(projections['landsd/281463:0']).area,otherOriginalContributions={u:missing.intersection(p).area for u,p in projections.items()if u!=row['uid']},installationApproved=False);out.append(r);print(r,flush=True)
 save(DOC/'summary.json',dict(rows=out,installationApproved=False));module('assembly_footprint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-assembly-footprint-accounting',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=out,installationApproved=False))
if __name__=='__main__':main()
