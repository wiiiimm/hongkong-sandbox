"""Recheck full podium geometry on the private neighbour-preserving terrain."""
import subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-preserve-oi-yuk-v1-20261017';SOURCE=BASE/'government-xl-oi-sin-podium-terrain-v1-20261017'
BATCH='government-xl-oi-sin-preserved-foundation-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/91128:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 DOC.mkdir();closure=DOC/'production-module-closure.json'
 js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root)));"
 subprocess.run(['node','--input-type=module','-e',js,str(closure)],cwd=ROOT,check=True);cl=read(closure);assert cl['completeAuditedLiteralImportClosure']and cl['unsupportedDynamicImports']==0
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((SOURCE/'selection.json.gz').relative_to(ROOT)),'--candidates',str((HERE/'local'/SOURCE.name).relative_to(ROOT)),'--terrain-candidates',str((PRIOR/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 rt=read(LOCAL/'runtime-geometry.json.gz');assert len(rt['rows'])==1;g=rt['rows'][0];assert g['uid']==UID;tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=read(SOURCE/'selection.json.gz')['rows'][0]['source']['building'];f=module('oi_sin_preserved_foundation',HERE/'xl-final-script-pass.py').foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));strict=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0
 save(DOC/'foundation.json',dict(uid=UID,foundation=f,strictFoundationAccepted=strict,fullAcceptance=False));refs=[Path(__file__),PRIOR/'result.json',PRIOR/'terrain-candidates.json',SOURCE/'selection.json.gz',LOCAL/'runtime-geometry.json.gz',closure,HERE/'xl-final-script-pass.py']
 for p,h in {**cl['inputHashes'],**rt['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 metrics=read(DOC/'metrics.json')['rows'];assert len(metrics)==1 and not metrics[0].get('error');m=metrics[0]
 summary=dict(uid=UID,strictFoundationAccepted=strict,minSurfaceGap=m['minSurfaceGap'],minLowGap=m['minLowGap'],maxLowGap=m['maxLowGap'],maxSamplerDelta=m['maxSamplerDelta'],missingTerrain=m['missingTerrain'],fullAcceptance=False)
 out=module('oi_sin_preserved_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-revised-private-terrain-complete-foundation-v1',list(set(refs)),dict(uids=[UID],summary=summary,nextStep='Resolve same-building tower/car-park neighbour support and complete native scope, staged/live browser and publication requirements.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
