"""Check complete collection primitives against an explicitly bounded inset cohort.

The explicit diagnostic construction bound is sixteen sources. Excluded co-imports are NOT removed
from the model collection; their complete original/literal projections must be
covered by the exact builder core. No terrain or approval is generated here.
"""
import argparse
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime']:
        p.add_argument('--'+name,required=True)
    p.add_argument('--inset-uid',action='append',required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    wanted=set(a.inset_uid);assert 0<len(wanted)==len(a.inset_uid)<=16
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert not doc.exists()
    cap=base/a.runtime;_,pins=authenticate(cap)
    refs=[Path(__file__),cap/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(cap/'selection.json.gz')['rows']
    geometry=take(HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']
    by={r['uid']:r for r in geometry}
    assert wanted<={r['uid'] for r in selection}==set(by)
    claim=reservations.claim('original-inset-mask-preflight-'+str(uuid.uuid4()),
        sorted('building:'+r['uid'] for r in selection),batch=a.batch,ttl=1800)
    assert claim['ok'];lease=claim['reservation']
    try:
        projection={};source_hashes={}
        for row in selection:
            uid=row['uid'];path=ROOT/row['candidate']['path'];raw=path.read_bytes()
            assert digest(raw)==row['sourceSHA256']==by[uid]['sourceSHA256']
            refs.append(path);source_hashes[uid]=row['sourceSHA256']
            original=decode_original_world_triangles(raw)
            literal=np.asarray(by[uid]['position']).reshape(-1,3)[np.asarray(by[uid]['index']).reshape(-1,3)]
            assert len(original)==len(literal)==row['triangles']
            projection[uid]={mode:shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in tri])
                             for mode,tri in [('original',original),('literal',literal)]}
        # Exactly the existing inset builder's construction policy.
        builder_projection=shapely.union_all([projection[uid]['literal'] for uid in sorted(wanted)])
        core=builder_projection.buffer(1,join_style='mitre')
        outer=core.buffer(3,join_style='mitre')
        rows=[]
        for uid in sorted(projection):
            for mode,poly in projection[uid].items():
                outside=poly.difference(core)
                rows.append(dict(uid=uid,mode=mode,inInsetCohort=uid in wanted,
                    completePrimitiveProjectionCovered=core.covers(poly),
                    outsideAreaM2=outside.area,outsideLengthM=outside.length,
                    minimumProjectionBoundaryClearanceM=poly.distance(core.boundary)))
        passed=all(r['completePrimitiveProjectionCovered'] for r in rows)
        out=dict(uids=sorted(projection),insetCohort=sorted(wanted),
            excludedFromInsetCohort=sorted(set(projection)-wanted),sourceSHA256ByUid=source_hashes,
            rows=rows,allCompleteOriginalAndLiteralPrimitivesCovered=passed,
            coreBounds=list(core.bounds),outerBounds=list(outer.bounds),
            coreBufferM=1,outerBufferM=3,sourceGeometryChanges=0,
            installationApproved=False,physicalAccepted=False,
            qualification='All complete collection faces, including projected lines and points, are represented. Core is constructed ONLY from the explicit <=16 original-model cohort using the unchanged inset builder rule. Exact Shapely covers in original and literal coordinates is a private construction preflight, not a rational layer/boundary certificate or source/ground/support/installation approval. Excluded sources remain in the co-import and require complete later four-world/source/terrain/runtime checks.')
        save(doc/'summary.json',out)
        assert reservations.owns(lease)
        module('original_inset_mask_preflight_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            a.batch,'complete-original-collection-bounded-inset-cohort-mask-preflight',list(dict.fromkeys(refs)),out)
        print(dict(allCovered=passed,insetCohort=sorted(wanted),excluded=out['excludedFromInsetCohort']),flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__=='__main__':
    main()
