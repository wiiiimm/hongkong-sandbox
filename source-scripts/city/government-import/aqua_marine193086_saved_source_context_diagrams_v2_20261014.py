"""ROOT-only scientific saved-array diagrams; not GPU/installation acceptance."""
from pathlib import Path
import sys,json,subprocess,uuid,numpy as np
import aqua_marine193086_three_foundation_source_attribution_v1_20261014 as attribution
from aqua_saved_context_display_v1_20261014 import plot_xyz,exact_coordinate_context,closed_display_crop
from aqua_saved_context_solid_display_v2_20261014 import solid_collection
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ref,check,module=attribution.ref,attribution.check,attribution.module
BATCH='government-xl-aqua-marine193086-saved-source-three-face-diagrams-v2-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';JOB='c178a7c9e75560f2dc41c2f794b69572d12975d95c7f6724a90a5464ca836458'
def load():
    data=attribution.prior.load();r=read(attribution.DOC/'result.json');v=read(attribution.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    p=read(attribution.DOC/'exact-three-source-face-attribution.json.gz');assert [q['originalFaceID']for q in p['rows']]==[7525,7526,7527]and len(p['allOtherPartialBelowMinusHalfSourceFaceIDs'])==278 and len(p['allBelowMinusHalfSampleSites'])==281 and not p['strictFoundationAccepted']and not p['ordinaryWarningResolved']and not p['roleAssigned']
    terminal=read(PROPOSAL/'V1-terminal-context.json');assert terminal['outerExitCode']==terminal['supervisorExitCode']==1 and terminal['supervisorReportedLeaseReleased']and terminal['noExportedPNGs']
    assert not list((BASE/terminal['priorBatch']).glob('*.png'))
    refs=distinct_refs(r['evidenceRefs']+[ref(attribution.DOC/'result.json'),ref(attribution.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__)),ref(PROPOSAL/'V1-terminal-context.json')]+terminal['priorEvidenceRefs'])
    for q in refs:check(q)
    return data,r,p,refs

def schema_only():
    data,r,p,refs=load();return dict(passed=True,caller=ref(Path(__file__)),jobId=JOB,exactFailedFaceIDs=[7525,7526,7527],allPartialBelowFaces=278,fullLiteralFaces=22735,fullSavedOriginalFaces=22735,capturedGroundFaces=584,scope=data[-1],sevenDisplayExportsPlanned=True,noSourceDecodeGeometryComputationRenderDBLeaseWorker=True)

def render(packet,pulse):
    a=read(attribution.prior.LOCAL/'runtime-geometry.json.gz')['rows'][0];pos=np.asarray(a['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(a['index'],dtype=np.int64).reshape(-1,3);tri=pos[ix];ground=np.asarray(a['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(tri)==22735 and len(ground)==584 and attribution.prior.digest(tri.tobytes())==packet['completeLiteralWorldSHA256']and attribution.prior.digest(ground.tobytes())==packet['completeActualGroundSHA256']
    # Already-saved original ordinals, no source decode/new identity proof.
    parts=read(attribution.PARTS)['rows'][0];original=np.empty_like(tri);seen=set()
    for part in parts['parts']:
        pt=np.asarray(part['position'],dtype='<f8').reshape(-1,3)[np.asarray(part['index'],dtype=np.int64).reshape(-1,3)];assert len(pt)==len(part['originalFaceIds'])
        for i,t in zip(part['originalFaceIds'],pt):assert i not in seen;seen.add(i);original[i]=t
    assert seen==set(range(22735))and attribution.prior.digest(original.tobytes())==packet['completeSavedOriginalWorldSHA256']
    ids=[q['originalFaceID']for q in packet['rows']];partial=packet['allOtherPartialBelowMinusHalfSourceFaceIDs'];failed=tri[ids];lc=exact_coordinate_context(tri,ids);oc=exact_coordinate_context(original,ids);continuation=sorted({i for q in lc for i in q['exactXYZSharedVertexFaceIDs']})
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dl=failed.min((0,1))-np.array([2.,1.,2.]);du=failed.max((0,1))+np.array([2.,4.,2.]);wl=np.minimum(tri.min((0,1)),original.min((0,1)));wu=np.maximum(tri.max((0,1)),original.max((0,1)));margin=np.maximum((wu-wl)*.025,.1);wl-=margin;wu+=margin;views=[]
    definitions=[('saved-original-full','original',False,False,28,-58,1.),('actual-literal-full','literal',False,False,28,-58,1.),('all-278-partial-below-context','literal',False,True,38,-58,.15),('three-face-solid-ground','literal',True,False,22,-58,1.),('three-face-exposed-ground','literal',True,False,22,-58,.12),('exact-XYZ-continuation','literal',True,False,18,120,.12),('all-278-partial-plan','literal',False,True,90,-90,.12)]
    for kind,world,detail,show_partial,elev,azim,ga in definitions:
        mesh=original if world=='original'else tri;take=closed_display_crop(mesh,dl,du)if detail else np.arange(len(mesh));gt=closed_display_crop(ground,dl,du)if detail else np.arange(len(ground));lower=dl if detail else wl;upper=du if detail else wu
        fig=plt.figure(figsize=(18,12),dpi=100);ax=fig.add_subplot(111,projection='3d');ax.set_proj_type('ortho')
        def surface(t,color,alpha=1.,edge='none',width=.1):
            if len(t):ax.add_collection3d(solid_collection(t,color,alpha,edge,width))
        surface(mesh[take],'#b9bec2');surface(ground[gt],'#c7b78c',ga,'#988766',.12)
        if show_partial:surface(mesh[partial],'#e79a32',1.,'#c27512',.25)
        if kind=='exact-XYZ-continuation':surface(mesh[sorted(set(continuation)-set(ids))],'#44a4bc',1.,'#276a80',.25)
        surface(mesh[ids],'#c5266b',1.,'#950747',1.)
        for face,t in zip(ids,mesh[ids]):
            c=plot_xyz(t.mean(0));ax.scatter(*c,color='#c5266b',s=30,depthshade=False);ax.text(*c,str(face),color='#950747',fontsize=9)
        pl,pu=plot_xyz(lower),plot_xyz(upper);ax.set_xlim(pl[0],pu[0]);ax.set_ylim(pl[1],pu[1]);ax.set_zlim(pl[2],pu[2]);ax.set_box_aspect(pu-pl);ax.view_init(elev=elev,azim=azim);ax.set_xlabel('world X / m');ax.set_ylabel('world Z / m');ax.set_zlabel('HKPD Y / m');ax.set_title('Aqua Marine | '+kind+' | original faces 7525 / 7526 / 7527')
        fig.text(.025,.035,'Scientific saved-array diagram. Magenta: 3 failed faces; orange: ALL 278 partial-below faces in context views; cyan: exact XYZ incidences.\nGround '+('opaque: buried geometry may be occluded.'if ga==1 else 'translucent solely to expose buried context; depth ordering is illustrative.')+' Detail boxes are display crops only; marker sizes are locators.\nSaved original / actual literal worlds labelled separately. Unshaded solid diagram colors are not authored GPU material. Source roles UNASSIGNED; strict foundation FALSE; burial warning UNRESOLVED.\nCoordinate incidence is not a topology, attachment or support certificate.',fontsize=9);fig.subplots_adjust(left=0,right=1,top=.94,bottom=.15);file=DOC/(kind+'-1800x1200.png');fig.savefig(file,dpi=100);plt.close(fig)
        pulse(force=True);views.append(dict(id=kind,image=ref(file),worldRepresentation=world,sourceFaceIDsSubmitted=take.tolist(),completeAssembly=not detail,all278PartialContextSubmitted=show_partial,partialFaceIDs=partial if show_partial else[],displayOnlyClosedAABBCrop=detail,displayWorldLimits=[lower.tolist(),upper.tolist()],capturedGroundFacetIDsSubmitted=gt.tolist(),groundAlpha=ga,occludedFacesMayBeHidden=True,originalFailedFaceIDs=ids,axesMapping='plot(X,Z,Y), HKPD Y vertical',actualGPURender=False))
    save(DOC/'saved-source-diagrams.json',dict(views=views,actualArrayRef=ref(attribution.prior.LOCAL/'runtime-geometry.json.gz'),exactAttribution=ref(attribution.DOC/'exact-three-source-face-attribution.json.gz'),savedOriginalSourceCensus=ref(attribution.PARTS),literalWorldSHA256=packet['completeLiteralWorldSHA256'],savedOriginalWorldSHA256=packet['completeSavedOriginalWorldSHA256'],groundSHA256=packet['completeActualGroundSHA256'],exactLiteralCoordinateContext=lc,exactSavedOriginalCoordinateContext=oc,all278PartialBelowFaceIDs=partial,rawFoundationVerbatim=packet['rawFoundationVerbatim'],minimumWholeSurfaceGapVerbatim=packet['minimumWholeSurfaceGapVerbatim'],originalMaterialAndNodeLineage=packet['exactSourceIndexBinding'],roleAssigned=False,noAreaAdjacencyOrSmallFacetWaiver=True,noNewSourceDecodeOrIdentityProof=True,strictFoundationAccepted=False,ordinaryWarningResolved=False,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));data,r,packet,refs=load();refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==attribution.prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',r)
    DOC.mkdir();render(packet,pulse);refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence();module(attribution.prior.FREEZER,'aqua_three_diagram_freezer').freeze(BATCH,'saved-source-diagrams-private-scientific-context-no-acceptance',[check(q)for q in refs],dict(uids=[attribution.prior.UID],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--render-saved-three-face-context-only'in sys.argv and not DOC.exists()and not LOCAL.exists();data,*_=load();scope=data[-1];prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-three-source-diagram-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
