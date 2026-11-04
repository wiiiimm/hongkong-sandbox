"""Exact-source platform identity and unchanged companion support revalidation."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-v5-identity-support-review-20261019';DOC=BASE/BATCH
NAMES=['extent-closeup-v1','component-support-review-v1','eight-runtime-v1','eight-runtime-v2','eight-foundations-v1','eight-foundations-v2','eight-neighbours-v2','component-identity-review-v1']
def main():
    assert not DOC.exists();folders={n:BASE/('government-xl-lai-chi-kok-'+n+'-20261019')for n in NAMES};refs=[Path(__file__)];pins={}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for d in folders.values():
            r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
            for e in r['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    old=read(HERE/'local'/folders['eight-runtime-v1'].name/'runtime-geometry.json.gz')['rows'];new=read(HERE/'local'/folders['eight-runtime-v2'].name/'runtime-geometry.json.gz')['rows'];assert len(old)==len(new)==8
    byold={r['uid']:r for r in old};bynew={r['uid']:r for r in new};assert set(byold)==set(bynew)
    podium='landsd/281463:0';unchanged=[]
    for uid,a in byold.items():
        b=bynew[uid];assert a['sourceSHA256']==b['sourceSHA256']and a['position']==b['position']and a['index']==b['index']
        for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
            name=uid.split('/')[1]+'-'+mode+'.json';fa=read(folders['eight-foundations-v1']/name);fb=read(folders['eight-foundations-v2']/name)
            assert fa['wholeWorldSHA256']==fb['wholeWorldSHA256']
            assert [x['faceId']for x in fa.get('buriedFaces',[])]==[x['faceId']for x in fb.get('buriedFaces',[])]
        if uid==podium:continue
        # Preserve multiplicity and vertex order, allowing only triangle enumeration order to differ.
        ta=sorted(map(tuple,np.asarray(a['drawnGroundGeometry']).reshape(-1,9)));tb=sorted(map(tuple,np.asarray(b['drawnGroundGeometry']).reshape(-1,9)));assert ta==tb
        unchanged.append(dict(uid=uid,sourceSHA256=a['sourceSHA256'],completeLocalTerrainTriangles=len(ta),completeLocalTerrainSHA256=digest(np.asarray(ta,dtype='<f8').tobytes()),modelAndPlatformGeometryUnchanged=True))
    support=read(folders['component-support-review-v1']/'ROOT-SUPPORT-REVIEW.json');assert support['sourceSpecificComponentSupportInterpretationAccepted']and set(support['uids'])=={r['uid']for r in unchanged}
    neighbours=read(folders['eight-neighbours-v2']/'summary.json');assert not neighbours['basicReasons']and not neighbours['unresolvedNatives']
    identitypath=BASE/'government-xl-next-five-original-identity-v1-20261018/281463:0/identity.json';raw=read(identitypath);assert str(identitypath.relative_to(ROOT))in pins
    assert raw['sourceSHA256']==bynew[podium]['sourceSHA256']=='1480540e0a32849425d5238eeea7ecb3a7124633226c1eae9cab2d041b968d86'
    assert raw['originalOwnership']['sourceGraphVerified']and raw['freshCurrentIdentity']['exactObjectAndCSUID']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']
    assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
    assert raw['freshCurrentIdentity']['sourceExcessCoveredByUnrelatedFormsM2']==0
    view=folders['extent-closeup-v1'];close=read(view/'summary.json');assert close['currentSourceAndFootprintUnchanged']and close['farFaces']==106
    image=view/'extent-closeup.png';assert str(image.relative_to(ROOT))in pins
    decision=dict(reviewer='Codex ROOT',uid=podium,sourceSHA256=raw['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],platformIdentityAccepted=True,rawIdentityReasons=raw['reasons'],rawIdentityProofSHA256=digest(identitypath.read_bytes()),sourceSpecificComponentSupportInterpretationAccepted=True,unchangedCompanionSupportDomains=unchanged,requiredAssemblySources={uid:r['sourceSHA256']for uid,r in bynew.items()},inspectedImage=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()),actuallyViewedByCoordinator=True),observations=[
        'Exact object, CSUID, original source graph and geographic-cell evidence identify the main platform. Its 106 far facets are a low terminal portion of a visibly contiguous sloping/stepped source appendage in both inspected views. No specific architectural function is inferred.',
        'The original source extends 13.678m beyond its recorded footprint. The excess overlaps no unrelated footprint under the existing identity classification. Other forms do intersect within the wider platform; their actual affected-domain checks are preserved rather than claiming no neighbouring structures.',
        'Accept the platform source identity with the raw extent warnings retained. This is not an extent-threshold increase, geometry edit, footprint repair or name assignment.',
        'For all seven companions, complete current local terrain triangle multisets, source geometry and supporting platform geometry are unchanged. The prior finite contact/embedded-wall interpretation is revalidated only within these identical support domains and current renderer evidence. The changed main-platform terrain is explicitly excluded from that transfer.'
    ],qualification='Exact eight-source assembly and current V5 terrain only. Main-platform grade, browser acceptance and publication remain separate.',mainPlatformGradeAccepted=False,installationApproved=False,publicationApproved=False,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True)
    save(DOC/'ROOT-IDENTITY-SUPPORT-REVIEW.json',decision)
    module('v5_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'v5-platform-identity-and-identical-companion-support',list(dict.fromkeys(refs)),dict(uids=sorted(bynew),platformIdentityAccepted=True,sourceSpecificComponentSupportInterpretationAccepted=True,mainPlatformGradeAccepted=False,installationApproved=False))
    print('Platform identity accepted; seven exact unchanged support domains revalidated.',flush=True)
if __name__=='__main__':main()
