"""ROOT-only saved-array attribution of actual3 foundation failures; no waiver."""
from pathlib import Path
import json,sys,subprocess,uuid,numpy as np,shapely
from shapely.geometry import Polygon
import aqua_marine193086_current_ordinary_physical_v3_20261014 as prior
from aqua_three_foundation_saved_attribution_v1_20261014 import trace_foundation,source_index_binding,validate_runtime_rows
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
ref,check,module=prior.ref,prior.check,prior.module
BATCH='government-xl-aqua-marine193086-three-foundation-source-attribution-v1-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';JOB='277bc12f33e1dc01cefae56fe00973a4e27a2a973cb0fae2e5658bdc345aa052';PARTS=BASE/'government-xl-aqua-marine-exact-source-terrain-20261010/complete-original-podium-footing-inputs.json.gz'
def load():
    data=prior.load();result=read(prior.DOC/'result.json');v=read(prior.DOC/'ROOT-VERIFIED.json');assert result['jobId']==v['jobId']==JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    diagnostic=read(prior.DOC/'diagnostic.json.gz');f=read(prior.DOC/'foundation.json')['rows'][0];assert f['uid']==prior.UID and not f['strictFoundationAccepted']and f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==3
    assert diagnostic['ordinaryNumericReasons']==['terrain-intersects-source-over-0.5m']and diagnostic['loaderAccepted']==diagnostic['runtimeChecksPassed']==1 and diagnostic['runtimeExceptions']==0 and validate_runtime_rows(diagnostic['rawRuntimeConcerns'],prior.UID)==diagnostic['rawRuntimeConcerns']and not diagnostic['neighbourRegressionReasons']and not diagnostic['nativeNeighbourChecks']['blocked']
    runtime=prior.LOCAL/'runtime-geometry.json.gz';raw=read(runtime);assert len(raw['rows'])==1 and raw['rows'][0]['uid']==prior.UID and raw['rows'][0]['sourceSHA256']==prior.SOURCE_SHA
    parts=read(PARTS)['rows'][0];assert parts['sourceSHA256']==prior.SOURCE_SHA and parts['wholeOriginalFaces']==22735 and parts['worldTriangleSHA256']==prior.WORLD_SHA
    refs=distinct_refs(result['evidenceRefs']+[ref(prior.DOC/'result.json'),ref(prior.DOC/'ROOT-VERIFIED.json'),ref(runtime),ref(PARTS)])
    for q in refs:check(q)
    return data,result,diagnostic,f,raw['rows'][0],parts,refs

def schema_only():
    data,r,d,f,a,p,refs=load();return dict(passed=True,caller=ref(Path(__file__)),actualSourceFaces=22735,actualGroundFaces=d['completeActualDrawnGroundFaces'],savedFullyBuriedUpwardFaces=3,strictFoundationAccepted=False,rawReasons=d['ordinaryNumericReasons'],scope=data[-1],noSelectorDescriptorsSourceDecodeNumericalDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    data,result,d,f,a,parts,refs=load();refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',result)
    DOC.mkdir();pos=np.asarray(a['position'],dtype='<f8').reshape(-1,3);index=np.asarray(a['index'],dtype=np.int64).reshape(-1,3);tri=pos[index];ground=np.asarray(a['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(tri)==22735 and len(ground)==584 and prior.digest(tri.tobytes())==d['actualLiteralWorldSHA256']
    binding=source_index_binding(a['index'],len(pos),data[5]['own']);row=data[0];target=Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]);final=module(HERE/'xl-final-script-pass.py','aqua_three_unchanged_foundation');replayed,mask,heights=trace_foundation(final,tri,ground,target,f['foundation']);ids=np.flatnonzero(mask).tolist();assert len(ids)==3
    source_by_face={};original=np.empty_like(tri)
    for part in parts['parts']:
        pt=np.asarray(part['position'],dtype='<f8').reshape(-1,3)[np.asarray(part['index'],dtype=np.int64).reshape(-1,3)]
        assert len(pt)==len(part['originalFaceIds'])
        for i,t in zip(part['originalFaceIds'],pt):assert i not in source_by_face;source_by_face[i]=part['component'];original[i]=t
    assert sorted(source_by_face)==list(range(22735))and prior.digest(original.tobytes())==prior.WORLD_SHA
    points=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1);gaps=points[:,:,1]-heights;all_below=np.flatnonzero((gaps<-.5).any(axis=1)).tolist();rows=[];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    ground_poly=shapely.polygons(ground[:,:,[0,2]]);valid=np.flatnonzero(shapely.area(ground_poly)>1e-10);tree=shapely.STRtree(ground_poly[valid])
    for face in ids:
        t=tri[face];vertices=index[face].tolist();incident=np.flatnonzero(np.isin(index,vertices).any(axis=1)).tolist();witnesses=[]
        for k,p in enumerate(points[face]):
            q=shapely.Point(p[0],p[2]);gids=[int(valid[i])for i in tree.query(q,predicate='intersects')];witnesses.append(dict(site=k,actualXYZ=p.tolist(),height=float(heights[face,k]),gap=float(gaps[face,k]),completeContainingSavedGroundFacetIDs=gids,completeContainingSavedGroundTriplets=ground[gids].tolist()))
        rows.append(dict(originalFaceID=face,sourcePrimitive=0,sourceVertexIndices=vertices,actualLiteralXYZ=t.tolist(),savedOriginalXYZ=original[face].tolist(),originalCensusComponentContext=source_by_face[face],censusComponentIsNotStructuralCertificate=True,geometricNormal=cross[face].tolist(),surfaceArea=float(np.linalg.norm(cross[face])/2),projectedArea=float(abs(cross[face,1])/2),existingUpwardPredicatePass=bool(cross[face,1]>.25*np.linalg.norm(cross[face])),actualYRange=[float(t[:,1].min()),float(t[:,1].max())],footprintIntersectionArea=float(Polygon(t[:,[0,2]]).intersection(target).area),centroidDistanceToTargetBoundaryM=float(Polygon(t[:,[0,2]]).centroid.distance(target.boundary)),allActualIndexIncidentFaceIDs=incident,allIncidentActualTriplets=tri[incident].tolist(),fourUnchangedFoundationSampleWitnesses=witnesses,architecturalRoleAssigned=None))
    save(DOC/'exact-three-source-face-attribution.json.gz',dict(rows=rows,exactSourceIndexBinding=binding,completeLiteralWorldSHA256=d['actualLiteralWorldSHA256'],completeSavedOriginalWorldSHA256=prior.WORLD_SHA,completeActualGroundSHA256=prior.digest(ground.tobytes()),completeActualDrawnGroundFaces=584,actualRuntimeArrays=ref(prior.LOCAL/'runtime-geometry.json.gz'),allCurrentGroundSourceInputRefs=[dict(path=p,sha256=h)for p,h in read(prior.LOCAL/'runtime-geometry.json.gz')['inputHashes'].items()],currentAndPrimaryFootprints=dict(current=row['source']['building'],providerEvidence=ref(prior.INPUT/'exact-current-primary.json')),savedFullOriginalSourceCensus=ref(PARTS),allOtherPartialBelowMinusHalfSourceFaceIDs=sorted(set(all_below)-set(ids)),allBelowMinusHalfSampleSites=[dict(face=i,sites=[dict(site=k,xyz=points[i,k].tolist(),gap=float(gaps[i,k]))for k in range(4)if gaps[i,k]<-.5])for i in all_below],rawFoundationVerbatim=f,unchangedFoundationReplayVerbatim=replayed,rawOrdinaryReasonsVerbatim=d['ordinaryNumericReasons'],minimumWholeSurfaceGapVerbatim=read(prior.DOC/'metrics.json')['rows'][0]['minSurfaceGap'],roleAssigned=False,strictFoundationAccepted=False,ordinaryWarningResolved=False,noAreaDistanceOrAdjacencyWaiver=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False))
    save(DOC/'pending-functional-source-review.json',dict(exactFailedFaceIDs=ids,proposedReviewOnly=True,sourceRoleUnassigned=True,rawStrictFoundationFalse=True,rawOrdinaryReason='terrain-intersects-source-over-0.5m',onlyExistingViewerFailuresMayReceiveExactSourceApplicability=True,noGenericSmallAreaBoundaryDistanceOrNormalException=True,noClaimIndependentSupportOrEngineeringTopology=True,actual3DSourceContextAndWholeFourWorldOrdinaryAndForeignCollisionStillRequired=True,currentSourceSHA256=prior.SOURCE_SHA,currentManifestSHA256=prior.CURRENT,currentSnapshot=prior.SNAPSHOT,newlyInstalled=0,publication=False))
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence();module(prior.FREEZER,'aqua_three_source_freezer').freeze(BATCH,'actual-three-foundation-source-attribution-raw-failures-preserved',[check(q)for q in refs],dict(uids=[prior.UID],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--attribute-actual-three-source-failures-only'in sys.argv and not DOC.exists()and not LOCAL.exists();data,*_=load();scope=data[-1];assert read(PROPOSAL/'actual-readonly-preparation.json')['passed'];resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-three-source-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
