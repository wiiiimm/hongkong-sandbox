"""Bind the bounded unchanged original podium/tower source-role interpretation.

Private browser admission only; identity, neighbour/browser and publication gates remain.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-84014-original-physical-review-v1-20261025'
SOURCES={'landsd/84014:0':'2f0657211c031b7a4744fa4c1f0397511d1f43e2160919d3ea885eaf12354d80','landsd/155042:0':'709128d4fc6bb2d963ea6309591ff6e7139e783930dc1f5ff606ad5abd4476f0','landsd/269721:0':'368998781f636a151356de6f08a92aa58cc1a80e53b298ec14b43abd68db7be2'}
FACES=[4493,4494,4495,4995,4996]


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(name,path):
        if name not in pins:
            r,pins[name]=authenticate(BASE/name);jobs[name]=r['jobId'];refs.append(BASE/name/'result.json')
        path=BASE/name/path;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime='government-xl-84014-three-original-runtime-v1-20261024'
    selection=take(runtime,'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    scope_name='government-xl-84014-three-original-current-scope-v1-20261025';scope=take(scope_name,'summary.json')
    assert scope['currentManifestSHA256']==selection['manifestSHA256']and set(scope['uids'])==set(SOURCES)
    forms={}
    for row in scope['rows']:
        assert row['currentNativeActorsChecked']==6908 and not row['nearbyNativeActors']
        for f in take(scope_name,row['uid'].split('/')[1]+'-forms.json.gz'):forms[f['building']['uid']]=f['building']
    assert set(forms)==set(SOURCES)|{'landsd/210816:0'}
    ground='government-xl-84014-current-ground-clearance-v1-20261024';g=take(ground,'summary.json')
    assert g['sourceSHA256']==SOURCES['landsd/84014:0']and len(g['rows'])==4
    assert all(r['completeSourceFaces']==10449 and r['compoundCapPathsPassed']and not r['negativeNonWallFaces']for r in g['rows'])
    raw={}
    for label,uid in [('tower1','landsd/155042:0'),('tower2','landsd/269721:0')]:
        name='government-xl-84014-'+label+'-original-podium-support-v1-20261024';checks=take(name,'summary.json')
        assert checks['sourceSHA256ByUid']=={uid:SOURCES[uid],'landsd/84014:0':SOURCES['landsd/84014:0']}
        paths=take('government-xl-84014-'+label+'-original-contact-paths-v1-20261024','summary.json')
        assert paths['allUnresolvedHaveFinitePaths']and len(paths['rows'])==4
        for check,path in zip(checks['rows'],paths['rows']):
            assert check['mode']==path['mode']and len(check['support']['unresolved'])==path['targets']and path['remaining']==0
            foundation=check['compoundFoundation'];assert foundation['completeTerrainTriangles']==foundation['triangles']and foundation['fullyBuriedTriangles']==foundation['fullyBuriedUpwardTriangles']==0
        name='government-xl-84014-'+label+'-complete-compound-clearance-v1-20261024';clearance=take(name,'summary.json');assert len(clearance['rows'])==4
        for row in clearance['rows']:
            assert row['negativeNonWallFaces']==(FACES if label=='tower1'else [])
            proof=take(name,row['mode']+'-cap-paths.json.gz')['proof']
            assert all(r['hasExactSharedEdgeClearCapPath']for r in proof['paths'])
            assert row['compoundCapPathsPassed']is (label=='tower2')
        raw[uid]=dict(strictInterfacePassed=checks['allFourModesPassed'],minimumCompoundGapM=[r['compoundFoundation']['minimumGapM']for r in checks['rows']],unresolvedSamples=[len(r['support']['unresolved'])for r in checks['rows']],finiteSourcePathsVerified=True,negativeNonWallFaces=FACES if label=='tower1'else [])
    name='government-xl-84014-tower1-five-ledge-vertex-clearance-v1-20261025';v=take(name,'summary.json');assert len(v['rows'])==20
    assert {r['sourceFace']for r in v['rows']}==set(FACES)and {r['mode']for r in v['rows']}=={'original','literal','left','balanced'}
    for row in v['rows']:
        assert row['normalY']==1.0 and min(row['xzSpanM'])<.03
        assert all(abs(p['gapM'])<.002 for p in row['vertices'])
    for name in ['government-xl-84014-three-original-pair-context-v1-20261024','government-xl-84014-current-foreign-contacts-v1-20261024','government-xl-84014-adjacent-low-basic-contact-views-v1-20261024','government-xl-84014-tower1-five-ledge-views-v1-20261025']:
        take(name,'summary.json')
    inspected=[BASE/'government-xl-84014-original-source-context-v1-20261024/whole-source-plan.png',BASE/'government-xl-84014-original-source-context-v1-20261024/whole-source-perspectives.png',BASE/'government-xl-84014-adjacent-low-basic-contact-views-v1-20261024/before-after-contact-context.png',BASE/'government-xl-84014-tower1-five-ledge-views-v1-20261025/region-1.png']
    assert all(p.exists()for p in inspected);refs.extend(inspected)
    review=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid={'landsd/155042:0':'landsd/84014:0','landsd/269721:0':'landsd/84014:0'},currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),sourceSpecificPhysicalInterpretationAccepted=True,completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=True,retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],emptyRetainedBasicSupportQualification='No basic actor receives support credit; both towers depend on the exact new original podium.',leaseResources=sorted('building:'+u for u in forms),terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,rawWarnings=raw,boundedFiveFacetInterpretation=dict(uid='landsd/155042:0',sourceSHA256=SOURCES['landsd/155042:0'],faceIds=FACES,interpretation='Five authored upward deck-junction strips, each less than3cm in its narrow XZ span, coincide with the original podium deck at all vertices within the existing2mm interface rule. Their interiors are partly concealed by the curved original podium edge. Every affected wall has an exact path to a clear cap, all18 actual rim warnings have finite source-to-source paths, and every compound whole/upward burial count remains zero. Preserve the negative interior gaps; no generic thin-face, area, contact or burial exemption is introduced.',rawWallOnlyCapContractStillFalse=True),inspectedSourceImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in inspected],otherDiagnosticImagesNotClaimedInspected=True,identityAccepted=False,completeNeighbourInterpretationAccepted=False,visualAcceptance=False,publication=False,installationApproved=False,qualification='Bounded source-evidence interpretation for private browser review of these exact three immutable originals only. Current source identity, full effective-neighbour review, desktop/mobile actual exports, publication and independent fixed521/old6908 readback remain mandatory. Strict raw negative flags and wall-only cap exclusions are retained.')
    save(out/'ROOT-PHYSICAL-REVIEW.json',review)
    module('podium84014_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-podium-two-tower-physical-source-review',refs,dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,reviewedForPrivateBrowser=True,sourceGeometryChanges=0,identityAccepted=False,visualAcceptance=False,publication=False))

if __name__=='__main__':main()
