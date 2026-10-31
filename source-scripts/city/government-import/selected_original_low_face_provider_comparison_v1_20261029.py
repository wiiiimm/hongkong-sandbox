"""Compare all exact current negative facets against byte-bound original terrain.

Literal-world nomination only; no source role, physical or publication approval.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage

def main():
    ap=argparse.ArgumentParser()
    for k in ['batch','runtime','low-faces','terrain-check','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();pins={};refs=[Path(__file__)]
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    source=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];current=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    low=take(a.low_faces,base/a.low_faces/'literal.json.gz');assert low['sourceWorldSHA256']==digest(source.tobytes())and low['groundSHA256']==digest(current.tobytes())
    checked=next(r for r in take(a.terrain_check,base/a.terrain_check/'summary.json')['rows']if r['uid']==a.uid);assert checked['sourceSHA256']==g['sourceSHA256']
    decoder=module('selected_low_provider_terrain',HERE/'xl-second-pass.py');parts=[]
    for name in checked['sourceTerrainPaths']:
        path=ROOT/name;meta=take(a.terrain_check,path)
        for b in meta.get('buffers',[]):take(a.terrain_check,path.parent/b['uri']) if False else None
        for b in meta.get('buffers',[]):
            p=path.parent/b['uri'];assert digest(p.read_bytes())==pins[a.terrain_check][str(p.relative_to(ROOT))];refs.append(p)
        parts.append(decoder.terrain_triangles(path))
    provider=np.concatenate(parts);xz=provider[:,:,[0,2]];glo,ghi=xz.min(1),xz.max(1);rows=[]
    for record in low['rows']:
        i=record['sourceFace'];t=source[i];assert np.array_equal(t,np.asarray(record['vertices']));txz=t[:,[0,2]]
        ids=np.flatnonzero(np.all(ghi>=txz.min(0),axis=1)&np.all(glo<=txz.max(0),axis=1));pairs=[]
        for j in ids:
            proof=verify(t,provider[j])
            if proof['exactClosedHorizontalProjectionsMeet']:pairs.append(dict(groundFace=int(j),proof=proof))
        coverage=exact_coverage(t,provider[ids]);minimum=min((Fraction(p['proof']['exactMinimumFiniteColumnGapM'])for p in pairs),default=None)
        normal=np.cross(t[1]-t[0],t[2]-t[0]);length=float(np.linalg.norm(normal))
        rows.append(dict(sourceFace=i,vertices=t.tolist(),normalYRatio=float(normal[1]/length)if length else None,currentMinimumGapM=record['minimumFiniteGapM'],providerMinimumGapM=str(minimum)if minimum is not None else None,providerStillBelowOrdinaryLimit=minimum is not None and minimum<Fraction(-1,2),providerCoverage=coverage,providerPairs=pairs))
    result=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],sourceWorldSHA256=low['sourceWorldSHA256'],completeDrawnGroundSHA256=low['groundSHA256'],allCurrentNegativeFacesCompared=len(rows),providerNegativeFaces=sum(r['providerStillBelowOrdinaryLimit']for r in rows),providerClearFaces=[r['sourceFace']for r in rows if r['providerCoverage']['exactProjectionCovered']and not r['providerStillBelowOrdinaryLimit']],sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every literal-world face in the complete exact current negative-clearance partition is compared with exact finite original-provider terrain pairs and complete projection coverage. Diagnostic nomination only; other coordinate streams, source roles, neighbours and publication remain independent.')
    save(out/'faces.json.gz',rows);save(out/'summary.json',result);refs.extend(HERE/n for n in ['xl-second-pass.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py']);module('selected_low_provider_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'all-current-literal-negative-faces-original-provider-comparison',list(dict.fromkeys(refs)),result)
    print(dict(compared=len(rows),providerNegative=result['providerNegativeFaces'],providerClear=len(result['providerClearFaces'])),flush=True)

if __name__=='__main__':main()
