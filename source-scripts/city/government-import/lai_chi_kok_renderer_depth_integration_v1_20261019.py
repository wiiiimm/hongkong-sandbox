"""Integrate the exact privately tested depth-only renderer; preserve old evidence."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-renderer-depth-integration-v1-20261019';DOC=BASE/BATCH
PREVIEW=BASE/'government-xl-lai-chi-kok-browser-1280-joint-v10-20261019';CAP=BASE/'government-xl-lai-chi-kok-eight-runtime-v4-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [PREVIEW,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 world=ROOT/'3d-viewer/city/world.js';helper=ROOT/'3d-viewer/city/native-terrain-depth.js';old=world.read_bytes();tested=(PREVIEW/'tested-world.js').read_bytes();assert old==(PREVIEW/'original-world.js').read_bytes()
 marker="mesh.receiveShadow=true;mesh.name='Lands Department · native source terrain triangles'";assert old.decode().count(marker)==1
 expected="import {applyNativeTerrainDepthBias} from './native-terrain-depth.js';\n"+old.decode().replace(marker,'applyNativeTerrainDepthBias(mesh.material);'+marker)
 assert tested==expected.encode();assert pins[str(helper.relative_to(ROOT))]==digest(helper.read_bytes())
 DOC.mkdir();archive=DOC/'original-world.js';archive.write_bytes(old)
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 world.write_bytes(tested)
 transition=dict(originalPath=str(world.relative_to(ROOT)),originalSHA256=digest(old),archivedOriginal=ref(archive),current=ref(world),helper=ref(helper),testedPreviewWorld=ref(PREVIEW/'tested-world.js'),qualification='Only the exact depth-only shader hook is changed. Historical receipts remain immutable and resolve this one old module revision explicitly to its byte-identical archive. No generic stale-hash bypass.')
 save(DOC/'transition.json',transition)
 tool=HERE/'acceptance-metrics-multi-retained.mjs';local=HERE/'local'/CAP.name
 cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--selection',str((CAP/'selection.json.gz').relative_to(ROOT)),'--candidates',str(local.relative_to(ROOT)),'--terrain-candidates',str((CAP/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((DOC/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 assert read(DOC/'runtime-geometry.json.gz')==read(local/'runtime-geometry.json.gz'),'Renderer geometry changed'
 metrics=read(DOC/'metrics.json');assert metrics['rows']==read(CAP/'metrics.json')['rows'],'Physical metrics changed'
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in pins.items():
  q=archive if p==str(world.relative_to(ROOT))and h==digest(old)else ROOT/p
  assert digest(q.read_bytes())==h;refs.append(q)
 refs.extend([world,helper,archive,PREVIEW/'tested-world.js'])
 save(DOC/'equivalence.json',dict(completeEightSourceGeometryEqual=True,completeDrawnTerrainGeometryEqual=True,completePhysicalMetricsEqual=True,transition=ref(DOC/'transition.json'),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False))
 module('depth_integrate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-tested-renderer-depth-integration',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in metrics['rows']],geometryAndPhysicalMetricsUnchanged=True,installationApproved=False))
if __name__=='__main__':main()
