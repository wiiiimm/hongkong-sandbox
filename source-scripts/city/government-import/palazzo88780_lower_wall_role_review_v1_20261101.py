"""Bound the single original88780 wall crossing to actual grade and exposed source."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'88780-lower-wall-role-review-v1-20261101'
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));uid='landsd/88780:0';assert reservations.owns(lease)and'building:'+uid in lease['resources'];out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name,external=None):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=external if external is not None else BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rt=P+'twenty-authentic-tin-runtime-v1-20261101';at=P+'twenty-original-attributes-v1-20261101';s=next(r for r in take(rt,'selection.json.gz')['rows']if r['uid']==uid);attr=next(r for r in take(at,'attributes.json.gz')['rows']if r['uid']==uid);g=next(r for r in take(rt,'',HERE/'local'/rt/'runtime-geometry.json.gz')['rows']if r['uid']==uid);asset=ROOT/s['candidate']['path'];assert digest(asset.read_bytes())==s['sourceSHA256']==attr['sourceSHA256']==g['sourceSHA256'];refs.append(asset);worlds=represented(attr,decode_original_world_triangles(asset.read_bytes()));ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);records=[]
    for mode,tri in worlds.items():
        raw=take(P+'88780-twenty-complete-ground-v1-20261101',{'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)+'.json.gz');grade=take(P+'88780-twenty-source-ground-contacts-v1-20261101',mode+'.json.gz');sha=digest(tri.astype('<f8').tobytes());gsha=digest(ground.tobytes());assert raw['sourceWorldSHA256']==grade['sourceWorldSHA256']==sha and raw['groundSHA256']==grade['completeGroundSHA256']==gsha
        assert len(raw['rows'])==1;r=raw['rows'][0];assert r['sourceFace']==21 and r['absoluteNormalYRatio']==0 and r['highestVertexAboveEveryOverlappingGroundFace']and np.asarray(r['vertices'],dtype='<f8').tobytes()==tri[21].tobytes()
        proof=grade['proof'];assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0 and grade['groundFacesOmitted']==0;contacts=[c for c in proof['contacts']if c['sourceFaceA']==21 and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2];assert contacts
        paths=take(P+'88780-finite-original-attachments-v1-20261101',mode+'.json.gz')['rows'];assert len(paths)==34 and all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 for r in paths)
        records.append(dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=gsha,rawNegativeFaces=[21],verticalOriginalWall=True,actualPositiveGradeContacts=contacts,exposedOriginalHighestVertex=True,all34OriginalPeerAttachmentsWithinExistingBounds=True))
    row=dict(uid=uid,sourceSHA256=s['sourceSHA256'],lowerSourceRoleAccepted=True,rows=records);result=dict(uids=[uid],rows=[row],sourceRoleAccepted=True,lowerSourceRoleOnly=True,sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictWarningsPreserved=True,groundRootCredit=False,physicalAcceptance=False,installationApproved=False,publication=False,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,qualification=__doc__+' Exactly one negative face21 in every world: a vertical original wall, actual positive finite source/ground intersections and a highest source vertex above every overlapping drawn-ground face. Existing34finite original peer routes retain endpoint/1mm bounds. No horizontal cap or closed-solid requirement invented. No whole-scene or publication approval and no fabricated geometry/root.')
    assert reservations.owns(lease);save(out/'summary.json',result);save(out/'ROOT-LOWER-SOURCE-REVIEW.json',result);refs.extend([HERE/'original_assembly_four_world_pair_context_v3_20261101.py',HERE/'exact_packed_world_geometry_20261009.py']);module('palazzo88780_wall_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-single-original-vertical-wall-actual-grade-role',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
