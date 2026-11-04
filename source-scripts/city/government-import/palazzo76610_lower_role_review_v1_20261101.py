"""Bounded lower-source role review for two exact original units; no installation."""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-palazzo76610-after-prosperous-'
BATCH=P+'two-lower-source-role-review-v1-20261101'
UIDS=['landsd/76610:0','landsd/340334:0']


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--lease');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()
    if not a.lease:
        assert not local.exists();lp=local/'reservation.json'
        claim=reservations.claim('palazzo-lower-role-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--lease',str(lp)])
    lease=read(Path(a.lease));assert reservations.owns(lease)and{'building:'+u for u in UIDS}<=set(lease['resources'])
    refs=[Path(__file__)];pins={}
    def take(batch,filename,external=None):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=external if external is not None else BASE/batch/filename
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=P+'fifteen-authentic-tin-runtime-v1-20261101';selection=take(runtime,'selection.json.gz');sources={r['uid']:r for r in selection['rows']};geometry={r['uid']:r for r in take(runtime,'',HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']}
    attrs={r['uid']:r for r in take(P+'fifteen-original-attributes-v1-20261101','attributes.json.gz')['rows']}
    identity=take(P+'fourteen-identity-review-v1-20261101','summary.json');assert identity['identityOnlyApproved']
    dimensions=take(P+'fourteen-ground-dimensions-v1-20261101','summary.json')
    outputs=[];images=[]
    for uid in UIDS:
        key=uid.split('/')[1].split(':')[0];row=sources[uid];attr=attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(asset)
        reviewed=next(r for r in identity['rows']if r['uid']==uid);assert reviewed['identityAccepted']and reviewed['sourceSHA256']==row['sourceSHA256']
        ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(asset.read_bytes())}
        for m,f in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[m]=np.asarray(attr[f],dtype='<f8').reshape(-1,3)[ix]
        ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);records=[]
        for mode,tri in worlds.items():
            oldmode={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)
            context=take(P+key+'-below-grade-source-context-v2-20261101',mode+'.json.gz')
            assert context['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes()) and context['completeGroundSHA256']==digest(ground.tobytes()),'Source/ground facts must match current15capture exactly'
            bad=set(context['completeNegativeFaces']);paths={r['sourceFace']:r for r in context['allWallCapPaths']};nonwall=set(context['negativeNonWallFaces']);raw_up=[]
            expected=set(range(5989,6001)) if key=='76610' else set(range(44,54))
            assert nonwall==expected|({16889}if key=='76610'else set())
            normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);assert all(normal[i,1]<0 for i in expected)
            component=take(P+key+'-lower-original-components-v1-20261101','summary.json');c=next(r for r in component['rows']if r['mode']==oldmode);assert c['sourceWorldSHA256']==context['sourceWorldSHA256'];faces={r['sourceFace']:r for r in c['faces']}
            boundary={j for i in expected for e in faces[i]['exactEdgeIncidence'] for j in e['incidentSourceFaces'] if j not in expected}
            assert all(np.linalg.norm(normal[j])>0 and abs(normal[j,1])<=.25*np.linalg.norm(normal[j])for j in boundary)
            grade={r['sourceFaceA']for r in context['completePositiveGradeContacts']}
            # Source lower patch remains connected by its exact original edges,
            # even when literal floating transforms make its triangles slightly tilted.
            graph={i:{j for e in faces[i]['exactEdgeIncidence'] for j in e['incidentSourceFaces'] if j in expected and j!=i}for i in expected};seen={min(expected)}
            while True:
                added=set().union(*(graph[i]for i in seen))-seen
                if not added:break
                seen|=added
            assert seen==expected
            unresolved={i for i,r in paths.items()if not r['hasExactSharedEdgeClearCapPath']}
            if key=='76610':
                assert len(bad)==531 and len(paths)==518 and len(boundary)==14 and boundary<=grade
                assert all(paths[j]['hasExactSharedEdgeClearCapPath']for j in boundary)
                exposed=take(P+'76610-wall-grade-exposure-v1-20261101',mode+'.json.gz');assert exposed['sourceWorldSHA256']==context['sourceWorldSHA256']and exposed['completeGroundSHA256']==context['completeGroundSHA256']
                assert {r['sourceFace']for r in exposed['rows']}==unresolved
                assert all(r['hasPositiveActualGradeSurfaceContact']and r['hasConservativelyOrExactlyExposedOriginalVertex']for r in exposed['rows'])
                dim=next(r for r in dimensions['rows']if r['mode']==oldmode);assert dim['sourceWorldSHA256']==context['sourceWorldSHA256']and dim['groundSHA256']==context['completeGroundSHA256']
                assert dim['upwardFacesWithNegativeGroundSurfacePairs']==[] and dim['upwardFacesWithOnlyNegativeLineOrPointPairs']==[16889]
                raw_up=[16889]
            else:
                assert len(bad)==34 and len(paths)==24 and not unresolved and len(boundary)==12
                assert all(j not in bad or paths[j]['hasExactSharedEdgeClearCapPath']for j in boundary)
                assert len(boundary&grade)==6
            records.append(dict(mode=mode,sourceWorldSHA256=context['sourceWorldSHA256'],completeGroundSHA256=context['completeGroundSHA256'],rawNegativeFaces=sorted(bad),downwardPatchFaces=sorted(expected),originalPatchBoundaryWallFaces=sorted(boundary),boundaryWallsWithActualGradeContacts=sorted(boundary&grade),wallsWithVerifiedOriginalClearCapPath=len(paths)-len(unresolved),gradeCrossingExposedWallsWithoutCap=len(unresolved),lineOnlyUpwardGroundWarningFaces=raw_up,rawStrictWarningsPreserved=True))
        view=P+key+'-below-grade-views-v1-20261101';report=take(view,'summary.json');wanted=[13,59]if key=='76610'else[1]
        for group in wanted:
            path=BASE/view/('low-group-'+str(group)+'.png');sha=digest(path.read_bytes());assert sha==pins[view][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha,inspection='Both opposite source/actual-ground perspectives individually inspected in the exported image'))
        outputs.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],rows=records,lowerSourceRoleAccepted=True,groundRootCredit=False,newPhysicalSupportBridgeCredit=False))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=UIDS,sourceSHA256ByUid={u:sources[u]['sourceSHA256']for u in UIDS},rows=outputs,sourceRoleAccepted=True,lowerSourceRoleOnly=True,sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictWarningsPreserved=True,strictDiagnosticFlagsRewritten=False,groundRootCredit=False,newPhysicalSupportBridgeCredit=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelAndEffort='Unknown from tool-visible metadata; not inferred',imagesActuallyInspected=images,physicalAcceptance=False,installationApproved=False,publication=False,interpretation=[
        'The twelve owner downward facets are an exact connected original lower strip with fourteen original side-wall interfaces. Every side has positive actual-grade contact and a verified original clear-cap path in each coordinate stream. Slight literal plane tilts are retained exactly; no coordinates or source normals are rounded.',
        'All remaining owner negative walls either have an independently verified original clear-cap path or positive actual-grade crossing plus an original vertex strictly above every actual drawn-ground surface at that XZ. The latter are partial wall skins; demanding a separate horizontal cap/closed solid would add an unrelated engineering requirement. Exact finite-column queries include vertical/collapsed ground; no negative wall is made a new support root.',
        'Owner upward16889 retains its raw finite-column warning, but every negative ground pair has exact primitive dimension<=1 and no negative two-dimensional ground surface. Those collapsed primitives remain drawn/context and provide no terrain height/root credit. No source face is removed.',
        'The small boundary model ten downward facets form an exact connected source lower patch with twelve original wall interfaces. Its24negative walls have clear upper paths, six boundary walls have actual grade contacts, and other boundary walls are ordinary-clear under the complete current partition. Its upper surfaces remain outside the complete negative partition. This is the original lower skin at source pose, not invented architecture or a shifted foundation.',
        'These three inspected exports corroborate the specific lower patches/line-only warning. The other57owner group exports were generated but are not claimed visually reviewed. Complete numerical face/source/ground accounting is independent of the selected diagnostic images.',
        'Accept only these two exact lower-source role interpretations. Existing support, whole-source physical placement, foreign/native crossings, affected-neighbour regression, runtime budgets, atomic desktop/mobile fallback/browser evidence, fenced review/publisher and installed readback remain mandatory. No whole assembly or publication acceptance transfers.'
    ])
    assert reservations.owns(lease);save(out/'ROOT-LOWER-SOURCE-REVIEW.json',result);save(out/'summary.json',result)
    module('palazzo_lower_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-two-exact-original-lower-source-role-review-only',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
