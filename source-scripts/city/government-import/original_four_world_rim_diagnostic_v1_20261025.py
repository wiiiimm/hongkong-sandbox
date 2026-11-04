"""Attribute canonical rim predicate failures without approving or editing sources."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_wall_rim_accounting_20261009 import original_samples
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)
    assert len(set(ix.ravel()))==len(literal)
    original=literal.copy();original[ix.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
    worlds=dict(original=original,literal=literal,
                leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),
                balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
    fullground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    polygons=shapely.polygons(fullground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
    ground,polygons=fullground[valid],polygons[valid];tree=shapely.STRtree(polygons)
    sampler=module('rim_diagnostic_same_sampler',HERE/'xl-final-script-pass.py');rows=[]
    for mode,vertices in worlds.items():
        bottom=float(vertices[:,1].min());samples=original_samples(vertices,ix,bottom)
        points=np.asarray([r['point']for r in samples]);heights=sampler.s.context.shared.samples(points[:,[0,2]],ground,tree)
        assert np.isfinite(heights).all();gaps=points[:,1]-heights;low=points[:,1]<=bottom+.35
        predicates=dict(hasLowSamples=bool(low.any()),completeSampleClearance=bool(gaps.min()>=-.5),
                        minimumGradeContact=bool(low.any()and gaps[low].min()<=.1),
                        maximumLowRimGap=bool(low.any()and gaps[low].max()<=1))
        records=[dict(**r,ground=float(h),gap=float(q),low=bool(l))for r,h,q,l in zip(samples,heights,gaps,low)]
        failed=[r for r in records if r['gap']<-.5 or(r['low']and r['gap']>1)]
        summary=dict(mode=mode,predicates=predicates,allCanonicalSamplePredicatesPass=all(predicates.values()),
                     samples=len(samples),lowSamples=int(low.sum()),minimumGapM=float(gaps.min()),
                     minimumLowGapM=float(gaps[low].min())if low.any()else None,
                     maximumLowGapM=float(gaps[low].max())if low.any()else None,
                     failedSamples=len(failed),sourceWorldSHA256=digest(vertices[ix].astype('<f8').tobytes()))
        save(out/(mode+'.json.gz'),dict(**summary,sourceSHA256=source['sourceSHA256'],completeOriginalSamples=records,
                                      failedSamplesVerbatim=failed,completeDrawnGroundSHA256=digest(fullground.tobytes()),
                                      canonicalPositiveProjectionGroundSHA256=digest(ground.tobytes())))
        rows.append(summary);print(summary,flush=True)
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=rows,
                sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,
                qualification='Exact same original sample attribution and drawn-ground sampler as canonical rims. Complete and positive-projection ground hashes both retained. Reports failed predicates only; no contact limit, source coordinate, role, dependency or publication approval changes.')
    save(out/'summary.json',result)
    refs += [HERE/'original_wall_rim_accounting_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']
    module('rim_diagnostic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-canonical-original-rim-predicate-attribution',refs,result)


if __name__=='__main__':main()
