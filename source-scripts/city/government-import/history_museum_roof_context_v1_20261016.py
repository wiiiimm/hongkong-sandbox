"""Exact original-source coverage of the retained roof form; no suppression approval."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-roof-context-v1-20261016';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-history-museum-native-regression-v1-20261016';REPAIR=BASE/'government-xl-history-museum-preserved-neighbours-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 geometry=HERE/'local'/REPAIR.name/'runtime-geometry.json.gz';g=read(geometry)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);selection=read(REPAIR/'selection.json.gz')['rows'][0];b=selection['source']['building'];inputs=read(REPAIR/'neighbour-inputs.json.gz');roof=next(r['building']for r in inputs['rows']if r['building']['uid']=='landsd/4760:0');foot=Polygon(roof['rings'][0],roof['rings'][1:]);polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;projection=shapely.union_all(polys[valid]);overlap=foot.intersection(projection);missing=foot.difference(projection);touch=shapely.intersects(polys,foot);ids=np.flatnonzero(touch).tolist();helper=module('museum_roof_foundation',HERE/'xl-final-script-pass.py');foundation=helper.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]))
 summary=dict(uid=selection['uid'],roofUid=roof['uid'],roofForm=roof,roofAreaM2=foot.area,coveredAreaM2=overlap.area,coverageFraction=overlap.area/foot.area,missingAreaM2=missing.area,sourceFaceIdsIntersectingRoof=ids,sourceIntersectingYRange=[float(tri[touch,:,1].min()),float(tri[touch,:,1].max())],pairedSourceIdentityApproved=False,suppressionApproved=False,foundation=foundation,fullAcceptance=False,contextSources=[dict(url='https://fpf.ccidahk.gov.hk/en/location/detail.php?id=442',finding='Government location record describes a raised piazza linking the History and Science museums; this does not identify each exact source facet.'),dict(url='https://hk.history.museum/en/web/mh/about-us/introduction.html',finding='Museum introduction describes the neighbouring buildings as one museum complex; no exact source ownership approval follows.')])
 DOC.mkdir();save(DOC/'context.json.gz',summary);save(DOC/'summary.json',{k:v for k,v in summary.items()if k not in ['roofForm','sourceFaceIdsIntersectingRoof']});refs += [geometry,REPAIR/'selection.json.gz',REPAIR/'neighbour-inputs.json.gz',HERE/'xl-final-script-pass.py',Path(helper.s.context.shared.__file__)]
 out=module('museum_roof_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-original-roof-form-coverage-and-repaired-foundation-v1',list(dict.fromkeys(refs)),dict(uids=[selection['uid'],roof['uid']],summary=read(DOC/'summary.json'),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],coverageFraction=summary['coverageFraction'],missingAreaM2=missing.area,fullyBuried=foundation['fullyBuriedTriangles']),flush=True)
if __name__=='__main__':main()
