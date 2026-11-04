"""Exact source/current terrain column-gap evidence for explicitly flagged source faces.

Diagnostic minima only; never a placement, burial-role or publication approval.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','continuous','discovery','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    ctx=take(a.continuous,base/a.continuous/(a.uid.split('/')[1]+'.json.gz'))
    discovery=take(a.discovery,base/a.discovery/'summary.json')
    assert row['sourceSHA256']==g['sourceSHA256']==ctx['sourceSHA256']==discovery['sourceSHA256']
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    source=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    assert digest(source.tobytes())==ctx['sourceBinding']['decodedWorldTrianglesSHA256']
    current=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);valid=shapely.area(shapely.polygons(current[:,:,[0,2]]))>1e-10;current=current[valid]
    assert digest(current.tobytes())==ctx['sourceBinding']['drawnGroundSHA256']
    decoder=module('original_wall_source_ground_decoder',HERE/'xl-second-pass.py');parts=[]
    for name in discovery['sourceTerrainPaths']:
        path=ROOT/name;meta=take(a.discovery,path)
        for b in meta.get('buffers',[]):
            f=path.parent/b['uri'];assert digest(f.read_bytes())==pins[a.discovery][str(f.relative_to(ROOT))];refs.append(f)
        parts.append(decoder.terrain_triangles(path))
    original=np.concatenate(parts);lo,hi=source.min((0,1)),source.max((0,1));keep=(original[:,:,0].max(1)>=lo[0]-1)&(original[:,:,0].min(1)<=hi[0]+1)&(original[:,:,2].max(1)>=lo[2]-1)&(original[:,:,2].min(1)<=hi[2]+1);original=original[keep]
    rows=[];proofs=[]
    for i in ctx['continuousAffectedFaces']:
        face=source[i];measurements={}
        for mode,ground in [('originalSourceTerrain',original),('currentRenderedTerrain',current)]:
            xz=ground[:,:,[0,2]];lo,hi=face[:,[0,2]].min(0),face[:,[0,2]].max(0)
            ids=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1));pairs=[]
            for j in ids:
                proof=verify(face,ground[j]);pairs.append(dict(groundFace=int(j),**proof))
            gaps=[Fraction(p['exactMinimumFiniteColumnGapM'])for p in pairs if p['exactClosedHorizontalProjectionsMeet']]
            assert gaps
            minimum=min(gaps);coverage=exact_coverage(face,ground)
            measurements[mode]=dict(exactMinimumGapM=str(minimum),belowOrdinaryClearanceLimit=minimum<Fraction(-1,2),completeGroundFaces=len(ground),completeGroundSHA256=digest(ground.tobytes()),projectionCovered=coverage['exactProjectionCovered'])
            proofs.append(dict(sourceFace=i,mode=mode,coverage=coverage,pairs=pairs))
        rows.append(dict(sourceFace=i,sourceFaceSHA256=digest(face.tobytes()),normalYRatio=ctx['faces'][i]['normalYRatio'],**measurements))
        print(dict(sourceFace=i,originalBelow=measurements['originalSourceTerrain']['belowOrdinaryClearanceLimit'],currentBelow=measurements['currentRenderedTerrain']['belowOrdinaryClearanceLimit']),flush=True)
    save(out/'proofs.json.gz',proofs);save(out/'faces.json',rows)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],comparedFaces=len(rows),originalTerrainBelowLimitFaces=sum(r['originalSourceTerrain']['belowOrdinaryClearanceLimit']for r in rows),currentTerrainBelowLimitFaces=sum(r['currentRenderedTerrain']['belowOrdinaryClearanceLimit']for r in rows),allFlaggedFacesCompared=True,sourceGeometryChanges=0,installationApproved=False,publication=False,status='exact-original-current-terrain-wall-comparison',qualification='Every AABB-nominated original/current terrain pair for every flagged source face receives exact barycentric same-XZ finite-column enumeration. Minima only; no pointwise terrain nonregression, basement/architectural-role interpretation, whole-model acceptance, threshold exemption or publication approval.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['xl-second-pass.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py'])
    module('source_terrain_wall_comparison_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-current-terrain-wall-comparison',refs,result)
    print({k:result[k]for k in ['comparedFaces','originalTerrainBelowLimitFaces','currentTerrainBelowLimitFaces']},flush=True)

if __name__=='__main__':main()
