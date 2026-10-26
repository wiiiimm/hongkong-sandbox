"""Exact subgrade context for all classified pair crossings in four represented worlds."""
import argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_segment_ground_clearance_v1_20261026 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','contacts','roles']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    finite=take(a.contacts,'summary.json');roles=take(a.roles,'summary.json');uids=finite['uids'];assert len(uids)==2 and roles['uids']==uids and roles['sourceSHA256ByUid']==finite['sourceSHA256ByUid']
    selected={r['uid']:r for r in take(a.runtime,'selection.json.gz')['rows']};geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    grounds={}
    for uid in uids:
        row=selected[uid];path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']==finite['sourceSHA256ByUid'][uid]==geometry[uid]['sourceSHA256'];refs.append(path);grounds[uid]=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    assert len(finite['rows'])==len(roles['rows'])==4 and {r['mode']for r in finite['rows']}=={r['mode']for r in roles['rows']}=={'original','literal','leftF32','balancedF32'}
    rows=[]
    for mode in finite['rows']:
        assert mode['allPairsExamined']and mode['sourceFacesOmitted']==0
        raw=take(a.contacts,mode['mode']+'.json.gz');classified=take(a.roles,mode['mode']+'.json.gz');role=next(r for r in roles['rows']if r['mode']==mode['mode'])
        assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0 and len(raw['contacts'])==len(classified)==mode['finiteContactPairs']==role['contactCount']
        assert all({k:v for k,v in c.items()if k!='contactRole'}==r for c,r in zip(classified,raw['contacts']))
        records=[]
        for c in classified:
            if c['contactRole']!='transverse-surface-crossing':continue
            assert c['dimension']==1 and len(c['exactPoints'])==2
            segment=[[F(x)for x in point]for point in c['exactPoints']];records.append(dict(sourceFaceA=c['sourceFaceA'],sourceFaceB=c['sourceFaceB'],exactSegment=c['exactPoints'],proofByGroundUid={uid:verify(segment,ground)for uid,ground in grounds.items()}))
        r=dict(mode=mode['mode'],sourceWorldSHA256ByUid=mode['sourceWorldSHA256ByUid'],completeContactCount=len(classified),completeContactRoles=role['roles'],transverseSegments=len(records),allTransverseSegmentsStrictlySubgrade=all(p['entireSegmentBelowEveryOverlappingGroundFacet']for c in records for p in c['proofByGroundUid'].values()),crossings=records);rows.append(r);save(out/(mode['mode']+'.json.gz'),r);print(dict(mode=r['mode'],crossings=len(records),allStrictlySubgrade=r['allTransverseSegmentsStrictlySubgrade']),flush=True)
    result=dict(uids=uids,sourceSHA256ByUid=finite['sourceSHA256ByUid'],completeGroundFacetsByUid={uid:len(g)for uid,g in grounds.items()},drawnGroundSHA256ByUid={uid:digest(g.tobytes())for uid,g in grounds.items()},rows=rows,allFourWorldTransverseSegmentsStrictlySubgrade=all(r['allTransverseSegmentsStrictlySubgrade']for r in rows),sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every classified transverse segment from all four authenticated complete finite-contact streams is checked against BOTH complete captured ground sets. Rational endpoints, full parameter coverage and all collapsed ground primitives retained. Absence of a crossing is recorded as zero, not inferred from another world. Shared-plane contacts, architectural roles, BASIC interference, identity, source terrain, visual and publication approval remain separate.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_original_segment_ground_clearance_v1_20261026.py','exact_original_triangle_pair_column_gap_20261010.py']);module('represented_pair_subgrade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-pair-transverse-segment-complete-ground-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
