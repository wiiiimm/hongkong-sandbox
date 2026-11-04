"""Record completed saved-source diagrams; no identity or installation approval."""
from pathlib import Path
import hashlib,importlib.util,json,sys
from run import ROOT,HERE,read,save,connect

BASE=ROOT/'docs/astra-city/government-import'
PACKET=BASE/'government-xl-lai-chi-kok281463-far-main-source-context-draft-v1-20261013'
OUTPUT=PACKET/'saved-source-context-output-v1'
BATCH='government-xl-lai-chi-kok281463-far-main-saved-context-receipt-v1-20261013'
DOC=BASE/BATCH
PRIOR='26011fd1f69bb7190fcb7d4852a188899f3c34888f8c4506bb69b902922cc3be'
def checked(path,expected):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,path
    return path
def main():
    assert sys.argv[1:]==['--record-completed-source-context-only'] and not DOC.exists()
    contract=read(PACKET/'input-contract.json');terminal=read(OUTPUT/'terminal.json')
    assert terminal['complete'] and terminal['allInputHashesUnchanged'] and terminal['noDB'] and terminal['noLease'] and not terminal['currentAcceptance']
    paths=[checked(ROOT/p,h)for p,h in contract['filePins'].items()]
    paths+=[checked(PACKET/'input-contract.json',terminal['contractSHA256']),checked(PACKET/'saved-far-main-context-draft-v1.py',terminal['codeSHA256']),checked(OUTPUT/'context.json',terminal['contextSHA256']),OUTPUT/'terminal.json',Path(__file__)]
    for pin in terminal['actualExports']:
        path=checked(ROOT/pin['path'],pin['sha256']);assert pin['dimensions']==[3000,1800];paths.append(path)
    prior=read(ROOT/contract['resultPath']);assert prior['jobId']==PRIOR
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PRIOR,)).fetchone()==('complete',prior)
    paths+=[checked(ROOT/p['path'],p['sha256'])for p in prior['evidenceRefs']]
    context=read(OUTPUT/'context.json')
    assert len(context['farOriginalFaceIds'])==106 and len(context['exactEdgeAdjacentOriginalFaceIds'])==11 and len(context['completeLocalBoxFaceIds'])==334
    assert len(context['sevenIndependentForeignActorsVerbatim'])==7
    assert all(context[k]is False for k in ['sourceRoleAccepted','identityAccepted','physicalAccepted','currentAcceptance'])
    DOC.mkdir(parents=True)
    save(DOC/'source-context-assessment.json',dict(uid=context['uid'],sourceSHA256=context['sourceSHA256'],worldTrianglesSHA256=context['worldTrianglesSHA256'],contextReference={'path':str((OUTPUT/'context.json').relative_to(ROOT)),'sha256':terminal['contextSHA256']},sourceFacetDescription='Compact low terminal segment/return connected to the larger original main podium/site mesh; exact architectural function not established.',mainComponentFaces=34463,farFaceCount=106,literalEdgeAdjacentFaces=11,completeLocalViewFacets=334,allSevenIndependentForeignActorsRetained=True,primaryPlanRegistrationEstablished=False,sourceRoleAccepted=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,renderLimitation='The isolated diagram footer ends beyond the right raster edge; complete caveats are retained in context.json and METHOD.md. No precision or acceptance credit is drawn from the diagram.',nextStep='Resolve exact site-feature identity where needed and retain all independent current-placement, support, foreign, runtime and browser checks.'))
    freezer=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
    spec=importlib.util.spec_from_file_location('lck_completed_context_freezer',freezer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.freeze(BATCH,'completed-saved-original-far-main-source-context-only',paths,dict(uids=[context['uid']],sourceOnly=True,sourceRoleAccepted=False,identityAccepted=False,physicalAccepted=False,currentAcceptance=False,priorCompleteSourceJob=PRIOR,contextReference={'path':str((OUTPUT/'context.json').relative_to(ROOT)),'sha256':terminal['contextSHA256']}))
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    for pin in result['evidenceRefs']:checked(ROOT/pin['path'],pin['sha256'])
    save(DOC/'ROOT-VERIFIED.json',dict(jobId=result['jobId'],exactNeonReadback=True,evidenceRefCount=len(result['evidenceRefs']),allEvidenceHashesVerified=True,sourceOnly=True,sourceContextLeaseReleasedByCompletedFreezer=True,newlyInstalled=0))
    print(json.dumps({'jobId':result['jobId'],'verifiedRefs':len(result['evidenceRefs']),'newlyInstalled':0}),flush=True)
if __name__=='__main__':main()
