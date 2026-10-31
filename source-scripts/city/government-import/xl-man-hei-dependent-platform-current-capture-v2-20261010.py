"""Fresh independent platform inputs, installed Man Oi binding and identity only.

Runs only after root confirms a stable live manifest. Reuses unchanged reviewed
producers in isolated modules with distinct output directories. No terrain,
government-source edits, current scene writes or publication are performed.
"""
import importlib.util,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from man_hei_dependent_platform_current_identity_v2_20261010 import DOC,INSTALLED,RAW,PLATFORM,verify_files,adapter,verify_native_rows

INPUT=ROOT/'docs/astra-city/government-import/government-xl-man-fuk-complete-retained-original-physical-v7-20261010/selection.json.gz'
PROOF=DOC.parent/'government-xl-man-hei-dependent-platform-current-proof-v2-20261010'

def module(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    assert not DOC.exists() and not INSTALLED.exists() and not RAW.exists() and not PROOF.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    subprocess.run([sys.executable,str(HERE/'xl-current-original-identity-diagnostic-20261010.py'),'--uid',PLATFORM,'--input',str(INPUT.relative_to(ROOT)),'--batch',RAW.name],cwd=ROOT,check=True)
    assert manifest.read_bytes()==before
    capture=module('manhei_fresh_platform_capture','xl-man-fuk-current-bound-envelope-capture-v3-20261010.py')
    capture.BATCH=DOC.name;capture.DOC=DOC;capture.RAW=RAW;capture.main()
    assert manifest.read_bytes()==before
    installed=module('manhei_fresh_installed_manoi','xl-man-fuk-current-installed-related-original-binding-v2-20261010.py')
    installed.DOC=INSTALLED;installed.CAP=DOC;installed.main()
    assert manifest.read_bytes()==before
    rows=read(DOC/'selection.json.gz')['rows'];contexts=read(DOC/'context.json.gz')['rows'];assert len(rows)==len(contexts)==1
    m=adapter();verify_native_rows(read(DOC/'original-source-lookup.json.gz')['rows'],m.RELATED_SHA)
    proof=verify_files(rows[0],contexts[0],HERE/'local'/PROOF.name)
    assert proof['passed'] and proof['reasons']==[] and proof['physicalAccepted'] is False
    assert proof['currentBinding']['manifestSHA256']==digest(before) and proof['currentBinding']['actualInstalledRelatedOriginalVerified'] is True
    save(PROOF/'identity.json',proof);save(PROOF/'selection.json.gz',dict(rows=rows));save(PROOF/'context.json.gz',dict(rows=contexts))
    assert manifest.read_bytes()==before
    fence=module('manhei_fresh_platform_proof_fence','xl-popcorn-source-investigations-checkpoints-20261009.py')
    paths=[Path(__file__),HERE/'man_hei_dependent_platform_current_identity_v2_20261010.py',HERE/'man_fuk_current_bound_envelope_identity_v3_20261010.py',HERE/'xl-man-fuk-current-bound-envelope-capture-v3-20261010.py',HERE/'xl-man-fuk-current-installed-related-original-binding-v2-20261010.py',INPUT,DOC/'result.json',INSTALLED/'result.json',RAW/'result.json']
    result=fence.freeze(PROOF.name,'fresh-independent-man-fuk-platform-identity-for-man-hei-v2',paths,dict(uids=[PLATFORM,m.RELATED],identityAccepted=True,physicalAccepted=False,manifestSHA256=digest(before),currentPlatformIdentityPolicy=proof['policy'],actualInstalledManOiOriginalVerified=True,nativeVersionsUnique=True,qualification='Fresh independent existing named platform identity only. Source meshes, source heights/poses and terrain unchanged. Man Hei mandatory assembly identity and all physical gates remain independent.'))
    print({'jobId':result['jobId'],'manifestSHA256':digest(before),'identityPassed':True},flush=True)

if __name__=='__main__':main()
