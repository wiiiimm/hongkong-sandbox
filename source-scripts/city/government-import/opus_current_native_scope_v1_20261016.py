"""Reuse authenticated complete current native bounds for the Opus parent domain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-current-native-scope-v1-20261016';DOC=BASE/BATCH
SAVED=BASE/'government-xl-disney-hotel-native-parent-scope-v2-20261016';CANDIDATE=BASE/'government-xl-opus-private-terrain-v3-20261016'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'];pins={}
 for folder in [SAVED,CANDIDATE]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for ref in r['evidenceRefs']:
   p,h=ref['path'],ref['sha256'];assert p not in pins or pins[p]==h;pins[p]=h
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 saved=read(SAVED/'complete-bounds.json.gz');m=read(ROOT/'3d-viewer/city/data/manifest.json');models={}
 for url in m['officialModelCatalogues']:
  assert '3d-viewer/'+url in pins
  for r in read(ROOT/'3d-viewer'/url)['models']:assert r['uid']not in models;models[r['uid']]=r
 assert set(models)=={r['uid']for r in saved['rows']}
 for p,h in saved['currentFormTileHashes'].items():assert pins[p]==h
 domain=read(CANDIDATE/'summary.json')['changedParentExtent'];touch=[]
 for r in saved['rows']:
  assert models[r['uid']]['sha256']==r['sourceSHA256']
  if not closed_disjoint(r['completeFourWorldBounds'],domain):touch.append(r)
 summary=dict(currentNativeActors=len(models),changedParentExtent=domain,touchingNativeUids=sorted(r['uid']for r in touch),currentCatalogueFormSourceAndModuleBytesUnchanged=True,allCurrentActorsNominated=True,fullAcceptance=False)
 DOC.mkdir();save(DOC/'scope.json',summary);save(DOC/'touching-bounds.json.gz',dict(rows=touch));refs += [SAVED/'complete-bounds.json.gz',CANDIDATE/'summary.json']
 r=module('opus_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-all-current-native-four-world-parent-scope-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/322573:0']+summary['touchingNativeUids'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
