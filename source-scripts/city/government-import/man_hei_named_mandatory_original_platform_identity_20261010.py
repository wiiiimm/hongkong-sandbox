"""Source-specific Man Hei identity dependent on its complete original platform.

This is not the Lei Tung complete missing-floor route: real uncovered strips
remain. Only original main-body upward floors within the authoritative podium
span contribute to the unchanged 95% target test. The platform must separately
pass its reviewed identity (including the named Man Oi relationship). Complete
sources, all current actors, collisions and physical support remain independent.
The current-binding adapter must replay both source identities and primary
receipts, and verify the named Housing Authority plan bytes before calling this.
"""
from copy import deepcopy
from datetime import datetime, timezone
import numpy as np
import shapely
from run import digest
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
from lei_tung_named_original_lower_platform_identity_20261010 import polygon, provider_polygon

UID='landsd/75694:0'; PLATFORM='landsd/266062:0'; RELATED='landsd/75697:0'
SOURCE_SHA='88baf17aa03fad5a07e68830b3ada8ba1cbda14160e82e97408b9b07acc7db01'
PLATFORM_SHA='22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
WORLD_SHA='5c9fbdbcb7d7750671964cab22bd44d4e1bf344a8ba910f4cdbe217c1908f1ba'
PLATFORM_WORLD_SHA='2042ad56fe266775639d4d50ecf94c2ac379f44dbcc2c5dac66fb0b58b3eaebe'
PLAN_URL='https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/chunmancourt_bH.pdf'
PLAN_SHA='c0d5da349badae78257871a6de8a97f2de2683ccce0ac4d03b774241b4c8360c'
EXPECTED={UID:('3639519467T20050430',1108238205,'Tower','B363951946701063C0','Man Hei House'), PLATFORM:('3644619608P20050726',1108246586,'Podium','B364461960802063C0','MAN FUK HOUSE (BLK A)')}
RAW_REASONS={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
POLICY='proposed-man-hei-exact-original-mandatory-lower-platform-identity-v1'

def named_proof(previous, platform_identity, upper_row, platform_row, upper, platform, current_forms, primary, named_plan):
    a=np.asarray(upper,float);b=np.asarray(platform,float)
    assert a.shape==(2286,3,3) and b.shape==(10661,3,3) and np.isfinite(a).all() and np.isfinite(b).all()
    assert digest(a.astype('<f8').tobytes())==WORLD_SHA and digest(b.astype('<f8').tobytes())==PLATFORM_WORLD_SHA
    assert previous['uid']==UID and previous['sourceSHA256']==SOURCE_SHA and previous['worldTrianglesSHA256']==WORLD_SHA
    assert previous['originalOwnership']['sourceGraphVerified']
    assert named_plan=={'url':PLAN_URL,'sha256':PLAN_SHA,'namedEstate':'Chun Man Court','namedBlock':'H','namedBuilding':'Man Hei House','role':'reference-typical-floor-plan-1F-15F'}
    assert platform_identity['uid']==PLATFORM and platform_identity['sourceSHA256']==PLATFORM_SHA and platform_identity['worldTrianglesSHA256']==PLATFORM_WORLD_SHA
    assert platform_identity['policy']=='man-fuk-exact-original-ha-block-a-k-envelope-identity-v3'
    assert platform_identity['passed'] is True and platform_identity['reasons']==[] and all(platform_identity['proof'].get(k) is True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    assert platform_identity['explicitRelatedUID']==RELATED and platform_identity['sourceGeometryChanges']==0
    assert platform_identity['currentRelatedActorCollisionExemption'] is False and platform_identity['currentRelatedActorTerrainExemption'] is False
    forms={f['uid']:f for f in current_forms};assert len(forms)==len(current_forms) and {UID,PLATFORM,RELATED}<=set(forms)
    # This prevents widening the dependent platform's already-reviewed foreign
    # actor exception. Its caller must freshly replay the named identity itself.
    retained=platform_identity['allOtherCurrentFormsRetained']
    assert len({f['uid'] for f in retained})==len(retained)
    assert {f['uid']:f for f in retained}==forms
    assert len(primary)==2 and len({p['attributes']['BuildingCSUID'] for p in primary})==2
    providers={}
    for row,sha in [(upper_row,SOURCE_SHA),(platform_row,PLATFORM_SHA)]:
        uid=row['uid'];assert uid in EXPECTED
        csuid,bid,kind,model,name=EXPECTED[uid];f=forms[uid]
        assert row['modelId']==model and row['sourceSHA256']==sha and row['source']['building']==f
        assert (f['buildingCSUID'],f['buildingId'],f['structureType'],f['name'])==(csuid,bid,kind,name)
        matches=[p for p in primary if p['attributes']['BuildingCSUID']==csuid];assert len(matches)==1
        p=matches[0];q=p['attributes'];providers[uid]=p
        assert (q['Status'],q['BuildingID'],q['BuildingBlockType'],str(q['GeoRefNo']),q['BuildingNameEN'])==('Active',bid,kind,csuid[:10],name)
        assert datetime.fromtimestamp(q['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:]
        assert q['BaseHeight']==f['baseHeightHKPD'] and q['TopHeight']==f['topHeightHKPD']
    assert upper_row['uid']==UID and platform_row['uid']==PLATFORM
    assert forms[PLATFORM]['baseHeightHKPD']==32.2 and forms[PLATFORM]['topHeightHKPD']==forms[UID]['baseHeightHKPD']==43.4
    aparts=components(a)['components'];bparts=components(b)['components'];assert [len(p['faceIndices']) for p in aparts]==[1254,166,166,684,8,8] and len(bparts)==93
    body=bparts[0]['faceIndices'];assert len(body)==8676
    norm=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);floors=[i for i in body if norm[i,1]>0 and 32.2<b[i,:,1].min()<=b[i,:,1].max()<=43.4]
    assert floors
    contacts=exact_component_contacts(a,range(len(a)),b,range(len(b)),maximum_pairs=1000000)
    positive=[c for c in contacts['contacts'] if c['dimension']>0];assert len(positive)==209
    own=shapely.union_all(shapely.polygons(a[:,:,[0,2]]));lower=shapely.union_all(shapely.polygons(b[floors][:,:,[0,2]]));pair=np.concatenate([a,b])
    paired=shapely.union_all(shapely.polygons(pair[:,:,[0,2]]));others=[f for f in current_forms if f['uid'] not in {UID,PLATFORM}]
    foreign=shapely.union_all([polygon(f['rings']) for f in others]);ordinary_foreign=shapely.union_all([polygon(f['rings']) for f in others if f['uid']!=RELATED])
    checks={};reasons=[r for r in previous['reasons'] if r not in RAW_REASONS]
    for label,target,platform_target in [('current',polygon(forms[UID]['rings']),polygon(forms[PLATFORM]['rings'])),('primary',provider_polygon(providers[UID]),provider_polygon(providers[PLATFORM]))]:
        whole=target.union(platform_target);missing=target.difference(own);remaining=missing.difference(lower)
        suppliers=[i for i in floors if shapely.Polygon(b[i][:,[0,2]]).intersection(missing).area>0]
        assert len(suppliers)==45 and not remaining.is_empty,'Real uncovered source strips must remain explicit'
        standalone=own.intersection(target).area/target.area;assert .94<standalone<.95
        metrics={'rawStandaloneUpperCoverage':standalone,'upperPlusOriginalMainBodyLowerFloorCoverage':own.union(lower).intersection(target).area/target.area,'genuineRemainingLowerFloorGapM2':remaining.area,'genuineRemainingLowerFloorGapGeoJSON':__import__('json').loads(shapely.to_geojson(remaining)),'completeOriginalSupplyingLowerFloorFaceIds':suppliers,'wholePairedTargetCoverage':paired.intersection(whole).area/whole.area,'wholePairedMaximumSourceExtentM':float(shapely.distance(shapely.points(pair[:,:,[0,2]].reshape(-1,2)),whole).max()),'allCurrentForeignPairExcessM2Retained':paired.difference(whole).intersection(foreign).area,'independentlyReviewedPlatformRelatedExcessM2Retained':paired.difference(whole).intersection(polygon(forms[RELATED]['rings'])).area,'allOtherForeignPairExcessM2':paired.difference(whole).intersection(ordinary_foreign).area,'ownTowerForeignExcessM2':own.difference(target).intersection(foreign).area,'rawUpperTargetOutsidePlatformM2':target.difference(platform_target).area}
        checks[label]=metrics
        if not(.95<=metrics['upperPlusOriginalMainBodyLowerFloorCoverage']<=1 and .95<=metrics['wholePairedTargetCoverage']<=1 and metrics['wholePairedMaximumSourceExtentM']<=10 and metrics['allOtherForeignPairExcessM2']<=1 and metrics['ownTowerForeignExcessM2']<=1):reasons.append('mandatory-original-platform-'+label+'-spatial-bound')
    raw=sorted(set(previous['reasons'])&RAW_REASONS);assert set(raw)==RAW_REASONS
    out=deepcopy(previous);passed=not reasons
    out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawStandaloneUpperCoverageReasonsRetained=raw,mandatoryOriginalRuntimeUIDs=[UID,PLATFORM],standaloneOriginalImportAccepted=False,completeMissingFloorClaim=False,completeOriginalFaceCounts=[2286,10661],completeOriginalPartCounts=[6,93],completeOriginalPositiveInterfaces=positive,independentCurrentProviderAssemblyChecks=checks,dependentPlatformIdentityPolicy=platform_identity['policy'],completeCurrentForeignActorsRetained=current_forms,foreignCollisionExemption=False,foreignTerrainExemption=False,foreignRemoval=False,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},qualification='Proposed named Man Hei principal tower footprint plus complete unchanged source platform. Raw94.8074% standalone failure and real partial uncovered strips remain. Only original mainbody upward lowerfloor facets within32.2..43.4 count toward unchanged95%; all10661platformfaces/93parts and2286towerfaces/6parts remain. Dependent platform identity must freshly independently pass its existing exact named ManOi relationship. No commonOP/property ownership, load-bearing or physical exemption. Mandatory both-original runtime; no standalone import.')
    return out
