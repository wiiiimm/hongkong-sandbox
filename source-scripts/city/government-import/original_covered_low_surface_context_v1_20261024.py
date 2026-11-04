"""Exact original overhead context for low surfaces lacking clear-cap paths.

No architectural, physical, identity or publication approval is inferred.
"""
import argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','low-faces','cap-paths','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    assert row['sourceSHA256']==attr['sourceSHA256']==g['sourceSHA256']
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field]).reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes())
    caps=take(a.cap_paths,base/a.cap_paths/'summary.json');assert caps['sourceSHA256']==row['sourceSHA256']
    rows=[]
    for mode,tri in worlds.items():
        low=take(a.low_faces,base/a.low_faces/(mode+'.json.gz'))
        assert low['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())and low['groundSHA256']==ground_sha
        bad={r['sourceFace']for r in low['rows']};partition=next(r for r in caps['rows']if r['mode']==mode)['completeGroundClearancePartition']
        walls=[r['sourceFace']for r in partition['paths']if not r['hasExactSharedEdgeClearCapPath']]
        nonwalls=partition['negativeNonWallFaces'];targets=sorted(set(walls)|set(nonwalls));assert targets and set(targets)<=bad
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
        roof_ids=[i for i in range(len(tri))if i not in bad and length[i]>0 and normals[i,1]/length[i]>.25]
        roofs=tri[roof_ids];polys=shapely.polygons(roofs[:,:,[0,2]]);tree=shapely.STRtree(polys)
        records=[]
        for faceid in targets:
            face=tri[faceid];projection=shapely.MultiPoint(face[:,[0,2]]).convex_hull
            slots=tree.query(projection,predicate='intersects');dominant=[];proofs=[]
            for slot in slots:
                i=roof_ids[int(slot)]
                if tri[i,:,1].max()<face[:,1].min():continue
                proof=verify(tri[i],face)
                if proof['exactClosedHorizontalProjectionsMeet']and F(proof['exactMinimumFiniteColumnGapM'])>=0:
                    dominant.append(i);proofs.append(dict(overheadFace=i,**proof))
            coverage=exact_coverage(face,tri[dominant])if dominant else dict(exactProjectionCovered=False)
            signed=float(normals[faceid,1]/length[faceid])if length[faceid]else None
            records.append(dict(sourceFace=faceid,rawClearCapPathUnresolved=faceid in walls,negativeNonWall=faceid in nonwalls,signedNormalYRatio=signed,completelyClearOriginalOverheadFaces=dominant,wholeSourceProjectionCoveredByDominatingClearOriginalFaces=coverage['exactProjectionCovered'],exactCoverage=coverage,exactDominanceProofs=proofs))
        save(out/(mode+'.json.gz'),dict(sourceWorldSHA256=low['sourceWorldSHA256'],completeDrawnGroundSHA256=ground_sha,allClearRoofIds=roof_ids,rows=records))
        result=dict(mode=mode,unresolvedWallFaces=len(walls),negativeNonWallFaces=nonwalls,targets=len(targets),covered=sum(r['wholeSourceProjectionCoveredByDominatingClearOriginalFaces']for r in records),uncoveredFaces=[r['sourceFace']for r in records if not r['wholeSourceProjectionCoveredByDominatingClearOriginalFaces']])
        rows.append(result);print(result,flush=True)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],rows=rows,allFourWorldTargetsHaveClearSourceOwnedOverhead=all(not r['uncoveredFaces']for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,architectureReview=False,physicalAcceptance=False,installationApproved=False,qualification='Every nominated whole source face projection is tested for exact coverage by dominating upward original facets of the SAME complete unchanged source. Overhead candidates are absent from the authenticated complete actual-ground negative partition, so they satisfy the existing ordinary0.5m clearance threshold. No borrowed roof, new source cut, structural purpose or ground/root/physical approval is inferred. Retain all raw cap failures and nonwall negatives; source roles and actual images require separate review.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_packed_world_geometry_20261009.py'])
    module('covered_low_source_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-source-owned-clear-overhead-context-for-low-original-surfaces',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
