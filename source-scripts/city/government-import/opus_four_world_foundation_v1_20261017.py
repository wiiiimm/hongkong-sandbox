"""Whole original Opus assembly foundation diagnostics in four captured worlds."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-four-world-foundation-v1-20261017';DOC=BASE/BATCH
WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-preserved-neighbours-v1-20261016';CAP=BASE/'government-xl-opus-actual-render-attributes-v2-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [WORLD,GROUND,CAP]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(WORLD/'world-triangles.json.gz');selection=consume(CAP/'input.json.gz')['rows'];gpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';geometry=consume(gpath)['rows']
 ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in geometry]);polygon=shapely.union_all([Polygon(r['building']['rings'][0],r['building']['rings'][1:]) for r in selection]);f=module('opus_four_foundation',HERE/'xl-final-script-pass.py');rows=[];DOC.mkdir()
 for mode,world in worlds.items():
  triangles=np.concatenate([np.asarray(world[r['uid']]) for r in selection]);assert len(triangles)==13557
  proof=f.foundation_context(triangles,ground,polygon);row=dict(mode=mode,foundation=proof);rows.append(row);print(row,flush=True)
 save(DOC/'summary.json',dict(rows=rows,fullAcceptance=False,newlyInstalled=0,qualification='Complete three-part original assembly against previously prepared preserved-neighbour terrain. Historical terrain context only; current neighbour, source-role and browser acceptance remain required.'))
 refs += [HERE/'xl-final-script-pass.py',Path(f.s.context.shared.__file__)]
 out=module('opus_four_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-three-part-four-world-foundation-v1',refs,dict(uids=[r['uid'] for r in selection],rows=rows,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId']),flush=True)
if __name__=='__main__':main()
