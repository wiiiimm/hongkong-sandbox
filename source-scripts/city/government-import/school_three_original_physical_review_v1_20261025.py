"""Exact school assembly physical/source-role review for private preview only."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from school_three_original_identity_review_v1_20261025 import SOURCES, RUNTIME, ATTRS
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-quality-music-school-three-physical-review-v1-20261025'
POD='landsd/244789:0'; WING='landsd/231606:0'; MAIN='landsd/244581:0'
PATCH='government-xl-quality-music-school-original-seam-terrain-v6-20261025'


def main():
    out=BASE/BATCH
    assert not out.exists()
    pins,receipts,refs={},{},[Path(__file__),HERE/'school_three_original_identity_review_v1_20261025.py',HERE/'exact_packed_world_geometry_20261009.py']
    def take(batch,name='summary.json',local=False):
        if batch not in pins:
            receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=(HERE/'local'/batch if local else BASE/batch)/name
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    selection=take(RUNTIME,'selection.json.gz');rows={r['uid']:r for r in selection['rows']}
    assert {u:r['sourceSHA256']for u,r in rows.items()}==SOURCES
    identity=take('government-xl-quality-music-school-three-bounded-identity-review-v1-20261025','ROOT-IDENTITY-REVIEW.json')
    assert identity['identityAccepted'] and identity['requiredOriginalAssembly']==SOURCES
    attrs=take(ATTRS,'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    attrs={r['uid']:r for r in attrs['rows']}
    geometry={r['uid']:r for r in take(RUNTIME,'runtime-geometry.json.gz',True)['rows']}
    oldruntime='government-xl-quality-music-school-ramp-return-runtime-v5-20261025'
    oldgeometry={r['uid']:r for r in take(oldruntime,'runtime-geometry.json.gz',True)['rows']}
    forms,worlds={},{ }
    canonical=module('school_physical_canonical',HERE/'xl-next-support-recovery-20261005.py');refs.append(HERE/'xl-next-support-recovery-20261005.py')
    for u,r in rows.items():
        f=forms[u]=r['source']['building'];tile=ROOT/'3d-viewer'/r['source']['tile']
        assert next(b for b in read(tile)['buildings']if b['uid']==u)==f;refs.append(tile)
        entry,_=canonical.diagnostic_entry(r['native'],f);entry['asset']=r['candidate']['entry']['asset']
        assert entry==r['candidate']['entry'] and entry['rootTranslation']==[-834500,0,816500]
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[u]==attrs[u]['sourceSHA256']==geometry[u]['sourceSHA256'];refs.append(asset)
        assert geometry[u]['position']==oldgeometry[u]['position'] and geometry[u]['index']==oldgeometry[u]['index']
        ix=np.asarray(attrs[u]['completeOriginalIndex']).reshape(-1,3)
        worlds[u]={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attrs[u][k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
        foundation=take('government-xl-school'+u.split('/')[1].split(':')[0]+'-seam-foundations-v6-20261025')
        assert len(foundation['rows'])==4 and all(x['triangles']==x['completeTerrainTriangles']==r['triangles'] and x['fullyBuriedTriangles']==x['fullyBuriedUpwardTriangles']==0 for x in foundation['rows'])
    coverage=take('government-xl-quality-music-school-seam-exact-coverage-v6-20261025')
    assert all(not r['stillUncoveredFaces']for r in coverage['rows'])
    continuous=take('government-xl-quality-music-school-seam-continuous-v6-20261025')
    for r in continuous['rows']:
        assert r['upwardContinuousMinimumGapM']>=-.5
        assert set(r['continuousAffectedFaces'])==set(r['affectedWallFaces'])
        assert len(r['continuousAffectedFaces'])=={MAIN:152,POD:37,WING:0}[r['uid']]
    panel_context=[]
    for u,count in [(MAIN,152),(POD,37)]:
        number=u.split('/')[1].split(':')[0]
        lowname='government-xl-school'+number+'-seam-complete-ground-v6-20261025'
        low=take(lowname)
        caps=take('government-xl-school'+number+'-seam-cap-paths-v6-20261025')
        assert len(low['rows'])==len(caps['rows'])==4
        for row in caps['rows']:
            mode=row['mode'];paths=row['completeGroundClearancePartition']['paths']
            assert len(paths)==count
            failed=[r['sourceFace']for r in paths if not r['hasExactSharedEdgeClearCapPath']]
            assert failed==(list(range(10594,10602))if u==MAIN else [])
            detail=take(lowname,mode+'.json.gz')
            assert detail['sourceWorldSHA256']==row['sourceWorldSHA256']
            assert all(r['absoluteNormalYRatio']<.25 for r in detail['rows'])
            byid={r['sourceFace']:r for r in detail['rows']}
            for face in failed:
                r=byid[face]
                assert r['highestVertexAboveEveryOverlappingGroundFace']
                pairs=[p['groundFace']for p in r['negativeGroundPairProofs']if min(Fraction(v['exactGapM'])for v in p['proof']['allExactBasicFeasibleColumnVertices'])<0<max(Fraction(v['exactGapM'])for v in p['proof']['allExactBasicFeasibleColumnVertices'])]
                assert pairs
                panel_context.append(dict(mode=mode,face=face,exactGroundCrossingPairs=pairs))
    strict=take('government-xl-quality-music-school-neighbour-podium-support-v1-20261025')
    assert strict['sourceSHA256ByUid']=={u:SOURCES[u]for u in [WING,POD]}
    for r in strict['rows']:
        for u in [WING,POD]:assert r['sourceWorldSHA256ByUid'][u]==digest(worlds[u][r['mode']].astype('<f8').tobytes())
        assert r['support']['strictContacts']==11 and len(r['support']['unresolved'])==97
        assert r['compoundFoundation']['fullyBuriedTriangles']==36 and r['compoundFoundation']['fullyBuriedUpwardTriangles']==27
    paths=take('government-xl-quality-music-school-neighbour-strict-root-paths-v1-20261025')
    assert all(r['targets']==r['finiteAttachmentPaths']==97 and r['disconnected']==r['aboveExistingEndpointCeiling']==0 for r in paths['rows'])
    rawcompound=take('government-xl-school231606-podium-complete-compound-v5-20261025')
    assert all(len(r['exactAffectedFaces'])==520 for r in rawcompound['rows'])
    foreign=take('government-xl-quality-music-school-ramp-return-foreign-contacts-v5-20261025')
    assert all(not m['allFiniteContactPairs'] and m['projectedOverlapAreaM2']==0 for r in foreign['rows']if r['foreignUid']not in SOURCES for m in r['modes']if m['mode']!='before-basic')
    raw_baseline_contacts=[dict(uid=r['uid'],foreignUid=r['foreignUid'],modes=[m for m in r['modes']if m['mode']=='before-basic' and (m['allFiniteContactPairs'] or m['projectedOverlapAreaM2'])])for r in foreign['rows']if r['foreignUid']not in SOURCES]
    scope='government-xl-quality-music-school-seam-scope-v6-20261025'
    s=take(scope,'scope.json');obligations={f['uid']:f for f in take(scope,'form-obligations.json.gz')}
    assert len(obligations)==s['intersectingForms']==22 and s['currentNativeActors']==6926
    assert not s['touchingNativeUids'] and not s['terrainContacts'] and s['positiveAreaTerrainOverlaps']==0
    assert all(obligations[u]==f for u,f in forms.items())
    neighbours=take('government-xl-quality-music-school-seam-form-checks-v6-20261025')
    assert neighbours['forms']==22 and neighbours['ordinaryFlagged']==0 and neighbours['flagged']==[]
    take('government-xl-school-ramp-return-independent-readback-v1-20261025')
    take(PATCH)
    assert receipts[PATCH]['status']=='private-terrain-validator-passed'
    newpatch=take(PATCH,'candidate-terrain.json',True)
    oldpatch=take('government-xl-quality-music-school-original-ramp-return-v5-20261025','candidate-terrain.json',True)
    for k in ['position','index']:assert newpatch['nativeMesh'][k][:len(oldpatch['nativeMesh'][k])]==oldpatch['nativeMesh'][k]
    assert len(newpatch['nativeMesh']['index'])//3==4580
    images=[]
    for batch,name in [('government-xl-school-original-courtyard-panel-context-v1-20261025','exact-source-role-context.png'),('government-xl-quality-music-school-three-identity-context-v6-20261025','source-record-context.png'),('government-xl-quality-music-school-ramp-return-source-views-v5-20261025','complete-original-assembly.png')]:
        take(batch);p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    resources={('building:'if u.startswith('landsd/')else'source-form:')+u for u in obligations}|{'terrain:city/data/terrain.json'}
    result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid={WING:POD},retainedNativeUids=[],retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],reviewer='ROOT',identityAccepted=True,identityProof=identity['identityProof'],identityProofByUid=identity['identityProofByUid'],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeCurrentNeighbourChecks=22,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),leaseResources=sorted(resources),imagesActuallyViewed=images,rawCanonicalFailuresPreserved=True,rawPreviousBasicContacts=raw_baseline_contacts,uncappedOriginalPanelGradeContext=panel_context,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,terrainEdits=True,visualAcceptance=False,installationApproved=False,publication=False,interpretation=[
        'Identity is separately accepted for the exact3source school permit assembly. Original fixed1x/sourceplacement/canonicalentries/14472faces are retained. The V6 derived terrain preserves all4425V5faces, adds155Float32 seam covers, and passes existing terrain validation and22surroundingforms. Exact residual proofs account for every source face; all upward surfaces pass unchanged-.5m clearance and no actual-ground whole/upwardwhole burial occurs in any stream.',
        'Actual-ground negatives are confined to152main/37podium original vertical walls. All37podium and144main faces have exact clear-cap attachment paths. Exactly8main faces10594..10601 form the inspected narrow original vertical assembly; every face crosses actual ground and its highestvertex is above every overlapping actualgroundfacet in all4streams. Accept these specific exposed original panel toes, retaining missingcap failures and every face. This creates no watertightness, engineering, generalwall or buriedfloor exemption.',
        'The original wing has11strict contacts with the original podium; all97remaining probes have finite sharedoriginaledge paths to strictroots within the existing endpoint ceiling. Depend only on that exact original podium; main andpodium retain their own ground contact. The diagnostic treating the entire original podium as earth yields36wholefacesincluding27upward and520partialaffectedfaces in thewing. This is the unchanged shared original school architecture envelope, not earth; preserve those raw negatives, rather than cutting the original auditorium/roof junction or requiring zero own-source interpenetration. Actual drawn ground is independently clear for thewing. No unrelated building or BASICproxy supplies support.',
        'ROOT inspected completeoriginal sourceviews, currentfootprint/GeoRef projections and exactcourtyard/paneldiagram; the translucent sourceview obscures some ground and doesnot establish visualruntime acceptance. Unrelated finitecontacts/projectionoverlap arezero for all four original streams. Previous BASIC proxies have56/46 contacts with44223 and podium.000965m2 overlap; those pre-existing baseline diagnostics remain, not new-original conflicts; V5sourcegeometry equality binds their unchanged interface proof, while all V6terrainchecks arefresh. Private preview only:12actualdesktop/mobile/day/night exports, picking/collision/failure/retry/jointactivation, actualterrainvisualinspection, guardedpublication/full6926oldassets/full521/globalBASICreadback remain mandatory.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result)
    module('school_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-school-original-assembly-physical-review-for-preview',refs,result)


if __name__=='__main__':
    main()
