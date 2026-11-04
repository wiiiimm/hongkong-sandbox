"""Current neighbour terrain regression with no terrain or neighbour changes."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview5-neighbours-v1-20261020';DOC=BASE/BATCH;SCOPE=BASE/'government-xl-parkview5-current-scope-v1-20261020';ATTR=BASE/'government-xl-star-parkview-actual-render-attributes-v1-20261020';UID='landsd/256113:0'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SCOPE,ATTR]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   if folder==ATTR and e['path']!=str((ATTR/'attributes.json.gz').relative_to(ROOT)):continue
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
attrpins={e['path']:e['sha256']for e in read(ATTR/'result.json')['evidenceRefs']};scopepins={e['path']:e['sha256']for e in read(SCOPE/'result.json')['evidenceRefs']};attributePath=str((ATTR/'attributes.json.gz').relative_to(ROOT));pins={**scopepins,attributePath:attrpins[attributePath]}
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
sources=[r for r in read(ATTR/'attributes.json.gz')['rows'] if r['uid'] in ['landsd/256113:0']];assert len(sources)==1;arrays=[np.asarray(r[k]).reshape(-1,3) for r in sources for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']];allp=np.concatenate(arrays);lo,hi=allp.min(0),allp.max(0);extent=[float(lo[0]-2),float(lo[2]-2),float(hi[0]+2),float(hi[2]+2)];inventory=read(SCOPE/'complete-bounds.json.gz')['rows'];required=[r['uid'] for r in inventory if not closed_disjoint(r['completeFourWorldBounds'],extent)];final=module('star_pod_near',HERE/'xl-final-script-pass.py');near=final.load_forms(extent);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries={e['uid'] for url in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']};inputs={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in near}
save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[],existingNative=b['uid'] in entries) for b,_,t in near],patches=[],candidateIds=[UID],requiredNativeUids=required,inputHashes=inputs));save(DOC/'scope.json',dict(uid=UID,extent=extent,allCurrentNativeActors=len(inventory),touchingNativeUids=required,terrainReplacements=[],neighbourSuppression=[],qualification='No terrain or neighbour geometry changes. These checks cover terrain regression only; source overlap and viewer collision evidence remain separate.'))
for tool in ['check-neighbours.mjs','check-native-neighbours.mjs']:subprocess.run(['node',str(HERE/tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);refs.append(HERE/tool)
report=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json');summary=dict(uids=[UID],forms=len(report['rows']),touchingNativeUids=required,terrainChanged=False,maxGroundChange=max(r['maxGroundChange'] for r in report['rows']),flagged=[r['uid'] for r in report['rows'] if r['reasons']],terrainRegressionOnly=True,installationApproved=False);save(DOC/'summary.json',summary)
for p,h in {**pins,**inputs,**report['inputHashes'],**native['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('star_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-terrain-neighbour-regression',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
