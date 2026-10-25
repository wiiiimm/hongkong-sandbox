"""Bind exact In One source-role, support, terrain and inspected browser evidence."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-inone-five-original-source-review-v2-20261025'
POD='landsd/277890:0'
SUPPORTS={f'landsd/{n}:0':POD for n in [278234,314698,314700,278458]}
RUNTIME='government-xl-inone-five-required-earth-runtime-v6-20261025'
BROWSER='government-xl-inone-five-required-earth-unapproved-browser-v2-20261025'
PATCH='government-xl-inone-five-required-earth-seam-terrain-v6-20261025'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};receipts={}
    def take(batch,name='summary.json',local=False):
        if batch not in pins:
            receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=(HERE/'local'/batch if local else BASE/batch)/name
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    identity=take('government-xl-inone-five-bounded-identity-review-v1-20261025','ROOT-IDENTITY-REVIEW.json');assert identity['identityAccepted']
    sources=identity['sourceSHA256ByUid'];assert set(sources)==set(SUPPORTS)|{POD}
    selected=take(RUNTIME,'selection.json.gz');rows={r['uid']:r for r in selected['rows']};assert {u:r['sourceSHA256']for u,r in rows.items()}==sources
    attrs=take('government-xl-inone-five-current-attributes-v1-20261025','attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']}
    worldhashes={}
    for u,r in rows.items():
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==sources[u]==attrs[u]['sourceSHA256'];refs.append(asset)
        f=r['source']['building'];tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==u)==f;refs.append(tile)
        assert r['candidate']['entry']['rootTranslation']==[-834500,0,816500]
        ix=np.asarray(attrs[u]['completeOriginalIndex']).reshape(-1,3)
        worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attrs[u][k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
        assert all(len(t)==r['triangles']for t in worlds.values());worldhashes[u]={m:digest(t.astype('<f8').tobytes())for m,t in worlds.items()}
    assert sum(r['triangles']for r in rows.values())==72571
    normalize=lambda m: {'leftF32':'left','balancedF32':'balanced'}.get(m,m)
    support_records=[]
    for u in SUPPORTS:
        n=u.split('/')[1].split(':')[0];batch='government-xl-inone-'+n+'-podium277890-support-v1-20261025';s=take(batch)
        assert s['sourceSHA256ByUid']=={u:sources[u],POD:sources[POD]} and len(s['rows'])==4
        for r in s['rows']:
            assert r['sourceWorldSHA256ByUid']=={v:worldhashes[v][normalize(r['mode'])]for v in [u,POD]}
            assert r['compoundFoundation']['fullyBuriedTriangles']==r['compoundFoundation']['fullyBuriedUpwardTriangles']==0
        if n in ['278234','314700']:assert s['allFourModesPassed']
        else:
            assert not s['allFourModesPassed']
            paths=take('government-xl-inone-'+n+'-podium277890-finite-paths-v1-20261025')
            assert paths['allUnresolvedHaveFinitePaths'] and len(paths['rows'])==4
            for r in paths['rows']:
                assert r['targets']==r['verifiedPaths']==1 and r['remaining']==0
                assert r['sourceWorldSHA256']==worldhashes[u][normalize(r['mode'])] and r['supportWorldSHA256']==worldhashes[POD][normalize(r['mode'])]
        support_records.append(dict(uid=u,supportUid=POD,strictPassed=s['allFourModesPassed'],finitePathReviewRequired=n in ['314698','278458']))
    complete=take('government-xl-inone-podium277890-required-earth-complete-ground-v6-20261025');assert complete['sourceSHA256']==sources[POD] and len(complete['rows'])==4
    assert all(r['completeSourceFaces']==10129 and not r['negativeNonWallFaces'] and r['compoundCapPathsPassed'] and r['allAffectedWallLike']for r in complete['rows'])
    coverage=take('government-xl-inone-five-required-earth-exact-coverage-v6-20261025');assert all(not r['stillUncoveredFaces']for r in coverage['rows'])
    continuous=take('government-xl-inone-five-required-earth-continuous-v6-20261025')
    for r in continuous['rows']:
        assert r['upwardContinuousMinimumGapM']>=-.5 and not r['otherAffectedFaces']
        assert set(r['continuousAffectedFaces'])==set(r['affectedWallFaces'])
        assert not r['continuousAffectedFaces']or r['uid']==POD
    take(PATCH);assert receipts[PATCH]['status']=='private-terrain-validator-passed'
    patch=read(ROOT/receipts[PATCH]['candidate']['path']);assert len(patch['nativeMesh']['index'])//3==512
    old='government-xl-inone-podium277890-required-earth-inset-v5-20261025';take(old);before=read(ROOT/receipts[old]['candidate']['path'])
    for k in ['position','index']:assert patch['nativeMesh'][k][:len(before['nativeMesh'][k])]==before['nativeMesh'][k]
    scope='government-xl-inone-five-required-earth-scope-v6-20261025';s=take(scope,'scope.json');forms={r['uid']:r for r in take(scope,'form-obligations.json.gz')}
    assert len(forms)==s['intersectingForms']==39 and s['currentNativeActors']==6931
    assert not s['touchingNativeUids']and not s['terrainContacts']and s['positiveAreaTerrainOverlaps']==0
    neighbours=take('government-xl-inone-five-required-earth-neighbours-v6-20261025');assert neighbours['forms']==39 and neighbours['flagged']==[] and neighbours['ordinaryFlagged']==0
    native=take('government-xl-inone-five-full-source-native-scope-v1-20261025');assert set(native['uids'])==set(sources)
    assert all(r['currentNativeActorsChecked']==6931 and not r['nearbyNativeActors']for r in native['rows'])
    obligations=dict(forms)
    for row in native['rows']:
        for entry in take('government-xl-inone-five-full-source-native-scope-v1-20261025',row['uid'].split('/')[1]+'-forms.json.gz'):
            form=entry['building'];uid=form['uid']
            if uid in obligations:assert obligations[uid]==form
            obligations[uid]=form
    assert len(obligations)==50 and len(set(obligations)-set(forms))==11
    contacts=take('government-xl-inone-five-current-foreign-contacts-v1-20261025');assert contacts['foreignPairs']==34
    context=take('government-xl-inone-podium-original-contact-context-v1-20261025');assert context['foreignContactActors']==10
    expected={f'landsd/{n}:0'for n in [143007,143008,143438,144312,144314,144315,277973,277974,277975,314699]};assert {r['foreignUid']for r in context['rows']}==expected
    for r in contacts['rows']:
        if r['foreignUid']in sources:continue
        if any(m['positiveContactPairs']for m in r['modes']if m['mode']!='before-basic'):assert r['uid']==POD and r['foreignUid']in expected
    peers=take('government-xl-inone-three-platform-original-interfaces-v1-20261025');assert peers['sourceSHA256ByUid'][POD]==sources[POD] and peers['completeUnorderedPairs']==3
    assert peers['sourceSHA256ByUid']['landsd/277973:0']=='0938a24dfb98fa47c7f91674a9d15f7eeb0519a51a4cb4efdad3f4047377a882'
    assert peers['sourceSHA256ByUid']['landsd/277974:0']=='c228a786763b304643263f101169c559c89d9707cfd7bc06c028c3073244e693'
    assert all(r.get('positiveSurfaceContacts',0)>0 for r in peers['rows'])
    inspection=take('government-xl-inone-five-final-private-export-inspection-v1-20261025','ROOT-EXPORT-INSPECTION.json');assert inspection['reviewer']=='ROOT'and inspection['visualAcceptance']
    images=inspection['imagesActuallyViewed'];assert len(images)==20 and {(i['uid'],i['width'],i['time'])for i in images}=={(u,w,t)for u in sources for w in [390,1280]for t in ['15:00','22:00']}
    reports=[]
    for width in [1280,390]:
        name=f'{width}/staged-browser.json';report=take(BROWSER,name);assert report['passed']and not report['errors']and report['retainedNativeOwnViews']==[]
        views=[v for v in report['views']if 'time'in v];assert len(views)==10
        for v in views:
            assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']
            assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']]and not v.get('suppressed',{})and not v['retained']
            path=BASE/BROWSER/str(width)/v['file'];image=next(i for i in images if i['path']==str(path.relative_to(ROOT)))
            assert (image['uid'],image['width'],image['time'])==(v['uid'],width,v['time'])and digest(path.read_bytes())==image['sha256']==pins[BROWSER][image['path']];refs.append(path)
        assert report['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==sources and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
        if width==390:
            failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==5 and {v['uid']for v in failed if v['fallbackRetained']}==set(sources)
        p=BASE/BROWSER/name;reports.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    catalogue=take(BROWSER,'catalogue.json',True);assert verify_support_scope(catalogue['models'],sources,SUPPORTS)
    assert all(m['proceduralWindows']is False and not m.get('suppressesBuildingUids')for m in catalogue['models'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==identity['currentManifest']['sha256'];refs.append(manifest)
    resources={('building:'if u.startswith('landsd/')else'source-form:')+u for u in obligations}|{'terrain:city/data/terrain.json'}
    observations=[
      'Approve only these five immutable government originals/current forms, fixed1x/sourcepose/72571faces, with four exact tower-to-original-podium dependencies. Two towers pass every strict contact; the two remaining single embedded rim witnesses have exact finite original-edge paths in all4streams. Raw strict failures remain. No BASICproxy or unrelated native supplies support.',
      'Final512face derived terrain retains445earlier triangles and adds67boundedFloat32seam covers. Every sourceface has exact drawn-ground projection coverage; all upward source surfaces pass unchanged-.5m clearance. Only36podium wallfaces have negative actual-ground witnesses and every one has its exact clear-cap path in all4streams. Accept those original wall toes as authored terrain/platform architecture, not buried floors or an all-wall exemption. Full39formneighbours pass and no existing native/terrain overlaps are omitted.',
      'The complete34pair BASIC-contact diagnostic and10exact external contact actors are retained. Seven actors share recorded station parentway449304998;143008is a small separately recorded low station-side structure with contacts only16.0..16.278mHKPD. The remaining277973podium/277974clubhouse belong to the adjacent development platform. Their independently recovered unchanged government originals also have positive exact authored interfaces with277890in all4streams. Thus zero cross-source interpenetration is not an appropriate new engineering requirement for this multi-level station/development assembly. Accept these exact measured station/platform interfaces; retain all neighbouring actors without suppression, ownership reassignment or source clipping. Coarse neighbouring BASIC volumes are an acknowledged incremental-viewer limitation, not evidence of source corruption.',
      'The independent identity review binds exact owned roots/currentobject-CSUIDroutes/wholeGeoRefcells and complete two permit families; raw32.8103mextended-podium/other-form spatial failures remain. ROOT inspected complete original plan/perspectives, MTR operator photo and official station/site32.20mPDplans. These establish bounded site/source-role context, not cadastral precision or a blanket common-owner claim.',
      *inspection['observations'],
      'Private source/physical/browser qualification only. Guarded publication, fresh live device exports, all6931oldassets/catalogueentries/full521sourcekeyledger/globalBASICreadback remain mandatory before installation credit.'
    ]
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,supportByUid=SUPPORTS,supportEvidence=support_records,reviewer='ROOT',currentManifest=identity['currentManifest'],identityAccepted=True,identityProof=identity['identityProof'],identityProofByUid=identity['identityProofByUid'],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,stagedInspection=inspection,retainedNativeUids=[],leaseResources=sorted(resources),totalNeighbourForms=50,terrainAffectedForms=39,supersedesReviewLeaseScope='government-xl-inone-five-original-source-review-v1-20261025',sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publication=False,originalSourceReviewAccepted=True,completeModelGeometryUnchanged=True,foreignContactRoleEvidence=context,originalAdjacentInterfaceEvidence=peers,observations=observations)
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_supported_catalogue_scope_v1_20261024.py'])
    module('inone_source_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-five-original-inone-source-physical-inspected-browser-review',refs,result)
if __name__=='__main__':main()
