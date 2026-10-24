"""UNEXECUTED saved-hole/eligible-mask attribution, not a terrain constructor."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,uuid,subprocess,hashlib
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import polyu_five_current_parent_actual_production_capture_v2_20261014 as capture
import polyu_saved_hole_mask_attribution_v1_draft_20261014 as geometry
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround,enclosing_float
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
from polyu_five_saved_nomination_binding_v2_20261014 import resolve_partition

BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved-hole-mask-attribution-v2-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='8f204d9c83bc0cc6ca45bb56da6da2fb8b70255c5af6c7dd37f346f73aceae9e'
CURRENT=capture.CURRENT;ELIGIBLE=['landsd/63758:0','landsd/305626:0'];ref,check=capture.ref,capture.check
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def triangles(values):
    a=np.asarray(values,dtype='<f8').reshape(-1,3,3);assert np.isfinite(a).all();return a


def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
    receipt=read(capture.DOC/'result.json');assert receipt['jobId']==JOB
    inputs=read(capture.DOC/'input.json.gz');replay=read(capture.DOC/'actual-production-replay.json.gz')
    guards=read(capture.DOC/'all25-original-production-guard-site-replay.json.gz');actors=read(capture.DOC/'complete-fresh-current-native59527-and24-BASIC.json.gz')
    patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');nom=read(check(inputs['newNomination']))
    assert replay['currentManifestSHA256']==CURRENT and replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
    assert patch['nativeMesh']['position']==nom['newNativeMesh']['position']and patch['nativeMesh']['index']==nom['newNativeMesh']['index']
    assert len(patch['nativeMesh']['index'])//3==55305 and len(guards['rows'])==25 and len(actors['basicRows'])==24
    before=triangles(replay['before']['closedDomainDrawnTriplets']);after=triangles(replay['after']['closedDomainDrawnTriplets']);assert len(before)==40 and len(after)==55333
    assert [r['uid']for r in guards['rows']]==capture.prior.UIDS
    assert sum(bool(r['error'])for r in replay['allCandidateGridSamples'])==1 and len(replay['allSamplerErrors'])==3
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
    resources=sorted(['building:'+u for u in capture.prior.UIDS]+['terrain-patch:'+u for u in capture.prior.UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
    return pins,receipt,inputs,replay,guards,actors,patch,nom,before,after,resources


def schema_only():
    p,r,i,replay,g,a,patch,n,before,after,resources=load()
    return dict(passed=True,caller=ref(Path(__file__)),captureJob=JOB,completeNativeFacets=55305,completeBefore40After55333=True,
        eligibleCompleteGuardSamples={u:next(x['checks']for x in g['rows']if x['uid']==u)for u in ELIGIBLE},
        uniqueThrowingCoordinates=3,canonicalResources=resources,noGeometryCoverageSamplerDBLeaseMath=True)


def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
    pins,receipt,inputs,replay,guards,actors,patch,nom,before,after,resources=load();assert resources==lease['resources']
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    validation=read(check(prep['helperValidationRef']));assert validation['passedTests']==8 and validation['failedTests']==0 and validation['exitCode']==0
    assert validation['executedCodeRefs']==[ref(Path(geometry.__file__)),ref(HERE/'test_polyu_saved_hole_mask_attribution_v1_draft_20261014.py')]
    refs=pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[prep['helperValidationRef'],ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
    refs=distinct_refs(refs+receipt['evidenceRefs']);last=time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    def fence():
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT and reservations.owns(lease)
    fence();DOC.mkdir();mesh=patch['nativeMesh'];stored=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);pos=stored.astype('<f4').astype('<f8');ix=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3);raw=pos[ix]
    assert raw.tobytes()==stored[ix].tobytes(),'saved candidate already exact Float32; no silent coordinate change'
    drawn,winding=drawn_native_faces(mesh)
    # Native complete mesh is attributed using original sampler index order.
    # Exact drawn counterpart multiplicities are separately verified in full.
    from collections import Counter
    assert not (Counter(t.tobytes()for t in drawn)-Counter(t.tobytes()for t in after))
    indices={name:CompleteGround(value)for name,value in [('beforeDraw',before),('afterDraw',after),('candidateNativeSampler',raw)]}
    records=read(capture.nomination.DOC/'complete-five-mask-partition-diagnostic.json.gz')['allEligibleMaskOccurrences'];assert len(records)==5553
    ideal_masks=[[(F(p[0]),F(0),F(p[1]))for p in r['exactClosedProjection']]for r in records]
    old_triangles=[[(F(v[0]),F(v[1]),F(v[2]))for v in r['previousLineageVerbatim']['exactProposedPoints']]for r in nom['completeOldPrivateMapping']]
    def envelopes(polys):
        lower=[];upper=[]
        for poly in polys:
            lower.append([enclosing_float(min(v[k]for v in poly),True)for k in [0,2]])
            upper.append([enclosing_float(max(v[k]for v in poly),False)for k in [0,2]])
        return np.asarray(lower),np.asarray(upper)
    mask_bounds=envelopes(ideal_masks);old_bounds=envelopes(old_triangles)
    def candidates(xz,bounds):
        # Actual sites are unchanged binary64 values; enclosing ideal polygons
        # cannot exclude a genuine closed member at the recorded exact point.
        p=np.asarray(list(map(float,xz)));lo,hi=bounds
        return np.flatnonzero(np.all(hi>=p,1)&np.all(lo<=p,1)).tolist()
    parent_by_mask={}
    for parent in nom['completeCapturedParentMapping']:
        for hit in parent['completeExactMaskPartition']['inside']:parent_by_mask.setdefault(hit['mask'],[]).append((parent['capturedParentFacet'],hit))
    sites={}
    def add(x,z,context):
        key=(float(x).hex(),float(z).hex());sites.setdefault(key,dict(x=x,z=z,contexts=[]))['contexts'].append(context)
    for row in replay['allCandidateGridSamples']:
        if row['error']:add(row['x'],row['z'],dict(kind='saved-grid-error',verbatim=row))
    for row in guards['rows']:
        for sample in row['rows']:
            if sample['samplerError']or row['uid']in ELIGIBLE:add(sample['x'],sample['z'],dict(kind='saved-guard-site',uid=row['uid'],verbatim=sample,wholeGuardRowReasons=row['reasons']))
    outputs=[];forms={r['uid']:r['exactCurrentForm']for r in guards['rows']};basic={r['uid']:r for r in actors['basicRows']};basic_ground={}
    for uid in set(ELIGIBLE)|{r['uid']for r in replay['allSamplerErrors']}:
        b=basic[uid];idx=np.asarray(b['index'],dtype=np.int64).reshape(-1,3);basic_ground[uid]={}
        for mode,field in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:
            w=triangles(np.asarray(b[field],dtype='<f8').reshape(-1,3)[idx]);basic_ground[uid][mode]=(w,CompleteGround(w))
    for site in sites.values():
        xz=(F(site['x']),F(site['z']));mask_ids=[j for j in candidates(xz,mask_bounds)if geometry.convex_member(xz,ideal_masks[j])]
        ideal_parent=[]
        for mask_id in mask_ids:
            for parent_id,hit in parent_by_mask.get(mask_id,[]):
                if geometry.convex_member(xz,[(F(v[0]),F(v[1]),F(v[2]))for v in hit['polygon']]):ideal_parent.append(dict(capturedParentFacet=parent_id,mask=mask_id,maskLineage=records[mask_id],exactOwnPlanePolygon=hit['polygon']))
        ideal_old=[]
        for j in candidates(xz,old_bounds):
            old=nom['completeOldPrivateMapping'][j]
            for ordinal,poly in enumerate(old['completeExactMaskPartition']['outside']):
                if geometry.convex_member(xz,[(F(v[0]),F(v[1]),F(v[2]))for v in poly]):ideal_old.append(dict(oldPrivateFace=j,outsidePolygon=ordinal,previousLineageVerbatim=old['previousLineageVerbatim'],exactOwnPlanePolygon=poly))
        probes={name:geometry.probe(xz,index.ground,index,native_admission=name=='candidateNativeSampler')for name,index in indices.items()}
        for row in probes['candidateNativeSampler']['closedMembers']:
            p=nom['candidateFaceProvenance'][row['face']]
            row['candidateProvenanceWithoutRepeatedPartition']={k:v for k,v in p.items()if k!='partitionProof'}
            row['completeNominationReference']=inputs['newNomination']
            if p['kind']!='unchangedPreviousPrivateDraw':
                proof=resolve_partition(nom,p)
                row['resolvedCompletePartitionBinding']=dict(pointer=p.get('partitionProofReference'),inlinePrefixProofPreservedInNomination='partitionProof'in p,completeOwnPlanePartition=proof['completeOwnPlanePartition'])
        actor_context={}
        for uid in {q['uid']for q in site['contexts']if 'uid'in q}:
            actor_context[uid]=dict(rawGIS=geometry.raw_ring_location(xz,forms[uid]['rings']),constructorProjections={m:geometry.probe(xz,w,c)for m,(w,c)in basic_ground[uid].items()},currentSuppressionVerbatim=basic[uid]['currentSuppressedByNativeUIDs'])
        outputs.append(dict(**site,exactXZ=list(map(str,xz)),completeClosedMaskMembers=[dict(mask=j,lineage=records[j])for j in mask_ids],idealRestoredParentMembers=ideal_parent,idealSourceOutsideMembers=ideal_old,actualCompleteProjectionProbes=probes,actorContext=actor_context,noCauseOrRepairInferredAutomatically=True))
        if len(outputs)%16==0:print(json.dumps(dict(savedSitesCompleted=len(outputs),totalSavedSites=len(sites))),flush=True)
        pulse()
    save(DOC/'complete-saved-hole-and-eligible-guard-attribution.json.gz',dict(rows=outputs,completeEligibleGuardSamples={u:next(r['checks']for r in guards['rows']if r['uid']==u)for u in ELIGIBLE},complete3DistinctSamplerErrorCoordinatesPreserved=True,windingBinding=winding,all25GuardFailuresVerbatim=guards,realValidatorFailureVerbatim=read(capture.DOC/'real-validator-outcome.json'),noWholeOwnedNativeFiniteReplay=True,noSourceGeometryOrTerrainEdit=True,physicalAccepted=False))
    # Same existing validator GEOS measurement, not a new exact coverage gate.
    from shapely.geometry import Polygon,LineString,Point,box,mapping
    from shapely.ops import unary_union
    extent=box(*inputs['fullParentDomain']);polygons=[Polygon(t[:,[0,2]])for t in raw];kept=[p for p in polygons if p.area>1e-10];union=unary_union(kept)
    native_draw_union=unary_union([p for p in polygons if p.area>0])
    native_height_union=unary_union([p for t,p in zip(raw,polygons)if abs(geometry.production_determinant(t.tolist()))>=1e-10])
    before_union=unary_union([Polygon(t[:,[0,2]])for t in before if Polygon(t[:,[0,2]]).area>0])
    after_union=unary_union([Polygon(t[:,[0,2]])for t in after if Polygon(t[:,[0,2]]).area>0])
    save(DOC/'actual-validator-rectangle-union-attribution.json.gz',dict(completeNativeFaces=55305,validatorIncludedFaces=len(kept),existingAreaAdmissionM2=1e-10,existingCoverageToleranceM2=max(.001,extent.area*1e-7),measuredSymmetricDifferenceAreaM2=union.symmetric_difference(extent).area,measuredMissingAreaM2=extent.difference(union).area,measuredOutsideAreaM2=union.difference(extent).area,missingGeometry=mapping(extent.difference(union)),outsideGeometry=mapping(union.difference(extent)),measurementUsesUnchangedValidatorGEOSNotExactFractionUnion=True,noToleranceOrApprovalChange=True))
    # Complete eligible support projection comparison is a bounded GEOS locator.
    # No symbolic112x55333 union subtraction or whole actor finite replay.
    projection_cache={};eligible_projection=[]
    for uid in ELIGIBLE:
        ring=forms[uid]['rings'];raw_gis=Polygon(ring[0],ring[1:]);modes=[]
        for mode,(world,_)in basic_ground[uid].items():
            key=(sha(world),hashlib.sha256(json.dumps(ring,separators=(',',':')).encode()).hexdigest());reused=key in projection_cache
            if not reused:
                primitives=[]
                for t in world:
                    xz=t[:,[0,2]].tolist();polygon=Polygon(xz)
                    if polygon.area>0:primitives.append(polygon)
                    else:
                        unique=sorted(set(tuple(p)for p in xz));primitives.append(Point(unique[0])if len(unique)==1 else LineString(unique))
                support=unary_union(primitives)
                projection_cache[key]=dict(completeFaces=len(world),constructorProjection=mapping(support),missingFromBeforeDraw=mapping(support.difference(before_union)),missingFromAfterDraw=mapping(support.difference(after_union)),missingFromCandidateDrawProjection=mapping(support.difference(native_draw_union)),missingFromCandidateHeightAdmittedProjection=mapping(support.difference(native_height_union)),missingFromValidatorIncludedProjection=mapping(support.difference(union)),rawGISNotInConstructor=mapping(raw_gis.difference(support)),rawGISNotInCandidateDrawProjection=mapping(raw_gis.difference(native_draw_union)),rawGISNotInCandidateHeightAdmittedProjection=mapping(raw_gis.difference(native_height_union)),noEPSBufferOrGeometryRepair=True,GEOSLocatorNotExactFractionOrOrdinaryCertificate=True)
            modes.append(dict(mode=mode,wholeWorldSHA256=sha(world),rawGISRingsSHA256=key[1],completeFaces=len(world),findings=projection_cache[key],exactSourceWorldAndRawGISTupleReuse=reused))
        eligible_projection.append(dict(uid=uid,rawGISProjection=mapping(raw_gis),worlds=modes,scope='completeCapturedBASICConstructorAndRawGISSupportProjectionLocatorOnly'))
    save(DOC/'complete-two-eligible-support-projection-attribution.json.gz',dict(actors=eligible_projection,noOrdinaryThresholdOrGuardReplay=True,noProviderOriginalGovernmentMeshClaim=True,noGeometryOrAcceptance=True))
    for index in indices.values():index.verify_binding()
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
    capture.prior.module('polyu_saved_hole_mask_freezer',capture.prior.FREEZER).freeze(BATCH,'saved-polyu-hole-mask-packing-causal-attribution-only',[check(q)for q in refs],dict(uids=capture.prior.UIDS,sourceOnly=True,noConstructionOrAcceptance=True,physicalAccepted=False,newlyInstalled=0))


def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--attribute-saved-holes-and-eligible-mask-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
    *_,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    claim=reservations.claim('polyu-saved-hole-mask-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
