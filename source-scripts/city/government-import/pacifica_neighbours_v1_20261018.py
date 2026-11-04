"""Full changed-domain basic neighbour checks for private Pacifica Mall terrain."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-neighbours-v1-20261018';DOC=BASE/BATCH;CAP=BASE/'government-xl-pacifica-expanded-grid-v4-20261018';SCOPE=BASE/'government-xl-pacifica-current-scope-v1-20261018';UID='landsd/283036:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,SCOPE]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
 scope=read(SCOPE/'scope.json');inventory=read(SCOPE/'complete-bounds.json.gz')['rows'];required=[r['uid']for r in inventory if not closed_disjoint(r['completeFourWorldBounds'],scope['changedParentExtent'])];save(DOC/'actor-scope.json',dict(completeActorCount=len(inventory),changedParentExtent=scope['changedParentExtent'],requiredNativeUids=required));refs.append(HERE/'heritage_saved_native_bounds_binding_v1_20261014.py')
 final=module('fu_neighbour_context',HERE/'xl-final-script-pass.py');near=final.load_forms(scope['changedParentExtent']);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for entry in read(path)['models']:entries[entry['uid']]=entry
 needed=set(required)
 for uid in required:needed.update(d['uid']for d in entries[uid].get('supportDependencies',[]))
 byuid={b['uid']:(b,tile)for b,_,tile in near}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']in needed and b['uid']not in byuid:byuid[b['uid']]=(b,tile['url'])
 assert needed<=set(byuid)
 inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes())for _,tile in byuid.values()};patches=read(CAP/'terrain-candidates.json');save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in entries)for b,_ in byuid.values()],patches=patches,candidateIds=[UID],requiredNativeUids=required,inputHashes=inputs))
 subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 subprocess.run(['node',str(HERE/'check-native-neighbours-multi-retained-scoped-v3.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 native=read(DOC/'native-neighbour-checks.json')
 geometrypath=HERE/'local'/CAP.name/'runtime-geometry.json.gz';g=read(geometrypath)['rows'][0];r=read(CAP/'selection.json.gz')['rows'][0];assert g['uid']==r['uid']==UID;tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=r['source']['building'];foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 report=read(DOC/'neighbour-checks.json');summary=dict(uid=UID,neighbourForms=len(byuid),requiredNativeUids=required,nativeChecks=native['rows'],flagged=[dict(uid=x['uid'],reasons=x['reasons'],beforeGap=x['beforeGap'],afterGap=x['afterGap'])for x in report['rows']if x['reasons']],foundation={k:v for k,v in foundation.items()if k!='components'},installationApproved=False);save(DOC/'summary.json',summary);print(summary,flush=True)
 for p,h in {**pins,**report['inputHashes'],**native['inputHashes'],**inputs}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([geometrypath,HERE/'xl-final-script-pass.py',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours-multi-retained-scoped-v3.mjs'])
 module('times_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'pacifica-full-parent-neighbours-and-foundation',list(dict.fromkeys(refs)),dict(uids=[UID],summary=summary,installationApproved=False))
if __name__=='__main__':main()
