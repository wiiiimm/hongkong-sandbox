"""UNEXECUTED historical saved source-region nominee; no current acceptance."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
import polyu_append_source_region_residual_repair_v1_draft_20261014 as helper
import polyu_compact_runtime_mesh_projection_v1_draft_20261014 as compact

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-append-source-region-residual-repair-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
GAP=BASE/'government-xl-polyu-saved-rectangle-gap-attribution-v1-20261014'
CAP=BASE/'government-xl-polyu-parent-cell-actual-production-capture-v4-20261014'
JOBS={GAP:'0081d773c62c80d053b81406714cad5f6dfec57a61fddf298fd29dce51afe894',CAP:'59491c7701e48dca8e907808ea8e0b487feaa5f6d8a8b6fbb57ca57fc733c6b2'}
HISTORICAL='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q):
    p=ROOT/q['path'];assert ref(p)==q,q['path'];return p
def fence(refs):
    for q in distinct_refs(refs):check(q)

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__));fence(pins['codeRefs']+pins['inputRefs'])
    receipts=[]
    for folder,jid in JOBS.items():
        receipt=read(folder/'result.json');cert=read(folder/'ROOT-VERIFIED.json')
        assert receipt['jobId']==cert['jobId']==jid and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased'];receipts.append(receipt)
    gap=read(GAP/'saved-coverage-region-and-guard-attribution.json.gz');inp=read(CAP/'input.json.gz')
    assert gap['historicalCapturedManifestSHA256']==inp['currentManifestSHA256']==HISTORICAL
    assert gap['completeNativeFacets']==147096 and len(gap['regions'])==54 and all(q['kind']=='missing'for q in gap['regions'])
    measure=gap['measurement'];assert measure['measuredMissingAreaM2']==0.0039889964664034565 and measure['measuredOutsideAreaM2']==0
    assert measure['existingCoverageToleranceM2']==0.00294 and measure['validatorIncludedFaces']==146987
    nref=inp['newNomination'];assert nref==gap['fullNominationReference'];nom=read(check(nref))
    assert nom['schema']=='private-source-plane-preserving-five-current-parent-mask-parent-cell-nomination-v4'
    mesh=nom['newNativeMesh'];binding=compact.mesh_binding(mesh)
    assert binding==inp['completeMeshBinding']and binding['completeIndexedFaces']==147096 and binding['completePositionVertices']==583413
    assert len(nom['completeOldPrivateMapping'])==3214 and len(nom['candidateFaceProvenance'])==147096
    assert nom['all8011PreviousPackedFacetsUnchanged']and nom['oldPositionBufferRetainedIncludingUnusedVertices']and nom['all3214OldMappingsVerbatim']
    domain=inp['fullParentDomain'];assert domain==[2002.5,-2067.5,2212.5,-1927.5]
    for i,row in enumerate(nom['completeOldPrivateMapping']):
        assert row['oldPrivateFace']==i and type(row['newCandidateFaces'])is list and all(type(j)is int and 0<=j<8011 for j in row['newCandidateFaces'])
        lineage=row['previousLineageVerbatim'];assert len(lineage['exactProposedPoints'])==len(lineage['exactOriginalPoints'])==3
        assert all(len(p)==3 for p in lineage['exactProposedPoints']+lineage['exactOriginalPoints'])
        for k in ['classification','exactAlphaAffine','globalOriginalTerrainFacet']:assert k in lineage
    validator=read(CAP/'real-validator-outcome.json');assert not validator['passed']and validator['actualFailure']['message']=='Native mesh does not cover the exact parent rectangle'
    return pins,receipts,gap,inp,nom,binding,domain,nref

def schema_only():
    pins,_,gap,_,_,binding,domain,_=load();fence(pins['codeRefs']+pins['inputRefs'])
    return dict(passed=True,caller=ref(Path(__file__)),historicalCapturedManifestSHA256=HISTORICAL,oldCompleteMeshBinding=binding,
        completeOldMappings=3214,completeMissingLocators=len(gap['regions']),fullParentDomain=domain,
        canonicalResources=['immutable-source-proof:'+BATCH],noPackingCoverageDBLeaseOrCurrentAcceptance=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
    pins,receipts,gap,inp,nom,binding,domain,nref=load();assert lease['resources']==['immutable-source-proof:'+BATCH]
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    validation=read(check(prep['helperValidationRef']));assert validation['passedTests']==8 and validation['failedTests']==0 and validation['exitCode']==0
    assert validation['executedCodeRefs']==[ref(Path(helper.__file__)),ref(HERE/'test_polyu_append_source_region_residual_repair_v1_draft_20261014.py')]
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[prep['helperValidationRef'],ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder,jid in JOBS.items():assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',read(folder/'result.json'))
    last=time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    def end_fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert reservations.owns(lease)
    end_fence();DOC.mkdir();targets,selection=helper.select_targets(gap,nom)
    save(DOC/'complete-source-region-selection.json.gz',serial(dict(targets=targets,selection=selection,previousNomination=nref,savedGapAttributionRef=ref(GAP/'saved-coverage-region-and-guard-attribution.json.gz'))))
    accounts=[];shared={}
    for i,target in enumerate(targets):
        account=helper.enclose_target(target,domain,shared);accounts.append(account)
        save(DOC/'source-region-progress'/(str(i).zfill(5)+'.json.gz'),serial(account));pulse()
        print(json.dumps(dict(sourceRegionsCompleted=i+1,total=len(targets),oldPrivateFace=target['oldPrivateFace'],outsidePolygon=target['outsidePolygon'])),flush=True)
    mesh,append_account=helper.append_pieces(nom['newNativeMesh'],accounts);new_binding=compact.mesh_binding(mesh);pulse()
    # Existing complete mappings remain immutable at the exact bound original
    # nominee; no huge provenance document is copied into a Node runtime input.
    output=dict(schema='private-polyu-append-complete-legacy-source-region-nomination-v1',previousFullNomination=nref,
        previousCompleteMeshBinding=binding,newCompleteMeshBinding=new_binding,newNativeMesh=mesh,
        originalPositionBufferAndIndexPrefixUnchanged=True,oldFaceProvenanceRange=[0,147096],completeOldMappingCount=3214,
        unchanged8011LiteralAndSourceOutsideFacets=True,unchanged1485First832Prefix=True,
        appendAccount=append_account,sourceRegionAccounts=accounts,selection=selection,fullParentDomain=domain,
        historicalCapturedManifestSHA256=HISTORICAL,currentAcceptance=False,physicalAccepted=False,installationApproved=False,
        freshFullProductionRectangleSamplerGuardsFiniteForeignNativeMAXValidatorAndCurrentDeltaQualificationPending=True)
    save(DOC/'private-append-only-source-region-nomination.json.gz',serial(output))
    save(DOC/'complete-preservation-and-counts.json',dict(previousMesh=binding,newMesh=new_binding,selectedSourceRegions=len(targets),appendedFaces=len(append_account['appendedFaces']),exactAlreadyPresent=len(append_account['exactExistingRepresentations']),allOldGeometryAndUnusedPositionsUnchanged=True,all8011OldTripletsIncludingLiteralCurrentUnchanged=True,currentAcceptance=False))
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);end_fence()
    spec=importlib.util.spec_from_file_location('append_source_region_freezer',FREEZER);freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
    result=freezer.freeze(BATCH,'historical-saved-source-plane-append-only-private-nomination-v1',[check(q)for q in refs],dict(uids=receipts[0]['uids'],sourceOnly=True,historicalCapturedManifestSHA256=HISTORICAL,
        currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,publication=False,
        oldFacets=147096,newFacets=new_binding['completeIndexedFaces'],selectedCompleteSourceRegions=len(targets),originalModelGeometryChanges=0))
    end_fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),newNativeFacets=new_binding['completeIndexedFaces'])),flush=True)

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:owned();return
    assert '--nominate-append-only-source-regions'in sys.argv and not DOC.exists()and not LOCAL.exists()
    load();LOCAL.mkdir(parents=True);claim=reservations.claim('polyu-source-append-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
    assert claim['ok'];lease={k:claim[k]for k in ['ok','owner','claimToken','batch','resources','generations']};save(LEASE,lease)
    try:
        p=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned']);assert p.returncode==0,p.returncode
    finally:
        if reservations.owns(lease):reservations.release(lease)
if __name__=='__main__':main()
