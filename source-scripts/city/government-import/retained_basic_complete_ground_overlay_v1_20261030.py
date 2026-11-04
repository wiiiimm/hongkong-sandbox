"""Measure unchanged retained BASIC footprint over actual before/after ground."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','before','after','scope','source-uid','basic-uid']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists()
    refs=[Path(__file__),HERE/'ronsdale_local_inset_v2_20261022.py'];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    forms=take(a.scope,base/a.scope/(a.source_uid.split('/')[1]+'-forms.json.gz'))
    form=next(r for r in forms if r['building']['uid']==a.basic_uid);basic=form['building']
    tile=ROOT/'3d-viewer'/form['tile'];assert digest(tile.read_bytes())==form['tileSHA256'];refs.append(tile)
    assert next(b for b in read(tile)['buildings']if b['uid']==a.basic_uid)==basic
    footprint=shapely.Polygon(basic['rings'][0],basic['rings'][1:]);assert footprint.is_valid and footprint.area>0
    rows={};fragments={};original=None
    for mode,batch in [('before',a.before),('after',a.after)]:
        data=take(batch,HERE/'local'/batch/'runtime-geometry.json.gz');g=next(r for r in data['rows']if r['uid']==a.source_uid)
        if original is None:original=g
        else:
            assert g['sourceSHA256']==original['sourceSHA256']
            assert np.array_equal(g['position'],original['position'])and np.array_equal(g['index'],original['index'])
        ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polygons=shapely.polygons(ground[:,:,[0,2]])
        valid=shapely.area(polygons)>0;clips=[];heights=[]
        for index in np.flatnonzero(valid&shapely.intersects(polygons,footprint)):
            clipped=polygons[index].intersection(footprint)
            if clipped.area==0:continue
            equation=plane(ground[index]);xz=shapely.get_coordinates(clipped)
            heights.extend((xz@equation[:2]+equation[2]).tolist());clips.append((clipped,equation))
        assert heights
        coverage=shapely.union_all([r[0]for r in clips]);fragments[mode]=clips
        vertical=[]
        for index in np.flatnonzero(~valid):
            hull=shapely.MultiPoint(ground[index][:,[0,2]]).convex_hull
            if hull.intersects(footprint):vertical.append(dict(faceIndex=int(index),vertices=ground[index].tolist()))
        rows[mode]=dict(completeFootprintAreaM2=footprint.area,uncoveredAreaM2=footprint.difference(coverage).area,groundRangeM=[min(heights),max(heights)],maximumBasicBottomAboveGroundM=basic['base']+basic.get('minimum',0)-min(heights),positiveAreaGroundFragments=len(clips),verticalOrDegenerateIntersections=vertical)
    changes=[];overlays=[]
    for old,op in fragments['before']:
        for new,np_ in fragments['after']:
            overlap=old.intersection(new)
            if overlap.area==0:continue
            eq=np_-op;xz=shapely.get_coordinates(overlap);changes.extend((xz@eq[:2]+eq[2]).tolist());overlays.append(overlap)
    assert changes
    result=dict(uids=[a.source_uid,a.basic_uid],sourceSHA256=original['sourceSHA256'],exactBasicForm=basic,rows=rows,completeOverlayMaximumAbsoluteGroundChangeM=max(map(abs,changes)),completeOverlayUncoveredAreaM2=footprint.difference(shapely.union_all(overlays)).area,sourceGeometryChanges=0,basicGeometryChanges=0,terrainEdits=False,installationApproved=False,physicalAcceptance=False,qualification='Complete actual drawn ground clipped to every positive-area part of the unchanged retained BASIC footprint, with exact plane-difference extrema at all overlay vertices. Raw numerical coverage and vertical/degenerate contacts retained; no source/support/architectural approval, geometry edit or threshold waiver.')
    save(doc/'summary.json',result)
    module('retained_basic_ground_overlay_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-retained-basic-current-ground-before-after-overlay',refs,result)
    print(dict(basicUid=a.basic_uid,maximumGroundChangeM=result['completeOverlayMaximumAbsoluteGroundChangeM'],before=rows['before']['groundRangeM'],after=rows['after']['groundRangeM'],overlayUncoveredM2=result['completeOverlayUncoveredAreaM2']))

if __name__=='__main__':main()
