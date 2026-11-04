"""UNEXECUTED receipt-only mask evidence freeze; no arithmetic replay/terrain."""
import importlib.util,json,sys
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
BASE=ROOT/'docs/astra-city/government-import';P=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/selective13-parent-restoration-draft-v1'
BATCH='government-xl-southside-half-distance-mask-receipt-only-v1-20261013';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
RESULT=P/'exact-half-distance-closed-mask-certificate-v1/certificate.json.gz';AUDIT=P/'readonly-exact-half-distance-mask-certificate-audit-v1.json';TERMINAL=P/'immutable-exact-half-distance-mask-certificate-execution-v1/terminal.json';PREP=P/'immutable-exact-half-distance-collar-import-preflight-v1/validation.json'
METHOD=P/'HALF-DISTANCE-MASK-RECEIPT-ONLY-FREEZER-DRAFT-METHOD.md'
EXPECTED={RESULT:'71fabd75966c74d67414e37ba95deff1d958ea7b2dc5092fed0122f998cdfb35',AUDIT:'7362afd308a6d985c188b6460d74ef377609f17a0903d2068917a3bc38b8c918',TERMINAL:'dbf589cedf8d25dd801b0483116e09838f22429c80b14a63d8e702efcc642d64',PREP:'def750e734686cbaeb104f3fd092b30cc49587ae1d94db3cc6ae3db1f55491c4'}
sha=lambda p:digest(p.read_bytes())
def preflight():
 assert not(BASE/BATCH).exists()
 for p,h in EXPECTED.items():assert sha(p)==h
 a,t,v=read(AUDIT),read(TERMINAL),read(PREP)
 assert t['actualExitCode']==0 and t['all68PreparationPinsUnchanged']and t['resultSHA256']==EXPECTED[RESULT]
 assert a['completeSourceRegionCertificates']==4784 and a['completeMaskCoreHulls']==831 and a['completeOriginalCoreLineage']==3653 and a['all4784StrictClosedMaskCertificatesPass']and a['allPrior3484And19And46ExactlyRetained']
 assert a['wrapperAndChildAbsent']and not Path('/proc/421022').exists()and not Path('/proc/421027').exists()and v['allPassed']and len(v['allInputHashes'])==68
 assert a['maskPackingIsNotCandidateTerrainPacking']and a['futureTerrainCoverageSeamSampler117And6650GuardsRemainUnproved']and a['currentAcceptance']is False
 refs=[Path(__file__),METHOD,*EXPECTED,P/'immutable-exact-half-distance-mask-certificate-execution-v1/execution.log'];assert sha(refs[-1])==t['logSHA256']
 for pins in [v['allInputHashes'],a['allInputHashes']]:
  for path,h in pins.items():p=ROOT/path;assert sha(p)==h;refs.append(p)
 prior_path=BASE/'government-xl-southside-core-collar-distance-receipt-only-v1-20261013/result.json';assert sha(prior_path)=='072e0d2305526957aeedaad7321257b06d48e1d9766f16974e0e265217a4cec2';prior=read(prior_path)
 assert prior['jobId']=='6cddbc4bad9ab9ad3a47440b5bf0f2b50952c3bb4628ebd4cbb2561aacc598af';refs.append(prior_path)
 for r in prior['evidenceRefs']:p=ROOT/r['path'];assert sha(p)==r['sha256'];refs.append(p)
 refs.extend([P/'readonly-core-collar-distance-pinned-neon-release-audit-v1.json',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'popcorn_original_ancillary_identity_20261009.py',HERE/'run.py',HERE.parent/'shared-modelling/db.py',HERE.parent/'shared-modelling/jobs.py',HERE.parent/'shared-modelling/reservations.py'])
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 return a,prior,sorted(set(refs))
def main():
 a,prior,refs=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(completeMaskHulls=831,completeLineage=3653,strictRegionCertificates=4784,evidencePaths=len(refs),noDB=True,noLease=True,noNumericalReplay=True,currentAcceptance=False)));return
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 pins={str(p.relative_to(ROOT)):sha(p)for p in refs};spec=importlib.util.spec_from_file_location('reviewed_mask_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 q=m.freeze(BATCH,'completed-source-bound-packed-mask-certificate-receipt-only',refs,dict(uids=['landsd/315025:0','landsd/300867:0'],completedMaskArtifact=dict(path=str(RESULT.relative_to(ROOT)),sha256=EXPECTED[RESULT]),completeClosedCoreHulls=831,completeOriginalLineage=3653,strictRegionCertificates=4784,priorFailedFiveMetreRecords=3484,priorFiveMetreImprovementCriterion=False,exactDerivedUniformWidthM=a['exactDerivedUniformWidthM'],exactMaxMaskVertexPackingErrorM=a['exactMaxMaskVertexPackingErrorM'],maskOnly=True,terrainPackingNotQualified=True,noNumericalReplay=True,noSourceDecode=True,noNewTerrain=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 for path,h in pins.items():assert sha(ROOT/path)==h
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 print(json.dumps(dict(jobId=q['jobId'],evidenceRefs=len(q['evidenceRefs']),receiptOnly=True,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
