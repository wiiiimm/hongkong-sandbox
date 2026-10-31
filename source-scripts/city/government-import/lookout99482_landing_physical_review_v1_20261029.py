"""Compose exact current Lookout identity, terrain and source-contact evidence."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from lookout99482_landing_source_role_account_v1_20261029 import UID,SOURCE,TERRAIN,P
BATCH=P+'landing-physical-review-v1-20261029'


def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def doc(suffix,name='summary.json'):
        batch=P+suffix+'-v1-20261029';return take(batch,base/batch/name)
    runtime=P+'landing-runtime-v1-20261029';sel=take(runtime,base/runtime/'selection.json.gz');assert len(sel['rows'])==1;source=sel['rows'][0]
    assert source['uid']==UID and source['sourceSHA256']==SOURCE and source['triangles']==25564
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SOURCE;refs.append(asset)
    tile=ROOT/'3d-viewer'/source['source']['tile'];building=next(b for b in read(tile)['buildings']if b['uid']==UID)
    assert building==source['source']['building'] and digest(tile.read_bytes())==source['source']['tileSHA256'];refs.append(tile)
    identity_batch='government-xl-runtime-fit-99482-reviewed-feature-scope-v1-20261022'
    identity=take(identity_batch,base/identity_batch/'ROOT-SOURCE-IDENTITY-DECISION.json')
    assert identity['sourceIdentityInterpretationApproved'] and identity['uid']==UID and identity['sourceSHA256']==SOURCE
    form_sha=digest(json.dumps(building,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode())
    assert identity['sourceFormSHA256']==form_sha
    scope=take(identity_batch,base/identity_batch/'prepared-scope.json')
    data=ROOT/'3d-viewer/city/official-model-reviewed-original-feature-data.js';registry=json.loads(data.read_text().split('Object.freeze(',1)[1].rsplit(');',1)[0]);key='reviewed-original-feature:'+UID
    assert registry[key]==scope and source['candidate']['entry']['footprintScope']==key;refs.append(data)
    role=doc('landing-source-role-account','ROOT-SOURCE-CONTACT-ROLE-ACCOUNT.json')
    assert role['sourceSpecificContactRoleAccounted'] and role['sourceSHA256']==SOURCE and role['terrainCandidateSHA256']==TERRAIN and len(role['rows'])==4
    assert next(r for r in role['rows']if r['mode']=='original')['sourceWorldSHA256']==identity['worldTrianglesSHA256']
    foundation=doc('landing-foundations');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
    patch=doc('landing-inset');assert patch['status']=='private-terrain-validator-passed'and patch['candidate']['sha256']==TERRAIN
    candidate=ROOT/patch['candidate']['path'];assert digest(candidate.read_bytes())==TERRAIN;refs.append(candidate)
    terrain_scope=doc('landing-scope','scope.json');assert terrain_scope['currentNativeActors']==7014 and not terrain_scope['touchingNativeUids']and terrain_scope['positiveAreaTerrainOverlaps']==0
    neighbours=doc('landing-neighbours');assert neighbours['forms']==terrain_scope['intersectingForms']==3 and not neighbours['basicFlags']and neighbours['requiredNativeUids']==neighbours['nativeResolved']==[]
    full=doc('full-model-scope');assert full['rows'][0]['currentNativeActorsChecked']==7014 and full['rows'][0]['nearbyNativeActors']==[]
    for path,sha in full['currentFormTileHashes'].items():
        q=ROOT/path;assert digest(q.read_bytes())==sha;refs.append(q)
    foreign=doc('foreign-contacts');assert foreign['foreignPairs']==1 and not foreign['independentlyMeasuredOverlappingNativePairs']
    for pair in foreign['rows']:
        assert pair['uid']==UID and pair['foreignUid']=='landsd/322621:0'and len(pair['modes'])==5
        assert all(r['allFiniteContactPairs']==r['positiveContactPairs']==0 for r in pair['modes'])
    metrics=take(runtime,base/runtime/'metrics.json');metric=metrics['rows'][0]
    assert metric['uid']==UID and metric['sourceSHA256']==SOURCE and metric['sourcePreserved']and metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004
    assert metric['lowRimChecks']>0 and metric['minLowGap']<=.1 and metric['maxLowGap']<=1
    for profile in metrics['profiles'].values():
        assert all(metric['budget'][k]<=profile[k]for k in ['triangles','geometryBytes','residentBytes','drawCalls'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==sel['manifestSHA256']==full['currentManifestSHA256'];refs.append(manifest)
    current=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;current.extend(read(path)['models']);refs.append(path)
    assert len(current)==len({r['uid']for r in current})==7014 and UID not in {r['uid']for r in current}
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SOURCE},identityProof=proof,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=msha),currentManifestSHA256=msha,currentNativeActors=7014,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,identityAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=3,sourceContactRoleAccount=role,retainedNativeRegression=dict(requiredNativeUids=[],nativeResolved=[],nativeRows=[]),nativeSupportByUid={},supportByUid={},retainedNativeUids=[],retainedCurrentBasicSupportUids=[],terrainCandidateSHA256=TERRAIN,sourceGeometryChanges=0,sourcePoseChanges=0,rawCanonicalFailuresPreserved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=False,installationApproved=False,publication=False,reviewer='Codex ROOT',basis=[
        'Reuse only the prior exact-source identity/feature-extent interpretation after proving identical current source form, complete original world SHA, byte revision and production footprint-scope record. Historical ObjectID/source route is retained; live OBJECTID renumbering is not a new identity assignment.',
        'Final landing terrain passes unchanged construction and four-world foundation policy. The bounded post-role account preserves every raw43 canonical failure and the sole tiny provider-buried underside; no general clearance or geometry change.',
        'The whole original feature was scoped against all7014installed actors, finding no native contact candidates. Three forms in the complete changed terrain domain pass regressions. The only extra foreign BASIC feature322621 has no finite source-surface contacts in before and all4original streams; its1.622m2raw projected overlap remains and it is neither suppressed nor relabelled.',
        'The unchanged25564face original passes both mobile and desktop per-model triangle/geometry/resident/draw-call budgets. Full-scene real browser appearance, picking/collision/failure/retry and publication remain mandatory separate gates.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'summary.json',result)
    refs.extend([HERE/'lookout99482_landing_source_role_account_v1_20261029.py'])
    module('lookout_landing_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-lookout-original-identity-physical-runtime-composition',list(dict.fromkeys(refs)),result)
    print(dict(batch=BATCH,identityAccepted=True,physicalEvidenceAccepted=True,installationApproved=False),flush=True)

if __name__=='__main__':main()
