"""ROOT-only private exact-array source review. No acceptance/publication edits."""
from pathlib import Path
from collections import Counter
import sys,json,subprocess,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_tower41_main_source_attribution_v1_20261014 as attribution
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_private_source_review_context_v1_20261014 import display_point,contact_summary
physical=attribution.physical;ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-joint-original-private-source-review-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'upton_joint_original_private_source_preview_v1_20261014.mjs'
JOB='af4e73ed5152fee5c2020757bb648b3208c4e5f90d261c7a335f34fe007a0dcf';GROUND='ad999dfa165259124705a82275cf559b474930d424e036411842680921969950';TERRAIN='f367dc82a617357da96ddeb004d4e6aa75329ca237a5f5033ce3f21daf1f7848'
VIEWS=[dict(id='assembly',title='Full unchanged tower and podium',camera=[-2470,145,155],target=[-2323,84,5]),dict(id='foot-southeast',title='Solid lower original source, southeast',camera=[-2273,38,52],target=[-2323,17,2]),dict(id='foot-northwest',title='Solid lower original source, northwest',camera=[-2374,35,-39],target=[-2323,17,-3]),dict(id='foot-north',title='Solid lower original source, north',camera=[-2325,33,-59],target=[-2323,17,-3]),dict(id='higher-overlap-detail',title='Lower contact layer and higher authored surfaces',camera=[-2299,28,11],target=[-2315,18,-3]),dict(id='foot-plan',title='Main original attachment plan',camera=[-2323,115,3],target=[-2323,17,3])]

def scope_uids():
    q=read(physical.metadata.capture.DOC/'input.json.gz')['fullScopeBindings']['currentWhole6650Scope'];check(q);s=read(ROOT/q['path'])
    basic={r['uid']for r in s['affectedBasic']};assert len(basic)==52 and s['completeNativeActors']==6650
    return sorted(basic|set(physical.OWNED+[physical.SECONDARY,physical.RETAINED,physical.FOREIGN]))

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    r=read(attribution.DOC/'result.json');v=read(attribution.DOC/'ROOT-VERIFIED.json')
    assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
    a=read(attribution.DOC/'main41-source-contact-attribution.json.gz');layers=read(attribution.DOC/'actual41-highest-and-all-source-layers.json.gz')
    assert a['completeNewGroundSHA256']==GROUND and a['completeCurrentGroundFaces']==11645 and a['allOriginal138Samples97Strict41FailuresRetained'] and not a['physicalAccepted']
    assert len(layers['rows'])==41 and Counter(q['classification']for q in layers['rows'])=={'contact-layer-with-higher-overlap':2,'no-layer-in-contact-interval':39}
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
    selection=read(physical.DOC/'selection.json.gz')['rows'];assert [r['uid']for r in selection]==physical.OWNED
    terrain=read(physical.DOC/'terrain-candidates.json');assert len(terrain)==1 and terrain[0]['sha256']==TERRAIN
    assert read(physical.DOC/'support-checks.json.gz')['rows'][0]['interface']['strictContacts']==97
    summaries=contact_summary(a['fourModeAuthenticatedMainContacts'],GROUND,11645)
    assert [r['sourceContacts']for r in summaries]==[197,197,199,199]
    return pins,a,layers,selection,terrain[0],summaries

def schema_only():
    p,a,l,s,t,c=load()
    return dict(passed=True,caller=ref(Path(__file__)),actualFailedSamples=41,uniqueIncidentFaces=len({q['faceIndex']for r in l['rows']for q in r['originalFailureVerbatim']['originalSourceFaces']}),fourModeSourceContactCounts=[r['sourceContacts']for r in c],canonicalWholeAffectedUIDs=scope_uids(),noRendererPlotsGroundOrSourceMathDBLeaseWorker=True,strictInterfacePassed=False,installationApproved=False)

def diagrams(runtime,ground,points,faces,contacts):
    # Display only: exact saved coordinates; axes permutation X,Z,Y is labelled.
    # No interpolation, buffering, simplification, source writes or support math.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    world={r['uid']:np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index'],dtype=np.int64)].reshape(-1,3,3) for r in runtime['rows']}
    fig,axes=plt.subplots(2,2,figsize=(16,12),dpi=200)
    pp=np.asarray([r['position']for r in points]);ff=np.asarray([r['vertices']for r in faces])
    for ax,(x,y,title,limits) in zip(axes.flat,[(0,2,'Plan: all source projections',(-2352,-2290,-30,40)),(0,1,'X / HKPD: full originals',(-2352,-2290,0,175)),(0,1,'X / HKPD: lower source',(-2352,-2290,0,29)),(2,1,'Z / HKPD: lower source',(-30,40,0,29))]):
        ax.add_collection(PolyCollection(ground[:,:,[x,y]],facecolors='#c8b89d',edgecolors='#a39783',linewidths=.12))
        for uid,color in zip(physical.OWNED,['#dc9251','#829dbb']):ax.add_collection(PolyCollection(world[uid][:,:,[x,y]],facecolors=color,edgecolors='#555555',linewidths=.13))
        ax.add_collection(PolyCollection(ff[:,:,[x,y]],facecolors='none',edgecolors='#dc3a16',linewidths=.8))
        for c in contacts:
            v=np.asarray(c['points']);ax.plot(v[:,x],v[:,y],color='#00aabb',linewidth=.9)
        for i,r in enumerate(points):ax.scatter(pp[i,x],pp[i,y],s=12,c='#155de0'if r['classification']=='contact-layer-with-higher-overlap'else'#e32620');ax.text(pp[i,x],pp[i,y],str(r['id']),fontsize=5)
        ax.set(xlim=limits[:2],ylim=limits[2:],title=title,xlabel=('X world metres'if x==0 else'Z world metres'),ylabel=('Z world metres'if y==2 else'Y metres HKPD'));ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.15)
    fig.suptitle('PRIVATE exact-array diagram: podium orange; tower blue; ground tan; failed points red/blue; source contacts cyan.\nAll13312 source faces/all11645 ground facets retained. Drawing projections are context; strict97/138 +41 failure remains.',fontsize=10)
    fig.tight_layout();fig.savefig(DOC/'saved-array-source-plan-elevations-3200x2400.png');plt.close(fig)
    return dict(path=str((DOC/'saved-array-source-plan-elevations-3200x2400.png').relative_to(ROOT)),dimensions=[3200,2400],displayOnly=True,allSourceFaces=13312,allDrawnGroundFaces=11645,displayAxesPermutationOnly=True,noGeneratedGeometry=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    pins,a,layers,selection,terrain,summaries=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs'])
    def fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
    for folder in [attribution.DOC,physical.DOC,physical.metadata.capture.DOC]:
        result=read(folder/'result.json')
        with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    fence();DOC.mkdir(parents=True)
    runtime=read(physical.LOCAL/'runtime-geometry.json.gz');actors={r['uid']:r for r in read(physical.finite.DOC/'complete-actual-union-finite-delta.json.gz')['actors']};sources=[]
    for r in selection:
        row=next(q for q in runtime['rows']if q['uid']==r['uid']);pos=np.asarray(row['position'],dtype='<f8').reshape(-1,3);tri=pos[np.asarray(row['index'],dtype=np.int64)].reshape(-1,3,3);digest=physical.finite.sha(tri)
        expected=next(w['wholeWorldSHA256']for w in actors[r['uid']]['worlds']if w['mode']=='literal');assert digest==expected and len(tri)==r['triangles']and row['sourceSHA256']==r['sourceSHA256']
        sources.append(dict(uid=r['uid'],faces=len(tri),actualLiteralWorldSHA256=digest,asset=ref(ROOT/r['candidate']['path']),currentForm=r['source']['building']))
    replay=read(physical.metadata.capture.DOC/'actual-production-replay.json.gz');ground=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);assert len(ground)==11645 and physical.finite.sha(ground)==GROUND
    points=[dict(id=i+1,**q)for i,q in enumerate(layers['rows'])];face_map={}
    tower=next(q for q in runtime['rows']if q['uid']==attribution.TOWER);pos=np.asarray(tower['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(tower['index'],dtype=np.int64).reshape(-1,3)
    for r in points:
        for f in r['originalFailureVerbatim']['originalSourceFaces']:
            assert np.array_equal(pos[ix[f['faceIndex']]],f['vertices']);entry=dict(faceIndex=f['faceIndex'],vertices=f['vertices']);old=face_map.setdefault(f['faceIndex'],entry);assert old==entry
    faces=list(face_map.values());assert len(faces)==36
    literal=next(w for w in a['fourModeAuthenticatedMainContacts']if w['mode']=='literal');contacts=[dict(index=i,dimension=c['dimension'],sourceFaceA=c['sourceFaceA'],sourceFaceB=c['sourceFaceB'],points=[display_point(p)for p in c['exactPoints']],exactSourceContactVerbatim=c)for i,c in enumerate(literal['exactSourceOnlyContactsVerbatim']['contacts'])];assert len(contacts)==197
    for r in points:
        ids={f['faceIndex']for f in r['originalFailureVerbatim']['originalSourceFaces']}
        r['savedLiteralMainContactsOnIncidentFaceIDs']=[c['index']for c in contacts if c['sourceFaceB']in ids]
        r['contactElsewhereOnFaceDoesNotResolveThisFailedPoint']=True
    save(DOC/'main-contact-ground-exposure-summary.json',dict(rows=summaries,actualCompleteGroundSHA256=GROUND,actualFailuresVerbatim=ref(attribution.DOC/'actual41-highest-and-all-source-layers.json.gz'),original138SamplesVerbatim=ref(physical.DOC/'support-checks.json.gz'),actualFourModeContactsAndProofs=ref(attribution.DOC/'main41-source-contact-attribution.json.gz'),positiveDimensionalSourceAttachmentsAreContextOnly=True,areaInteriorNotQualified=True,strictInterfacePassed=False,physicalAccepted=False,installationApproved=False))
    save(DOC/'numbered41-faces-source-contact-key.json.gz',dict(points=points,incidentSourceFaces=faces,literalMainContactPrimitives=contacts,noFunctionalRoleInference=True,noLowerLayerWaiver=True))
    image=diagrams(runtime,ground,points,faces,contacts);pulse(True);save(DOC/'saved-array-diagram.json',image)
    save(DOC/'preview-input.json',dict(batch=BATCH,catalogue=ref(physical.LOCAL/'catalogue.json'),terrain=ref(ROOT/terrain['path']),replaces=terrain['replaces'],ground=dict(domain=terrain['bounds'],sha256=GROUND),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),sources=sources,points=points,incidentSourceFaces=faces,mainContactPrimitives=contacts,views=VIEWS,executionRefs=refs))
    command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))+'/'];p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-private-preview-log.json',dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0;pulse(True)
    report=read(DOC/'actual-private-source-preview.json');assert len(report['views'])==len(VIEWS)and not report['errors']and report['sourceInterpretationOnly']and not report['physicalAccepted']
    refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton_private_source_view_freezer').freeze(BATCH,'private-full-original-source-functional-interpretation-images-no-contact-approval',[check(q)for q in distinct_refs(refs)],dict(uids=physical.OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--capture-private-source-review-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
    uids=scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-private-view-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
