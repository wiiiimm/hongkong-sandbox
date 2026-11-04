"""Whole immutable mall comparison with authentic official 5m DTM; no publication."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-dtm-comparison-v1-20261020';DOC=BASE/BATCH;ATTR=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
def main():
 assert not DOC.exists();r=read(ATTR/'result.json');refs=[Path(__file__),ATTR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256'] for e in r['evidenceRefs']};p=ATTR/'input.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 row=next(r for r in read(p)['rows']if r['uid']=='landsd/289787:0');asset=ROOT/row['path'];assert digest(asset.read_bytes())==row['entry']['sha256'];refs.append(asset)
 tri=decode_original_world_triangles(asset.read_bytes());lo=tri.min((0,1));hi=tri.max((0,1));bounds=[float(lo[0]-10),float(lo[2]-10),float(hi[0]+10),float(hi[2]+10)]
 dtm=module('mount_original_dtm',HERE/'xl-original-dtm-terrain-followthrough.py');ground,proof=dtm.original_faces(bounds)
 helper=module('mount_dtm_foundation',HERE/'xl-final-script-pass.py');b=row['building'];f=helper.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]))
 save(DOC/'comparison.json',dict(uid=row['uid'],sourceSHA256=row['entry']['sha256'],dtm=proof,foundation=f,fullAcceptance=False,limitation='Archival DTM and building source revisions differ; no runtime replacement or source placement approval.'))
 local=HERE/'local'/BATCH/'original-dtm.json.gz';save(local,dict(originalTerrain=ground.tolist(),provenance=proof));refs.extend([local,HERE/'xl-original-dtm-terrain-followthrough.py',ROOT/dtm.SOURCE,ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 summary=dict(uids=[row['uid']],foundation=f,fullAcceptance=False,sourceGeometryChanges=0,terrainPublished=False)
 module('mount_dtm_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-original-mall-official-five-metre-dtm-comparison',refs,summary)
 print(summary,flush=True)
if __name__=='__main__':main()
