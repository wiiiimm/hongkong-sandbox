"""Bound this exact original open-sided pier source without changing its subtype."""
from pathlib import Path
import re
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_20261009 import exact_coverage

BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-open-sided-229852-after-plaza-'
UID='landsd/229852:0';CSUID='3970708732T20080306';MODEL='B397070873201063C0'
SHA='5d92d9d44da6261830820fdf22a794c392df6f9adf08f9551980067a1048507b'
BATCH=P+'final-source-review-v1-20261025'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(P+'runtime-v1-20261025','selection.json.gz');assert len(selection['rows'])==1
    row=selection['rows'][0];form=row['source']['building'];assert row['uid']==UID and row['sourceSHA256']==SHA and row['modelId']==MODEL and row['triangles']==17127
    assert form['buildingCSUID']==CSUID and form['objectId']==229852 and form['structureType']=='Open-sided Structure'
    assert form['baseHeightHKPD'] is None and form['topHeightHKPD'] is None
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    assert row['candidate']['entry']['rootTranslation']==[-834500,0,816500] and row['candidate']['entry'].get('verticalPlacementOffsetHKPD',0)==0
    native=row['native']['model'];assert native['sourceEntry']==f'BUILDING/{MODEL}/{MODEL}.gltf'
    assert len(native['matching']['officialCandidates'])==len(native['matching']['officialMatches'])==len(native['matching']['viewerMatches'])==1
    candidate=native['matching']['officialCandidates'][0];assert candidate['objectId']==229852 and candidate['buildingCSUID']==CSUID
    live=take(P+'primary-records-v1-20261025','footprints.json')['features'];assert len(live)==1
    official=live[0]['attributes'];assert official['Status']=='Active' and official['BuildingCSUID']==CSUID and official['BuildingBlockType']=='Open-sided Structure' and official['GeoRefNo']==CSUID[:10] and official['BuildingID']==form['buildingId']
    # OBJECTID is a versioned row identifier. Retain both exact snapshots; the
    # unique CSUID and stable BuildingID bind the live active subtype record.
    assert official['OBJECTID']==229486
    identity=take(P+'identity-v1-20261025','229852:0/identity.json');assert not identity['passed'] and identity['originalOwnership']['sourceGraphVerified']
    assert identity['originalOwnership']['originalRootName']==MODEL and not identity['geographicCell']
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==17127 and np.isfinite(tri).all()
    assert np.max(np.abs(np.asarray([tri.min((0,1)),tri.max((0,1))])-native['worldBounds']))<.002
    assert re.fullmatch(r'B[0-9]{10}01063C0',MODEL) and MODEL[1:11]==CSUID[:10] and CSUID[10]=='T'
    # Decode the registered one-metre cell directly. Do not call the old router
    # with a false Tower label or mutate either official/current structureType.
    east=800000+int(CSUID[:5]);north=800000+int(CSUID[5:10]);cell=box(east-834500,816500-north-1,east-834500+1,816500-north)
    target=Polygon(form['rings'][0],form['rings'][1:]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
    assert target.covers(cell) and projection.covers(cell)
    x0,z0,x1,z1=cell.bounds
    halves=[exact_coverage(f,tri) for f in np.asarray([[[x0,0,z0],[x1,0,z0],[x1,0,z1]],[[x0,0,z0],[x1,0,z1],[x0,0,z1]]])]
    assert all(h['exactProjectionCovered'] for h in halves)
    save(out/'exact-georef-cell.json.gz',dict(uid=UID,sourceSHA256=SHA,subtype=form['structureType'],modelTypeCode=MODEL[11:13],csuidComponentCode=CSUID[10],worldXZBounds=list(cell.bounds),wholeOriginalFacesAccounted=17127,exactHalves=halves,covered=True,rawGenericSubtypeFailurePreserved=True))
    spatial=identity['freshCurrentIdentity'];assert spatial['exactObjectAndCSUID'] and spatial['targetCoveredBySourceProjection']>=.999999 and spatial['sourceExcessCoveredByUnrelatedFormsM2']==0
    assert 17.50<spatial['sourceExcessMaximumDistanceFromTargetM']<17.51 and .309<spatial['sourceExcessFraction']<.310
    urbanpath=ROOT/'3d-viewer/city/data/regional/urban.json';urban=read(urbanpath);refs.append(urbanpath)
    def find(value):
        if isinstance(value,dict):
            if value.get('id')=='urban-way-155231234-0':return value
            for v in value.values():
                found=find(v)
                if found:return found
        elif isinstance(value,list):
            for v in value:
                found=find(v)
                if found:return found
    pier=find(urban);assert pier['name']=='Blake Pier at Stanley' and pier['kind']=='pier'
    pierpoly=Polygon(pier['rings'][0]);fraction=projection.intersection(pierpoly).area/projection.area;assert .973<fraction<.974
    save(out/'pier-location-context.json',dict(place=pier,sourceProjectionWithinNamedPier=fraction,sourceExcessOutsideNamedPierM2=float(projection.difference(pierpoly).area),currentCanopyTargetWithinNamedPier=float(target.intersection(pierpoly).area/target.area),officialSourceRecord=official,originalPinnedObjectId=229852,liveObjectId=229486,stableCSUID=CSUID,stableBuildingID=official['BuildingID'],primaryContextSources=['https://www.gohk.gov.hk/en/spots/spot_detail.php?spot=Blake+Pier+at+Stanley','https://www.archsd.gov.hk/en/exhibition/stanley-waterfront-improvement-project.html'],qualification='Named pier/location and restored roof context; numeric original identity separately bound to exact root/CSUID/GeoRef/active subtype. No source geometry or subtype edits.'))
    attributes=take(P+'attributes-v1-20261025','attributes.json.gz');assert attributes['startEndAllInputsVerified'] and attributes['rows'][0]['sourceSHA256']==SHA
    foundation=take(P+'foundations-v1-20261025');assert len(foundation['rows'])==4 and foundation['establishedFoundationPolicyPassed']
    for r in foundation['rows']:
        assert r['completeTerrainTriangles']==r['triangles']==17127 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 and r['minimumGapM']>.5
        take(P+'foundations-v1-20261025',r['mode']+'.json')
    ground=take(P+'complete-ground-v1-20261025');assert len(ground['rows'])==4 and all(r['noAffectedFaces'] and not r['exactAffectedFaces'] for r in ground['rows'])
    scope=take(P+'model-scope-v1-20261025');assert len(scope['rows'])==1 and scope['rows'][0]['currentNativeActorsChecked']==6943 and scope['rows'][0]['nearbyNativeActors']==[]
    forms=take(P+'model-scope-v1-20261025','229852:0-forms.json.gz');assert len(forms)==1 and forms[0]['building']==form
    contacts=take(P+'empty-native-contacts-v1-20261025');assert contacts['rows']==[] and contacts['emptyNativeContactSetProved'] and contacts['boundsProofs'][0]['currentNativeActorsChecked']==6943
    for name in ['whole-source-plan.png','whole-source-perspectives.png']:
        take(P+'identity-views-v1-20261025');path=BASE/(P+'identity-views-v1-20261025')/name;assert digest(path.read_bytes())==pins[P+'identity-views-v1-20261025'][str(path.relative_to(ROOT))];refs.append(path)
    browser=P+'unapproved-browser-v1-20261025';images=[];reports=[]
    for w in [390,1280]:
        report=take(browser,f'{w}/staged-browser.json');assert report['passed'] and not report['errors']
        for v in [v for v in report['views'] if 'time' in v]:
            assert v['uid']==v['pick']==v['collision']==UID and v['sourceSHA256']==SHA and v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces']
            path=BASE/browser/str(w)/v['file'];key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[browser][key];refs.append(path);images.append(dict(uid=UID,width=w,time=v['time'],path=key,sha256=pins[browser][key]))
        if w==390:assert any(v.get('phase')=='failed-download' and v['fallbackRetained'] for v in report['views'])
        assert report['jointViews'] and all(j['models'][0]['sourceSHA256']==SHA and j['models'][0]['active'] for j in report['jointViews'])
        path=BASE/browser/str(w)/'staged-browser.json';reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    assert len(images)==4 and {(i['width'],i['time']) for i in images}=={(w,t) for w in [390,1280] for t in ['15:00','22:00']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={},retainedNativeUids=[],retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],terrainEdits=False,reviewer='ROOT',identityAccepted=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=1,totalNeighbourForms=1,leaseResources=['building:'+UID],visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,originalSourceReviewAccepted=True,rawGenericTypeAndExtentFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,observations=[
        'Accept only this exact immutable original root,17127faces, fixed1x/sourcepose and exact registeredCSUID/GeoRef. Official active record remains Open-sided Structure with null recorded heights; do not relabel it Tower or invent height fields. Pinned/source ObjectID229852 and liveGIS ObjectID229486 are distinct versioned row IDs bound by identical stableCSUID andBuildingID. Original generic unsupported-type/extent failures remain archived; this bounded subtype admission does not globally allow arbitrary01/T mappings.',
        'Exact finite facets cover both halves of the registered one-metre GeoRef cell and the full current canopy footprint. Preserve17.506m source extent/30.9224percent excess. Full government body includes original deck/access geometry beyond the canopy-only footprint.97.3121percent of source projection lies on the existing named Blake Pier at Stanley polygon; remaining16.0132m2 is disclosed, not clipped or treated as a new tolerance. Source graph/root/CSUID evidence establishes ownership; named-pier/official restored-roof context supports location and architectural-role interpretation only.',
        'Complete four-world current-ground checks cover all17127faces, zero buried/upward-buried/negative-clearance facets. This open-sided pier body is admitted independently, no invented soil-support or watertightness criterion and no borrowed BASIC/installed support. All6943current native bounds and the complete one-form scope prove no other actor contact. Zero terrain, coastline or current actor metadata edits.',
        'ROOT actually opened both complete source diagrams and all4private actual desktop/mobile day/night exports. Roof, original supports, deck and access visible/picking/collision/failure-retry pass. Original night material is dark. Existing coarse shoreline cuts beneath part of the pier; this pre-existing basemap limitation is disclosed, not a claim of accurate coastline or reason to move/scale/remodel this source. Guarded live checks/fresh4exports/full6943oldassets/full521/globalBASICreadback still required.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'selected_original_empty_native_contacts_v1_20261025.py'])
    module('open_sided_original_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-open-sided-pier-source-identity-role-browser-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
