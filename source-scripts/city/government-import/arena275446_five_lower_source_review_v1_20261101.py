"""Bounded unchanged lower-source roles and exact current rim-route accounting.

No whole-scene physical, neighbour, runtime, installation or publication approval.
"""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';BATCH=P+'five-lower-source-review-v1-20261101';OWNER='landsd/275446:0'
DOWN={17933,19125,19126,19171,19172,19189,19190,19195,19196,19222,19223,19224,19225,19248,19249,19309,19310,19333,19334,19339,19340,19366,19367,19368,19369};ZERO={8600,19043,19382}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';planpath=BASE/(P+'five-current-ground-parallel-plan-v1-20261101.json');plan=read(planpath)
    if not a.owned:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('kai-tak-original-lower-review-'+str(uuid.uuid4()),plan['resources'],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(plan['resources'])and not out.exists();refs=[Path(__file__),planpath];pins={};direct={}
    def take(batch,name,external=None):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=external if external is not None else BASE/batch/name;sha=digest(path.read_bytes());assert sha==pins[batch][str(path.relative_to(ROOT))];refs.append(path);direct[str(path.relative_to(ROOT))]=sha;return read(path)
    rt=plan['runtime'];at=plan['attributes'];selection=take(rt,'selection.json.gz');sources={r['uid']:r for r in selection['rows']};attrs={r['uid']:r for r in take(at,'attributes.json.gz')['rows']};geometry={r['uid']:r for r in take(rt,'',HERE/'local'/rt/'runtime-geometry.json.gz')['rows']};assert set(sources)==set(plan['uids'])
    routes=P+'four-canonical-ground-paths-v1-20261101';route_summary=take(routes,'summary.json');assert route_summary['allCanonicalRenderingWarningsHavePaths']and route_summary['noRoundedWitnessMatching']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest);direct[str(manifest.relative_to(ROOT))]=digest(manifest.read_bytes());rows=[];images=[]
    for uid,source in sources.items():
        assert reservations.owns(lease);key=uid.split('/')[1].split(':')[0];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attrs[uid]['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(asset);direct[str(asset.relative_to(ROOT))]=source['sourceSHA256']
        attr=attrs[uid];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds=represented(attr,decode_original_world_triangles(asset.read_bytes()));literal=np.asarray(attr['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3);positions=dict(literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition'],dtype='<f8').reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition'],dtype='<f8').reshape(-1,3));positions['original']=literal.copy();positions['original'][ix.ravel()]=worlds['original'].reshape(-1,3)
        ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gsha=digest(ground.tobytes());fnd=take(P+key+'-retained-parent-foundations-v1-20261101','summary.json');assert fnd['establishedFoundationPolicyPassed']and all(r['fullyBuriedUpwardTriangles']==0 for r in fnd['rows']);mode_rows=[]
        for mode,tri in worlds.items():
            cm={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);sha=digest(tri.astype('<f8').tobytes());assert np.array_equal(positions[mode][ix],tri)
            raw=take(P+key+'-retained-parent-complete-ground-v1-20261101',cm+'.json.gz');context=take(P+key+'-current-below-grade-context-v1-20261101',mode+'.json.gz');rim=take(P+key+'-retained-parent-canonical-rims-v1-20261101',mode+'.json.gz')
            assert raw['sourceWorldSHA256']==context['sourceWorldSHA256']==rim['sourceWorldSHA256']==sha and raw['groundSHA256']==context['completeGroundSHA256']==rim['groundSHA256']==gsha and raw['completeSourceFaces']==len(tri)==source['triangles']
            bad={r['sourceFace']for r in raw['rows']};walls=set(context['negativeWallFaces']);assert bad==set(context['completeNegativeFaces']);caps={r['sourceFace']:r for r in context['allWallCapPaths']};assert set(caps)==walls and all(r['hasExactSharedEdgeClearCapPath']for r in caps.values())
            normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);assert all(length[i]>0 and abs(normal[i,1])<=.25*length[i]for i in walls)
            down=DOWN if uid==OWNER else set();zero=ZERO if uid==OWNER else set();assert set(context['negativeNonWallFaces'])==down|zero and bad==walls|down|zero
            assert all(length[i]>0 and normal[i,1]<-.25*length[i]for i in down)and all(length[i]==0 for i in zero)
            groups=context['coplanarDownwardGroups'];assert {i for g in groups for i in g['negativeDownwardFaces']}==down
            for group in groups:
                assert set(group['negativeDownwardFaces'])<=set(group['allConnectedCoplanarDownwardFaces'])
                assert all(i not in bad or i in walls|down|zero for i in group['boundaryFaces'])
                assert all(r['hasExactSharedEdgeClearCapPath']for r in group['boundaryWallClearCapPaths'].values())
            sample_expected=original_samples(positions[mode],ix,float(positions[mode][:,1].min()));samples=rim['completeOriginalSamples'];assert len(samples)==len(sample_expected)==rim['samples']
            negative=[]
            for i,(r,e)in enumerate(zip(samples,sample_expected)):
                assert all(r[k]==v for k,v in e.items())and r['gap']==r['point'][1]-r['ground']
                if r['gap']<-.5:assert set(r['originalIncidentFaces'])<=bad;negative.append(i)
            warning_indices=[i for i,r in enumerate(samples)if r['low']and(r['gap']<-.5 or r['gap']>1)]
            path_record=None
            if uid==OWNER:
                assert rim['maximumRimGapM']<=1 and rim['minimumRimGapM']<=.1
                assert all(set(samples[i]['originalIncidentFaces'])<=bad for i in warning_indices)
                grade_walls={r['sourceFaceA']for r in context['completePositiveGradeContacts']} & walls;assert grade_walls
                component=take(P+'podium-lower-component-context-v1-20261101','summary.json');detail=next(r for r in component['rows']if r['mode']==cm);assert detail['sourceWorldSHA256']==sha;byface={r['sourceFace']:r for r in detail['faces']};assert set(byface)==DOWN|ZERO
                assert all(byface[i]['downward']and byface[i]['areaM2']>0 for i in DOWN)and all(byface[i]['areaM2']==0 for i in ZERO)
            else:
                paths=take(routes,key+':0/'+mode+'.json.gz');assert paths['sourceWorldSHA256']==sha and paths['completeGroundSHA256']==gsha and paths['completeRawCanonicalWarningIndices']==warning_indices and paths['wholeOriginalSamples']==len(samples)and paths['everyRenderingCanonicalWarningAccounted']and paths['allRenderingCanonicalWarningPathsPass']
                assert paths['nonrenderingOnlyWarnings']==[]and [r['witness']['sampleIndex']for r in paths['rows']]==warning_indices
                assert all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 for r in paths['rows'])
                path_record=dict(exactCurrentWarnings=len(warning_indices),allReachIndependentlyMeasuredActualGround=True,noRoundedWitnessMatching=True)
            mode_rows.append(dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=gsha,completeOriginalFaces=len(tri),negativeWallFaces=sorted(walls),negativeDownwardFaces=sorted(down),retainedZeroAreaSourceFaces=sorted(zero),allNegativeSampleIndices=negative,allRawRimWarningIndices=warning_indices,rawSampleMinimumM=rim['minimumSampleGapM'],rawLowRimRangeM=[rim['minimumRimGapM'],rim['maximumRimGapM']],canonicalWarningRoutes=path_record,sourceRoleOnly=True))
        rows.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],lowerSourceRoleAccepted=True,rows=mode_rows))
    for key,numbers in [('275446',[2,4,5]),('318701',[1,2,3])]:
        batch=P+key+'-retained-parent-low-views-v2-20261101';take(batch,'summary.json')
        for n in numbers:
            path=BASE/batch/f'low-group-{n}.png';sha=digest(path.read_bytes());assert sha==pins[batch][str(path.relative_to(ROOT))];refs.append(path);direct[str(path.relative_to(ROOT))]=sha;images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha))
    for name,sha in direct.items():assert digest((ROOT/name).read_bytes())==sha
    assert reservations.owns(lease)
    result=dict(uids=sorted(sources),sourceSHA256ByUid={u:r['sourceSHA256']for u,r in sources.items()},rows=rows,sourceRoleAccepted=True,lowerSourceRoleOnly=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelAndEffort='Unknown from tool-visible metadata; not inferred',reviewer='Codex ROOT',imagesActuallyInspected=images,sourceGeometryChanges=0,sourcePoseChanges=0,rawCanonicalFlagsPreserved=True,physicalAcceptance=False,installationApproved=False,publication=False,interpretation=[
        'Every negative actual-ground source facet is accounted in all four independently represented streams. All negative real walls retain exact original paths to ordinary-clear upper source facets. All ordinary source faces remain subject to the complete unchanged -.5m clearance partition.',
        'The podium has25downward lower-skin facets: one sloped original underside and two original lower incline/closure regions. The three labelled opposite-perspective exports show those lower surfaces within their original surrounding walls and clear upper geometry. Exact original component/edge accounts and all exact-plane groups are retained; literal plane splits are not rounded or merged. These are bounded original lower skins, not a newly surveyed basement or invented foundation.',
        'The three collinear zero-area source triangles remain in the original assets, index/vertex accounts and raw sample diagnostics. They receive no rendered surface, terrain-height, root, support or graph-bridge credit. Their zero area is independently reproduced in every coordinate representation.',
        'Every below-clearance original sample has only source-face incidences in the fully accounted negative partition. The podium retains actual positive grade-crossing wall contacts and the existing minLow<=.1/maxLow<=1 policy; no new near-zero ordinary-vertex requirement is invented. Its23wholly buried facets and tiny original buried-area fraction remain raw; the existing complete four-world foundation policy passes without upward burial.',
        'All four companions retain their raw below-grade wall and raised-rim diagnostics. Every exact current canonical rim-warning sample, including triangle centres and duplicated indexed positions, reaches independently measured actual drawn-ground strict roots through unchanged original edges within the existing endpoint ceiling and1mm incidence bound. Earlier deduplicated witness counts are not substituted. No native-podium dependency or intercomponent support is invented.',
        'Three current podium and three Mall3lower-source diagrams were individually inspected, both opposite perspectives in each. The three zero-area diagrams and other generated diagnostics are not claimed visually inspected. Lower roles and current original-ground routes alone are accepted here; identity, retained BASIC/native/inter-original interfaces, complete affected terrain, runtime, real browser/fallback and full guarded publisher remain independent.'
    ])
    save(out/'ROOT-LOWER-SOURCE-REVIEW.json',result);save(out/'summary.json',result);refs.extend(HERE/n for n in ['original_assembly_four_world_pair_context_v3_20261101.py','exact_packed_world_geometry_20261009.py','original_wall_rim_accounting_20261009.py'])
    module('kai_tak_lower_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-five-original-lower-source-role-and-exact-canonical-warning-review',refs,result)

if __name__=='__main__':main()
