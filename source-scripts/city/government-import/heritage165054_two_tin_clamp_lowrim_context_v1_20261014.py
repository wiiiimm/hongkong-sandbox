"""ROOT-only bounded saved-original two-TIN clamp/low-rim attribution; no constructor."""
from pathlib import Path
import gzip,hashlib,json,math,subprocess,sys,uuid
import heritage165054_authentic_tin_nomination_v2_20261014 as north
import heritage165054_south20b_terrain_acquisition_v3_20261014 as south
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=north.ROOT; HERE=north.HERE; BASE=north.BASE; UID=north.UID; CURRENT=north.CURRENT; SNAPSHOT=north.SNAPSHOT
BATCH='government-xl-heritage165054-two-TIN-clamp-lowrim-context-v1-20261014'; DOC=BASE/BATCH; PROPOSAL=BASE/(BATCH+'-proposal'); LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'reservation.json'
SOUTH_JOB='da1798af1875cf3e95b1988eae28dc64984dbfefe9ac42d94e5e5e13acff523e'
NORTH_JOB=south.NORTH_JOB; ARRAY=north.LOCAL/'complete-original-terrain-triangles.json.gz'; OWN=HERE/'local'/north.source.ORDINARY.name/'runtime-geometry.json.gz'
read=north.read; ref=north.ref; check=north.check; module=north.module; save=north.save

def tag_points(geometry,np):
    """Match unchanged resolve-pass.sample_points order exactly; labels are source lineage only."""
    vertices=np.asarray(geometry['position']).reshape(-1,3); idx=np.asarray(geometry['index']).reshape(-1,3); faces=vertices[idx]; bottom=vertices[:,1].min()
    incidence=[[] for _ in vertices]
    for face,indices in enumerate(idx):
        for v in indices: incidence[int(v)].append(face)
    tags=[dict(kind='source-POSITION',vertexID=i,originalFaceIDs=incidence[i]) for i in range(len(vertices))]
    tags += [dict(kind='source-face-centre',originalFaceIDs=[i]) for i in range(len(faces))]
    for f,face in enumerate(faces):
        for edge,(a,b) in enumerate(zip(face,np.roll(face,-1,axis=0))):
            if max(a[1],b[1])>bottom+.35: continue
            count=math.ceil(np.linalg.norm((a-b)[[0,2]]))
            if count>1: tags += [dict(kind='existing-low-rim-edge-sample',originalFaceIDs=[f],edge=edge,edgeNumerator=i,edgeDenominator=count) for i in range(1,count)]
    return tags

def same_source_height_samples(left,right,np):
    # Missing NaN entries can be compared without dropping their witness rows.
    # Exact finite values and signed infinities retain NumPy equality semantics.
    return np.array_equal(left,right,equal_nan=True)

def resources(actors):
    from run import reservations
    assert len(actors)==45 and UID in actors
    return reservations.normalise(['building:'+UID,'immutable-source-sheet:7-SW-15D','immutable-source-sheet:7-SW-20B','immutable-source-proof:'+BATCH])

def inputs():
    n=read(north.DOC/'result.json'); nv=read(north.DOC/'ROOT-VERIFIED.json'); s=read(south.DOC/'result.json'); sv=read(south.DOC/'ROOT-VERIFIED.json')
    assert n['jobId']==nv['jobId']==NORTH_JOB and s['jobId']==sv['jobId']==SOUTH_JOB and s['authenticTerrainAcquired'] is True and s['geometryDecoded'] is False
    for v in [nv,sv]: assert v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
    d=read(north.DOC/'diagnostic.json'); assert d['construction']['candidate'] is None and d['construction']['existingConstructorFailure']['reason']=='native-terrain-near-water-clamp'
    scope=read(north.DOC/'proposal-input.json'); assert scope['currentManifestSHA256']==CURRENT and scope['currentSnapshot']==SNAPSHOT and len(scope['scope']['allActorsForNominationLease'])==45
    refs=distinct_refs(n['evidenceRefs']+s['evidenceRefs']+[ref(north.DOC/'result.json'),ref(north.DOC/'ROOT-VERIFIED.json'),ref(south.DOC/'result.json'),ref(south.DOC/'ROOT-VERIFIED.json'),ref(ARRAY),ref(OWN)])
    for q in refs: check(q)
    return scope,s['jobId'],refs

def load():
    pins=read(PROPOSAL/'draft-pins.json'); assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']: check(q)
    data=inputs(); assert data[2]==pins['inputRefs'] and data[1]==pins['southAcquisitionJob']; return pins,data

def owned():
    from run import reservations,connect
    import numpy as np
    import shapely
    pins,data=load(); scope,southjob,refs=data; prep=read(PROPOSAL/'actual-readonly-preparation.json'); assert prep['passed'] and prep['caller']==ref(Path(__file__))
    lease=read(LEASE); assert reservations.owns(lease) and lease['resources']==pins['canonicalResources'] and not DOC.exists()
    refs=distinct_refs(refs+pins['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]); pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs: check(q); pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT; pulse(force=True)
    fence()
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder,job in [(north.DOC,NORTH_JOB),(south.DOC,southjob)]: assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',read(folder/'result.json'))
    DOC.mkdir(); resolution=module(HERE/'resolve-pass.py','heritage_context_standard'); prior=read(ARRAY); nt=np.asarray(prior['wholeOriginalTriangles'],dtype='<f8')
    assert nt.shape==(101426,3,3) and hashlib.sha256(nt.tobytes()).hexdigest()==prior['wholeTriangleSHA256']=='66e69abdb644b6c5e3447a40089adb024fda2a05e208b89a6bf48a020709c925'
    member=read(south.DOC/'authentic-terrain-members.json'); gltf=check(next(e['extracted'] for e in member['originalUnmodifiedMembers'] if e['name'].endswith('.gltf')))
    st=resolution.context.triangles(gltf); assert st.ndim==3 and st.shape[1:]==(3,3) and np.isfinite(st).all(); whole=np.concatenate([nt,st]); bb=scope['region']; core=scope['authenticCore']
    keep=(whole[:,:,0].max(axis=1)>=bb[0])&(whole[:,:,0].min(axis=1)<=bb[2])&(whole[:,:,2].max(axis=1)>=bb[1])&(whole[:,:,2].min(axis=1)<=bb[3]); selected=np.flatnonzero(keep)
    source_id=lambda i:dict(sheet='7-SW-15D' if i<len(nt) else '7-SW-20B',originalFaceID=int(i if i<len(nt) else i-len(nt)))
    save(LOCAL/'whole-south-original-terrain-triangles.json.gz',dict(source=ref(gltf),completeOriginalTriangles=st.tolist(),completeTriangleSHA256=hashlib.sha256(st.astype('<f8').tobytes()).hexdigest(),sourceGeometryChanges=0))
    geometries=read(OWN)['rows']; assert len(geometries)==1 and geometries[0]['uid']==UID; geometry=geometries[0]; assert geometry['sourceSHA256']=='1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f' and len(geometry['position'])==129744 and len(geometry['index'])==45420; points,bottom=resolution.sample_points(geometry); tags=tag_points(geometry,np); assert len(tags)==len(points)==59406
    old_low=points[:,1]<=bottom+.35; assert int(old_low.sum())==16875
    def evaluate(triangles):
        polys=shapely.polygons(triangles[:,:,[0,2]]); usable=shapely.area(polys)>1e-12; tri=triangles[usable]; return resolution.context.shared.samples(points[:,[0,2]],tri,shapely.STRtree(polys[usable]))
    nh=evaluate(nt); both=evaluate(whole); scoped=evaluate(whole[keep]); assert same_source_height_samples(both,scoped,np),'Whole-source projection is not equivalent to closed parent-domain facet selection'
    ncovered=np.isfinite(nh); assert int(ncovered.sum())==29877 and float((points[ncovered,1]-nh[ncovered]).min())==read(north.DOC/'source-tin-point-diagnostic.json')['audit']['gapRange'][0]
    covered=np.isfinite(both); gaps=np.where(covered,points[:,1]-both,np.inf); bad=covered&(gaps<-.5); missing=~covered
    valid=shapely.area(shapely.polygons(whole[:,:,[0,2]]))>1e-12; supportIDs=np.flatnonzero(valid); supportTree=shapely.STRtree(shapely.polygons(whole[valid][:,:,[0,2]])); witnesses=[]
    for i in np.flatnonzero(missing|bad):
        containing=supportTree.query(shapely.Point(points[i,0],points[i,2]),predicate='covered_by'); tids=supportIDs[containing]
        witnesses.append(dict(pointID=int(i),xyz=points[i].tolist(),sourceLineage=tags[i],existingLowRimDefinition=bool(old_low[i]),originalTINCovered=bool(covered[i]),sourceMaxHeight=float(both[i]) if covered[i] else None,gap=float(gaps[i]) if covered[i] else None,allContainingOriginalTINFacets=[dict(**source_id(int(t)),xyz=whole[t].tolist()) for t in tids],sourceRoleAssigned=False,individualSupportProved=False))
        pulse()
    clamps=[]; parent=read(ROOT/'3d-viewer/city/data/terrain.json'); raw=resolution.terrain.fine.DemSampler(parent)
    for i in selected:
        tri=whole[i]
        if tri[:,1].min()>=1.2: continue
        clipped=resolution.exact.rect(list(tri),bb); inner=resolution.exact.rect(list(tri),core)
        clamps.append(dict(**source_id(int(i)),xyz=tri.tolist(),lowSourceVertices=[dict(vertexID=int(j),xyz=p.tolist(),insideParentDomain=bool(bb[0]<=p[0]<=bb[2] and bb[1]<=p[2]<=bb[3]),parentRawHeight=float(raw.ground(p[0],p[2])),parentRawWater=bool(raw.ground(p[0],p[2])<=0)) for j,p in enumerate(tri) if p[1]<1.2],parentClippedPoints=[v.tolist() for v in clipped],parentClippedMinY=min(float(v[1]) for v in clipped) if len(clipped)>=3 else None,coreClippedPoints=[v.tolist() for v in inner],coreClippedMinY=min(float(v[1]) for v in inner) if len(inner)>=3 else None,existingConstructorClipContextOnlyNotCertified=True,noWaterOrThresholdWaiver=True)); pulse()
    def summary(mask):
        ids=np.flatnonzero(mask); good=ids[covered[ids]]
        return dict(points=len(ids),covered=len(good),missing=len(ids)-len(good),belowMinus05=int(bad[ids].sum()),gapRange=[float(gaps[good].min()),float(gaps[good].max())] if len(good) else None)
    report=dict(uid=UID,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,priorOneSheetJob=NORTH_JOB,southAcquisitionJob=southjob,wholeSourceNorthFaces=len(nt),wholeSourceSouthFaces=len(st),selectedCompleteOriginalFacets=[source_id(int(i)) for i in selected],auditPointOrderExactlyPreserved=True,wholeVsParentScopedMaxHeightsExactlyEqual=True,summary=dict(all=summary(np.ones(len(points),dtype=bool)),existingLowRim=summary(old_low),aboveExistingGlobalLowRim=summary(~old_low)),allMissingOrBelowMinus05Witnesses=witnesses,allSelectedInputClampFacetContexts=clamps,rawPriorOneSheetDiagnostic=read(north.DOC/'diagnostic.json'),rawCurrentOrdinaryStrictFalseAndIntersectionPreserved=ref(north.source.ORDINARY/'diagnostic.json.gz'),lowRimIsExistingSamplingDefinitionNotAnAssignedSourceFootRole=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainGeometryChanges=0,terrainNominated=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0)
    save(DOC/'exact-saved-source-clamp-and-lowrim-context.json.gz',report); refs=distinct_refs(refs+[ref(p) for folder in [DOC,LOCAL] for p in folder.rglob('*') if p.is_file() and p.name!='reservation.json']); fence()
    module(north.source.FREEZER,'heritage_two_tin_context_freezer').freeze(BATCH,'bounded-two-original-TIN-existing-sampler-clamp-lowrim-witnesses-no-construction-or-waiver',[check(q) for q in refs],dict(uids=[UID],sourceOnly=True,terrainNominated=False,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only' in sys.argv:
        p,d=load(); print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),southAcquisitionJob=d[1],canonicalResources=len(p['canonicalResources']),savedNorthFaces=101426,savedOrdinaryPoints=59406,noGeometryDecodeCalculationDBLeaseWorker=True))); return
    if '--owned' in sys.argv: return owned()
    assert sys.argv[1:]==['--attribute-saved-two-tin-clamp-and-lowrim-only'] and not DOC.exists() and not LOCAL.exists();p,d=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    claim=reservations.claim('heritage-two-TIN-context-'+str(uuid.uuid4()),p['canonicalResources'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
