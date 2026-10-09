"""Fresh complete current original cap-wall paths; no burial/root acceptance."""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_strict_clear_cap_wall_paths_20261009 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261009-118230-current-cap-paths-v1';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
CONTEXT=BASE/'xl-terrain-recovery-20261009-118230-boundary-current-complete-context-v3/diagnostic.json.gz'
SOURCE_GRAPH=BASE/'government-xl-two-harbourfront-complete-original-roof-paths-20261009'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists();claim=reservations.claim('harbourfront-current-cap-paths-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  row=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);ctx=read(CONTEXT);geom=read(GEOMETRY);g=geom['rows'][0]
  world=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(tri)==ctx['wholeSourceFaces']==19438 and world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
  assert g['sourceSHA256']==ctx['sourceSHA256']==row['sourceSHA256'] and ctx['originalOpenExteriorPaths']['sourceAndPhysicalBindings']['decodedWorldTrianglesSHA256']==digest(world.tobytes())
  assert ctx['wholeSourceUncoveredFaces']==0 and not ctx['otherAffectedFaces']
  for p,sha in geom['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha
  receipt=read(SOURCE_GRAPH/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
  graph=read(SOURCE_GRAPH/'diagnostic.json.gz');assert graph['sourceSHA256']==digest(raw) and graph['decodedWorldTrianglesSHA256']==digest(tri.tobytes())
  contacts=[r['originalFaces'] for r in graph['exactCylinderInterfaces'] if r['dimension']>0]
  binding=dict(sourceSHA256=digest(raw),completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeRuntimeWorldTrianglesSHA256=digest(world.tobytes()),currentDrawnGroundSHA256=digest(np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3).tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx['faces']),exactOriginalContactListSHA256=canonical(contacts),currentPhysicalSHA256=digest((PHYSICAL/'result.json').read_bytes()),completeCurrentContextSHA256=digest(CONTEXT.read_bytes()),originalContactDiscoveryReceiptSHA256=digest((SOURCE_GRAPH/'result.json').read_bytes()))
  proof=verify(tri,ctx['faces'],contacts,expected_binding=binding,current_binding=binding);assert proof['allAffectedHavePaths'] and proof['affectedOriginalWallFaces']==ctx['affectedWallFaces']
  refs=[ref(p) for p in [Path(__file__),asset,GEOMETRY,CONTEXT,PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',SOURCE_GRAPH/'result.json',SOURCE_GRAPH/'diagnostic.json.gz',HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'test_original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']]
  save(DOC/'diagnostic.json.gz',dict(**proof,uid=row['uid'],sourceSHA256=digest(raw),binding=binding,rawWallOnlyContractPreserved=ctx['originalOpenExteriorPaths'],evidenceRefs=refs,originalPackedWorldRoundoffM=float(np.max(np.abs(world-tri))),currentPhysicalAccepted=False))
  spec=importlib.util.spec_from_file_location('harbourfront_cap_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'current-complete-original-strict-clear-cap-wall-paths-v1',[ROOT/r['path'] for r in refs],dict(uids=[row['uid']],sourceSHA256=digest(raw),allOriginalWallPathsProved=True,affectedOriginalWallCount=len(proof['affectedOriginalWallFaces']),rawExposureFailures=proof['rawExposureFailures'],scriptFullAcceptancePassed=False,burialRoleAccepted=False,groundRootCredit=False,nextStep='Compose narrow complete original low exterior annular curb role, exact genuine grade/root proofs and every independent current physical/browser/publication gate.'))
  print(json.dumps(dict(originalFaces=len(tri),affectedWalls=len(proof['paths']),allPaths=proof['allAffectedHavePaths'],rawExposureFailures=proof['rawExposureFailures'],contactsReplayed=len(contacts),fullAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
