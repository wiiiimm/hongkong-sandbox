"""Full foundation diagnostic for the whole-neighbour preserved hotel terrain."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-disney-hotel-restored-foundation-v1-20261016';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-disney-hotel-whole-neighbour-ground-v2-20261016'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 path=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';g=read(path)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);selection=read(PRIOR/'selection.json.gz')['rows'][0];b=selection['source']['building'];assert len(tri)==15425 and g['sourceSHA256']==selection['sourceSHA256']
 helper=module('hotel_restored_foundation',HERE/'xl-final-script-pass.py');foundation=helper.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));DOC.mkdir();save(DOC/'foundation.json',foundation)
 refs += [path,PRIOR/'selection.json.gz',HERE/'xl-final-script-pass.py']
 r=module('hotel_restored_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hotel-restored-ground-whole-foundation-v1',list(dict.fromkeys(refs)),dict(uids=[selection['uid']],foundation=foundation,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],foundation=foundation),flush=True)
if __name__=='__main__':main()
