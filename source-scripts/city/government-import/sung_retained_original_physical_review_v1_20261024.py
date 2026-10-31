"""Bind current exact-original Sung/Lee/Nam evidence and one support-only update."""
from pathlib import Path
from copy import deepcopy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-';batch=prefix+'sung-retained-physical-review-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(s,f='summary.json',local=False):
        name=prefix+s
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=(HERE/'local'/name if local else base/name)/f;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take('sung-three-retained-runtime-v1-20261024','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==3 and sum(r['triangles']for r in selection['rows'])==15144
    geom={r['uid']:r for r in take('sung-three-retained-runtime-v1-20261024','runtime-geometry.json.gz',True)['rows']}
    four=take('sung-four-retained-runtime-v1-20261024','selection.json.gz');fourrows={r['uid']:r for r in four['rows']};fourgeom={r['uid']:r for r in take('sung-four-retained-runtime-v1-20261024','runtime-geometry.json.gz',True)['rows']}
    attrs={r['uid']:r for r in take('sung-four-retained-attributes-v1-20261024','attributes.json.gz')['rows']}
    for uid in sources:
        assert all(np.array_equal(np.asarray(geom[uid][k]),np.asarray(fourgeom[uid][k]))for k in ['position','index','drawnGroundGeometry'])
    foundations=[]
    for token in ['79098','45779','47160']:
        rows=take('sung-retained-'+token+'-foundations-v1-20261024')['rows'];assert len(rows)==4 and all(r['completeTerrainTriangles']==r['triangles']and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in rows);foundations.extend(rows)
    for token,count,lowname,capname in [('79098',138,'sung-retained-79098-low-faces-v1-20261024','sung-retained-79098-cap-paths-v1-20261024'),('45779',171,'sung-podium-retained-low-faces-v1-20261024','sung-podium-retained-cap-paths-v1-20261024')]:
        low=take(lowname);cap=take(capname);assert all(len(r['exactAffectedFaces'])==count and r['allAffectedWallLike']and r['allAffectedHaveExposedHighestVertex']for r in low['rows']);assert cap['allFourCompleteGroundClearCapPaths']
        ground=np.asarray(geom['landsd/'+token+':0']['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
        assert all(r['completeDrawnGroundSHA256']==digest(ground.tobytes())for r in cap['rows'])
    assert all(not r['exactAffectedFaces']for r in take('sung-retained-47160-low-faces-v1-20261024')['rows'])
    compound=[];strict=[]
    for token in ['79098','47160','79099']:
        pair=take('sung-retained-'+token+'-podium-support-v1-20261024');assert len(pair['rows'])==4 and all(r['compoundFoundation']['completeTerrainTriangles']==r['compoundFoundation']['triangles']and r['compoundFoundation']['fullyBuriedTriangles']==r['compoundFoundation']['fullyBuriedUpwardTriangles']==0 for r in pair['rows']);strict.append(pair)
        context=take('sung-retained-'+token+'-compound-clearance-v1-20261024');assert len(context['rows'])==4 and all(r['compoundCapPathsPassed']and r['allAffectedWallLike']and not r['negativeNonWallFaces']for r in context['rows']);compound.append(context)
        take('sung-retained-'+token+'-podium-envelope-v1-20261024')
    for token,count in [('47160',58),('79099',70)]:
        paths=take('sung-retained-'+token+'-podium-contact-paths-v1-20261024');assert len(paths['rows'])==4 and all(r['targets']==r['verifiedPaths']==count and r['remaining']==0 and not r['strictInterfacePassed']for r in paths['rows'])
    rim=take('sung-lee-nam-proposed-native-rims-v2-20261024');assert rim['allFourActorFractionsPass']and rim['originalRuntimeVertexIndexWeightingPreserved']and len(rim['rows'])==8
    assert all(r['supportFraction']==1 for r in rim['rows']if r['uid']=='landsd/79099:0')
    identity={};raw_identity={}
    bounded=take('sung-fung-podium-identity-review-v2-20261024','45779:0-review.json');assert bounded['identityOnlyApproved']and bounded['requiredUnchangedAssemblySources']==sources
    for row in selection['rows']:
        uid=row['uid'];proof=take('sung-three-retained-current-identity-v1-20261024',uid.split('/')[1]+'/identity.json');raw_identity[uid]=proof
        if uid=='landsd/45779:0':
            assert set(proof['reasons'])==set(bounded['rawReasonsRetained']);assert proof['sourceFormSHA256']==bounded['sourceFormSHA256']and proof['worldTrianglesSHA256']==bounded['worldTrianglesSHA256'];identity[uid]=bounded['identityProof']
        else:assert proof['passed']and not proof['reasons'];identity[uid]=proof['proof']
        assert all(identity[uid][k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    foreign=take('sung-retained-current-basic-contacts-v1-20261024');external=[r for r in foreign['rows']if r['foreignUid']not in sources];assert len(external)==5 and all(not m['positiveContactPairs']and not m['projectedOverlapAreaM2']for r in external for m in r['modes']if m['mode']!='before-basic')
    nativecontacts=take('sung-retained-current-native-contacts-v1-20261024');assert len(nativecontacts['rows'])==1
    pair=nativecontacts['rows'][0];assert pair['uid']=='landsd/45779:0'and pair['nativeUid']=='landsd/79099:0'and all(not r['areaContactPairs']for r in pair['modes'])
    neighbour=take('sung-three-retained-native-neighbours-v1-20261024');assert neighbour['forms']==38 and not neighbour['basicFlags'];native=take('sung-three-retained-native-neighbours-v1-20261024','native-neighbour-checks.json');assert len(native['rows'])==5 and all(r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['rows'])
    scene=take('sung-three-complete-retained-scope-v1-20261024','scope.json');forms=take('sung-three-complete-retained-scope-v1-20261024','form-obligations.json.gz');assert len(forms)==38 and set(scene['uids'])==set(sources)
    patch=take('sung-podium-complete-retained-inset-v2-20261024');assert patch['status']=='private-terrain-validator-passed'and patch['terrainTriangles']==12324
    preserved=take('sung-podium-complete-retained-inset-v2-20261024','exact-retained-below-clamp.json');assert len(preserved['preservedExistingFaces'])==1 and preserved['everyFaceExactlyMatchesInstalledFloat32']and preserved['everyFaceOutsideEdit']and not preserved['globalValidatorChanged']
    mp=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert digest(mp.read_bytes())==selection['manifestSHA256']==four['manifestSHA256'];refs.extend([mp,pointer]);manifest=read(mp)
    # Build a private catalogue replacement that changes ONLY Nam's dependency.
    owner='landsd/79099:0';matches=[]
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;cat=read(path)
        for entry in cat['models']:
            if entry['uid']==owner:matches.append((url,path,cat,entry))
    assert len(matches)==1
    url,path,before,entry=matches[0];assert entry==fourrows[owner]['candidate']['entry']and entry['supportDependencies']==[dict(uid='landsd/45779:0',state='surveyed-footprint-fallback',csuid='3777116537P20060312')]
    asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.extend([path,asset])
    snapshot=read(pointer)['snapshotId']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,owner)).fetchone()==('installed-verified',entry['sha256'])
    after=deepcopy(before);newentry=next(m for m in after['models']if m['uid']==owner);newentry['supportDependencies']=[dict(uid='landsd/45779:0',state='installed',buildingCSUID='3777116537P20060312',sha256=sources['landsd/45779:0'])]
    assert {k:v for k,v in entry.items()if k!='supportDependencies'}=={k:v for k,v in newentry.items()if k!='supportDependencies'}
    for old,new in zip(before['models'],after['models']):assert old==new or old['uid']==new['uid']==owner
    afterpath=out/'nam-catalogue-after.json';save(afterpath,after)
    update=dict(ownerUid=owner,ownerSHA256=entry['sha256'],url=url,beforeSHA256=digest(path.read_bytes()),source=str(afterpath.relative_to(ROOT)),sha256=digest(afterpath.read_bytes()),beforeEntry=entry,afterEntry=newentry,changedFields=['supportDependencies'],sourceGeometryChanges=0,approvalScope='Private staged verification only; no production mutation yet')
    images=[];take('sung-four-retained-context-views-v1-20261024')
    for filename in ['complete-original-assembly.png','base-only-diagnostic.png']:
        name=prefix+'sung-four-retained-context-views-v1-20261024';imagepath=base/name/filename;assert digest(imagepath.read_bytes())==pins[name][str(imagepath.relative_to(ROOT))];refs.append(imagepath);images.append(dict(path=str(imagepath.relative_to(ROOT)),sha256=digest(imagepath.read_bytes())))
    resources={'building:'+f['uid']for f in forms}|{'terrain:city/data/terrain.json','terrain:'+patch['candidate']['replaces']['url']}
    review=dict(uids=list(sources),reviewer='ROOT',sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=38,retainedNativeUids=neighbour['requiredNativeUids'],currentManifest=dict(path=str(mp.relative_to(ROOT)),sha256=digest(mp.read_bytes())),identityProof={k:all(v[k]for v in identity.values())for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},identityProofByUid=identity,leaseResources=sorted(resources),supportByUid={'landsd/47160:0':'landsd/45779:0'},installedSupportUpdate=update,imagesActuallyViewed=images,rawStrictSupport= strict,rawCompoundClearance=compound,rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=False,installationApproved=False,publication=False,basis=[
        'Accept only these three unchanged original sources and the exact original-podium relationship to existing Nam. All complete sources have four-world actual-ground coverage and no wholly buried or upward-buried face. Ground negatives are138 Sung and171podium lower wall faces with exposed upper vertices and clear original cap paths; Lee has no negative actual-ground facet. The two partially intersecting public ramps are cleared by the authentic-TIN inset and explicit retained-terrain replacement, not a wall waiver.',
        'Full compound negative partitions against actual ground plus original podium contain only original wall-like facets, all with finite positive-contact paths to clear source caps in each world. Preserve raw compound minima about-15.888/-1.494/-12.742m and upper-vertex diagnostics that are false for some owned-envelope walls. These are original interleaved base/perimeter joints beneath their own elevated platform envelope, not admitted below-ground walking or roof surfaces. No whole/upward source face is excused.',
        'Preserve strict low-rim failures: Sung0/226 is ground-rooted and receives no invented podium support dependency; Lee116/174 and Nam137/207 retain58/70unresolved vertical probes. All58/70 have exact original-surface paths to positive podium contacts under unchanged endpoint-height/residual limits. The unchanged viewer vertex-weighted rim rule independently passes64percentLee/100percentNam in all4streams. Original positions, facets and all policy thresholds remain unchanged.',
        'All5unrelated basic source pairs have zero finite positive contacts and projected overlap in each world. Current source/native comparison includes complete original Nam, preserving375/397line-contact pairs with no area intersections and strict bounding separation for other nominations. Current terrain replacement has38whole-form checks and5full installed-native checks, all passing nonregression. Existing23459313whole/6upward negatives remain unchanged and are not newly approved.',
        'ROOT viewed both full four-source and26m display-only base plots. Original stepped platforms wrap complementary tower cut-outs; lower bodies are partly occluded by the original podium. Display clipping changes no asset. Treat original partial surface joints as authored visual assembly, without inventing per-component structural engineering gates or claiming every base wall independently visible.',
        'Only Nam supportDependencies may change, from the exact current surveyed fallback to this exact original podium UID/CSUID/SHA. Nam geometry, identity, approval flags and all other catalogue entries remain unchanged. This is a private staged proposal requiring source plus all5retained desktop/mobile views, picking/collision/failure/retry and later atomic publication/live/full-ledger readback before installation credit.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',review);save(out/'raw-identity.json',raw_identity);refs.append(afterpath)
    module('sung_retained_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-current-original-sung-lee-nam-physical-and-support-update-interpretation',list(dict.fromkeys(refs)),dict(uids=list(sources),sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,installationApproved=False,sourceGeometryChanges=0))


if __name__=='__main__':main()
