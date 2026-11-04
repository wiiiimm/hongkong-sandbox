"""Prepare exact Park current rebind after root's unrelated atomic publication.

Never stages/publishes. Full changed source/terrain bounds and every old numeric
input must pass the existing reviewed disjoint rebind; current forms repeat too.
"""
import argparse,subprocess,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010'
BATCH='xl-terrain-recovery-20261010-park-haven-post-atomic-disjoint-rebind-v2';DOC=BASE/BATCH
OLD='44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-current-manifest',required=True);a=p.parse_args();start=ref(ROOT/'3d-viewer/city/data/manifest.json');assert start['sha256']==a.expected_current_manifest and start['sha256']!=OLD
 assert not DOC.exists();subprocess.run([str(Path('/tmp/astra-city-venv/bin/python')),str(HERE/'xl-terrain-recovery-20261010-coupled-disjoint-current-rebind-v6.py'),'--physical',str(PHYS.relative_to(ROOT)),'--batch',BATCH,'--historical-git-ref','15f25d9c','--retained-native','landsd/246270:0'],cwd=HERE,check=True)
 proof=read(DOC/'diagnostic.json.gz');assert proof['currentManifestSHA256']==start['sha256'] and len(proof['completeCurrentIdentities'])==2
 spec=importlib.util.spec_from_file_location('park_fresh_regional_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);candidate=read(PHYS/'terrain-candidates.json');old=read(PHYS/'neighbour-inputs.json.gz');forms=m.load_forms(candidate[0]['bounds']);assert len(forms)==24 and [f for f,_,_ in forms]==[r['building']for r in old['rows']]
 assert {str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms}==old['inputHashes']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')==start
 save(DOC/'complete-current-form-repeat.json',dict(currentManifest=start,completeCurrentForms=24,completeCurrentFormHashes=old['inputHashes'],unchangedNumericSourceEvidence=ref(PHYS/'result.json'),strictDisjointRebind=ref(DOC/'diagnostic.json.gz'),sourceGeometryChanges=0,fullAcceptance=False,newlyInstalled=0,evidenceRefs=[ref(Path(__file__)),ref(HERE/'xl-final-script-pass.py')]))
 print(dict(currentRebindPassed=True,forms=24,fullAcceptance=False,stageExecuted=False),flush=True)
if __name__=='__main__':main()
