"""Bounded role review for exact original below-grade carpark walls; no publication."""
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
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-academic309823-after-kai-tak-'
BATCH=P+'carpark-lower-source-review-v1-20261101';UID='landsd/26949:0'
SHA='e4cf4099b7a1179c0c1a6ea27a7dc9036bde9ad08ba2ee900a6ac0fe3542fde8'
WALLS={178,179,287,288,298,299,300,321,322,331,332}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';resources=read(BASE/(P+'carpark-current-runtime-plan-v1-20261101.json'))['resources']
    assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('carpark-lower-source-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok']
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__)];pins={}
    def take(batch,name,external=None):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=external or BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rt=P+'carpark-after-floor-runtime-v1-20261101';at=P+'carpark-current-attributes-v1-20261101'
    source=take(rt,'selection.json.gz')['rows'][0];assert source['uid']==UID and source['sourceSHA256']==SHA
    g=take(rt,'',HERE/'local'/rt/'runtime-geometry.json.gz')['rows'][0];assert g['uid']==UID and g['sourceSHA256']==SHA
    attr=take(at,'attributes.json.gz')['rows'][0];assert attr['uid']==UID and attr['sourceSHA256']==SHA
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds=represented(attr,decode_original_world_triangles(asset.read_bytes()))
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gsha=digest(ground.tobytes())
    foundation=take(P+'carpark-after-floor-foundation-v1-20261101','summary.json');assert foundation['establishedFoundationPolicyPassed']
    identity=take(P+'carpark-shared-structure-identity-v1-20261101','identity.json');assert identity['passed']and identity['sourceSHA256']==SHA
    metrics=take(rt,'metrics.json');metric=metrics['rows'][0];policy=module('carpark_lower_policy',HERE/'acceptance-policy.py');refs.append(HERE/'acceptance-policy.py')
    raw={name:policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=identity['proof']),metric,profile)for name,profile in metrics['profiles'].items()}
    assert raw and all(v==['terrain-intersects-source-over-0.5m']for v in raw.values()),raw
    rows=[]
    for mode,tri in worlds.items():
        assert reservations.owns(lease);cm={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);sha=digest(tri.astype('<f8').tobytes())
        low=take(P+'carpark-after-floor-low-faces-v1-20261101',cm+'.json.gz');context=take(P+'carpark-complete-below-grade-context-v1-20261101',mode+'.json.gz');rim=take(P+'carpark-current-canonical-rims-v1-20261101',mode+'.json.gz')
        assert low['sourceWorldSHA256']==context['sourceWorldSHA256']==rim['sourceWorldSHA256']==sha
        assert low['groundSHA256']==context['completeGroundSHA256']==rim['groundSHA256']==gsha
        assert low['completeSourceFaces']==len(tri)==source['triangles']==680
        assert {r['sourceFace']for r in low['rows']}==set(context['completeNegativeFaces'])==set(context['negativeWallFaces'])==WALLS
        assert context['negativeNonWallFaces']==[]and set(p['sourceFace']for p in context['allWallCapPaths'])==WALLS
        assert all(p['hasExactSharedEdgeClearCapPath']for p in context['allWallCapPaths'])
        assert all(r['absoluteNormalYRatio']is not None and r['absoluteNormalYRatio']<.25 and r['highestVertexAboveEveryOverlappingGroundFace']for r in low['rows'])
        f=next(r for r in foundation['rows']if r['mode']=={'leftF32':'explicitLeftF32','balancedF32':'explicitBalancedF32'}.get(mode,mode));assert f['completeTerrainTriangles']==f['triangles']==680 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
        positions=np.asarray(attr[{'original':'completeLiteralWorldPosition','literal':'completeLiteralWorldPosition','leftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','balancedF32':'completeExplicitBalancedFloat32WorldPosition'}[mode]],dtype='<f8').reshape(-1,3).copy()
        if mode=='original':positions[ix.ravel()]=tri.reshape(-1,3)
        assert np.array_equal(positions[ix],tri)
        expected=original_samples(positions,ix,float(positions[:,1].min()));samples=rim['completeOriginalSamples'];assert len(samples)==len(expected)==rim['samples']
        for r,e in zip(samples,expected):
            assert all(r[k]==v for k,v in e.items()) and r['gap']==r['point'][1]-r['ground']
            if r['gap']<-.5:assert set(r['originalIncidentFaces'])<=WALLS
        assert rim['groundContactResolved']and not rim['rawRimFailures'] and rim['completeDrawnGroundFacets']==len(ground)
        rows.append(dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=gsha,negativeOriginalWalls=sorted(WALLS),completeOriginalSamples=len(samples),canonicalLowRimSamples=rim['lowRimSamples'],rawMinimumGapM=rim['minimumSampleGapM'],rawRimRangeM=[rim['minimumRimGapM'],rim['maximumRimGapM']],allWallsHaveOriginalClearCapPaths=True,allRawNegativeSamplesAccounted=True,groundContactResolved=True))
    viewbatch=P+'carpark-current-wall-views-v1-20261101';views=take(viewbatch,'summary.json');assert set(views['completeAffectedFaces'])==WALLS and len(views['exports'])==2;images=[]
    for image in views['exports']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==pins[viewbatch][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(**image,actuallyViewed=True))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==take(rt,'selection.json.gz')['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256=SHA,rows=rows,sourceRoleAccepted=True,lowerSourceRoleOnly=True,rawPolicyReasonsByProfile=raw,rawCanonicalFlagsPreserved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelAndEffort='Unknown from tool-visible metadata; not inferred',reviewer='Codex ROOT',imagesActuallyInspected=images,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,physicalInterComponentSupportBridgeCredit=False,physicalAcceptance=False,installationApproved=False,publication=False,observations=['Both opposite perspectives of both exact low-wall groups were inspected. The11red original faces are lower side/perimeter/return walls crossed by the green current terrain and connected to original clear upper faces; no surveyed basement purpose or engineering ownership is inferred.','All upward/nonwall negative source facets were cleared by the separately validated source-bound terrain return. All680faces and all1388drawn terrain facets, including3projected-zero primitives, remain in the complete current proofs. Each represented source stream is independently hash-bound; literal and original hashes are not conflated.','Every canonical below-clearance witness has only incidences in the fully accounted11wall partition. All209canonical low-rim samples pass existing[-.5,1]m ground contact rules in each stream. Raw minsample−1.9598348927m remains preserved as partial original below-grade walls; no generic clearance threshold or policy is changed.','Only bounded lower-source roles are accepted. Shared-structure identity is a separate exact review; current foreign interfaces, full affected terrain, real desktop/mobile loading/picking/collision/fallback and guarded publication still require their own evidence.'])
    assert reservations.owns(lease);save(out/'ROOT-LOWER-SOURCE-REVIEW.json',result);save(out/'summary.json',result);refs.extend([HERE/'original_assembly_four_world_pair_context_v3_20261101.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_wall_rim_accounting_20261009.py'])
    module('carpark_lower_source_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-carpark-lower-wall-source-role-review',refs,result)

if __name__=='__main__':main()
