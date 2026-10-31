"""Bind exact original lower-closure context; no root, bridge or installation credit."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census

BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-prosperous235568'
UID='landsd/235568:0'
SHA='ef354fbb79cbbf576a0e146cf019f2a1ae73c75b031dde2ece59dcdee8f78ac2'
BATCH=P+'-lower-source-context-v1-20261031'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lease',required=True);a=ap.parse_args()
    lease=read(Path(a.lease));assert reservations.owns(lease) and 'building:'+UID in lease['resources']
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    runtime=P+'-six-original-patch-runtime-v1-20261031';attrs=P+'-six-original-attributes-v1-20261031'
    row=next(r for r in take(runtime,'selection.json.gz')['rows']if r['uid']==UID)
    attr=next(r for r in take(attrs,'attributes.json.gz')['rows']if r['uid']==UID)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']==SHA;refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k],dtype='<f8').reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    components=take(P+'-podium-downward-component-context-v1-20261031','summary.json')
    caps=take(P+'-podium-complete-cap-paths-v1-20261031','summary.json')
    grade=P+'-podium-four-world-grade-contacts-v1-20261031'
    outputs=[]
    for mode,tri in worlds.items():
        assert reservations.owns(lease)
        oldmode={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)
        low=take(P+'-podium-complete-ground-v1-20261031',oldmode+'.json.gz')
        assert digest(tri.astype('<f8').tobytes())==low['sourceWorldSHA256']
        contacts=take(grade,mode+'.json.gz')
        assert contacts['sourceWorldSHA256']==low['sourceWorldSHA256'] and contacts['completeGroundSHA256']==low['groundSHA256']
        assert contacts['sourceFaces']==17333 and contacts['proof']['allPairsExamined'] and contacts['proof']['sourceFacesOmitted']==0
        bad={r['sourceFace']for r in low['rows']};norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(norm,axis=1)
        walls={i for i in bad if length[i]>0 and abs(norm[i,1])<=.25*length[i]}
        lower=bad-walls;assert len(bad)==85 and len(walls)==65 and len(lower)==20 and all(norm[i,1]<-.25*length[i]for i in lower)
        cap=next(r for r in caps['rows']if r['mode']==oldmode)
        assert cap['sourceWorldSHA256']==low['sourceWorldSHA256'] and cap['completeDrawnGroundSHA256']==low['groundSHA256']
        paths={p['sourceFace']:p for p in cap['completeGroundClearancePartition']['paths']}
        assert set(paths)==walls and all(p['hasExactSharedEdgeClearCapPath']for p in paths.values())
        context=next(r for r in components['rows']if r['mode']==oldmode)
        assert context['sourceWorldSHA256']==low['sourceWorldSHA256'];faces={r['sourceFace']:r for r in context['faces']}
        assert set(faces)==lower
        block=faces[9557]['componentFaceIds'];assert len(block)==84
        assert all(faces[i]['componentFaceIds']==block for i in lower-{14856,14857})
        topology=census(tri[block],list(range(len(block))))
        assert topology['boundaryEdges']==topology['nonmanifoldEdges']==topology['twoFaceOrientationConflicts']==0
        up=[i for i in block if norm[i,1]>.25*length[i]]
        down=[i for i in block if norm[i,1]<-.25*length[i]]
        sides=sorted(set(block)-set(up)-set(down))
        assert len(up)==len(down)==20 and len(sides)==44 and not(set(up)&bad)
        positive=[c for c in contacts['proof']['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
        block_grade=[c for c in positive if c['sourceFaceA']in set(block)]
        assert set(sides)<={c['sourceFaceA']for c in block_grade}
        # Preserve exact lower-edge incidence, without using a buried underside
        # to create any root or connection between independent source parts.
        underside=[]
        for i in [14856,14857]:
            f=faces[i];assert f['downward'] and f['wholeSharedEdgeComponentFaces']==14311
            boundaries=[]
            for edge in f['exactEdgeIncidence']:
                incident=edge['incidentSourceFaces'];assert len(incident)==2 and i in incident
                other=next(j for j in incident if j!=i)
                if other in {14856,14857}:continue
                assert other in walls and other in paths
                wall_grade=[c for c in positive if c['sourceFaceA']==other]
                assert wall_grade
                boundaries.append(dict(edge=edge,originalWallFace=other,clearCapPath=paths[other],positiveGradeContacts=wall_grade))
            assert len(boundaries)==2
            underside.append(dict(sourceFace=i,rawNegativeProof=next(r for r in low['rows']if r['sourceFace']==i),originalSideInterfaces=boundaries))
        record=dict(mode=mode,sourceWorldSHA256=low['sourceWorldSHA256'],completeGroundSHA256=low['groundSHA256'],
                    completeNegativeFaces=sorted(bad),negativeWallFaces=sorted(walls),all65WallCapPaths=list(paths.values()),
                    original84FaceClosedSkin=dict(sourceFaceIds=block,sourceTopology=topology,upwardCaps=up,downwardCaps=down,wallFaces=sides,
                        allUpwardCapsOutsideNegativePartition=True,completeActualGradeContacts=block_grade,
                        negativeDownwardFaceIds=sorted(lower-{14856,14857})),
                    originalTwoUndersideFaces=underside,lowerFacesProvideNoRootOrBridge=True)
        save(out/(mode+'.json.gz'),record);outputs.append({k:v for k,v in record.items()if k not in ['all65WallCapPaths','original84FaceClosedSkin','originalTwoUndersideFaces']})
        print(dict(mode=mode,closedSkinFaces=len(block),allSideFacesMeetGrade=True,sourceUndersideFaces=2),flush=True)
    images=take(P+'-podium-low-face-views-v1-20261031','summary.json')['exports']
    for r in images:
        path=ROOT/r['path'];assert digest(path.read_bytes())==r['sha256'];refs.append(path)
    result=dict(uids=[UID],sourceSHA256=SHA,rows=outputs,imagesActuallyInspectedByROOT=images,
                sourceRoleProposalOnly=True,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,
                sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,interComponentBridgeCredit=False,
                qualification='Exact original lower-closure context only. All85 complete negative faces retained:65 original walls have clear-cap paths;18 downward negatives belong to an original84-face closed skin with20 clear upper caps and44 actual grade-contacting sides;2 other downward faces retain every original lower-side interface, finite actual grade contacts and independent wall/cap paths. All7 exported group views were inspected by ROOT. No engineering function, new source facets, root, bridge, burial exemption, whole physical acceptance or publication approval inferred.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py'])
    assert reservations.owns(lease)
    module('prosperous_lower_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-world-exact-original-lower-closure-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
