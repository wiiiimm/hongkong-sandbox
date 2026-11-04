"""Locate every newly buried original face in the two failed neighbours."""
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-native-regression-faces-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-olympic-station-retained-neighbours-v4-20261022';r,pins=authenticate(prior);refs=[__file__,prior/'result.json'];doc.mkdir()
 for name in ['neighbour-inputs.json.gz','neighbour-checks.json','installed-dependency-bindings.json']:
  p=prior/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];(doc/name).write_bytes(p.read_bytes());refs.append(p)
 for p,h in read(prior/'native-neighbour-checks.json')['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 tool=HERE/'check-olympic-native-regression-faces-v1-20261022.mjs'
 with(doc/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(doc.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 report=read(doc/'native-neighbour-checks.json');assert report['diagnosticOnly']and{r['uid']for r in report['rows']}=={'landsd/265848:0','landsd/265851:0'}
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=['landsd/81242:0'],neighbourRows=report['rows'],installationApproved=False,newlyInstalled=0,publication=False,sourceGeometryChanges=0);save(doc/'summary.json',result);refs.append(tool);module('olympic_failure_faces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-neighbour-regression-face-attribution',refs,result);print([{'uid':r['uid'],'faces':r['newlyBuriedFaces']}for r in report['rows']],flush=True)
if __name__=='__main__':main()
