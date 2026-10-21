"""Bind a fresh diagnostic selection of the two unchanged towers and original podium."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-three-source-selection-v1-20261022';DOC=BASE/BATCH
UIDS=['landsd/256898:0','landsd/256702:0','landsd/233771:0']
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-remaining-forty-original-identity-v2-20261021';towers=take(n,BASE/n/'selection.json.gz');n='government-xl-ronsdale-inset-runtime-v2-20261022';podium=take(n,BASE/n/'selection.json.gz');rows=[copy.deepcopy(next(r for r in (towers if u!=UIDS[-1]else podium)['rows']if r['uid']==u))for u in UIDS]
 review=take('government-xl-ronsdale-tower1-identity-review-v1-20261022',BASE/'government-xl-ronsdale-tower1-identity-review-v1-20261022/identity.json');assert review['passed'] and not review['reasons'];assert all(any(r['uid']==u and r['sourceSHA256']==h for r in rows)for u,h in review['requiredSourceSHA256ByUid'].items())
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());refs.append(manifest)
 for r in rows:
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
 selected=dict(manifestSHA256=mh,nativeResultSHA256ByKey={r['native']['cacheKey']:r['native']['resultSha']for r in rows},rows=rows);save(DOC/'selection.json.gz',selected)
 module('ronsdale_three_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-unchanged-original-three-source-selection',refs,dict(uids=UIDS,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},manifestSHA256=mh,installationApproved=False));print([(r['uid'],r['triangles'])for r in rows],flush=True)
if __name__=='__main__':main()
