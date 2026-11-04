"""Apply the canonical contact band to two exact intersecting original wall sets."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_canonical_wall_rim_accounting_v1_20261029 import verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
BATCH=PREFIX+'two-canonical-wall-grade-accounts-v1-20261029';RUNTIME=PREFIX+'seven-upward-floor-runtime-v1-20261029';ATTRS=PREFIX+'seven-final-ground-attributes-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');runtime=take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz');attrs=take(ATTRS,BASE/ATTRS/'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    cap_batch=PREFIX+'final-ground-cap-path-revalidation-v1-20261029';cap_summary=take(cap_batch,BASE/cap_batch/'summary.json');assert cap_summary['allPriorPassingPathsRetainFinalGroundEligibility']
    view_batch=PREFIX+'source-bound-full-scene-root-observations-v1-20261029';views=take(view_batch,BASE/view_batch/'ROOT-IMAGE-OBSERVATIONS.json');assert views['imagesActuallyReviewed']and views['actualExportedImagesRepresented']==28
    policy=module('canonical_grade_policy_authority',HERE/'acceptance-policy.py');assert policy.POLICY=='original-government-import-v1'
    # This is an explicit policy-contract witness only, not model acceptance.
    row=dict(state='runtime-validated-awaiting-acceptance',sourceSHA256='same',identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True))
    metric=dict(sourcePreserved=True,sourceSHA256='same',minSurfaceGap=-.46,minLowGap=-.46,maxLowGap=-.18,maxSamplerDelta=0,missingTerrain=0,lowRimChecks=441,identity=dict(overlap=1,centroidDistance=0),budget=dict(triangles=1,geometryBytes=1,residentBytes=1))
    profile=dict(triangles=2,geometryBytes=2,residentBytes=2);assert policy.reasons(row,metric,profile)==[];assert 'ground-contact-unresolved'in policy.reasons(row,dict(metric,minLowGap=.10001),profile)
    out.mkdir();rows=[];roles=[]
    for sid in [238142,92881]:
        uid='landsd/'+str(sid)+':0';source=next(r for r in selection['rows']if r['uid']==uid);captured=next(r for r in runtime['rows']if r['uid']==uid);attr=next(r for r in attrs['rows']if r['uid']==uid);asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==captured['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
        index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3);assert len(set(index.ravel()))==len(literal);original=literal.copy();original[index.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
        worlds=dict(original=original,literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3));ground=np.asarray(captured['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes())
        rim_batch=PREFIX+'upward-floor-'+str(sid)+'-0-canonical-rims-v1-20261029';grade_batch=PREFIX+str(sid)+'-all-lower-wall-ground-interfaces-v1-20261029';grade_summary=take(grade_batch,BASE/grade_batch/'summary.json');assert grade_summary['allSelectedFacesIntersectAndRemainExposed']
        old_batch=PREFIX+'final-ground-'+str(sid)+'-0-cap-paths-v1-20261029'
        for mode,position in worlds.items():
            grade_mode={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);tri=position[index];sha=digest(tri.astype('<f8').tobytes())
            rim=take(rim_batch,BASE/rim_batch/(mode+'.json.gz'));grade=take(grade_batch,BASE/grade_batch/(grade_mode+'.json.gz'));old=take(old_batch,BASE/old_batch/(grade_mode+'.json.gz'))
            assert sha==rim['sourceWorldSHA256']==grade['sourceWorldSHA256']==old['sourceWorldSHA256'];assert ground_sha==rim['completeDrawnGroundSHA256']==grade['completeGroundSHA256']
            transported=next(r for r in cap_summary['rows']if r['uid']==uid and r['mode']==grade_mode);cap=take(cap_batch,BASE/cap_batch/transported['proof']);assert cap['sourceWorldSHA256']==sha and cap['finalGroundSHA256']==ground_sha
            partition=old['completeGroundClearancePartition'];assert partition['allAffectedHavePaths'];walls=sorted(r['sourceFace']for r in partition['paths']);assert walls==grade_summary['sourceFaces']==sorted(f['sourceFace']for f in grade['faces'])
            witnesses=[]
            for face in walls:
                f=next(f for f in grade['faces']if f['sourceFace']==face);assert f['positiveFiniteSurfaceContacts']>0 and f['highestVertexAboveEveryGroundFacet']and Fraction(f['highestVertexMinimumGapM'])>0
                candidates=[c for c in grade['contactProof']['contacts']if c['sourceFaceA']==face and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2];assert candidates
                witness=candidates[0];gf=witness['sourceFaceB'];assert type(gf)is int and 0<=gf<len(ground)
                points=finite_intersection_points(rational_face(tri[face]),rational_face(ground[gf]));measure=contact_measure(points);assert measure['dimension']>0
                witnesses.append(dict(sourceFace=face,groundFace=gf,independentExactFiniteContact=measure,exposedOriginalTopGapM=f['highestVertexMinimumGapM']))
            # ROOT qualifies these exact original wall-like surfaces as grade
            # crossings: all remain exposed, meet actual terrain finitely, and
            # retain their unchanged current clear-cap eligibility.
            role=dict(uid=uid,mode=mode,sourceSHA256=source['sourceSHA256'],sourceWorldSHA256=sha,completeGroundSHA256=ground_sha,wallFaces=walls,sourceSpecificIntersectingWallRoleApproved=True,reviewer='ROOT',evidenceInterpretationUsedAI=True,aiGeometryModelling=False,basis='Immutable native wall surfaces genuinely cross final terrain and retain exposed upper vertices and final clear-cap paths. Buried lower ends are retained as authored; no fabricated near-zero low-rim vertex or engineering/cadastral claim. Actual source exports inspected.',witnesses=witnesses);roles.append(role)
            expected=dict(checks=rim['samples'],lowRimChecks=rim['lowSamples'],minSurfaceGap=rim['minimumGapM'],minLowGap=rim['minimumLowGapM'],maxLowGap=rim['maximumLowGapM'])
            proof=verify(position,index,float(position[:,1].min()),rim['completeOriginalSamples'],approved_wall_faces=walls,wall_role_review_approved=True,positive_finite_grade_faces=[r['sourceFace']for r in witnesses],expected_metric=expected)
            name=str(sid)+'-'+mode+'-account.json';save(out/name,proof);rows.append(dict(uid=uid,mode=mode,verified=proof['verified'],ordinaryRimSamples=proof['ordinaryRimSamples'],strictOrdinaryAnchorSamples=proof['strictOrdinaryAnchorSamples'],canonicalMinimumLowGapM=proof['canonicalMinimumLowGapM'],rawReviewedClearanceFailuresRetained=proof['rawReviewedClearanceFailuresRetained'],independentlyRecomputedPositiveFiniteWallContacts=len(witnesses),proof=name));print(rows[-1],flush=True)
    save(out/'ROOT-EXACT-GRADE-WALL-ROLES.json',dict(uids=sorted({r['uid']for r in rows}),rows=roles,physicalAcceptance=False,publication=False))
    result=dict(uids=sorted({r['uid']for r in rows}),rows=rows,allTwoCanonicalWallRimAccountsVerified=all(r['verified']for r in rows),canonicalPolicy=policy.POLICY,nearZeroOrdinarySampleRequired=False,oldStrictSampleAttemptPreserved=True,ordinaryClearanceMinimumLimitM=-.5,contactMinimumUpperLimitM=.1,rimMaximumLimitM=1,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Canonical import contact is minLowGap<=.1 with maxLowGap<=1; no[-.1,.1]ordinary vertex requirement exists in the authority or its negative-band regression tests. Every original sample is reconstructed unchanged. Only the exact current reviewed walls with independently recomputed positive finite source/ground intersections and retained final clear-cap eligibility receive partial-clearance accounting. All ordinary clearance failures still reject. Raw source/rim gaps and older stricter-diagnostic failure stay recorded. No whole-source physical/publication approval.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['acceptance-policy.py','test_canonical_negative_grade_contact_v1_20261023.py','original_canonical_wall_rim_accounting_v1_20261029.py','test_original_canonical_wall_rim_accounting_v1_20261029.py','original_wall_rim_accounting_20261009.py','exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
    module('sha_tin_canonical_grade_account_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'canonical-contact-source-specific-exact-intersecting-wall-rim-accounting',list(dict.fromkeys(refs)),read(out/'summary.json'))


if __name__=='__main__':main()
