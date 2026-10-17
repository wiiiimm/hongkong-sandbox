"""ROOT-only two-original-TIN bare nominee + bounded18 source-facet context; no approval."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys,uuid
import heritage165054_two_tin_clamp_lowrim_context_v1_20261014 as prior
from aqua_facade_bottom_context_v1_20261014 import descriptor
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=prior.ROOT;HERE=prior.HERE;BASE=prior.BASE;UID=prior.UID;CURRENT=prior.CURRENT;SNAPSHOT=prior.SNAPSHOT
BATCH='government-xl-heritage165054-two-TIN-nearwater-bare-nomination-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';JOB='e0dbec8ca24e4ec2757a16936d1bd8f5953fa22f0bd86021c587ffa9bb53ad1d'
CONTEXT=prior.DOC/'exact-saved-source-clamp-and-lowrim-context.json.gz';SOUTH_ARRAY=prior.LOCAL/'whole-south-original-terrain-triangles.json.gz';ORIGINAL=BASE/'government-xl-heritage165054-source-context-draft-v1-20261014/source-context-output-v1/complete-original-array.json.gz';CAPTURE=prior.north.CAPTURE
SOURCE_FACES=[12130,12131,12132,12150,12191,12192,12193,12194,12195,12199,12201,12202,12203,12249,12288,12290,12292,12293]
read=prior.read;ref=prior.ref;check=prior.check;save=prior.save;module=prior.module

def bind_context(c):
    assert c['uid']==UID and c['currentManifestSHA256']==CURRENT and c['currentSnapshot']==SNAPSHOT and not c['terrainNominated'] and not c['physicalAccepted']
    assert c['summary']['all']['points']==c['summary']['all']['covered']==59406 and c['summary']['all']['missing']==0 and c['summary']['all']['belowMinus05']==22 and c['summary']['aboveExistingGlobalLowRim']['belowMinus05']==0
    w=c['allMissingOrBelowMinus05Witnesses'];assert len(w)==22 and all(x['existingLowRimDefinition'] and x['originalTINCovered'] for x in w)
    assert sorted({i for x in w for i in x['sourceLineage']['originalFaceIDs']})==SOURCE_FACES
    assert len(c['allSelectedInputClampFacetContexts'])==408 and all(not v['parentRawWater'] for f in c['allSelectedInputClampFacetContexts'] for v in f['lowSourceVertices'])
    return c

def selected_source_offsets(c,north_faces,south_faces):
    assert north_faces==c['wholeSourceNorthFaces']==101426 and south_faces==c['wholeSourceSouthFaces']==97667
    rows=c['selectedCompleteOriginalFacets']; assert len(rows)==6906
    assert sum(r['sheet']=='7-SW-15D' for r in rows)==5223 and sum(r['sheet']=='7-SW-20B' for r in rows)==1683
    slots=[]
    for r in rows:
        assert r['sheet'] in ['7-SW-15D','7-SW-20B'] and type(r['originalFaceID']) is int
        limit=north_faces if r['sheet']=='7-SW-15D' else south_faces
        assert 0<=r['originalFaceID']<limit
        slots.append(r['originalFaceID']+(0 if r['sheet']=='7-SW-15D' else north_faces))
    assert len(set(slots))==len(slots)
    return slots

def inputs():
    r=read(prior.DOC/'result.json');v=read(prior.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased'];c=bind_context(read(CONTEXT));scope=read(prior.north.DOC/'proposal-input.json')
    captured=read(CAPTURE);assert captured['uid']==UID and captured['completeOriginalFaceCount']==15140 and captured['sourceSHA256']=='1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f'
    refs=distinct_refs(r['evidenceRefs']+[ref(p)for p in [prior.DOC/'result.json',prior.DOC/'ROOT-VERIFIED.json',ORIGINAL,CAPTURE,SOUTH_ARRAY,HERE/'xl-stage-central-nested.py',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/rendered-patch-height.js']])
    for q in refs:check(q)
    return c,scope,refs

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    c,s,refs=inputs();assert refs==pins['inputRefs'];return pins,c,s,refs

def owned():
    from run import reservations,connect
    import numpy as np
    import shapely
    pins,c,scope,refs=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
    lease=read(LEASE);assert reservations.owns(lease) and lease['resources']==pins['canonicalResources'] and not DOC.exists()
    refs=distinct_refs(refs+pins['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence()
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',read(prior.DOC/'result.json'))
    DOC.mkdir();original=read(ORIGINAL);assert original['completeOriginalFaceCount']==15140 and original['sourceGeometryChanges']==original['sourcePoseChanges']==0;provider=np.asarray(original['completeOrderedOriginalTriangles'],dtype='<f8');assert provider.shape==(15140,3,3)
    capture=read(CAPTURE);idx=np.asarray(capture['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'providerOriginal':provider}
    for label,key in [('literal','completeLiteralWorldPosition'),('leftFloat32','completeLeftFloat32WorldPosition'),('balancedFloat32','completeBalancedFloat32WorldPosition')]:worlds[label]=np.asarray(capture[key],dtype='<f8').reshape(-1,3)[idx]
    descriptions={label:[descriptor(i,t[i])for i in SOURCE_FACES]for label,t in worlds.items()};continuation={}
    for label,tri in worlds.items():
        selectedEdges={};edgeFaces={}
        for i in SOURCE_FACES:
            keys=[tuple(float(v)for v in p)for p in tri[i]]
            for e in range(3):selectedEdges.setdefault(tuple(sorted((keys[e],keys[(e+1)%3]))),set()).add(i)
        for i,t in enumerate(tri):
            keys=[tuple(float(v)for v in p)for p in t]
            for e in range(3):
                k=tuple(sorted((keys[e],keys[(e+1)%3])))
                if k in selectedEdges:edgeFaces.setdefault(k,set()).add(i)
        continuation[label]=[dict(exactSharedEdge=[list(v)for v in edge],selectedFaceIDs=sorted(selectedEdges[edge]),allExactSourceFaceIDs=sorted(faces),sourceRelationContextOnlyNotTopologyOrSupportCertificate=True)for edge,faces in sorted(edgeFaces.items())]
    save(DOC/'exact18-four-world-source-context.json.gz',dict(uid=UID,CSUID='3712526467T20050430',sourceSHA256=capture['sourceSHA256'],sourceFaceIDs=SOURCE_FACES,fourWorldDescriptors=descriptions,exactSharedSourceEdgeContext=continuation,all22SavedBelowMinus05WitnessesVerbatim=c['allMissingOrBelowMinus05Witnesses'],all408SourceClampContextsRetained=ref(CONTEXT),rawSourcePointSummaryVerbatim=c['summary'],rawCurrentOrdinaryStrictFalsePreserved=ref(prior.north.source.ORDINARY/'diagnostic.json.gz'),sourceRoleAssigned=False,warningResolved=False,noTinyAreaNormalAdjacencyWaiver=True,noEngineeringOrStructuralGate=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False))
    north=read(prior.ARRAY);south=read(SOUTH_ARRAY);nt=np.asarray(north['wholeOriginalTriangles'],dtype='<f8');st=np.asarray(south['completeOriginalTriangles'],dtype='<f8');assert nt.shape==(101426,3,3) and st.shape==(97667,3,3)
    assert hashlib.sha256(nt.tobytes()).hexdigest()==north['wholeTriangleSHA256'] and hashlib.sha256(st.tobytes()).hexdigest()==south['completeTriangleSHA256'];whole=np.concatenate([nt,st]);ids=selected_source_offsets(c,len(nt),len(st));native=whole[ids];assert native.shape==(len(ids),3,3)
    low=native[:,:,1].min(axis=1)<1.2;polys=shapely.polygons(native[low][:,:,[0,2]]);lowProjection=shapely.union_all(polys);modelPolygons=shapely.polygons(provider[:,:,[0,2]]);projection=shapely.union_all(modelPolygons[shapely.area(modelPolygons)>1e-10])
    lowProof=dict(completeOriginalLowFacetIDs=[c['selectedCompleteOriginalFacets'][i]for i in np.flatnonzero(low)],faces=int(low.sum()),heightRangeM=[float(native[low,:,1].min()),float(native[low,:,1].max())],projectedAreaM2=float(lowProjection.area),modelIntersectionAreaM2=float(lowProjection.intersection(projection).area),parentRawWaterFalseForAll897SavedLowVertices=True,policy='Retain authentic original low-HKPD source facets through existing near-water constructor argument; preserve exact parent grid water classification. Native renderer retains these source heights. No terrain floor or arbitrary lowering to clear the22 source witnesses.',existingImplementation=ref(HERE/'xl-stage-central-nested.py'))
    save(DOC/'source-bound-nearwater-constructor-context.json',lowProof)
    resolution=module(HERE/'resolve-pass.py','heritage_two_TIN_nearwater');sources=[]
    for acq in [prior.north.source,prior.south]:
        member=read(acq.DOC/'authentic-terrain-members.json');d=read(acq.LOCAL/'original/download.json');sources.append(dict(sheet=d['sheet'],revision=d['revisionDate'],sourceETag=d['sourceETag'],directorySHA256=d['directorySHA256'],sourceFiles=[m['extracted']for m in member['originalUnmodifiedMembers']]))
    try:
        patch=resolution.make_patch(dict(uids=[UID],cells=scope['cells']),read(ROOT/'3d-viewer/city/data/terrain.json'),native,sources,allow_native_below_clamp=True)
        path=LOCAL/(patch['id']+'.json');save(path,patch);candidate=dict(path=str(path.relative_to(ROOT)),sha256=ref(path)['sha256'],uids=[UID],bounds=scope['region'],cells=scope['cells'],triangles=len(patch['nativeMesh']['index'])//3);save(DOC/'terrain-candidates.json',[candidate]);construction=dict(candidate=candidate,bareExistingValidatorPassed=True)
    except(AssertionError,ValueError)as error:construction=dict(candidate=None,bareExistingValidatorPassed=False,existingConstructorFailure=dict(type=type(error).__name__,reason=str(error)),noOverlapApprovalOrThresholdWaiver=True)
    save(DOC/'diagnostic.json',dict(uid=UID,construction=construction,nearwaterSourceProof=ref(DOC/'source-bound-nearwater-constructor-context.json'),exact18SourceContext=ref(DOC/'exact18-four-world-source-context.json.gz'),all22SourceBelowMinus05WarningsUnresolved=True,rawStrictFoundationRemainsFalse=True,noFullSamplingRepeated=True,wholeCurrent45Actor91ResourcePhysicalQualificationRequired=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p)for folder in[DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']);fence();module(prior.north.source.FREEZER,'heritage_bare_nearwater_freezer').freeze(BATCH,'two-original-TIN-existing-nearwater-constructor-bare-validator-and18-source-context-no-warning-resolution',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,terrainCandidateCreated=construction['candidate']is not None,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:
        p,c,s,refs=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),sourceContextJob=JOB,sourceFaces=SOURCE_FACES,rawBadSourcePoints=22,sourceOnlyResources=len(p['canonicalResources']),noGeometrySourceDecodeConstructionDBLeaseWorker=True)));return
    if '--owned'in sys.argv:return owned()
    assert sys.argv[1:]==['--nominate-original-two-tin-nearwater-bare-only'] and not DOC.exists() and not LOCAL.exists();p,*_=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    claim=reservations.claim('heritage-two-TIN-nearwater-'+str(uuid.uuid4()),p['canonicalResources'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
