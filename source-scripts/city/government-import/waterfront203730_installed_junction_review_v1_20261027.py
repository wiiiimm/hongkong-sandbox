"""Bounded exact original lower-junction review; no geometry or global policy edits."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

P='government-xl-after-qe-waterfront203730-';OLD='government-xl-after-dragon-next-five-waterfront-'
UID='landsd/203730:0';PARENT='landsd/273061:0'
SHA='ef6b1eef5ee27f3c9f027d48436cc31722c8c41b4179e68f90f0d9542e03232e';PSHA='029934eb9578d41e7ca13b6c1e4583715819749587f1334948cd357da623c21a'
NONWALL=[4050,4092,4973,4974,4975,4976,4977,6070,10665]
MODES=['original','literal','leftF32','balancedF32']


def verify_scope(facts):
    assert facts['sourceSHA256']==SHA and facts['nativeSHA256']==PSHA and facts['sourceFaces']==10667
    assert set(facts['worlds'])==set(MODES)and len(facts['worlds'])==4
    for mode,row in facts['worlds'].items():
        assert row['recordedTowerBaseHKPD']=='32.1'and Fraction(row['exactHighestNativeContactHKPD'])<Fraction('32.1')
        assert row['canonicalAnchors']==412 and row['remainingRimTargets']==row['finiteCanonicalPaths']==5
        assert row['rawStrictSupportPassed']is False and row['rawCompoundCapsPassed']is False
        assert row['allCrossingsHaveOriginalFacetPairContact']is True
        assert row['originalCrossingSourceFaces']==[4092,9500,9501,9502,9522]
        assert row['rawCompoundNonWallFaces']==NONWALL and row['negativeWallCount']==27 and row['all27WallCapPathsPassed']
        assert row['compoundBuriedTriangles']==6 and row['compoundBuriedUpwardTriangles']==0 and row['allBuriedFacesWallLike']
        assert row['buriedFacesHaveCapPaths']and row['wholeActualGroundBurial']==0
        assert row['rawTransverseCrossings']==(1010 if mode=='literal'else 26)
    return True


def main():
    base=ROOT/'docs/astra-city/government-import';batch=P+'physical-review-v1-20261027';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,file='summary.json'):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/file;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def part(suffix,file='summary.json'):return take(P+suffix+'-v1-20261026',file)
    def runtime(name):
        take(name,'selection.json.gz');path=HERE/'local'/name/'runtime-geometry.json.gz';assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return next(r for r in read(path)['rows']if r['uid']==UID)
    selected=part('ground','selection.json.gz');source=selected['rows'][0];assert selected['rows']==[source]and source['uid']==UID and source['sourceSHA256']==SHA
    g=runtime(P+'ground-v1-20261026');oldg=runtime('government-xl-after-dragon-next-five-ground-v1-20261026')
    assert np.array_equal(np.asarray(g['drawnGroundGeometry']),np.asarray(oldg['drawnGroundGeometry']))
    attrs=part('attributes','attributes.json.gz');assert attrs['startEndAllInputsVerified'];attr=attrs['rows'][0]
    natives=part('native-contacts','native-input.json.gz')['rows'];assert len(natives)==1 and natives[0]['uid']==PARENT;native=natives[0]
    nattrs=part('native-contacts','native-attributes.json.gz')['rows'];assert len(nattrs)==1;na=nattrs[0]
    assert native['entry']['sha256']==PSHA==na['sourceSHA256']and native['entry']['publicationApproved']and native['entry']['sourceIdentityReviewed']
    assets=[ROOT/source['candidate']['path'],ROOT/native['path']]
    for path,sha in zip(assets,[SHA,PSHA]):assert digest(path.read_bytes())==sha;refs.append(path)
    originals=[decode_original_world_triangles(path.read_bytes())for path in assets];assert [len(t)for t in originals]==[10667,203738]
    fields=dict(literal='completeLiteralWorldPosition',leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',balancedF32='completeExplicitBalancedFloat32WorldPosition')
    worlds={UID:{'original':originals[0]},PARENT:{'original':originals[1]}}
    for uid,attributes in [(UID,attr),(PARENT,na)]:
        ix=np.asarray(attributes['completeOriginalIndex']).reshape(-1,3)
        for mode,field in fields.items():worlds[uid][mode]=np.asarray(attributes[field],dtype='<f8').reshape(-1,3)[ix]
    assert np.array_equal(worlds[UID]['literal'],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    identity=take(P+'identity-review-v1-20261027','ROOT-IDENTITY-REVIEW.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==SHA and identity['freshPrimaryFootprint']['BaseHeight']==32.1
    scope=part('model-scope');assert len(scope['rows'])==1 and scope['rows'][0]['currentNativeActorsChecked']==6984 and [x['uid']for x in scope['rows'][0]['nearbyNativeActors']]==[PARENT]
    forms=part('model-scope','203730:0-forms.json.gz');assert len(forms)==5
    foreign=part('foreign-contacts');assert foreign['foreignPairs']==len(foreign['rows'])==3 and all(m['allFiniteContactPairs']==0 for r in foreign['rows']for m in r['modes'])
    contacts=part('native-contacts');assert len(contacts['rows'])==1;pair=contacts['rows'][0]
    roles=take(P+'native-roles-v1-20261027');lineage=take(P+'native-lineage-v1-20261027');assert len(lineage['rows'])==1
    foundations=part('foundations');assert len(foundations['rows'])==4 and all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 and r['completeTerrainTriangles']==10667 for r in foundations['rows'])
    component=take(P+'negative-components-v2-20261027');assert component['sourceSHA256']==SHA and len(component['rows'])==4
    rawsupport=take(OLD+'support-binding-v1-20261026');assert not rawsupport['allFourModesPassed']and rawsupport['installedNativeEntry']==native['entry']
    compound=take(OLD+'compound-v1-20261026');assert len(compound['rows'])==4
    final=module('waterfront_current_foundation_kernel',HERE/'xl-final-script-pass.py');refs.append(HERE/'xl-final-script-pass.py');world_records={}
    original_roles=take(P+'native-roles-v1-20261027','203730:0--273061:0--original.json.gz')
    original_crossing_faces=sorted({c['sourceFaceA']for c in original_roles if c['contactRole']=='transverse-surface-crossing'})
    for mode in MODES:
        tri,support=worlds[UID][mode],worlds[PARENT][mode];ssha=digest(tri.astype('<f8').tobytes());nsha=digest(support.astype('<f8').tobytes())
        old=take(OLD+'support-v1-20261026','203730:0-'+mode+'.json.gz');assert old['sourceWorldSHA256']==ssha and old['supportWorldSHA256']==nsha
        paths=take(OLD+'strict-root-paths-v2-20261026',mode+'.json.gz');assert paths['sourceWorldSHA256']==ssha and paths['supportWorldSHA256']==nsha and paths['noIntercomponentJoins']and paths['canonicalStrictAnchorCount']==412
        assert len(paths['rows'])==5 and all(r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 and r['terminal']['kind']=='canonical-strict-vertical-support-anchor'for r in paths['rows'])
        label={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);low=take(OLD+'compound-v1-20261026',label+'.json.gz');caps=take(OLD+'compound-v1-20261026',label+'-cap-paths.json.gz')
        combined=np.concatenate([ground,support]);assert digest(combined.astype('<f8').tobytes())==low['groundSHA256']==caps['compoundGroundSHA256']and low['sourceWorldSHA256']==caps['sourceWorldSHA256']==ssha
        wall_paths=caps['proof']['paths'];assert all(r['hasExactSharedEdgeClearCapPath']for r in wall_paths);wall_ids={r['sourceFace']for r in wall_paths}
        # Reproduce the established complete-foundation witnesses to expose face IDs.
        lo,hi=tri.min((0,1)),tri.max((0,1));near=combined[(combined[:,:,0].max(1)>=lo[0]-1)&(combined[:,:,0].min(1)<=hi[0]+1)&(combined[:,:,2].max(1)>=lo[2]-1)&(combined[:,:,2].min(1)<=hi[2]+1)]
        polygons=shapely.polygons(near[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;near,polygons=near[valid],polygons[valid]
        points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),near,shapely.STRtree(polygons)).reshape(-1,4);gaps=points[:,:,1]-heights
        buried=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1));normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(normals,axis=1)/2
        assert len(buried)==old['compoundFoundation']['fullyBuriedTriangles']and float(areas[buried].sum())==old['compoundFoundation']['fullyBuriedAreaM2']
        row=next(r for r in roles['rows']if r['mode']==mode);assert row['sourceWorldSHA256']==ssha and row['nativeWorldSHA256']==nsha
        lin=next(r for r in lineage['rows'][0]['modes']if r['mode']==mode)
        world_records[mode]=dict(recordedTowerBaseHKPD='32.1',exactHighestNativeContactHKPD=row['exactContactBounds'][1][1],canonicalAnchors=paths['canonicalStrictAnchorCount'],remainingRimTargets=5,finiteCanonicalPaths=len(paths['rows']),rawStrictSupportPassed=old['strictSupport']['passed'],rawCompoundCapsPassed=caps['proof']['allAffectedHavePaths'],allCrossingsHaveOriginalFacetPairContact=lin['allRepresentedCrossingsHaveOriginalFacetPairContacts'],originalCrossingSourceFaces=original_crossing_faces,rawCompoundNonWallFaces=caps['proof']['negativeNonWallFaces'],negativeWallCount=len(wall_paths),all27WallCapPathsPassed=all(r['hasExactSharedEdgeClearCapPath']for r in wall_paths),compoundBuriedTriangles=len(buried),compoundBuriedUpwardTriangles=old['compoundFoundation']['fullyBuriedUpwardTriangles'],allBuriedFacesWallLike=bool(np.all(np.abs(normals[buried,1])<=.25*np.linalg.norm(normals[buried],axis=1))),buriedFacesHaveCapPaths=set(map(int,buried))<=wall_ids,wholeActualGroundBurial=next(r['fullyBuriedTriangles']for r in foundations['rows']if r['mode']=={'leftF32':'explicitLeftF32','balancedF32':'explicitBalancedF32'}.get(mode,mode)),rawTransverseCrossings=row['roles']['transverse-surface-crossing'],buriedSourceFaceIds=buried.tolist())
    facts=dict(sourceSHA256=SHA,nativeSHA256=PSHA,sourceFaces=10667,worlds=world_records);assert verify_scope(facts)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==selected['manifestSHA256']==identity['currentManifestSHA256'];refs.append(manifest)
    images=[];retained=[];reports=[];browser_name=P+'private-browser-v3-20261027';browser,_=authenticate(base/browser_name);assert browser['allBrowserDiagnosticsPassed']and not browser['downloadFailureTestsSkipped'];refs.append(base/browser_name/'result.json')
    for width in [1280,390]:
        report=take(browser_name,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];rp=base/browser_name/str(width)/'staged-browser.json';reports.append(dict(path=str(rp.relative_to(ROOT)),sha256=digest(rp.read_bytes())))
        for kind,rows,target in [('source',report['views'],images),('retained',report['retainedNativeOwnViews'],retained)]:
            views=[r for r in rows if r.get('file')];assert len(views)==2
            for view in views:
                path=base/browser_name/str(width)/view['file']
                assert digest(path.read_bytes())==pins[browser_name][str(path.relative_to(ROOT))];refs.append(path)
                assert view['fullyFramed']and not view['fallbackFaces']and view['active']and view['visible']
                assert view['sourceSHA256']==(SHA if kind=='source'else PSHA)
                if kind=='source':assert view['pick']==view['collision']==UID and view['solidAppearance']
                target.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=view['uid'],width=width,time=view['time']))
    assert len(images)==len(retained)==4
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={UID:PARENT},nativeSupportByUid={UID:PARENT},retainedNativeEntries={PARENT:native['entry']},reviewer='ROOT',identityAccepted=True,identityProof=identity['identityProof'],rawIdentityReasonsRetained=identity['rawReasonsRetained'],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeCurrentNeighbourChecks=5,leaseResources=sorted('building:'+r['building']['uid']for r in forms),retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=msha),currentManifestSHA256=msha,terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawCanonicalFailuresPreserved=True,unresolvedExternalBasicContacts=[],acceptedInstalledSupportContacts=[dict(uid=UID,nativeUid=PARENT,physicalInterpretationAccepted=True,rawContactSummary=pair)],junctionFacts=facts,rawSupportAndCompoundVerdicts=rawsupport,rawCompoundClearance=compound,sourceComponents=component,imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,browserReports=reports,visualAcceptance=False,installationApproved=False,publication=False,interpretation=[
        'Accept only the exact unchanged government Tower VI source on the exact currently installed Elements native source. All actual-earth faces clear, all three BASIC neighbours have zero contacts, and every native contact is below31.226m HKPD, below the official32.1m tower-record base. This is the lower provider-authored apron/podium junction, not a claim that podium roofs are earth or that all source diagnostics passed.',
        '412 canonical strict support anchors are unchanged. The five remaining rim warnings have finite original shared-edge paths to those anchors in all four worlds under unchanged endpoint-height/1mm residual limits. Raw strict passedFalse and compound capsFalse remain. The six whole compound-buried faces are independently identified as wall-like and have original clear-cap paths. No whole upward floor is buried;27negative wall faces all retain paths.',
        'The nine non-wall compound negatives remain explicit:4050 is a downward minimum closure of a24face lower plinth,4092 is a downward lower face of the9190face body;4973..4977/6070 are upward horizontal lower-body facets;10665 is an upward sloping face of a48face lower detail. Roofs over these partially covered authored lower details are not treated as terrain. This exact same-site lower-junction interpretation grants no generic horizontal-floor, source-crossing or threshold exception.',
        'The26 original crossings are retained on five lower source faces. Every984extra literal crossing is an existing original point/edge pair under tiny exact transform-evaluation deltas; no new facet pair exists. All raw1010literal crossings remain recorded. This authoring junction is accepted only for these pinned bytes, fixed1x/source pose and explicit native dependency; neither source nor Elements is cut, shifted, simplified or re-skinned.',
        'ROOT actually opened all eight final V3 exports, desktop1280/mobile390, day/night for source and retained Elements. The east view exposes complete source roof, body and lower apron; defaultV2 foreground occlusion is not used for appearance approval. Native provider surfaces are plain grey/dark at night with procedural windows disabled; no invented facade or night lighting is asserted. Retained owner views remain the unchanged original. Final live publication, fresh live observations, global retained BASIC checks and full old-asset/521-ledger readback remain mandatory.'])
    result=__import__('json').loads(__import__('json').dumps(result,allow_nan=False));save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'junction-facts.json',facts)
    refs.extend([HERE/'original_installed_support_model_only_contract_v1_20261027.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('waterfront_junction_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-exact-waterfront-installed-elements-lower-junction-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
