"""Preserve regenerated raw rim samples in all four coordinate representations.
Diagnostics only: no clearance/contact assertion is waived or approved.
"""
import argparse
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_wall_rim_accounting_20261009 import original_samples
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as exact_column
from fractions import Fraction


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    r=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attr['sourceSHA256']==g['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)
    assert len(set(ix.ravel()))==len(literal)
    tri=decode_original_world_triangles(asset.read_bytes());original=literal.copy();original[ix.ravel()]=tri.reshape(-1,3);assert np.array_equal(original[ix],tri)
    worlds=dict(original=original,literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]])
    nonzero=shapely.area(polys)>0
    assert nonzero.any()
    sampler=module('raw_rim_sampler',HERE/'xl-final-script-pass.py');tree=shapely.STRtree(polys[nonzero]);rows=[]
    for mode,positions in worlds.items():
        bottom=float(positions[:,1].min());samples=original_samples(positions,ix,bottom);points=np.asarray([s['point']for s in samples]);heights=sampler.s.context.shared.samples(points[:,[0,2]],ground[nonzero],tree);assert np.isfinite(heights).all()
        finite_checks=[]
        for face in np.flatnonzero(~nonzero):
            facet=ground[face];lo,hi=facet[:,[0,2]].min(0),facet[:,[0,2]].max(0)
            candidates=np.flatnonzero(np.all(points[:,[0,2]]>=lo,axis=1)&np.all(points[:,[0,2]]<=hi,axis=1))
            for i in candidates:
                proof=exact_column(np.repeat(points[i][None,:],3,axis=0),facet)
                if proof['exactClosedHorizontalProjectionsMeet']:
                    height=float(Fraction(float(points[i,1]))-Fraction(proof['exactMinimumFiniteColumnGapM']))
                    heights[i]=max(heights[i],height)
                finite_checks.append(dict(sample=int(i),groundFace=int(face),proof=proof))
        gaps=points[:,1]-heights;low=points[:,1]<=bottom+.35;assert low.any()
        bad=[]
        for i,s in enumerate(samples):
            if low[i]and(gaps[i]<-.5 or gaps[i]>1):bad.append(dict(**s,ground=float(heights[i]),gap=float(gaps[i])))
        result=dict(mode=mode,sourceWorldSHA256=digest(positions[ix].astype('<f8').tobytes()),groundSHA256=digest(ground.tobytes()),samples=len(samples),completeDrawnGroundFacets=len(ground),zeroXZDrawnGroundFacets=int((~nonzero).sum()),exactZeroXZColumnChecks=finite_checks,lowRimSamples=int(low.sum()),minimumSampleGapM=float(gaps.min()),minimumRimGapM=float(gaps[low].min()),maximumRimGapM=float(gaps[low].max()),rawRimFailures=bad,groundContactResolved=bool(gaps[low].min()<=.1 and gaps[low].max()<=1 and gaps[low].min()>=-.5))
        save(out/(mode+'.json.gz'),result);rows.append(result);print({k:result[k]for k in ['mode','lowRimSamples','minimumRimGapM','maximumRimGapM','groundContactResolved']},flush=True)
    save(out/'summary.json',dict(uids=[a.uid],sourceSHA256=r['sourceSHA256'],rows=rows,installationApproved=False,sourceGeometryChanges=0,physicalAcceptance=False))
    refs.extend(HERE/n for n in ['xl-final-script-pass.py','original_wall_rim_accounting_20261009.py','exact_packed_world_geometry_20261009.py','exact_original_triangle_pair_column_gap_20261010.py'])
    module('raw_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-four-world-raw-contact-rim-sample-diagnostic',refs,dict(uids=[a.uid],sourceSHA256=r['sourceSHA256'],rows=rows,installationApproved=False))


if __name__=='__main__':main()
