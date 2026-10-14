"""ROOT-only private standard original-TIN core/parent-collar nomination; never accept/apply."""
from pathlib import Path
import gzip,hashlib,json,math,struct,subprocess,sys,uuid
import heritage165054_authentic_terrain_acquisition_v1_20261014 as source
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=source.ROOT; HERE=source.HERE; BASE=source.BASE; UID=source.UID; CURRENT=source.CURRENT; SNAPSHOT=source.SNAPSHOT
BATCH='government-xl-heritage165054-authentic-tin-nomination-v1-20261014'; DOC=BASE/BATCH; PROPOSAL=BASE/(BATCH+'-proposal'); LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'reservation.json'
ACQUISITION_JOB='921a7e7a2cfc84b2c4927268a400fe9ffdb4651e0a7e523b9f274600066ad2f0'
ROW=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v1-20261014/exact-source-row-current-form.json'
CAPTURE=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v2-20261014/collision-output-v2/complete-current-star-and-museum-geometry.json.gz'
POSITION=BASE/'xl-terrain-recovery-20261010-complete-current-native-position-inventory-v3/inventory.json.gz'
LITERAL=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v1-20261011/inventory.json.gz'
read=source.read; ref=source.ref; check=source.check; module=source.module

def save(p,o):
    p.parent.mkdir(parents=True,exist_ok=True); raw=json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    with p.open('xb') as f: f.write(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw+b'\n')
def closed_touch(a,b): return not (a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1])
def projected(b): return [b[0][0],b[0][2],b[1][0],b[1][2]]
def nominated_domain(bounds,parent):
    lo,hi=bounds; g=parent['meta']['georef']; c=g['aE']; assert c>0 and g['aN']==-c
    cells=[math.floor((lo[0]-20+834500-g['bE'])/c),math.floor((lo[2]-20-816500+g['bN'])/c),math.ceil((hi[0]+20+834500-g['bE'])/c),math.ceil((hi[2]+20-816500+g['bN'])/c)]
    bb=[g['bE']+cells[0]*c-834500,816500-g['bN']-cells[1]*g['aN'],g['bE']+cells[2]*c-834500,816500-g['bN']-cells[3]*g['aN']]
    assert cells==[528,306,532,309] and bb==[2492.5,-10047.5,2772.5,-9837.5]
    return cells,bb

def scope_metadata(current,parent_region):
    """Conservative nomination only. Old bounds never become current regression/outside approval."""
    original={r['uid']:r for r in read(POSITION)['rows']}; literal={r['uid']:r for r in read(LITERAL)['rows']}; refs=[ref(POSITION),ref(LITERAL)]; native=[]; unknown=[]; nomination=[]
    fields=['sha256','modelId','buildingCSUID','objectId','sourceTile','worldBounds','rootTranslation','scale']
    for url in current['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url; refs.append(ref(p))
        for e in read(p)['models']:
            native.append(e['uid']); old=original.get(e['uid']); f=literal.get(e['uid'])
            if not old or not f or old['sourceSHA256']!=e['sha256'] or f['sourceSHA256']!=e['sha256'] or json.dumps({k:old['rawCurrentEntry'].get(k) for k in fields},sort_keys=True,separators=(',',':'),allow_nan=False)!=json.dumps({k:e.get(k) for k in fields},sort_keys=True,separators=(',',':'),allow_nan=False):
                unknown.append(dict(uid=e['uid'],entry=e,catalogue=ref(p),reason='no-exact-saved-complete-source-bounds-binding')); continue
            assert old['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted'] and f['wholeUnusedPositionVerticesIncluded'] and f['sourceFacesOmitted']==0
            boxes=[old['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],f['completeLiteralBounds'],f['completeLeftAssociatedF32Bounds'],f['completeBalancedF32Bounds']]
            if any(closed_touch(projected(b),parent_region) for b in boxes): nomination.append(dict(uid=e['uid'],entry=e,catalogue=ref(p),source=old['source'],savedWholeBounds=boxes,historicalBoundsOnlyNoCurrentRegressionCredit=True))
    assert len(native)==len(set(native))==6653
    forms=[]
    for tile in current['tiles']:
        p=ROOT/'3d-viewer'/tile['url']; data=read(p)
        for b in data['buildings']:
            points=[v for ring in b.get('rings',[]) for v in ring]
            model=b.get('modelGeometry'); assert model is None or isinstance(model,dict)
            positions=[] if model is None else model.get('position',[]); assert len(positions)%3==0
            points += [[v[0],v[2]] for v in zip(*[iter(positions)]*3)]
            if not points: continue
            # BASIC makeBuildings uses original ring coordinates then Float32 attributes;
            # include both exact source coordinates and their actual Float32 cast.
            cast=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
            xx=[q for v in points for q in [v[0],cast(v[0])]]; zz=[q for v in points for q in [v[1],cast(v[1])]]
            bb=[min(xx),min(zz),max(xx),max(zz)]
            if closed_touch(bb,parent_region): forms.append(dict(building=b,tile=tile['url'],tileRef=ref(p),sourceAndFloat32ProjectedBounds=bb,existingNative=b['uid'] in native))
        if any(f['tile']==tile['url'] for f in forms): refs.append(ref(p))
    assert len({f['building']['uid'] for f in forms})==len(forms) and UID in {f['building']['uid'] for f in forms}
    actors=sorted({UID,*[f['building']['uid'] for f in forms],*[r['uid'] for r in nomination],*[r['uid'] for r in unknown]})
    return dict(completeCurrentNativeCatalogueCount=6653,knownNativeWholeBoundsTouching=nomination,missingOrChangedWholeBoundsActorsRetained=unknown,currentProjectedFormsTouching=forms,allActorsForNominationLease=actors,fullCurrentOriginalLiteralFloat32ParentDomainRegressionAndExteriorStillRequired=True,oldBoundsInventoryIsHistoricalContextOnly=True),refs

def inputs():
    _,_,old_refs=source.inputs(); acquired=read(source.DOC/'result.json'); verified=read(source.DOC/'ROOT-VERIFIED.json')
    assert acquired['jobId']==verified['jobId']==ACQUISITION_JOB and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
    members=read(source.DOC/'authentic-terrain-members.json'); assert members['sourceArchive']==source.PIN and members['geometryDecoded'] is False and len(members['originalUnmodifiedMembers'])==2
    refs=distinct_refs(old_refs+acquired['evidenceRefs']+[ref(source.DOC/'result.json'),ref(source.DOC/'ROOT-VERIFIED.json'),ref(ROW),ref(CAPTURE)])
    for e in members['originalUnmodifiedMembers']: check(e['extracted'])
    row=read(ROW); captured=read(CAPTURE); assert captured['uid']==UID and captured['sourceSHA256']==row['sourceSHA256']=='1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f'
    assert captured['completeOriginalFaceCount']==15140 and captured['sourcePoseChanges']==0 and captured['sourceGeometryChanges']==0
    boxes=[row['candidate']['entry']['worldBounds'],*captured['wholeUnusedWorldBounds'].values()]; assert len(boxes)==4
    bounds=[[min(b[0][i] for b in boxes) for i in range(3)],[max(b[1][i] for b in boxes) for i in range(3)]]
    parent=read(ROOT/'3d-viewer/city/data/terrain.json'); cells,region=nominated_domain(bounds,parent); core=[region[0]+10,region[1]+10,region[2]-10,region[3]-10]
    assert all(core[0]<=b[0][0]<=b[1][0]<=core[2] and core[1]<=b[0][2]<=b[1][2]<=core[3] for b in boxes)
    current=read(ROOT/'3d-viewer/city/data/manifest.json'); routing=[]
    for e in current['terrainPatches']:
        p=ROOT/'3d-viewer'/e['url']; patch=read(p); c=patch['coarseCells']; assert cells[2]<=c[0] or cells[0]>=c[2] or cells[3]<=c[1] or cells[1]>=c[3],'existing-native-terrain-overlap'
        routing.append(dict(entry=e,asset=ref(p))); refs.append(ref(p))
    scope,scope_refs=scope_metadata(current,region); refs=distinct_refs(refs+scope_refs)
    for q in refs: check(q)
    return dict(row=row,capturedBounds=boxes,cells=cells,region=region,core=core,parent=parent,terrainRouting=routing,scope=scope,memberPacket=members),refs

def load():
    pins=read(PROPOSAL/'draft-pins.json'); assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']: check(q)
    data,refs=inputs(); assert refs==pins['inputRefs']; return pins,data,refs

def owned():
    from run import connect,reservations
    import numpy as np
    pins,data,refs=load(); prep=read(PROPOSAL/'actual-readonly-preparation.json'); assert prep['passed'] and prep['caller']==ref(Path(__file__))
    lease=read(LEASE); assert reservations.owns(lease) and not DOC.exists(); refs=distinct_refs(refs+pins['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs: check(q); pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT; pulse(force=True)
    fence()
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder,job in [(source.ORDINARY,source.JOB),(source.DOC,ACQUISITION_JOB)]: assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',read(folder/'result.json'))
    DOC.mkdir(); save(DOC/'proposal-input.json',dict(currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,cells=data['cells'],region=data['region'],authenticCore=data['core'],scope=data['scope'],allCurrentTerrainRouting=data['terrainRouting'],completeFourWorldUnusedMuseumBounds=data['capturedBounds'],sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False))
    resolution=module(HERE/'resolve-pass.py','heritage_standard_resolution'); assert resolution.rectangle_for([[min(b[0][i] for b in data['capturedBounds']) for i in range(3)],[max(b[1][i] for b in data['capturedBounds']) for i in range(3)]],data['parent'])==data['cells'] and resolution.extent(data['cells'],data['parent'])==data['region']
    gltf=check(next(e['extracted'] for e in data['memberPacket']['originalUnmodifiedMembers'] if e['name'].endswith('.gltf')))
    whole=resolution.context.triangles(gltf); assert whole.ndim==3 and whole.shape[1:]==(3,3) and np.isfinite(whole).all()
    bb=data['region']; keep=(whole[:,:,0].max(axis=1)>=bb[0])&(whole[:,:,0].min(axis=1)<=bb[2])&(whole[:,:,2].max(axis=1)>=bb[1])&(whole[:,:,2].min(axis=1)<=bb[3]); ids=np.flatnonzero(keep); native=whole[keep]
    assert len(native)>0
    save(LOCAL/'complete-original-terrain-triangles.json.gz',dict(source=ref(gltf),wholeOriginalTriangles=whole.tolist(),wholeTriangleSHA256=hashlib.sha256(whole.astype('<f8').tobytes()).hexdigest(),selectedOriginalFaceIDs=ids.tolist(),noProjectedVerticalOrDegenerateFiltering=True))
    geometry=read(HERE/'local'/source.ORDINARY.name/'runtime-geometry.json.gz')['rows']; assert len(geometry)==1 and geometry[0]['uid']==UID
    points,bottom=resolution.sample_points(geometry[0]); audit=resolution.audit_native(points,bottom,native); save(DOC/'source-tin-point-diagnostic.json',dict(uid=UID,audit=audit,diagnosticOnlyNotWholeSurfaceAcceptance=True,rawCurrentOrdinary=ref(source.ORDINARY/'diagnostic.json.gz')))
    sources=[dict(sheet=source.PIN['sheet'],revision=read(source.LOCAL/'original/download.json')['revisionDate'],sourceETag=source.PIN['etag'],directorySHA256=source.PIN['directorySHA256'],sourceFiles=[e['extracted'] for e in data['memberPacket']['originalUnmodifiedMembers']])]
    try:
        patch=resolution.make_patch(dict(uids=[UID],cells=data['cells']),data['parent'],native,sources)
        path=LOCAL/(patch['id']+'.json'); save(path,patch); candidate=dict(path=str(path.relative_to(ROOT)),sha256=ref(path)['sha256'],uids=[UID],bounds=bb,cells=data['cells'],triangles=len(patch['nativeMesh']['index'])//3)
        save(DOC/'terrain-candidates.json',[candidate]); construction=dict(candidate=candidate,bareExistingValidatorPassed=True,sourceCorePlanePolicy='unchanged original TIN in existing constructor core; existing 10m parent collar',fullActualPackedDomainRegressionRequired=True)
    except (AssertionError,ValueError) as error:
        construction=dict(candidate=None,bareExistingValidatorPassed=False,existingConstructorFailure=dict(type=type(error).__name__,reason=str(error)),noWaiverOrOverlapApproval=True)
    save(DOC/'diagnostic.json',dict(uid=UID,wholeSourceTerrainTriangles=len(whole),wholeSourceTerrainTriangleSHA256=hashlib.sha256(whole.astype('<f8').tobytes()).hexdigest(),selectedWholeOriginalFaceIDs=ids.tolist(),selectedWholeOriginalFaces=len(native),construction=construction,sourceTINPointDiagnostic=audit,rawCurrentReasonRetained='terrain-intersects-source-over-0.5m',rawCurrentStrictFoundationAccepted=False,allCurrentNativePatchesPreserved=True,StarOriginalFootprintRejectionPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p) for folder in [DOC,LOCAL] for p in folder.rglob('*') if p.is_file() and p.name!='reservation.json']); fence()
    module(source.FREEZER,'heritage_nomination_freezer').freeze(BATCH,'private-standard-authentic-TIN-parent-collar-candidate-existing-validator-no-acceptance',[check(q) for q in refs],dict(uids=[UID],sourceOnly=True,terrainCandidateCreated=construction['candidate'] is not None,geometrySourceChanges=0,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only' in sys.argv:
        pins,data,refs=load(); print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),cells=data['cells'],region=data['region'],currentCatalogue=6653,nominationActors=len(data['scope']['allActorsForNominationLease']),wholeSourceBoundsUnknownActors=len(data['scope']['missingOrChangedWholeBoundsActorsRetained']),noTerrainOrBuildingCalculationDBLeaseWorker=True))); return
    if '--owned' in sys.argv: return owned()
    assert sys.argv[1:]==['--nominate-authentic-original-tin-only'] and not DOC.exists() and not LOCAL.exists()
    pins,data,refs=load(); assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    actors=data['scope']['allActorsForNominationLease']; resources=['building:'+u for u in actors]+['terrain-patch:'+u for u in actors]+['immutable-source-proof:'+BATCH]
    claim=reservations.claim('heritage-authentic-nomination-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600); assert claim['ok']; lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str))); subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease): assert reservations.release(lease)['ok']
if __name__=='__main__': main()
