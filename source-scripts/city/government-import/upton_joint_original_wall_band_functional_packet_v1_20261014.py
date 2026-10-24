"""ROOT-only36 actual source-face descriptors; scoped proposed functional context."""
from pathlib import Path
import sys,json,time,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_joint_original_private_source_review_v1_20261014 as review
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_wall_band_functional_context_v1_20261014 import face_descriptor,proposal
physical=review.physical;ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-joint-original-wall-band-functional-packet-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PREVIEW_JOB='b3694f4081686c35bcb8716282d699890a5fac25af20f4e5891df02cbea66611'

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    r=read(review.DOC/'result.json');v=read(review.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==PREVIEW_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    key=read(review.DOC/'numbered41-faces-source-contact-key.json.gz');assert len(key['points'])==41 and len(key['incidentSourceFaces'])==36 and len(key['literalMainContactPrimitives'])==197
    exposed=read(review.DOC/'main-contact-ground-exposure-summary.json');assert exposed['actualCompleteGroundSHA256']==review.GROUND and not exposed['strictInterfacePassed']
    for row in exposed['rows']:assert not row['positiveContactsWithUnprovedChordOrLineExposure']and row['strictlyExposedWholeLineContacts']==(197 if row['mode']in ['original','literal']else 198)
    finite=read(physical.finite.DOC/'complete-actual-union-finite-delta.json.gz');assert finite['newGroundSHA256']==review.GROUND and finite['completeNewDrawnFaces']==11645 and finite['completeNativeActorScope']==6650 and len(finite['completeBasicRows'])==1911
    assert {r['uid']for r in finite['actors']}==set(physical.OWNED+[physical.SECONDARY,physical.RETAINED])
    assert sum(next(w['completeFaces']for w in r['worlds']if w['mode']=='original')for r in finite['actors']if r['uid']in physical.OWNED)==13312
    assert sum(len(r['completeScope']['selectedFaceIDs'])for r in finite['completeBasicRows'])==2114
    for actor in finite['actors']:
        for world in actor['worlds']:
            f=world['findings'];assert not f['currentClearCandidateUnproved']
            if actor['uid']in physical.OWNED:assert not f['candidateUncovered']and not f['candidateOrdinaryUnproved']
    affected=[r for r in finite['completeBasicRows']if r.get('findings')];assert len(affected)==52
    for r in affected:assert all(not w['findings']['currentClearCandidateUnproved']for w in r['findings']['worlds'])
    foundations=read(physical.DOC/'foundation.json');assert foundations['existingCompleteCompoundContractUnchanged']and len(foundations['rows'])==2
    for r in foundations['rows']:
        f=r['foundation'];assert r['strictFoundationAccepted']and f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedUpwardTriangles']==0 and f['fullyBuriedAreaFraction']==0
    validation=read(physical.DOC/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==2 and validation['exceptions']==0
    raw=read(physical.DOC/'current-physical-raw-gates.json');strict=read(physical.DOC/'support-checks.json.gz')['rows'][0]['interface'];assert len(strict['unresolved'])==41
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
    return pins,key,exposed,finite,foundations,validation,raw,strict

def schema_only():
    p,k,e,f,ff,v,r,s=load();return dict(passed=True,caller=ref(Path(__file__)),actual36OriginalFaceIDs=sorted(q['faceIndex']for q in k['incidentSourceFaces']),rawReasons=r['rawReasons'],strictInterfacePassed=False,noWorldArithmeticDescriptorsDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    pins,key,exposed,finite,foundations,validation,raw,strict=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs'])
    def fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
    for folder in [review.DOC,physical.DOC,physical.finite.DOC]:
        result=read(folder/'result.json')
        with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    fence();DOC.mkdir(parents=True)
    # Reindex immutable saved four-mode streams; no decoder/source transform,
    # finite selection, contact or ground numerical proof is replayed.
    baseline=physical.finite.baseline;attrs=read(baseline.CAP/'whole-domain-current-actors.json.gz');original={r['uid']:r for r in read(baseline.ORIGINAL)['rows']};actors={r['uid']:r for r in finite['actors']};world_bindings=[];descriptors=[];ids=sorted(q['faceIndex']for q in key['incidentSourceFaces'])
    selection={r['uid']:r for r in read(physical.DOC/'selection.json.gz')['rows']}
    for row in attrs['rows']:
        uid=row['uid']
        if uid not in physical.OWNED:continue
        ix=np.asarray(row['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'original':np.asarray(original[uid]['completeOriginalBinary64WorldTriangles'],dtype='<f8').reshape(-1,3,3)}
        for mode,field in zip(baseline.MODES[1:],baseline.FIELDS):worlds[mode]=np.asarray(row[field],dtype='<f8').reshape(-1,3)[ix]
        for mode in baseline.MODES:
            w=worlds[mode];saved=next(r for r in actors[uid]['worlds']if r['mode']==mode);assert physical.finite.sha(w)==saved['wholeWorldSHA256']and len(w)==saved['completeFaces']and row['sourceSHA256']==actors[uid]['sourceSHA256']==selection[uid]['sourceSHA256']
            world_bindings.append(dict(uid=uid,buildingCSUID=selection[uid]['candidate']['entry']['buildingCSUID'],sourceSHA256=row['sourceSHA256'],mode=mode,wholeWorldSHA256=saved['wholeWorldSHA256'],completeOriginalFaces=len(w),completeOriginalIndexCanonicalBinary64SHA256=physical.finite.sha(ix),allUnusedPositionAttributesRetainedInInput=ref(baseline.CAP/'whole-domain-current-actors.json.gz')))
            if uid==review.attribution.TOWER:descriptors.append(dict(mode=mode,wholeWorldSHA256=saved['wholeWorldSHA256'],faces=[face_descriptor(i,w[i].tolist())for i in ids]))
        pulse(True)
    assert len(world_bindings)==8 and len(descriptors)==4 and all(len(r['faces'])==36 for r in descriptors)
    unmatched=[r['id']for r in key['points']if not r['savedLiteralMainContactsOnIncidentFaceIDs']];disposition=proposal(raw['rawReasons'],strict,unmatched,True)
    save(DOC/'exact36-four-world-source-face-descriptors.json.gz',dict(rows=descriptors,completeSourceBindings=world_bindings,sourceGeometryChanges=0,exactNonzeroProjectedAreasNeverSnapped=True,verticalBandIsFunctionalInterpretationNotAllExactNormalYZeroClaim=True))
    save(DOC/'proposed-functional-wall-band-disposition.json',dict(**disposition,scope=dict(uids=physical.OWNED,sourceBindings=world_bindings,currentManifestSHA256=physical.CURRENT,completeActualGroundSHA256=review.GROUND,completeActualDrawnGroundFaces=11645,terrainSHA256=review.TERRAIN),actual41FacesAndPointAssociationVerbatim=ref(review.DOC/'numbered41-faces-source-contact-key.json.gz'),full13312FourWorldOrdinaryAndAll6650Native1911BASIC52RegressionProof=ref(physical.finite.DOC/'complete-actual-union-finite-delta.json.gz'),bothCompleteCompoundFoundationsVerbatim=ref(physical.DOC/'foundation.json'),wholeSourcePickingCollisionAndLoaderVerbatim=ref(physical.DOC/'validation.json'),source197OriginalLiteralAnd198Float32ExposedLinesVerbatim=ref(review.DOC/'main-contact-ground-exposure-summary.json'),reviewedDisplayV1Verbatim=ref(review.DOC/'actual-private-source-preview.json'),allHistoricalNegativesRetained=ref(physical.DOC/'current-physical-raw-gates.json'),description='The reviewed unchanged assembly joins the tower facade to a stepped multilayer podium. The41 samples are lower edges on these36 authored lower facade-band faces; global bottom/max projected roof tests do not identify41 independent support feet. Actual97/138+41 remains false. Exact source attachments elsewhere and both complete compound foundations are preserved source/placement facts, not independent support proof for13 unmatched points. Proposed applicability is only these two exact original sources/current ground; no architectural/engineering root certificate or topology inference.',remainingRequiredGates=['ROOT exact-source functional review','displayV2 clean full-indexed source framing','current physical-source applicability adapter','staged/live desktop/mobile day/night actual source picking/collision/sampler/load/retry','guarded publication and installed ledger/Neon readback']))
    refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton_wall_band_descriptor_freezer').freeze(BATCH,'exact-source-wall-band-descriptors-proposed-functional-applicability-no-strict-pass',[check(q)for q in distinct_refs(refs)],dict(uids=physical.OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--prepare-exact-wall-band-functional-context-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load();uids=review.scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-functional-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
