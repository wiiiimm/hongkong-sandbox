"""Freeze completed regression geometry without rerunning its failed envelope."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-native-regression-faces-v1-20261022'
def main():
 doc=BASE/BATCH;assert not(doc/'result.json').exists();prior=BASE/'government-xl-olympic-station-retained-neighbours-v4-20261022';_,pins=authenticate(prior);refs=[Path(__file__),HERE/'olympic_native_regression_faces_v1_20261022.py',prior/'result.json'];report=read(doc/'native-neighbour-checks.json');assert report['diagnosticOnly']and{r['uid']for r in report['rows']}=={'landsd/265848:0','landsd/265851:0'}
 for name in ['neighbour-inputs.json.gz','neighbour-checks.json','installed-dependency-bindings.json']:
  p=prior/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];assert(doc/name).read_bytes()==p.read_bytes();refs.append(p)
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 save(doc/'producer-failure.json',dict(session=4919,exitCode=1,geometryCompleted=True,neonJobCreated=False,error='Mixed string/Path in freezer reference list; original calculations and worker log retained.',recovery='Convert exact reference paths to Path objects only; no geometry replay.'))
 result=read(doc/'summary.json');module('olympic_regression_completed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-neighbour-regression-face-attribution',refs,result)
 for r in report['rows']:print({'uid':r['uid'],'faces':r['newlyBuriedFaces']},flush=True)
if __name__=='__main__':main()
