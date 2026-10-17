"""Fence final actual production native sampler versus441 independent drawn rays."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261010-festival-current-finite-sampler-ray-checkpoint-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;REPORT=HERE/'local/xl-terrain-recovery-20261010-festival-gap-sampler-ray-v3/diagnostic.json.gz'
def main():
 assert not DOC.exists();r=read(REPORT);assert r['passed'] and len(r['rows'])==441 and r['completeGapRegionCount']==51 and all(v['passed'] and v['delta']<=.004 for v in r['rows']);assert r['maxDelta']<=.004
 for p,h in r['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 save(DOC/'diagnostic.json.gz',r);paths=[Path(__file__),REPORT,*[ROOT/p for p in r['inputHashes']]];sp=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.freeze(BATCH,'complete-production-finite-native-sampler-441-independent-actual-ray-v1',paths,dict(uids=['landsd/91827:0','landsd/104302:0'],passed=True,probes=441,all51OriginalGapRegionsCovered=True,maxDeltaM=r['maxDelta'],strictDeltaLimitM=.004,sourceGeometryChanges=0,terrainProposalGeometryChanged=True,installationApproved=False))
if __name__=='__main__':main()
