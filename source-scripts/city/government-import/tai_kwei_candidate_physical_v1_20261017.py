"""Check private combined Tai Kwei terrain with unchanged production geometry and basic neighbours."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-tai-kwei-current-physical-v1-20261017';TERRAIN=BASE/'government-xl-tai-kwei-private-terrain-v1-20261017';BATCH='government-xl-tai-kwei-candidate-physical-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/106413:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in [PRIOR,TERRAIN]:
   r=read(p/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p/'result.json')
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=read(PRIOR/'selection.json.gz');manifest_path=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest_path.read_bytes())==selection['manifestSHA256'];manifest=read(manifest_path);candidates=read(TERRAIN/'terrain-candidates.json');assert len(candidates)==1
 save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',candidates);final=module('tai_kwei_candidate_final',HERE/'xl-final-script-pass.py');forms=final.load_forms(candidates[0]['bounds']);live={e['uid']for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']}
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in live or bool(b.get('modelGeometry')))for b,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/url).relative_to(ROOT)):digest((ROOT/'3d-viewer'/url).read_bytes())for _,_,url in forms},candidateIds=[UID],patches=candidates))
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str((HERE/'local'/PRIOR.name).relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 subprocess.run(['node',str(HERE/'check-native-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 native=read(DOC/'native-neighbour-checks.json');scope=BASE/'government-xl-tai-kwei-current-native-scope-v1-20261017/scope.json';assert sorted(r['uid']for r in native['rows'])==read(scope)['touchingNativeUids'];assert read(scope)['changedParentExtent']==candidates[0]['bounds'];refs.append(scope)
 rt=read(LOCAL/'runtime-geometry.json.gz');assert len(rt['rows'])==1;g=rt['rows'][0];old=read(HERE/'local'/PRIOR.name/'runtime-geometry.json.gz')['rows'][0]
 assert g['position']==old['position']and g['index']==old['index']and g['sourceSHA256']==old['sourceSHA256']
 t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=selection['rows'][0]['source']['building'];f=final.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));strict=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0 and not f['fullyBuriedUpwardTriangles'];save(DOC/'foundation.json',dict(uid=UID,foundation=f,strictFoundationAccepted=strict))
 metrics=read(DOC/'metrics.json');assert not any(r.get('error')for r in metrics['rows']);neighbours=read(DOC/'neighbour-checks.json');failed=[dict(uid=r['uid'],reasons=r['reasons'])for r in neighbours['rows']if r['reasons']]
 for p,h in {**metrics['inputHashes'],**rt['inputHashes'],**native['inputHashes'],**read(DOC/'neighbour-inputs.json.gz')['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([LOCAL/'runtime-geometry.json.gz',HERE/'local'/PRIOR.name/'runtime-geometry.json.gz',HERE/'check-neighbours.mjs',HERE/'xl-final-script-pass.py',TERRAIN/'terrain-candidates.json']);assert digest(manifest_path.read_bytes())==selection['manifestSHA256']
 out=module('tai_kwei_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-private-combined-terrain-production-foundation-basic-native-neighbours-v2',list(dict.fromkeys(refs)),dict(uids=[UID],strictFoundationAccepted=strict,foundation=f,basicNeighbourCount=len(neighbours['rows']),basicNeighbourFailures=failed,installedNativeResults=native['rows'],allActualGeometryRepresentationsStillRequired=True,fullAcceptance=False,nextStep='Resolve concrete failures, then check every installed actor nominated by complete combined-domain scope in all actual geometry representations, followed by runtime/browser checks.'))
 print(dict(jobId=out['jobId'],strictFoundationAccepted=strict,buried=f['fullyBuriedTriangles'],basicNeighbours=len(neighbours['rows']),basicNeighbourFailures=failed,nativeResults=[dict(uid=r['uid'],passed=r['passed'])for r in native['rows']]),flush=True)
if __name__=='__main__':main()
