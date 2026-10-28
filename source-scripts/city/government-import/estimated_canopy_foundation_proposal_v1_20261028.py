"""Private continuous-ground test of the existing illustrative-post mechanism.

Only wholly unsurveyed, non-native BASIC canopies qualify. The production builder
extends post bottoms; every roof, X/Z coordinate and government mesh stays fixed.
"""
import argparse
import subprocess
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','contacts','ground-uid','uid']:
        p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert not doc.exists()
    refs=[Path(__file__)];pins={}
    for name in [a.runtime,a.contacts]:
        folder=base/name;_,bound=authenticate(folder);refs.append(folder/'result.json')
        for path,sha in bound.items():
            assert path not in pins or pins[path]==sha
            pins[path]=sha
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    basic=next(r for r in take(base/a.contacts/'basic.json')['rows'] if r['uid']==a.uid)
    building=basic['currentBuilding']
    assert building['kind']=='roof' and building['structureType']=='Open-sided Structure'
    assert building['baseSource']=='terrain-estimated' and building['heightSource']=='estimated'
    assert building.get('baseHeightHKPD') is None and building.get('topHeightHKPD') is None
    assert not building.get('modelGeometry') and building.get('foundationBase') is None
    selection=take(base/a.runtime/'selection.json.gz')
    source=next(r for r in selection['rows'] if r['uid']==a.ground_uid)
    captured=next(r for r in take(HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows'] if r['uid']==a.ground_uid)
    assert captured['sourceSHA256']==source['sourceSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    tile=ROOT/'3d-viewer/city/data/tiles'/(building['tile']+'.json')
    assert [b for b in read(tile)['buildings'] if b['uid']==a.uid]==[building];refs.append(tile)
    installed=set()
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path)
        installed.update(m['uid'] for m in read(path)['models'])
    assert a.uid not in installed
    claim=reservations.claim('estimated-canopy-foundation-'+str(uuid.uuid4()),
        sorted({'building:'+a.uid,'building:'+a.ground_uid,'terrain:city/data/terrain.json'}),batch=a.batch,ttl=1800)
    assert claim['ok'];lease=claim['reservation']
    try:
        save(doc/'input.json',dict(building=building,expectedUid=a.uid))
        tool=HERE/'estimated_canopy_foundation_geometry_v1_20261028.mjs';refs.append(tool)
        def call(mode):
            with (doc/(mode+'.log')).open('w') as log:
                subprocess.run(['node',str(tool),str(doc.relative_to(ROOT))+'/',mode],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        call('describe')
        parts=read(doc/'description.json')['parts']
        assert parts and all(part['kind']=='roof' or part['kind']=='post' and part['illustrative'] for part in parts)
        ground=np.asarray(captured['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
        polygons=shapely.polygons(ground[:,:,[0,2]])
        valid=shapely.area(polygons)>1e-10
        coverage=shapely.union_all(polygons[valid])
        measures=[];all_post_heights=[]
        for part in parts:
            polygon=shapely.Polygon(part['rings'][0],part['rings'][1:])
            heights=[];face_ids=[]
            for index in np.flatnonzero(valid & shapely.intersects(polygons,polygon)):
                clipped=polygons[index].intersection(polygon)
                if clipped.area<=1e-10:continue
                coords=shapely.get_coordinates(clipped)
                one,two,three=ground[index];normal=np.cross(two-one,three-one)
                ys=one[1]-(normal[0]*(coords[:,0]-one[0])+normal[2]*(coords[:,1]-one[2]))/normal[1]
                heights.extend(ys.tolist());face_ids.append(int(index))
            assert heights
            row=dict(kind=part['kind'],groundRange=[min(heights),max(heights)],
                completeClippedFaceIds=face_ids,uncoveredAreaM2=polygon.difference(coverage).area,
                top=part['top'],originalBottom=part['bottom'])
            if part['kind']=='post':
                all_post_heights.extend(heights)
                row['postTopAboveAllGround']=part['top']>max(heights)+.02
            else:
                degenerate=[]
                for index in np.flatnonzero(~valid):
                    low,high=ground[index].min(0),ground[index].max(0)
                    if polygon.intersects(shapely.box(low[0],low[2],high[0],high[2]).buffer(1e-9)):
                        degenerate.append(int(index));heights.extend(ground[index,:,1].tolist())
                row['verticalOrDegenerateConservativeFaceIds']=degenerate
                row['groundRangeIncludingVerticals']=[min(heights),max(heights)]
                row['wholeRoofAboveAllGround']=part['bottom']>max(heights)+.02
            measures.append(row)
        assert all_post_heights
        foundation=float(min(all_post_heights))
        assert foundation<building['base']-.02
        for row in measures:
            if row['kind']=='post':
                row['foundationAtOrBelowAllGround']=foundation<=row['groundRange'][0]+.002
        qualified_posts=all(r['uncoveredAreaM2']<1e-8 and r['foundationAtOrBelowAllGround'] and r['postTopAboveAllGround'] for r in measures if r['kind']=='post')
        qualified_roof=all(r['wholeRoofAboveAllGround'] for r in measures if r['kind']=='roof')
        save(doc/'proposal.json',dict(uid=a.uid,foundationBase=foundation,originalBase=building['base'],
            roofElevationUnchanged=True,source='Minimum of exact drawn terrain clipped to every complete current illustrative post footprint.',
            noNewGovernmentGeometry=True,publication=False))
        save(doc/'continuous-part-ground-proof.json',dict(rows=measures,completeDrawnGroundSHA256=digest(ground.tobytes())))
        call('propose')
        proof=read(doc/'render-proof.json')
        assert proof['roofPartsExactlyUnchanged'] and proof['allXZExactlyUnchanged'] and proof['onlyIllustrativePostBottomVerticesChanged']
        assert proof['governmentGeometryChanges']==0
        summary=dict(uid=a.uid,uids=[a.uid],foundationBase=foundation,
            originalBase=building['base'],fullPostFootprintsMeetGround=qualified_posts,wholeRoofClear=qualified_roof,
            roofAndRecordedElevationsUnchanged=True,completePostCount=sum(p['kind']=='post' for p in parts),
            existingIllustrativeFoundationMechanism=True,privateIllustrativeGeometryChanges=1,
            renderProof=proof,sourceGeometryChanges=0,sourcePoseChanges=0,visibilitySuppressionApproved=False,
            fullAcceptance=False,collisionAndVisualAcceptancePending=True,installationApproved=False,
            qualification='Private proposal using existing foundationBase only. Every complete illustrative post footprint has continuous clipped-face coverage/ground bounds and unchanged top; the unchanged roof is tested conservatively against all intersecting ground, including vertical/degenerate face bounds. Deep non-native footings are intentional. This never qualifies government-source facets, changes surveyed/estimated roof elevations, hides a form, or clears coarse raw flags automatically.')
        save(doc/'summary.json',summary)
        for path,sha in proof['inputHashes'].items():
            assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
        refs.append(ROOT/'source-scripts/city/island-detail-integration/illustrative_foundations.py')
        assert reservations.owns(lease)
        module('estimated_canopy_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            a.batch,'existing-estimated-canopy-private-post-foundation-continuous-ground-proposal',list(dict.fromkeys(refs)),summary)
        print(dict(foundationBase=foundation,posts=summary['completePostCount'],allPostsQualified=qualified_posts,roofClear=qualified_roof),flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__=='__main__':
    main()
