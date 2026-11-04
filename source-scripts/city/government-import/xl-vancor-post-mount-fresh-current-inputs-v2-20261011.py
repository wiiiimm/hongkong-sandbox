"""Fresh post-Mount source identity/regional/BASIC/render diagnostics only."""
import subprocess,sys
from run import ROOT,HERE,read,digest
MANIFEST='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def main():
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 batch='government-xl-vancor-post-mount-current-identity-v2-20261011'
 subprocess.run([sys.executable,str(HERE/'xl-current-original-identity-diagnostic-20261010.py'),'--uid','landsd/147956:0','--input','docs/astra-city/government-import/government-xl-lee-kong-four-original-source-recovery-v1-20261011/selection.json.gz','--batch',batch],cwd=ROOT,check=True)
 r=read(ROOT/'docs/astra-city/government-import'/batch/'result.json');assert r['rawIdentityPassed']and not r['rawIdentityReasons']and r['manifestSHA256']==MANIFEST
 for n in ['xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011.py','xl-vancor-basic-253697-whole-projection-diagnostic-v2-20261011.py','xl-vancor-own-retained-actual-render-capture-v2-20261011.py']:
  assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
  subprocess.run([sys.executable,str(HERE/n)],cwd=ROOT,check=True)
if __name__=='__main__':main()
