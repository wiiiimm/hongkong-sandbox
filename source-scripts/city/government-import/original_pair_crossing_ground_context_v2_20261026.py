"""Bind every original-pair transverse segment to exact full drawn-ground clearance."""
import argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_ground_clearance_v1_20261026 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','contacts']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    context=take(a.contacts,base/a.contacts/'summary.json');uids=context['uids'];assert len(uids)==2 and context['completePairExamined']
    selected={r['uid']:r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']};geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']};hashes={}
    for row in context['rows']:
        uid=row['uid'];s=selected[uid];path=ROOT/s['candidate']['path'];assert digest(path.read_bytes())==s['sourceSHA256']==row['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(path);tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['completeSourceFaces'];hashes[uid]=s['sourceSHA256']
    grounds={uid:np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)for uid in uids}
    raw=take(a.contacts,base/a.contacts/'complete-classified-contacts.json.gz');crossings=[r for r in raw if r['contactRole']=='transverse-surface-crossing'];assert len(raw)==sum(context['contactDimensions'].values());records=[]
    for c in crossings:
        assert c['dimension']==1 and len(c['exactPoints'])==2
        segment=[[F(x)for x in point]for point in c['exactPoints']];proofs={uid:verify(segment,ground)for uid,ground in grounds.items()};records.append(dict(sourceFaceA=c['sourceFaceA'],sourceFaceB=c['sourceFaceB'],exactSegment=c['exactPoints'],proofByGroundUid=proofs))
    save(out/'crossing-segment-ground-proofs.json.gz',records)
    result=dict(uids=uids,sourceSHA256ByUid=hashes,drawnGroundSHA256ByUid={uid:digest(ground.tobytes())for uid,ground in grounds.items()},completeGroundFacetsByUid={uid:len(ground)for uid,ground in grounds.items()},completeOriginalContactDimensions=context['contactDimensions'],completeOriginalContactRoles=context['contactRoles'],transverseSegments=len(records),allOriginalTransverseSegmentsStrictlySubgrade=bool(records)and all(p['entireSegmentBelowEveryOverlappingGroundFacet']for r in records for p in r['proofByGroundUid'].values()),rows=records,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Original-world crossings only, independently checked against BOTH per-source complete captured ground sets (which need not be identical). Rational contact endpoints and complete rational finite source-segment/ground intersections; parameter interval union must cover the full segment. Every drawn ground facet including collapsed/vertical primitives is considered through a conservative broad phase. This proves only the stated crossing/terrain relationship; shared-face architecture, represented worlds, BASIC contacts, identity, source-role, visual and publication acceptance remain separate.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_original_segment_ground_clearance_v1_20261026.py','exact_original_triangle_pair_column_gap_20261010.py','exact_packed_world_geometry_20261009.py']);module('original_pair_subgrade_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-pair-crossing-segment-complete-ground-context',list(dict.fromkeys(refs)),result);print({k:result[k]for k in ['transverseSegments','allOriginalTransverseSegmentsStrictlySubgrade']})

if __name__=='__main__':main()
