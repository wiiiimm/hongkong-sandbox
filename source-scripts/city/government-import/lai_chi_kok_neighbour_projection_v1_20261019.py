"""Locate every BASIC regression against complete original source projection."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-neighbour-projection-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-complete-neighbours-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 cap=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v1-20261019';row=read(cap/'selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw);xz=t[:,:,[0,2]];polys=shapely.polygons(xz);proj=shapely.union_all(polys);tree=shapely.STRtree(polys)
 buildings={x['building']['uid']:x['building']for x in read(SRC/'neighbour-inputs.json.gz')['rows']};checks=[x for x in read(SRC/'neighbour-checks.json')['rows']if x['reasons']];out=[]
 for x in checks:
  b=buildings[x['uid']];p=shapely.Polygon(b['rings'][0],b['rings'][1:]);assert p.is_valid
  ids=tree.query(p,predicate='intersects').tolist();overlap=p.intersection(proj)
  out.append(dict(uid=x['uid'],name=b.get('name'),building=b,regression=x,footprintAreaM2=p.area,originalSourceProjectionOverlapM2=overlap.area,sourceProjectionDistanceM=p.distance(proj),sourceFaceIds=ids,sourceBounds=np.asarray(t[ids]).min((0,1)).tolist()if ids else None,sourceTop=np.asarray(t[ids]).max((0,1)).tolist()if ids else None,parentRestorationMayConflictWithSource=bool(overlap.area>1e-8)))
 save(DOC/'projection.json',dict(rows=out,installationApproved=False));refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 summary=[dict(uid=x['uid'],name=x['name'],footprintAreaM2=x['footprintAreaM2'],sourceOverlapM2=x['originalSourceProjectionOverlapM2'],sourceFaces=len(x['sourceFaceIds']))for x in out]
 module('lai_neighbour_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-basic-regression-complete-source-projection',refs,dict(uids=[row['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
