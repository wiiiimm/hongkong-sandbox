"""ROOT source-role review of one exact original ground-crossing wall.

This source-specific interpretation never grants whole-source physical acceptance.
"""
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify

BATCH='government-xl-nam-cheong-wall-role-root-review-v1-20261023'
UID='landsd/268867:0'
RUNTIME='government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
ATTR='government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
GRADE='government-xl-nam-cheong-wall-grade-path-v2-20261023'
VERTICAL='government-xl-nam-cheong-complete-vertical-ground-and-wall-scope-v1-20261023'
BASIC='government-xl-nam-cheong-wall-actual-basic-scope-v1-20261023'
VIEWS='government-xl-nam-cheong-wall-source-views-v2-20261023'


def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH
    assert not doc.exists()
    refs,pins=[Path(__file__)],{}
    for name in [RUNTIME,ATTR,GRADE,VERTICAL,BASIC,VIEWS]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(RUNTIME,base/RUNTIME/'selection.json.gz')
    selected=next(r for r in selection['rows'] if r['uid']==UID)
    g=next(r for r in take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz')['rows'] if r['uid']==UID)
    a=next(r for r in take(ATTR,base/ATTR/'attributes.json.gz')['rows'] if r['uid']==UID)
    asset=ROOT/selected['candidate']['path'];raw=asset.read_bytes()
    assert digest(raw)==a['sourceSHA256']==g['sourceSHA256']==selected['sourceSHA256']
    refs.append(asset)
    vert=take(VERTICAL,base/VERTICAL/'summary.json');assert not vert['additionalUnclassifiedFaces']
    basic=take(BASIC,base/BASIC/'summary.json');assert len(basic['rows'])==4 and all(r['allActualMeshBoundsStrictlySeparated'] and r['proposedCompanionStrictlySeparated'] for r in basic['rows'])
    views=take(VIEWS,base/VIEWS/'summary.json');images=[]
    assert len(views['views'])==4
    for image in views['views']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==pins[VIEWS][str(path.relative_to(ROOT))]
        refs.append(path);images.append(image)
    ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(raw),**{name:np.asarray(a[key]).reshape(-1,3)[ix] for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);groundxz=ground[:,:,[0,2]]
    rows=[]
    for mode,tri in modes.items():
        prior=take(GRADE,base/GRADE/(mode+'.json.gz'))
        assert prior['sourceWorldSHA256']==digest(tri.tobytes()) and prior['groundSHA256']==digest(ground.tobytes())
        assert prior['allChosenCapsOrdinaryClear'] and prior['positiveUpperGradeInterface']
        assert prior['originalPath']==[11390,11391,11411,11410,2642]
        wall=tri[11390];normal=np.cross(wall[1]-wall[0],wall[2]-wall[0]);ratio=abs(normal[1]/np.linalg.norm(normal))
        assert ratio<.25
        vertex=int(np.argmax(wall[:,1]));point=wall[vertex]
        ids=np.flatnonzero(np.all(groundxz.min(1)<=point[[0,2]],axis=1)&np.all(groundxz.max(1)>=point[[0,2]],axis=1))
        proofs=[dict(groundFace=int(i),proof=verify(np.repeat(point[None,:],3,axis=0),ground[i])) for i in ids]
        gaps=[Fraction(r['proof']['exactMinimumFiniteColumnGapM']) for r in proofs if r['proof']['exactClosedHorizontalProjectionsMeet']]
        assert gaps and min(gaps)>0
        save(doc/(mode+'-exposed-point.json.gz'),dict(sourceFace=11390,originalVertex=vertex,point=point.tolist(),allInclusiveGroundFaceCandidates=list(map(int,ids)),proofs=proofs,exactPositiveMinimumGapM=str(min(gaps)),completeGroundFaces=len(ground)))
        rows.append(dict(mode=mode,originalSourceFaces=len(tri),sourceWorldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),wallNormalYRatio=ratio,exactExposedVertexGapM=str(min(gaps)),finiteUpperGradeInterfaceVerified=True,exactSharedEdgePathToOrdinaryClearUpwardCap=prior['originalPath']))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==vert['currentManifestSHA256']==basic['currentManifestSHA256']
    refs.append(manifest)
    report=dict(uids=[UID],sourceSHA256=selected['sourceSHA256'],sourceFace=11390,reviewer='Codex ROOT',imagesActuallyViewed=images,rows=rows,
                sourceSpecificWallInterpretationAccepted=True,sourceEvidenceInterpretationUsedAI=True,
                interpretation='Original lower steep exterior wall portion on a continuous sloping wall sheet ending at an upward horizontal source cap at about7.982mHKPD. The original wall crosses the authored ground and remains exposed above it. It is not an upward floor or an independently displaced building component.',
                rawWallClearanceFailurePreserved=True,rawMinimumGapM=-.5052863905816707,
                providerExteriorProvenanceBinding=dict(exactImmutableOriginalAssetSHA256=selected['sourceSHA256'],exactOriginalFace=11390,exactCurrentWorldRows=rows,reviewedSourceImages=images),
                limits=['Role interpretation applies only to this exact original face/source/current ground binding. No source, terrain, scale, pose or threshold change.', 'Raw continuous clearance remains failed. This records source-role applicability; ordinary-face/whole-source/root/support and exact contract integration remain separate.', 'All6860installednative whole bounds, all36actualbasic actors and the proposed FuYun original are disjoint from this wall; this says nothing about other NamCheong faces crossing foreign actors.', 'No sourcebridge/roofextension identity, pair or foreign collision acceptance, structural engineering certification, staged browser or publication approval.'],
                physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False)
    save(doc/'ROOT-WALL-ROLE-REVIEW.json',report)
    refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'])
    module('nam_wall_role_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-one-original-ground-crossing-wall-role-root-review',refs,report)


if __name__=='__main__':
    main()
