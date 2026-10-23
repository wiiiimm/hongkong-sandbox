"""Measure complete original pair coverage and the podium's tower-shaped void."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-west-kowloon-bus-37934-roof-pair-projection-v1-20261024';out=base/batch;assert not out.exists();runtime='government-xl-next-repairs-west-kowloon-bus-six-original-runtime-v2-20261024';_,pins=authenticate(base/runtime);path=base/runtime/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];selection=read(path);rows=[r for r in selection['rows']if r['uid']in ['landsd/37934:0','landsd/231056:0']];assert {r['uid']for r in rows}=={'landsd/37934:0','landsd/231056:0'}
    mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==selection['manifestSHA256'];refs=[Path(__file__),base/runtime/'result.json',path,mp];projections={};targets={};vertices=[];allforms={}
    for r in rows:
        p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes());assert len(t)==r['triangles'];projections[r['uid']]=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));vertices.append(t[:,:,[0,2]].reshape(-1,2))
        b=r['source']['building'];targets[r['uid']]=Polygon(b['rings'][0],b['rings'][1:]);tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert [f for f in read(tile)['buildings']if f['uid']==r['uid']]==[b];refs.append(tile)
        for f in read(tile)['buildings']:allforms[f['uid']]=f
    uids=set(projections);source=shapely.union_all(list(projections.values()));target=shapely.union_all(list(targets.values()));excess=source.difference(target);others=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:])for u,b in allforms.items()if u not in uids]);podium='landsd/37934:0';tower='landsd/231056:0';missing=targets[podium].difference(projections[podium])
    result=dict(uids=sorted(uids),sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},completeSourceFaces=sum(r['triangles']for r in rows),sourceProjectionAreaM2=float(source.area),targetUnionAreaM2=float(target.area),completePairTargetCoverage=float(source.intersection(target).area/target.area),maximumSourceVertexExtentM=float(shapely.distance(shapely.points(np.concatenate(vertices)),target).max()),unrelatedExcessAreaM2=float(excess.intersection(others).area),sourceExcessAreaM2=float(excess.area),podiumTargetMissingFromPodiumSourceM2=float(missing.area),podiumMissingCoveredByOriginalTowerM2=float(missing.intersection(projections[tower]).area),podiumMissingRemainingAfterOriginalTowerM2=float(missing.difference(projections[tower]).area),podiumTowerProjectedOverlapM2=float(projections[podium].intersection(projections[tower]).area),installationApproved=False,identityApproved=False,physicalAcceptance=False,publication=False,sourceGeometryChanges=0,qualification='Complete unchanged source projections and current target forms. GEOS area/extent measurements only; no assumption that an overlapping name or same OSM parent proves source identity. No buffered union, gap filling or physical acceptance.')
    save(out/'summary.json',result);save(out/'projected-regions.json',dict(completeSourceProjectionWKT=source.wkt,completeTargetUnionWKT=target.wkt,podiumMissingAfterTowerWKT=missing.difference(projections[tower]).wkt));refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('west_37934_roof_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'west-kowloon-shaft-roof-complete-original-pair-projection-diagnostic',list(dict.fromkeys(refs)),result);print({k:v for k,v in result.items()if k not in ['qualification','sourceSHA256ByUid']},flush=True)


if __name__=='__main__':main()
