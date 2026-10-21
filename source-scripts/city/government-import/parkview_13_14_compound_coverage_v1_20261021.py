"""Measure complete unchanged pair against both exact official footprints."""
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-13-14-compound-coverage-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];data={}
for batch,name in [('government-xl-next-three-primary-coverage-v1-20261021','coverage.json.gz'),('government-xl-parkview-14-companion-projection-v2-20261021','projection.json.gz'),('government-xl-parkview-13-14-primary-context-v1-20261021','context.json.gz')]:
 folder=BASE/batch;_,pins=authenticate(folder);p=folder/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);data[name]=read(p)
old=next(r for r in data['coverage.json.gz']['rows']if r['uid']=='landsd/253980:0');projection=data['projection.json.gz'];shapes={};permits={}
for r in data['context.json.gz']['rows']:
 provider=r['provider'];assert provider['spatialReference']['latestWkid']==2326;f=provider['features'][0];shape=shapely.GeometryCollection()
 for ring in f['geometry']['rings']:shape=shape.symmetric_difference(shapely.Polygon([(x-834500,816500-y)for x,y in ring]))
 assert shape.is_valid;shapes[r['uid']]=shape;permits[r['uid']]=sorted({f['attributes']['OPNo']for f in r['opStructures']['features']if f['attributes'].get('OPNo')})
assert shapes['landsd/253980:0'].equals(shapely.from_wkt(old['primaryWKT']))
a=shapely.from_wkt(old['sourceProjectionWKT']);b=shapely.from_wkt(projection['companionProjectionWKT']);source=a.union(b);official=shapely.union_all(list(shapes.values()));missing=official.difference(source)
summary=dict(uids=sorted(shapes),sourceSHA256ByUid={'landsd/253980:0':old['sourceSHA256'],'landsd/255260:0':projection['companionSourceSHA256']},occupationPermits=permits,officialAreaM2=official.area,sourceProjectionAreaM2=source.area,combinedFootprintCoverage=source.intersection(official).area/official.area,sourceInsideOfficial=source.intersection(official).area/source.area,uncoveredAreaM2=missing.area,officialPartOverlapM2=shapes['landsd/253980:0'].intersection(shapes['landsd/255260:0']).area,originalPartOverlapM2=a.intersection(b).area,originalPartsDistanceM=a.distance(b),installationApproved=False,identityAccepted=False,nextStep='Qualify exact adjoining source pair identity and current physical support with the installed podium; combined coverage alone is not acceptance.')
save(DOC/'coverage.json.gz',dict(**summary,combinedSourceWKT=source.wkt,combinedOfficialWKT=official.wkt,uncoveredWKT=missing.wkt));module('parkview_pair_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pair-primary-coverage',refs,summary);print(summary,flush=True)
