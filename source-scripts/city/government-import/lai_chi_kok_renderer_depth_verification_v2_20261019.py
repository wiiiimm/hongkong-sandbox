"""Verify full geometry equality separately from the intentional module revision."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from lai_chi_kok_renderer_revision_20261019 import resolve,DOC as INTEGRATION,OLD,NEW
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-renderer-depth-verification-v2-20261019';DOC=BASE/BATCH
assert not DOC.exists();cap=BASE/'government-xl-lai-chi-kok-eight-runtime-v4-20261019';preview=BASE/'government-xl-lai-chi-kok-browser-1280-joint-v10-20261019';refs=[Path(__file__),HERE/'lai_chi_kok_renderer_revision_20261019.py',HERE/'lai_chi_kok_renderer_depth_integration_v1_20261019.py']
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [cap,preview]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  refs.extend(resolve(e['path'],e['sha256'])for e in r['evidenceRefs'])
old=read(HERE/'local'/cap.name/'runtime-geometry.json.gz');new=read(INTEGRATION/'runtime-geometry.json.gz');assert old['rows']==new['rows'] and len(new['rows'])==8
changed={k:[old['inputHashes'].get(k),new['inputHashes'].get(k)]for k in old['inputHashes'].keys()|new['inputHashes'].keys()if old['inputHashes'].get(k)!=new['inputHashes'].get(k)}
assert changed=={'3d-viewer/city/world.js':[OLD,NEW]}
metrics=read(INTEGRATION/'metrics.json');assert metrics['rows']==read(cap/'metrics.json')['rows']
for p,h in new['inputHashes'].items():refs.append(resolve(p,h))
world=ROOT/'3d-viewer/city/world.js';assert world.read_bytes()==(preview/'tested-world.js').read_bytes()
refs.extend(p for p in INTEGRATION.iterdir()if p.is_file());refs.extend([world,ROOT/'3d-viewer/city/native-terrain-depth.js',preview/'tested-world.js'])
save(DOC/'equivalence.json',dict(completeEightSourceGeometryEqual=True,completeDrawnTerrainGeometryEqual=True,completePhysicalMetricsEqual=True,onlyInputChanges=changed,transition=dict(path=str((INTEGRATION/'transition.json').relative_to(ROOT)),sha256=digest((INTEGRATION/'transition.json').read_bytes())),failedFirstComparison='Compared inputHashes together with geometry; expected renderer revision was the only difference.',installationApproved=False))
module('depth_verify_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-tested-renderer-depth-integration-verified',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in metrics['rows']],geometryAndPhysicalMetricsUnchanged=True,installationApproved=False))
