"""Bind a private seven-original / three BASIC continuation / canopy fixture."""
import copy,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
BATCH=PREFIX+'source-bound-full-scene-fixture-v1-20261029'
PREVIEW=PREFIX+'seven-upward-floor-private-preview-v1-20261029'
SCOPE=PREFIX+'seven-upward-floor-scope-v1-20261029'
PATCH=PREFIX+'seven-upward-floor-terrain-return-v1-20261029'
PROPOSAL=PREFIX+'three-basic-ground-proposals-v2-20261029'


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists()
    forms=read(BASE/SCOPE/'form-obligations.json.gz')
    resources=sorted({'building:'+b['uid']for b in forms}|{'terrain:city/data/terrain.json'})
    if not a.owned:
        assert not local.exists()
        claim=reservations.claim('sha-tin-private-full-scene-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=1800);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)<=set(lease['resources'])
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    assert forms==take(SCOPE,'form-obligations.json.gz')and len(forms)==70
    scope=take(SCOPE,'scope.json');assert len(scope['uids'])==7 and not scope['touchingNativeUids']
    take(PREVIEW,'summary.json')
    oldstage=HERE/'local'/PREVIEW
    catpath=oldstage/'catalogue.json';formpath=oldstage/'source-forms.json'
    for path in [catpath,formpath]:assert digest(path.read_bytes())==pins[PREVIEW][str(path.relative_to(ROOT))];refs.append(path)
    cat=copy.deepcopy(read(catpath));source_forms=read(formpath);uids=sorted(scope['uids'])
    assert sorted(e['uid']for e in cat['models'])==uids
    replacement=take(PREFIX+'canopy-conditional-replacement-review-v1-20261029','summary.json')
    assert replacement['conditionalReplacementDecisionApproved']and replacement['basicUid']=='landsd/92340:0'and replacement['sourceUid']=='landsd/231013:0'
    for e in cat['models']:
        assert not e.get('supportDependencies')and not e.get('activationGroup')and not e.get('suppressesBuildingUids')
        assert not e['publicationApproved']and not e['placementReviewed']and e.get('verticalPlacementOffsetHKPD',0)==0
        # Availability group only: no invented physical support relationship.
        e['activationGroup']=uids
        if e['uid']==replacement['sourceUid']:
            assert e['sha256']==replacement['sourceSHA256'];e['suppressesBuildingUids']=replacement['proposedSuppression']['suppressesBuildingUids'];assert e['suppressesBuildingUids']==['landsd/92340:0']
        asset=oldstage/e['asset'];assert digest(asset.read_bytes())==e['sha256'];dest=local/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());refs.extend([asset,dest])
    save(local/'catalogue.json',cat);save(local/'source-forms.json',source_forms)
    patch=take(PATCH,'summary.json');candidate=ROOT/patch['candidate']['path'];assert digest(candidate.read_bytes())==patch['candidate']['sha256']==pins[PATCH][str(candidate.relative_to(ROOT))];refs.append(candidate)
    proposal=take(PROPOSAL,'summary.json')
    proof=take(PREFIX+'three-basic-geometry-preservation-v1-20261029','summary.json');assert len(proof['rows'])==3 and all(r['allOriginalAttributesPreserved']and r['nativeGeometryAttributesUnchanged']for r in proof['rows'])
    take(PREFIX+'three-basic-continuation-foreign-volume-v1-20261029','summary.json')
    canopy=take(PREFIX+'canopy-post-foundation-v1-20261029','proposal.json');assert canopy['uid']==replacement['basicUid']and canopy['foundationBase']==replacement['proposedBasicFallbackFoundationBase']
    changes=[]
    for r in proposal['rows']:
        assert r['originalBuilding']in forms and r['proposedBuilding']==dict(r['originalBuilding'],nativeFallbackGround=r['hint'])
        assert r['hint']['terrainSHA256']==patch['candidate']['sha256']
        changes.append(dict(uid=r['uid'],before=r['originalBuilding'],after=r['proposedBuilding'],hint=r['hint'],role='source-bound-basic-continuation',proposalApproved=False))
    b=replacement['exactBasicForm'];assert b in forms
    changes.append(dict(uid=b['uid'],before=b,after=dict(b,foundationBase=canopy['foundationBase']),foundationBase=canopy['foundationBase'],role='existing-estimated-open-canopy',proposalApproved=False))
    by_tile={}
    for change in changes:
        tile=ROOT/'3d-viewer/city/data/tiles'/(change['before']['tile']+'.json')
        assert digest(tile.read_bytes())==pins[SCOPE][str(tile.relative_to(ROOT))];refs.append(tile)
        by_tile.setdefault(tile,[]).append(change)
    overlays=[]
    for tile,rows in by_tile.items():
        after=copy.deepcopy(read(tile))
        for change in rows:
            idx=next(i for i,b in enumerate(after['buildings'])if b['uid']==change['uid']);assert after['buildings'][idx]==change['before'];after['buildings'][idx]=change['after']
        target=local/('private-source-bound-'+tile.name);save(target,after);refs.append(target)
        overlays.append(dict(url=str(tile.relative_to(ROOT/'3d-viewer')),beforeSHA256=digest(tile.read_bytes()),source=str(target.relative_to(ROOT)),afterSHA256=digest(target.read_bytes()),changes=rows))
    original=ROOT/'3d-viewer/city/building-geometry.js';wrapper=ROOT/'3d-viewer/city/source-bound-basic-geometry-private.js';shadow=local/'private-building-geometry.js'
    text=wrapper.read_text().replace("from './building-geometry.js';","from './building-geometry-original-private.js';")+"\nexport {prepareModelGeometry,isOpenSidedBuilding} from './building-geometry-original-private.js';\n";shadow.write_text(text);refs.extend([original,wrapper,shadow])
    config=dict(diagnosticOnly=True,publication=False,stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(candidate.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=patch['candidate']['sha256'],resolution=5,area='Private source-bound BASIC fallback experiment')],privateSourceBoundTileOverlays=overlays,privateBasicGeometryModule=dict(url='city/building-geometry.js',originalAlias='city/building-geometry-original-private.js',source=str(shadow.relative_to(ROOT)),sha256=digest(shadow.read_bytes()),originalSHA256=digest(original.read_bytes()),wrapperSHA256=digest(wrapper.read_bytes())),viewerURL='http://127.0.0.1:4177/city.html',browserUids=uids,additionalRetainedUids=[],retainedBuildingUids=['landsd/235892:0','landsd/236080:0','landsd/24712:0','landsd/257099:0'],jointUids=uids,fitJointCamera=True,fitJointCameraMobile=True,fitBox=True,failureTestUids=[],captureDirectionByModel={uid:[1,2,-1]for uid in uids})
    save(local/'config.json',config)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[SCOPE][str(manifest.relative_to(ROOT))];refs.append(manifest)
    tool=HERE/'ronsdale_three_live_browser_v20_20261029.mjs';old=HERE/'ronsdale_three_live_browser_v19_20261028.mjs';addition="\n await (await import('./private_source_bound_browser_routes_v1_20261029.mjs')).bindPrivateSourceBoundRoutes(page,config,root,mode,report);"
    assert tool.read_text().replace(addition,'')==old.read_text();refs.extend([tool,old,HERE/'private_source_bound_browser_routes_v1_20261029.mjs',local/'catalogue.json',local/'source-forms.json',local/'config.json'])
    save(out/'fixture-inputs.json',dict(configPath=str((local/'config.json').relative_to(ROOT)),resources=resources,uids=uids,currentManifestSHA256=digest(manifest.read_bytes()),diagnosticOnly=True,publication=False))
    result=dict(uids=uids,privateProposalOnly=True,originalModels=7,basicContinuations=3,estimatedCanopyPostBottoms=1,conditionalCanopySuppression=['landsd/92340:0'],activationGroup=uids,physicalSupportRelationshipsInvented=0,productionFilesWritten=0,failureTestsDeliberatelyDeferred=True,physicalAcceptance=False,collisionReviewApproved=False,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Private exact-input fixture: seven immutable originals, one validated terrain, three private illustrative BASIC lower continuations, one post-bottom-only canopy fallback proposal and conditional duplicate canopy suppression. Source and survey fields unchanged. Common activation is conservative availability metadata, not physical support. Every original V19 assertion remains; V20 adds only guarded private route setup. Browser, physical, interface and publication acceptance remain pending.')
    save(out/'summary.json',result);assert reservations.owns(lease)
    module('sha_tin_private_fixture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-seven-original-source-bound-basic-and-conditional-canopy-fixture',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
