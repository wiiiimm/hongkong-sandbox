"""Add independently verified actual-JavaScript root0 to complete Park acceptance."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-terrain-recovery-park-haven-current-complete-ordinary-role-v3-20261010';DOC=BASE/BATCH
LITERAL=BASE/'government-xl-terrain-recovery-park-haven-literal-rendered-root-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prior=module('park_complete_current_v2','xl-terrain-recovery-20261010-park-haven-current-complete-ordinary-role-v2.py')
def recheck():
 result=prior.recheck();receipt=read(LITERAL/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 actual=module('park_root_actual_js','xl-terrain-recovery-20261010-park-haven-literal-rendered-root-v1.py').recheck();assert actual==read(LITERAL/'diagnostic.json.gz') and actual['strictLiteralRenderedRoot']is True and actual['manifestSHA256']==result['currentManifest']['sha256'] and actual['component']==0 and result['completeStrictStructuralGraph']['ordinaryGroundRootComponents']==[0]
 result.update(contract='park-haven-complete-current-ordinary-original-support-v3-with-independent-literal-js-root',independentLiteralRenderedGenuineRoot=actual,arithmeticParityRootCredit=False)
 result['evidenceRefs']=sorted({r['path']:r for r in result['evidenceRefs']+[ref(Path(__file__)),ref(Path(prior.__file__)),*[ref(p)for p in sorted(LITERAL.iterdir())if p.is_file()]]}.values(),key=lambda r:r['path']);return result

def main():
 assert not DOC.exists();result=recheck();save(DOC/'typed-role.json.gz',result);f=module('park_actual_root_current_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'complete-current-original-support-plus-literal-js-root-v3',[ROOT/r['path']for r in result['evidenceRefs']],dict(uids=result['uids'],currentTypedPhysicalAccepted=True,reasons=[],completeOriginalFaces=11173,completeOriginalComponents=554,strictLiteralRenderedRoot=True,arithmeticParityRootCredit=False,typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0));print(dict(currentTypedPhysicalAccepted=True,literalRoot=True,faces=11173,parts=554),flush=True)
if __name__=='__main__':main()
