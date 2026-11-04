"""Measure original component coverage of the podium footprint; no mesh changes."""
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-inone-podium-clubhouse-coverage-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-inone-adjoining-identity-v2-20261022';_,pins=authenticate(prior);p=prior/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=read(p)['rows'];refs=[Path(__file__),p,prior/'result.json',HERE/'exact_packed_world_geometry_20261009.py'];projections={};forms={}
 for row in rows:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
  t=decode_original_world_triangles(asset.read_bytes());assert len(t)==row['triangles'];polys=shapely.polygons(t[:,:,[0,2]]);projections[row['uid']]=shapely.union_all(polys[shapely.area(polys)>1e-10]);b=row['source']['building'];forms[row['uid']]=shapely.make_valid(shapely.Polygon(b['rings'][0],b['rings'][1:]))
 pod='landsd/277973:0';club='landsd/277974:0';missing=forms[pod].difference(projections[pod]);combined=projections[pod].union(projections[club]);remaining=forms[pod].difference(combined)
 summary=dict(uids=[pod,club],sourceHashes={r['uid']:r['sourceSHA256']for r in rows},podiumFootprintAreaM2=forms[pod].area,podiumAloneMissingAreaM2=missing.area,missingCoveredByClubhouseOriginalM2=missing.intersection(projections[club]).area,missingCoveredByClubhouseFootprintM2=missing.intersection(forms[club]).area,combinedMissingAreaM2=remaining.area,combinedCoverage=1-remaining.area/forms[pod].area,podiumMissingWKT=missing.wkt,remainingWKT=remaining.wkt,sourceGeometryChanges=0,installationApproved=False,qualification='Component projection accounting only; no support, terrain, identity or publication approval. Source assets remain separate and unchanged.')
 save(doc/'coverage.json',summary)
 module('inone_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-clubhouse-projection-accounting',refs,summary)
 print({k:v for k,v in summary.items()if not k.endswith('WKT')},flush=True)
if __name__=='__main__':main()
