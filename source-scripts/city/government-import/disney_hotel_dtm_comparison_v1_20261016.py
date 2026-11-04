"""Compare unresolved source contacts with the cached official five-metre DTM."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-disney-hotel-dtm-comparison-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-disney-hotel-current-contacts-v1-20261016'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 dtm=module('hotel_official_dtm',HERE/'xl-original-dtm-terrain-followthrough.py');faces,proof=dtm.original_faces([-12090,-2350,-11790,-2180]);helper=module('hotel_dtm_foundation',HERE/'xl-final-script-pass.py');polys=shapely.polygons(faces[:,:,[0,2]]);tree=shapely.STRtree(polys)
 contacts=read(PRIOR/'contacts.json.gz');points=np.asarray([r['position'] for r in contacts['failures']]);heights=helper.s.context.shared.samples(points[:,[0,2]],faces,tree);assert np.isfinite(heights).all()
 rows=[dict(**r,officialDtmHeight=float(h),officialDtmGapM=float(r['position'][1]-h))for r,h in zip(contacts['failures'],heights)]
 geometry=HERE/'local/government-xl-disney-hotel-whole-neighbour-ground-v2-20261016/runtime-geometry.json.gz';g=read(geometry)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];selection=BASE/'government-xl-disney-hotel-whole-neighbour-ground-v2-20261016/selection.json.gz';b=read(selection)['rows'][0]['source']['building'];foundation=helper.foundation_context(tri,faces,Polygon(b['rings'][0],b['rings'][1:]))
 summary=dict(failedSampleCount=len(rows),lowRim=[dict(position=r['position'],currentGapM=r['gapM'],officialDtmGapM=r['officialDtmGapM'])for r in rows if r['reason']=='low-rim-gap'],remainingBurialSamples=sum(r['officialDtmGapM']<-.5 for r in rows),foundation=foundation,fullAcceptance=False,limitation='Archival DTM and source building revisions differ; this comparison is not a runtime terrain candidate or acceptance.')
 DOC.mkdir();save(DOC/'comparison.json.gz',dict(source=proof,rows=rows,summary=summary));save(DOC/'summary.json',summary)
 refs += [HERE/'xl-original-dtm-terrain-followthrough.py',ROOT/dtm.SOURCE,ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json',HERE/'xl-final-script-pass.py',Path(helper.s.context.shared.__file__),geometry,selection,PRIOR/'contacts.json.gz']
 r=module('hotel_dtm_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'official-five-metre-dtm-hotel-contact-comparison-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/236354:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
