"""Measure original companion coverage of a target's missing footprint and cell.

Analytical projections only. No model edits, identity or installation approval.
"""
from pathlib import Path
import argparse
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def above_height_projection(triangles,height):
    polygons=[]
    for tri in triangles:
        points=[]
        for a,b in zip(tri,np.roll(tri,-1,axis=0)):
            ai,bi=a[1]>=height,b[1]>=height
            if ai:points.append(a)
            if ai!=bi:points.append(a+(b-a)*((height-a[1])/(b[1]-a[1])))
        if len(points)>=3:
            p=shapely.Polygon(np.asarray(points)[:,[0,2]])
            if p.area>0:polygons.append(p)
    return shapely.union_all(polygons)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','selection','identity','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.selection,base/a.selection/'selection.json.gz');target=next(r for r in selected['rows'] if r['uid']==a.uid)
    identity=take(a.identity,base/a.identity/(a.uid.split('/')[1]+'/identity.json'))
    assert identity['sourceSHA256']==target['sourceSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    form=target['source']['building'];polygon=shapely.Polygon(form['rings'][0],form['rings'][1:]);height=form['topHeightHKPD']
    projection={};high={};bindings={};counts={}
    for row in selected['rows']:
        uid=row['uid'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(f for f in read(tile)['buildings'] if f['uid']==uid)==row['source']['building'];refs.append(tile)
        tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['native']['model']['triangles']
        projection[uid]=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));high[uid]=above_height_projection(tri,height);bindings[uid]=row['sourceSHA256'];counts[uid]=len(tri)
    own=projection[a.uid];missing=polygon.difference(own);combined=shapely.union_all(list(projection.values()));combined_high=shapely.union_all(list(high.values()))
    raw=identity['freshCurrentIdentity']['targetCoveredBySourceProjection'];measured=own.intersection(polygon).area/polygon.area;assert abs(raw-measured)<1e-9
    cb=identity['geographicCell']['worldXZBounds'];cell=shapely.box(*cb)
    rows=[dict(uid=uid,originalFaces=counts[uid],missingTargetAreaCoveredM2=projection[uid].intersection(missing).area,missingTargetAreaCoveredAtOrAboveRecordedTopM2=high[uid].intersection(missing).area,originalProjectionCoversTargetCell=bool(projection[uid].covers(cell))) for uid in projection]
    result=dict(uids=sorted(bindings),targetUid=a.uid,sourceSHA256ByUid=bindings,currentManifestSHA256=selected['manifestSHA256'],completeOriginalFaces=sum(counts.values()),targetAreaM2=polygon.area,recordedTargetTopHKPD=height,ownCoverageFraction=measured,missingOwnTargetAreaM2=missing.area,combinedCoverageFraction=combined.intersection(polygon).area/polygon.area,remainingUncoveredTargetAreaM2=polygon.difference(combined).area,combinedMissingTargetAreaCoveredAtOrAboveRecordedTopM2=combined_high.intersection(missing).area,wholeTargetCellCoveredByCombinedProjection=bool(combined.covers(cell)),rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,identityApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Float64 analytical area projections of complete decoded original sources. Faces are clipped above the recorded target height only for a diagnostic projection; no clipped model is emitted. Combined coverage is not source ownership, exact rational cell proof, support/terrain/browser acceptance or permission to partially remove a baseline model.')
    save(out/'summary.json',result)
    save(out/'projection-diagnostic.json.gz',dict(target=shapely.to_geojson(polygon),missingOwnTarget=shapely.to_geojson(missing),combinedOriginalProjection=shapely.to_geojson(combined),combinedAtOrAboveRecordedTop=shapely.to_geojson(combined_high)))
    module('companion_projection_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-companion-target-projection-coverage-diagnostic',refs,result)
    print({k:result[k] for k in ['targetUid','ownCoverageFraction','missingOwnTargetAreaM2','combinedCoverageFraction','remainingUncoveredTargetAreaM2','combinedMissingTargetAreaCoveredAtOrAboveRecordedTopM2','wholeTargetCellCoveredByCombinedProjection','rows']},flush=True)


if __name__=='__main__':main()
