"""Fence exact Garden primary/source positives and rejected direct-podium lead."""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,digest
BATCH='government-xl-garden-complete-original-source-role-evidence-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMES=['government-xl-garden-original-identity-role-leads-20261010','government-xl-garden-current-primary-identity-context-20261010','government-xl-garden-exact-structure-permits-20261010','government-xl-garden-common-op-original-terrace-context-20261010','government-xl-garden-complete-original-role-renders-20261010']
def main():
 assert not DOC.exists();paths=[Path(__file__)]
 for n in NAMES:
  for p in (DOC.parent/n).rglob('*'):
   if p.is_file() and p.name!='complete-source-terrace-overlay-2400x1500.png':paths.append(p)
 for filename in ['xl-garden-original-identity-role-leads-20261010.py','xl-garden-current-primary-identity-context-20261010.py','xl-garden-exact-structure-permits-20261010.py','xl-garden-common-op-original-terrace-context-20261010.py','xl-garden-complete-original-role-renders-20261010.py']:paths.append(HERE/filename)
 for name,filename in [('government-xl-garden-common-op-original-terrace-context-20261010','diagnostic.json.gz'),('government-xl-garden-original-identity-role-leads-20261010','diagnostic.json.gz'),('government-xl-garden-complete-original-role-renders-20261010','render-provenance.json')]:
  for rel,sha in read(DOC.parent/name/filename)['inputHashes'].items():
   p=ROOT/rel;assert digest(p.read_bytes())==sha;paths.append(p)
 DOC.mkdir(parents=True);(DOC/'README.md').write_text('Authoritative current exact structure records and reverse building relations establish Tower109491 and Podium162285 share occupation permitH159/83; No1Garden304714 H39/83 and Hollywood213929 H229/77 remain distinct. Entire109491 source plate0/96faces contains all33farfaces and44 positive own-source interfaces, but its126.936m² projection is wholly outside current/provider/original162285 podium, withzero exact original podium contacts. CommonOP alone does not resolve the18.452m extent hold. Exact complete No1Garden821faces/main779 and Hollywood546faces retain three upward roof edges642–644 at133.2569885HKPD above whole actual foreign maximum129.72899HKPD; distinct body and all foreign physical actors remain. Correct complete source renders2400x1500 exported and inspected with east/south/HKPD axes; earlier unbound diagnostic image is excluded, not evidence. No source edits, no legal ownership or support/collision/terrain exemption. No physical or installed credit; No1Garden current identity-only promotion is separate.\n')
 s=importlib.util.spec_from_file_location('garden_complete_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.freeze(BATCH,'complete-garden-original-primary-roles-and-source-specific-negative-v1',paths,{'uids':['landsd/109491:0','landsd/162285:0','landsd/304714:0','landsd/213929:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'physicalAccepted':False,'currentHeldReason':'tower-terrace-extent-role-needs-independent-complete-boundary-evidence','nextStep':'No1Garden independently replayed named roof-edge identity may enter complete physical checks; tower terrace stays held until complete original extent role is positively established.'});print(r['jobId'],flush=True)
if __name__=='__main__':main()
