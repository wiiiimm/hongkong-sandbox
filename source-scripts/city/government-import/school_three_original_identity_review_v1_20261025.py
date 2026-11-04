"""Bounded source identity review of the exact three original school components."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-quality-music-school-three-bounded-identity-review-v1-20261025'
RUNTIME = 'government-xl-quality-music-school-seam-runtime-v6-20261025'
ATTRS = 'government-xl-quality-music-school-seam-attributes-v6-20261025'
SOURCES = {'landsd/244581:0':'26427158252a7943232c9c281d20dbbf24326c9aba26be028da4cb19d75e5393','landsd/244789:0':'71fe74b86400021233c7e29869de099708f751e04842a9fcd2a3b24746a358e9','landsd/231606:0':'15a4f826ddc8fb73c93a99e0f33210b922ec4bf8587e35fcfcddfceeca9e687d'}


def main():
    out = BASE / BATCH
    assert not out.exists()
    pins, refs = {}, [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py']
    def take(batch, filename='summary.json'):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        p = BASE/batch/filename
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    selected = take(RUNTIME,'selection.json.gz')
    rows = {r['uid']:r for r in selected['rows']}
    assert {u:r['sourceSHA256'] for u,r in rows.items()} == SOURCES
    attr = take(ATTRS,'attributes.json.gz')
    assert attr['startEndAllInputsVerified']
    attrs = {r['uid']:r for r in attr['rows']}
    forms, worlds, identities = {}, {}, {}
    for u,r in rows.items():
        asset = ROOT/r['candidate']['path']
        assert digest(asset.read_bytes()) == SOURCES[u] == attrs[u]['sourceSHA256']
        refs.append(asset)
        f = forms[u] = r['source']['building']
        tile = ROOT/'3d-viewer'/r['source']['tile']
        assert next(x for x in read(tile)['buildings'] if x['uid']==u) == f
        refs.append(tile)
        raw = take('government-xl-after-tvb-next-three-with-companions-identity-v1-20261025',u.split('/')[1]+'/identity.json')
        assert raw['sourceSHA256']==SOURCES[u] and raw['originalOwnership']['sourceGraphVerified']
        assert raw['exactCurrentComponentRoute']['qualified'] and raw['freshCurrentIdentity']['exactObjectAndCSUID']
        identities[u] = raw
        ix = np.asarray(attrs[u]['completeOriginalIndex']).reshape(-1,3)
        worlds[u] = {'original':decode_original_world_triangles(asset.read_bytes()), **{mode:np.asarray(attrs[u][field]).reshape(-1,3)[ix] for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
        assert all(len(t)==r['triangles'] for t in worlds[u].values())
    permit = take('government-xl-quality-music-school-complete-permit-v1-20261025')
    assert permit['permit']=='KN27/2004(OP)' and permit['exactSelectedPermitMembership']
    assert set(permit['completePermitCSUIDs']) == {f['buildingCSUID'] for f in forms.values()}
    assert len(permit['completeStructureIDs'])==3
    primary = take('government-xl-quality-music-school-three-primary-records-v1-20261025','footprints.json')
    official = {r['attributes']['BuildingCSUID']:r['attributes'] for r in primary['features']}
    for f in forms.values():
        r=official[f['buildingCSUID']]
        assert r['Status']=='Active' and r['BuildingBlockType']==f['structureType']
        assert r['BaseHeight']==f['base'] and abs(r['TopHeight']-f['base']-f['height'])<1e-8
    context = take('government-xl-quality-music-school-three-identity-context-v6-20261025')
    assert context['requiredOriginalAssembly']==SOURCES
    assert all(r['completeAssemblyTargetCoverage']>=.95 and r['completeAssemblyWholeCellCovered'] for r in context['rows'])
    spatial = take('government-xl-quality-music-school-ramp-return-compound-spatial-v5-20261025')
    assert spatial['requiredOriginalAssembly']==SOURCES and not spatial['allFourSpatialLimitsPassed']
    diagnostic = take('government-xl-school-original-courtyard-panel-context-v1-20261025')
    flagged = set(diagnostic['extentFaceIds'])
    assert len(flagged)==64
    target = shapely.union_all([shapely.Polygon(f['rings'][0],f['rings'][1:]) for f in forms.values()])
    details=[]
    for mode in worlds['landsd/244581:0']:
        for u in SOURCES:
            t=worlds[u][mode]
            distances=shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3)
            ids=set(np.flatnonzero(distances.max(1)>10).tolist())
            assert ids==(flagged if u=='landsd/244581:0' else set())
            if ids:
                low=t[sorted(ids)]
                assert low[:,:,1].min()>88.18 and low[:,:,1].max()<88.87
                details.append(dict(uid=u,mode=mode,extentFaceIds=sorted(ids),yRangeM=[float(low[:,:,1].min()),float(low[:,:,1].max())]))
    photo=HERE/'local/government-xl-school-primary-campus-page-v1-20261025/operator-school1.jpg'
    photo_hash=digest(photo.read_bytes())
    assert photo_hash=='2ccd920bcdd7f4ea46437ad2281d66e260c46cbcfcd7ae1cd4398f70a6f3edc1'
    images=[]
    for batch,name in [('government-xl-school-original-courtyard-panel-context-v1-20261025','exact-source-role-context.png')]:
        p=BASE/batch/name
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))]
        refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    refs.append(manifest)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,reviewer='ROOT',identityAccepted=True,identityProof=proof,identityProofByUid={u:proof for u in SOURCES},rawIdentityProofs=identities,rawExtentFailureRetained=True,genericIdentityPolicyChanges=False,sourceSpecificExtentContext=details,figuresActuallyViewed=images,officialPhoto=dict(pageURL='https://www.icsc.org.hk/about-icqm',sha256=photo_hash,actuallyViewed=True,dateUnknown=True),sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAcceptance=False,visualRuntimeAcceptance=False,installationApproved=False,observations=[
        'The three exact current object/CSUID routes and original source graphs are bound to the complete three-structure official KN27/2004(OP) membership. Different current parent identifiers are retained; common parentage is not claimed. All three recorded GeoRef cells are exactly covered by the original assembly and each target exceeds95percent compound coverage.',
        'The main original contains64 low curved courtyard facets beyond the smaller GIS building outlines. These same64 facets account for every greater-than10m extension in all four coordinate streams; their source height lies only88.186..88.861m HKPD. ROOT inspected the exact source diagram and operator campus photograph showing the curved stepped outdoor theatre and surrounding school wings. This corroborates the retained courtyard architecture, not cadastral dimensions or a precise identification of every small facet. The source bytes, authoritative component route and complete school permit establish identity.',
        'Accept identity only for these three exact hashes/current forms as the original school assembly. Preserve all raw individual coverage/cell/other-form/extent failures and the compound11.3078m extent failure. The generic10m threshold remains unchanged. No invented outline buffer, convex hull, source geometry edit or blanket campus ownership exemption is used.',
        'This is identity approval only. Exact physical terrain clearance, original component interfaces/support, complete unrelated neighbours, actual desktop/mobile exports, guarded installation and old-asset/globalBASIC/full521readback remain separate mandatory checks.'
    ])
    save(out/'ROOT-IDENTITY-REVIEW.json',result)
    module('school_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-school-three-original-identity-review',refs,{k:v for k,v in result.items() if k!='rawIdentityProofs'})


if __name__=='__main__':
    main()
