"""Bind inspected Yoho previews and exact native deck context; no installation approval."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-yoho-'
BATCH=P+'five-current-review-checkpoint-v2-20261024';BROWSER=P+'five-unapproved-preview-v2-20261024'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(batch,path):
        if batch not in pins:
            job,pins[batch]=authenticate(BASE/batch);jobs[batch]=job['jobId'];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=P+'five-inset-runtime-v1-20261024';selection=take(runtime,BASE/runtime/'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==5
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for name in ['five-current-model-scope-v1','five-current-identity-v1','five-current-basic-contacts-v1','56771-downward-context-v1','five-original-pair-context-v1']:
        batch=P+name+'-20261024';take(batch,BASE/batch/('exact-context.json'if name=='56771-downward-context-v1'else'summary.json'))
    native=P+'five-native-contacts-v1-20261024';ns=take(native,BASE/native/'summary.json');assert all(not p['rawCurrentNativeEntry'].get('supportDependencies')and not p['rawCurrentNativeEntry'].get('retainedBasicSupportDependencies')for p in ns['rows'])
    attrs=P+'five-current-attributes-v1-20261024';a=next(r for r in take(attrs,BASE/attrs/'attributes.json.gz')['rows']if r['uid']=='landsd/231756:0');na=next(r for r in take(native,BASE/native/'native-attributes.json.gz')['rows']if r['uid']=='landsd/121143:0');areas=[]
    for mode,field in [('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        ts=[np.asarray(z[field]).reshape(-1,3)[np.asarray(z['completeOriginalIndex']).reshape(-1,3)]for z in [a,na]];proof=take(native,BASE/native/('231756:0--121143:0--'+mode+'.json.gz'));cs=[c for c in proof['contacts']if c['dimension']==2];assert len(cs)==10;polys=[];heights=set();normals=[]
        for c in cs:
            points=np.asarray([[float(Fraction(v))for v in point]for point in c['exactPoints']]);polys.append(shapely.Polygon(points[:,[0,2]]).convex_hull);heights.update(points[:,1].tolist());ny=[]
            for t,i in zip(ts,[c['sourceFaceA'],c['sourceFaceB']]):
                f=t[i];n=np.cross(f[1]-f[0],f[2]-f[0]);ny.append(float(n[1]/np.linalg.norm(n)))
            assert ny==[1.,-1.];normals.append(ny)
        assert heights=={17.82699966430664};areas.append(dict(mode=mode,contactPairs=len(cs),horizontalAreaM2=shapely.union_all(polys).area,heightHKPD=sorted(heights),normalYPairs=normals,qualification='Coincident original podium upper surface and installed tower underside; raw Float32 contact polygons retained. Orientation and height evidence only, no general collision exemption.'))
    images=[];sheets=[];reports=[]
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    for width in [1280,390]:
        path=BASE/BROWSER/str(width)/'staged-browser.json';report=take(BROWSER,path);assert report['passed']and not report['errors'];reports.append(ref(path))
        views=[v for v in report['views']if 'time'in v];retained=report['retainedNativeOwnViews'];assert len(views)==10 and len(retained)==6
        for v in views:
            assert v['sourceSHA256']==sources[v['uid']]and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']
        for v in views+retained:
            image=path.parent/v['file'];take_image=ref(image);assert take_image['sha256']==pins[BROWSER][take_image['path']];refs.append(image);images.append(dict(**take_image,uid=v['uid'],width=width,time=v['time']))
        for time in ['1500','2200']:
            sheet=BASE/(P+'five-root-inspection-v2-20261024')/str(width)/(str(width)+'-'+time+'.jpg');assert sheet.is_file();refs.append(sheet);sheets.append(ref(sheet))
    assert len(images)==32
    plot=BASE/(P+'56771-downward-context-v1-20261024')/'original-local-context.png';assert digest(plot.read_bytes())==pins[P+'56771-downward-context-v1-20261024'][str(plot.relative_to(ROOT))];refs.append(plot)
    yaw=P+'56771-original-yaw-v1-20261024';take(yaw,BASE/yaw/'proof.json')
    inspection=dict(reviewer='ROOT',imagesActuallyViewed=images,inspectionSheetsActuallyViewed=sheets,localSourcePlotActuallyViewed=ref(plot),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualFinding='All32 full-frame source/retained images inspected through four sheets; mobile original podium daytime PNG also inspected at original resolution. V1 mobile daytime podium was fully foreground-occluded and rejected. V2 changes only its capture direction to[1,3,-1]; podium terraces, holes and tower relationships are now visible. Tower frames retain partial foreground basic-tower occlusion, especially Blocks2/3, and ordinary tower-on-podium occlusion; visible rooflines and facade bodies are coherent. Originals remain dark at night with proceduralWindows false, while legacy neighbours retain bright windows. This is bounded visual evidence, not a claim of photographic/engineering accuracy or complete physical approval.',sourceGeometryChanges=0,sourcePoseChanges=0,productionChanged=False,visualInspectionComplete=True,physicalAcceptance=False,identityAccepted=False,installationApproved=False)
    save(out/'ROOT-EXPORT-INSPECTION.json',inspection);save(out/'native-deck-area-context.json',dict(rows=areas,installationApproved=False))
    remaining=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifestSHA256=selection['manifestSHA256'],completedJobs=jobs,visualInspectionComplete=True,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,remaining=['Finish bounded exact-source architectural/identity and neighbour interpretation, retaining all raw negatives.','Bind full current physical review, three native dependencies to original podium and unchanged retained native metadata.','Prepare support-aware qualification preserving the tested terrain target UID231756 only and all global retained-basic guards.','Run guarded publication/live verification and independently compare all521 rows/all6876previous native actors before installation credit.'],fixedXLInstalled=343,fixedXLUnfinished=178,fixedXLTotal=521,proposedSourceActors=5,expectedFixedXLDeltaUnverified=4,qualification='Evidence checkpoint only. V2 browser and exact diagnostics do not install models. No optimisation or AI geometry modelling.')
    save(out/'remaining-work.json',remaining)
    module('yoho_review_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-yoho-inspected-preview-and-remaining-installation-obligations',list(dict.fromkeys(refs)),remaining)

if __name__=='__main__':main()
