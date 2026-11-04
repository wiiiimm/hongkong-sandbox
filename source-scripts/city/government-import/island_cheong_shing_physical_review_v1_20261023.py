"""Bind the exact unchanged two-family display assembly after complete current checks."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from island_cheong_shing_named_identity_v1_20261023 import EXACT


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-physical-review-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name,local=False):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=(HERE/'local'/batch if local else base/batch)/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    suite=take('government-xl-island-cheong-shing-repaired-scene-suite-v1-20261023','summary.json');assert suite['status']=='complete-current-scene-evidence-awaiting-physical-browser-publication'and len(suite['completed'])==11
    capture='government-xl-island-cheong-shing-four-original-runtime-v4-20261023';selection=take(capture,'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert sources=={u:r[2]for u,r in EXACT.items()}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    geometry={r['uid']:r for r in take(capture,'runtime-geometry.json.gz',True)['rows']};assert set(geometry)==set(sources)
    attributes=take('government-xl-island-cheong-shing-four-original-attributes-v1-20261023','attributes.json.gz');assert attributes['startEndAllInputsVerified'];attributes={r['uid']:r for r in attributes['rows']}
    identity=take('government-xl-island-cheong-shing-named-identity-review-v1-20261023','summary.json');assert identity['identityAccepted']and identity['coInstallationRequired']==sources
    continuous=take('government-xl-island-cheong-shing-current-continuous-v2-20261023','summary.json');coverage=take('government-xl-island-cheong-shing-current-exact-coverage-v2-20261023','summary.json');assert {r['uid']for r in continuous['rows']}=={r['uid']for r in coverage['rows']}==set(sources)
    assert sum(r['wholeSourceFaces']for r in continuous['rows'])==13848 and all(not r['continuousAffectedFaces']for r in continuous['rows'])
    assert all(not r['stillUncoveredFaces']and r['exactCovered']==r['rawFloatingUncovered']for r in coverage['rows'])
    for uid in sources:
        f=take('government-xl-island-cheong-shing-current-foundations-'+uid.split('/')[1].split(':')[0]+'-v2-20261023','summary.json');assert len(f['rows'])==4 and all(r['completeTerrainTriangles']==r['triangles']and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in f['rows'])
    for number in ['159422','269430']:
        rim=take('government-xl-island-cheong-shing-current-rims-'+number+'-v2-20261023','summary.json');assert len(rim['rows'])==4 and all(r['passed']for r in rim['rows'])
    strict=take('government-xl-island-industrial-tower-main-podium-fourworld-paths-v1-20261023','summary.json');assert len(strict['rows'])==4 and all(r['targets']==108 and r['verifiedPaths']==56 and r['remaining']==52 for r in strict['rows'])
    uphill=take('government-xl-island-industrial-attachment-fourworld-replay-v1-20261023','summary.json');assert len(uphill['rows'])==4 and all(r['freshFinitePaths']==r['paths']==52 and r['maximumSurfaceResidualM']<=.001 and r['strictEndpointHeightPassed']==0 for r in uphill['rows'])
    assert all(len(r['secondaryComponents'])==1 and r['secondaryComponents'][0]['faceIds']==[794,797]and r['secondaryComponents'][0]['diameterOfAABBMetres']<.006 and r['secondaryComponents'][0]['convexWholeComponentDistanceUpperBoundM']<.000001272 for r in uphill['rows'])
    cheong=take('government-xl-cheong-shing-tower-podium-fourworld-paths-v1-20261023','summary.json');assert cheong['allUnresolvedHaveFinitePaths']and len(cheong['rows'])==4 and all(r['targets']==r['verifiedPaths']==7 and r['remaining']==0 for r in cheong['rows'])
    embedding=take('government-xl-island-cheong-shing-source-internal-embedding-v1-20261023','summary.json');assert len(embedding['rows'])==8 and embedding['actualTerrainNegativeHalfMetreSamples']==0 and all(r['negativeHalfMetreSourceFaces']==r['verticalFaces']==2 and r['otherRenderableFaces']==r['nonrenderingFaces']==0 for r in embedding['rows'])
    panels=take('government-xl-island-cheong-shing-original-joint-panels-v3-20261023','summary.json');assert [{r['sourceFace']for r in row['rows']}for row in panels['rows']]==[{11160,11161},{303,305}]and all(r['exactSharedEdgeNeighbours']and r['nonverticalUpwardFaceReachable']for row in panels['rows']for r in row['rows'])
    # No prior source/support path applies to changed model bytes or coordinates.
    clearance=[]
    for row in selection['rows']:
        uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==sources[uid]==attributes[uid]['sourceSHA256'];refs.append(asset)
        literal=np.asarray(geometry[uid]['position']).reshape(-1,3)[np.asarray(geometry[uid]['index']).reshape(-1,3)];a=attributes[uid];ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(raw)}
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[ix]
        assert np.array_equal(literal,worlds['literal'])
        if uid not in ['landsd/20270:0','landsd/274231:0']:continue
        paths=strict['rows']if uid=='landsd/20270:0'else cheong['rows'];ground=np.asarray(geometry[uid]['drawnGroundGeometry']).reshape(-1,3,3)
        for mode,t in worlds.items():
            assert digest(t.astype('<f8').tobytes())==next(r for r in paths if r['mode']==mode)['sourceWorldSHA256']
            lo,hi=t.min((0,1)),t.max((0,1));mask=np.all(ground.max(1)[:,[0,2]]>=lo[[0,2]],axis=1)&np.all(ground.min(1)[:,[0,2]]<=hi[[0,2]],axis=1);assert mask.any();gap=float(lo[1]-ground[mask,:,1].max());assert gap>0;clearance.append(dict(uid=uid,mode=mode,conservativeWholeMeshClearanceM=gap))
    nativebatch='government-xl-island-cheong-shing-four-source-current-neighbours-v2-20261023';native=take(nativebatch,'summary.json');assert not native['basicFlags']and len(native['nativeRows'])==59;failed=[r for r in native['nativeRows']if not r['passed']];assert len(failed)==1 and failed[0]['uid']=='landsd/177605:0'
    unchanged=take('government-xl-island-cheong-shing-hoi-yu-unchanged-context-v2-20261023','summary.json');assert unchanged['proposalTerrainNonRegressionProved']and not unchanged['existingNativeReaccepted']and not unchanged['rawSupportPolicyPassed']and unchanged['rawNativeRegression']==failed[0]
    images=[]
    for n,f in [('government-xl-island-cheong-shing-original-joint-panels-v3-20261023','original-joint-panels.png'),('government-xl-island-cheong-shing-full-boundary-context-v1-20261023','four-complete-originals.png')]:
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    terrain=take('government-xl-island-industrial-paired-surface-binding-v6-20261023','summary.json');assert terrain['bothEffectiveMembersRequired']and len(terrain['members'])==2
    review=dict(uids=sorted(sources),reviewer='ROOT',sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,imagesActuallyViewed=images,continuousTowerTerrainUpperBounds=clearance,exactTerrainReplacements=[r['replaces']for r in terrain['members']],retainedNativeRegression=dict(requiredNativeUids=native['requiredNativeUids'],rawNativeFailures=['landsd/177605:0']),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawCanonicalFailuresPreserved=True,installationApproved=False,publicationApproved=False,basis='Accept these exact four original meshes together as two adjacent government-authored visual Tower/Podium assemblies. Both podiums retain strict grade clearance and contact rules. Both entire tower meshes clear actual terrain in every coordinate mode. Their canonical low-rim points are connected by finite nondegenerate source surfaces to positive-dimensional original podium contacts; the 52 Island points whose source path climbs 0.462480705m are source-authored local wall attachment, not independent ground/support roots. This is a named source visual-assembly interpretation, not a changed endpoint-height tolerance or engineering support certificate. The four small vertical corner-return faces are attached to their own original wall meshes and overlap only the synthetic highest-own-podium envelope; actual terrain causes none of those embedding warnings. They are retained as original joint detail without floor, ground or independent structural-root credit. The two Island roof triangles794/797 remain a 6mm original detail, within1.272micrometres of one main triangle, accepted only as visual detail with no structural contact credit. All11nonrendering faces remain without support credit. All existing source boundary/intersection and strict endpoint negatives remain explicit; no global rule changes, mesh edits, scale/pose changes, new ownership claims or legacy-model reacceptance. Device appearance, collision/picking, failure recovery and publication remain separate.',scope='Private staged browser readiness only; no publication, installation credit or approval transfer to other bytes, source parts, terrain revisions or current scenes.')
    save(out/'ROOT-PHYSICAL-REVIEW.json',review);refs.extend(HERE/n for n in ['island_cheong_shing_named_identity_v1_20261023.py','exact_packed_world_geometry_20261009.py']);module('island_cheong_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-original-four-source-display-assembly-physical-interpretation',refs,dict(uids=sorted(sources),sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,sourceGeometryChanges=0,installationApproved=False))

if __name__=='__main__':main()
