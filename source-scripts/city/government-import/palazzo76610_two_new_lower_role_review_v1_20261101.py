"""Bounded lower-source role review for two immutable original units; no publication."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'two-new-lower-role-review-v1-20261101'
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease);out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__),HERE/'local'/BATCH/'FAILED-FIRST-LAUNCH.json',HERE/'local'/BATCH/'FAILED-SECOND-LAUNCH.json']
    def take(batch,name,external=None):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=external if external is not None else BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rt=P+'twenty-authentic-tin-runtime-v1-20261101';at=P+'twenty-original-attributes-v1-20261101';selection={r['uid']:r for r in take(rt,'selection.json.gz')['rows']};attrs={r['uid']:r for r in take(at,'attributes.json.gz')['rows']};geometry={r['uid']:r for r in take(rt,'',HERE/'local'/rt/'runtime-geometry.json.gz')['rows']};metrics=take(rt,'summary.json');rows=[]
    for key,count,walls,nonwall in [('252556',43,40,{850,852,853}),('252558',24,24,set())]:
        uid='landsd/'+key+':0';assert'building:'+uid in lease['resources'];source=selection[uid];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attrs[uid]['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(asset)
        worlds=represented(attrs[uid],decode_original_world_triangles(asset.read_bytes()));ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gsha=digest(ground.tobytes());m=next(r for r in metrics['rows']if r['uid']==uid);assert m['fullyBuriedTriangles']==m['fullyBuriedUpwardTriangles']==0
        low=P+key+'-twenty-complete-ground-v1-20261101';context=P+key+'-twenty-below-grade-context-v1-20261101';attachment=P+key+'-saved-ground-attachments-v1-20261101';strict=take(P+key+'-original-owner-support-v1-20261101','summary.json');records=[]
        original=take(context,'original.json.gz');closure=set();boundary=set()
        if nonwall:
            assert len(original['coplanarDownwardGroups'])==1;group=original['coplanarDownwardGroups'][0];closure=set(group['allConnectedCoplanarDownwardFaces']);boundary=set(group['boundaryFaces']);assert closure==set(range(844,870))and nonwall<=closure and not boundary&set(original['completeNegativeFaces'])and set(group['boundaryWallFaces'])<=boundary and boundary-set(group['boundaryWallFaces'])=={585}
        for mode,tri in worlds.items():
            name={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);raw=take(low,name+'.json.gz');detail=take(context,mode+'.json.gz');paths=take(attachment,mode+'.json.gz');sha=digest(tri.astype('<f8').tobytes());assert raw['sourceWorldSHA256']==detail['sourceWorldSHA256']==paths['sourceWorldSHA256']==sha and raw['groundSHA256']==detail['completeGroundSHA256']==paths['completeGroundSHA256']==gsha
            negative={r['sourceFace']:r for r in raw['rows']};assert len(negative)==count and set(negative)==set(detail['completeNegativeFaces'])and all(r['highestVertexAboveEveryOverlappingGroundFace']for r in negative.values())
            assert len(detail['negativeWallFaces'])==walls and set(detail['negativeNonWallFaces'])==nonwall
            grade={c['sourceFaceA']for c in detail['completePositiveGradeContacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2};caps={r['sourceFace']:r for r in detail['allWallCapPaths']};assert set(caps)==set(detail['negativeWallFaces'])
            assert all(caps[f]['hasExactSharedEdgeClearCapPath']or f in grade for f in caps)
            for f in nonwall:assert np.cross(tri[f,1]-tri[f,0],tri[f,2]-tri[f,0])[1]<0
            groups=detail['coplanarDownwardGroups'];assert {f for g in groups for f in g['negativeDownwardFaces']}==nonwall
            for group in groups:assert set(group['allConnectedCoplanarDownwardFaces'])<=closure and set(group['boundaryFaces'])<=closure|boundary
            direct=next(r for r in strict['rows']if r['mode']==mode);assert [r['witness']for r in paths['rows']]==direct['support']['unresolved'] and all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 and r['terminal']['contact']['peerUid']=='current-drawn-ground'for r in paths['rows'])
            records.append(dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=gsha,rawNegativeFaces=sorted(negative),negativeWallFaces=detail['negativeWallFaces'],negativeDownwardFaces=sorted(nonwall),uncappedWallsWithActualGradeContact=detail['wallsWithoutSharedEdgeClearCapPath'],allNegativeFacesHaveExposedOriginalVertex=True,allSupportWarningsReachActualGroundWithinExistingBounds=True,sourceRoleOnly=True))
        rows.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],lowerSourceRoleAccepted=True,originalDownwardClosureFaces=sorted(closure),originalClearBoundaryFaces=sorted(boundary),rows=records))
    result=dict(uids=[r['uid']for r in rows],rows=rows,sourceRoleAccepted=True,lowerSourceRoleOnly=True,sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictWarningsPreserved=True,groundRootsInvented=False,interComponentBridgesAdded=False,physicalAcceptance=False,installationApproved=False,publication=False,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelAndEffort='Unknown from tool-visible metadata; not inferred',qualification=__doc__+' All67negative source faces accounted.252556has40lowerwalls and three downward closure facets in an original26face plane bounded by28ordinary-clear facets (27walls and the clear source facet585). Literal exact planes split that unchanged source closure; no rounding or tolerance used.252558has24lowerwalls; uncapped walls have actual positive grade contacts and exposed original vertices, without inventing a horizontal cap requirement. All64raw support witnesses reach actual drawn terrain through original source incidence and exact saved contacts within unchanged endpoint/1mm bounds. This binds lower roles and actual contact routes only, not whole-scene identity/neighbour/visual/publisher approval.')
    assert reservations.owns(lease);save(out/'ROOT-LOWER-SOURCE-REVIEW.json',result);save(out/'summary.json',result);refs.extend([HERE/'original_assembly_four_world_pair_context_v3_20261101.py',HERE/'exact_packed_world_geometry_20261009.py']);module('palazzo_two_new_lower_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-two-original-lower-wall-and-closure-source-role-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
