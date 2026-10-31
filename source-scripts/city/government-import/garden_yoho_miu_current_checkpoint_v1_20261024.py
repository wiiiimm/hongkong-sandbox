"""Persist completed original-source recovery work and actionable remaining holds."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-garden-yoho-miu-current-checkpoint-v1-20261024'

def main():
    out=BASE/BATCH;assert not out.exists()
    prefixes=('government-xl-next-repairs-garden-terrace2-','government-xl-next-repairs-yoho-','government-xl-next-repairs-miu-fat-')
    receipts=[];refs=[Path(__file__)];pending=[]
    for folder in sorted(BASE.iterdir()):
        if not folder.is_dir()or not folder.name.startswith(prefixes)or'20261024'not in folder.name:continue
        p=folder/'result.json'
        if not p.exists():pending.append(folder.name);continue
        r=read(p);assert r['batch']==folder.name
        receipts.append(r);refs.append(p)
        for ref in r['evidenceRefs']:
            path=ROOT/ref['path'];assert digest(path.read_bytes())==ref['sha256'],ref['path']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        found={jid:(status,result)for jid,status,result in db.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId']for r in receipts],)).fetchall()}
    assert all(found[r['jobId']]==('complete',r)for r in receipts)
    ledger=BASE/'government-xl-sung-original-assembly-supported-retained-original-installed-v1-20261024/full-xl-current-count.json';state=read(ledger)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==state['manifestSHA256'];assert state['counts']==dict(installedVerified=342,remaining=179,total=521)
    refs.extend([ledger,manifest]);allmodels=[]
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;allmodels.extend(read(p)['models']);refs.append(p)
    assert len(allmodels)==len({m['uid']for m in allmodels})==6873
    holds=[
      dict(uid='landsd/109491:0',name='Garden Terrace Block 2',humanState='Held for further processing',requiresHumanDecision=False,requiresAIGeometry=False,reasons=['Current strict rim maximum low gap 34.14300537109375 m remains unresolved.','Full-source extent and original contacts with related podium/Garden Terrace Block 3 require source-role qualification.'],nextStep='Review exact original podium/source-role evidence; do not rerun unchanged failed rim checks or require separate engineering roots for every decorative component.'),
      dict(uid='landsd/61738:0',name='Yoho Town Block 2',humanState='Held for further processing',requiresHumanDecision=False,requiresAIGeometry=False,reasons=['Recovered exact original podium 231756; 253/256 strict contacts plus all three unresolved probes have verified finite original paths in every coordinate stream. Raw strict failures remain.','Podium continuous-ground negatives prevent rim-check precondition; preserve actual affected public surfaces.','Current native Block 1 and related/basic open-structure interfaces need source-specific review before any support replacement.'],nextStep='Consume finite-path and complete low-face results; retain strict negatives. Check exact original/native parent dependencies and current neighbours before staged/browser/publication work.'),
      dict(uid='landsd/165889:0',name='Miu Fat main complex',humanState='Held for further processing',requiresHumanDecision=False,requiresAIGeometry=False,reasons=['Hall 241215 has 441/441 strict support contacts on original main complex; this is not final physical acceptance.','Gateway 197385 is covered by exact original source in four streams and has no installed support users. Coverage approval is private staged validation only; BASIC fallback activation/failure/retry still required.','Original small walkway 233638 and elderly home 6393 have 56 exact authored crossings requiring bounded interface interpretation. Elderly home has 73 exact low wall faces, all with exposed highest original vertices; clear-cap continuation and bounded role review remain separate.','Full identity, original interfaces, retained neighbours and device/browser publication gates remain.'],nextStep='Use four-original capture and exact source evidence. Do not fabricate terrain to fit an installer. Complete held interface/ground checks, dynamic gateway fallback tests and guarded model-only supported installation.'),
    ]
    result=dict(uids=[r['uid']for r in holds],counts=state['counts'],nativeDetailedActors=6873,currentSnapshot=state['snapshotId'],completedEvidenceJobs=[dict(batch=r['batch'],jobId=r['jobId'])for r in receipts],foldersWithoutCompletedReceipt=pending,holds=holds,newInstallationsThisCheckpoint=0,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,requiresHumanDecision=False,qualification='Completed immutable source evidence and remaining work saved for resumption. Incomplete/failed producers are explicitly listed, never treated as accepted receipts. Full fixed521 objective remains active; no corruption, permanent rejection, optimisation, geometry modelling or installation credit is inferred.')
    save(out/'remaining-work.json',result)
    module('current_three_source_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-source-recovery-held-followups',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
