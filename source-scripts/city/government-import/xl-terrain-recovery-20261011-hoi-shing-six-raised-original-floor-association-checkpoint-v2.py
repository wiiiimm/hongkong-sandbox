"""Freeze completed immutable v1 arithmetic after missing-summary-uids error.

No numerical re-execution or changed result. Original failure/diagnostic/source
pins are retained; original conditional host obligations and raw negatives stay.
"""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-v1'
BATCH='xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-checkpoint-v2';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not(OLD/'result.json').exists();original=OLD/'diagnostic.json.gz';pin=ref(original);d=read(original)
 assert d['sourceOnly']and not d['currentAcceptance']and not d['rootOrBridgeCredit']and not d['roleAssigned']
 assert d['completeOriginalFaces']==19374 and [r['originalBody']for r in d['rows']]==[21,22,25,94,95,100]
 assert all(r['conditionalCompleteFloorWithinExistingContactBand']and not r['structuralRootOrBridgeCredit']for r in d['rows'])
 assert [len(r['allOriginalGlobalBottomDownwardFaces'])for r in d['rows']]==[54,47,65,13,24,4]
 for r in d['evidenceRefs']:assert ref(ROOT/r['path'])==r
 log=Path('/tmp/hoi-shing-six-raised-original-floor-association-v1-20261011.log');raw=log.read_bytes();assert b"KeyError: 'uids'"in raw
 DOC.mkdir();(DOC/'original-freeze-summary-schema-failure.log').write_bytes(raw)
 save(DOC/'receipt-recovery.json',dict(completeUntouchedNumericDiagnostic=pin,missingField='result.uids',allMathCompletedBeforeReceiptFailure=True,mathReexecuted=False,oldProducer=ref(HERE/'xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-v1.py'),allConditionalSourceHostObligationsPreserved=True))
 paths=[ROOT/r['path']for r in d['evidenceRefs']]+[original,Path(__file__),DOC/'receipt-recovery.json',DOC/'original-freeze-summary-schema-failure.log']
 spec=importlib.util.spec_from_file_location('freeze_hoi_completed',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'six-original-floors-completed-conditional-numeric-receipt-recovery-v2',paths,dict(uids=['landsd/318801:0','landsd/318830:0'],sourceOnly=True,currentAcceptance=False,conditionalPositiveBodies=[21,22,25,94,95,100],complete207OriginalFloorFacetsWithinExistingBand=True,numericalDiagnostic=pin,numericalReexecution=False,originalGeometryChanges=0,rootOrBridgeCredit=False,hostQualificationStillRequired=True,newlyInstalled=0))
 assert ref(original)==pin
if __name__=='__main__':main()
