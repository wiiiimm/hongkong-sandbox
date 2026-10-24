"""Bind the exact six original terminus parts and their bounded physical interpretation."""
from pathlib import Path
import numpy as np
import copy,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';p='government-xl-next-repairs-west-kowloon-bus-';batch=p+'six-physical-review-v2-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(s,f='summary.json',local=False):
        n=p+s
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=(HERE/'local'/n if local else base/n)/f;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take('six-original-runtime-v2-20261024','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==6 and sum(r['triangles']for r in selection['rows'])==18310
    geom={r['uid']:r for r in take('six-original-runtime-v2-20261024','runtime-geometry.json.gz',True)['rows']};oldgeom={r['uid']:r for r in take('five-original-runtime-v1-20261024','runtime-geometry.json.gz',True)['rows']}
    attrs={r['uid']:r for r in take('six-original-attributes-v1-20261024','attributes.json.gz')['rows']};oldattrs={r['uid']:r for r in take('five-original-attributes-v1-20261024','attributes.json.gz')['rows']};equivalence=[]
    for uid,g in oldgeom.items():
        assert sources[uid]==g['sourceSHA256']==geom[uid]['sourceSHA256'];fields=['position','index','drawnGroundGeometry'];assert all(np.array_equal(np.asarray(g[k]),np.asarray(geom[uid][k]))for k in fields)
        for k in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert np.array_equal(np.asarray(attrs[uid][k]),np.asarray(oldattrs[uid][k]))
        equivalence.append(dict(uid=uid,completeActualSourceAndGroundIdentical=True,allFourIndexedCoordinateStreamsIdentical=True))
    protected=take('protected-return-runtime-v1-20261024','runtime-geometry.json.gz',True)['rows'][0];assert all(np.array_equal(np.asarray(protected[k]),np.asarray(geom['landsd/255415:0'][k]))for k in ['position','index','drawnGroundGeometry'])
    foundation=[]
    for number in ['255415','231056','261098','267223','267327','37934']:
        name=('six-foundation'if number=='37934'else'five-foundation')+number+'-v1-20261024';rows=take(name)['rows'];assert len(rows)==4 and all(r['completeTerrainTriangles']==r['triangles']and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in rows);foundation.extend(rows)
    mainlow=take('protected-return-low-faces-v1-20261024');assert all(len(r['exactAffectedFaces'])==527 and r['allAffectedWallLike']for r in mainlow['rows']);assert take('complete-ground-cap-paths-v2-20261024')['allFourCompleteGroundClearCapPaths']
    for number,count in [('261098',8),('267327',16),('37934',8)]:
        low=take('shaft'+number+'-low-faces-v1-20261024');assert all(len(r['exactAffectedFaces'])==count and r['allAffectedWallLike']and r['allAffectedHaveExposedHighestVertex']for r in low['rows']);assert take('shaft'+number+'-cap-paths-v1-20261024')['allFourCompleteGroundClearCapPaths']
    rawsupport=[]
    for number,count in [('231056',57),('267223',2)]:
        q=take('roof'+number+'-support-v1-20261024');path=take('roof'+number+'-contact-paths-v1-20261024');assert len(path['rows'])==4 and all(r['targets']==r['verifiedPaths']==count and r['remaining']==0 and not r['strictInterfacePassed']for r in path['rows']);rawsupport.append(q)
    embedding=take('internal-roof-embedding-v1-20261024');assert embedding['actualTerrainNegativeHalfMetreSamples']==0;assert all(r['negativeHalfMetreSourceFaces']==r['verticalFaces']and r['otherRenderableFaces']==r['nonrenderingFaces']==0 for r in embedding['rows'])
    jointviews=take('roof-interface-views-v1-20261024');assert all(r['allIncidentHaveUpwardOriginalPath']for r in jointviews['rows'])
    identity={};rawpolicy=[];fresh_identity=[];metrics=take('six-original-runtime-v2-20261024','metrics.json');policy=module('west_six_raw_policy',HERE/'acceptance-policy.py')
    for row in selection['rows']:
        uid=row['uid'];raw=take('six-original-identity-v1-20261024',uid.split('/')[1]+'/identity.json');assert raw['sourceSHA256']==sources[uid]
        if uid=='landsd/37934:0':
            reviewed=take('37934-identity-review-v1-20261024','37934:0-review.json');assert reviewed['identityOnlyApproved']and reviewed['requiredUnchangedAssemblySources']==sources;proof=reviewed['identityProof']
        else:assert raw['passed']and not raw['reasons'];proof=raw['proof']
        assert all(proof[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']);identity[uid]=proof
        metric=copy.deepcopy(next(r for r in metrics['rows']if r['uid']==uid))
        if not metric['identity']:
            assert uid=='landsd/37934:0'
            g=geom[uid];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));f=row['source']['building'];target=shapely.Polygon(f['rings'][0],f['rings'][1:]);metric['identity']=dict(overlap=projection.intersection(target).area/min(projection.area,target.area),centroidDistance=projection.centroid.distance(target.centroid));fresh_identity.append(dict(uid=uid,rawCachedMetricIdentity={},computedCompleteActualProjectionIdentity=metric['identity'],qualification='Fresh full actual source projection measurement for the empty cached proxy; exact named identity review remains independently required. No fabricated identity values or change to the frozen raw metric.'))
        reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=proof),metric,metrics['profiles']['mobile']);assert set(reasons)<={'terrain-intersects-source-over-0.5m','ground-contact-unresolved'},(uid,reasons);rawpolicy.append(dict(uid=uid,reasons=reasons))
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sources[uid];refs.append(asset)
    scope=take('six-original-scope-v1-20261024');assert len(scope['rows'])==6 and all(r['currentNativeActorsChecked']==6864 and not r['nearbyNativeActors']for r in scope['rows']);forms={}
    for r in scope['rows']:
        for form in take('six-original-scope-v1-20261024',r['uid'].split('/')[1]+'-forms.json.gz'):forms[form['building']['uid']]=form['building']
    foreign=take('six-original-foreign-v1-20261024');external=[r for r in foreign['rows']if r['foreignUid']not in sources];positive=[r for r in external if any(m['positiveContactPairs']or m['projectedOverlapAreaM2']for m in r['modes']if m['mode']!='before-basic')];assert len(positive)==1 and positive[0]['uid']=='landsd/255415:0'and positive[0]['foreignUid']=='landsd/292042:0'
    prism=take('292042-existing-prism-context-v1-20261024');assert len(prism['rows'])==4 and all(r['allPositiveProjectionWithinOldPrism']and r['sourceFaces']==[5223,6292]for r in prism['rows'])
    assert len(take('five-original-exact-contacts-v1-20261024')['rows'])==10 and len(take('six-new-original-pairs-v1-20261024')['rows'])==5
    neighbour=take('protected-return-neighbours-v1-20261024');assert not neighbour['flagged'];patch=take('protected-return-inset-v1-20261024');assert patch['status']=='private-terrain-validator-passed'
    images=[]
    for name,files in [('wall-source-views-v2-20261024',['wall-690.png','wall-6953.png','wall-14955.png','wall-15064.png','wall-15253.png','wall-15363.png']),('roof-interface-views-v1-20261024',['231056.png','267223.png']),('shaft261098-wall-views-v1-20261024',['wall-22.png']),('shaft267327-wall-views-v1-20261024',['wall-6.png']),('shaft37934-wall-views-v2-20261024',['wall-4.png']),('six-original-plots-v1-20261024',['complete-original-assembly.png','base-only-diagnostic.png']),('foreign-contact-views-v1-20261024',['292042:0.png'])]:
        take(name)
        for f in files:
            n=p+name;path=base/n/f;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    review=dict(uids=list(sources),reviewer='ROOT',sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=len(forms),terrainChangedNeighbourForms=6,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),identityProof={k:all(v[k]for v in identity.values())for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},identityProofByUid=identity,leaseResources=sorted({'building:'+u for u in forms}|{'terrain:city/data/terrain.json'}),supportByUid={'landsd/231056:0':'landsd/255415:0','landsd/267223:0':'landsd/255415:0'},imagesActuallyViewed=images,rawPolicyReasons=rawpolicy,rawCanonicalFailuresPreserved=True,rawStrictSupportPassed=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=False,installationApproved=False,publication=False,basis=[
        'Accept these exact six unchanged government meshes together as the original terminus deck, two raised roofs and three narrow shafts. Every source face has actual ground coverage and no entire/upward face is buried in all four coordinate representations. Five prior mathematical proof inputs are independently identical to the fresh six-source actual arrays and ground; the new shaft has separate current proofs.',
        'The527main and8/16/8shaft clearance negatives are lower wall/pier surfaces cut by coarse current grade. Complete finite all-ground proofs retain only walllike negatives, with original paths to ordinary-clear upper caps in every world. ROOT inspected the representative main warnings and full lower-shaft diagrams: upper bodies remain visible. No walking/roof surface is admitted below grade and no wholly buried source face is excused. Not every main wall was separately rendered; numeric proof covers all527. Orange overlays obscure some red wall colouring; the independent finite evidence remains authoritative.',
        'The two original roofs have59raw low-rim failures against the highest-own-podium envelope. All59connect by finite original-surface paths to positive-dimensional original podium contacts in all four representations under unchanged endpoint ceilings. Roof231056 lower vertical valance is partly embedded in the original parapet; all56below-half-metre source faces are vertical and clear actual terrain by over6.6m. Fourtinyverticalfaces lie wholly below that own-podium envelope, never actual ground. Roof267223 has two shallow sloping corner joints. ROOT inspected both complete interface views. These exact source-authored visual joints are accepted without claiming strict-interface success, a new structural root or a global embedding allowance.',
        'Original37934 has five finite line contacts with the deck and43with roof231056, including four shared-plane areas; these are retained source joints inside the coinstalled terminus assembly. Its full continuous shaft clears complete actual-ground/foundation obligations, and the bounded exact identity review requires all six source hashes together. Current recorded basic heights remain14.7/20.4; original geometry remains at5.558317..20.4m without translation.',
        'All6864current native bounds are separate. Every scoped non-peer basic is free of positive contacts/area except292042. Its four boundary traces on sourcefaces5223/6292remain within the exact old closed BASIC prism, including strict old floor/roof height bounds; exact rational full projection subtraction proves the measured intrusion occupies previously occupied source space. Accept this retained existing boundary relationship only for these source/current hashes; no size waiver, new ownership claim, suppression or arbitrary collision exemption.',
        'The protected local original-TIN return passes existing final terrain/coast/coverage guards and all six changed-domain neighbour checks. The complete whole-source scope and finite foreign checks cover eleven unique current forms. No unrelated model, existing retained support, original vertex, scale or pose is changed. Staged/live desktop/mobile day/night appearance, picking/collision, failure/retry and guarded publication/readback remain mandatory.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',review);save(out/'exact-input-equivalence.json',equivalence);save(out/'raw-support-negatives.json',rawsupport);save(out/'fresh-empty-proxy-identity.json',fresh_identity);refs.append(HERE/'acceptance-policy.py');module('west_six_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-six-original-terminus-visual-assembly-physical-interpretation',refs,dict(uids=list(sources),sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,installationApproved=False,sourceGeometryChanges=0))

if __name__=='__main__':main()
