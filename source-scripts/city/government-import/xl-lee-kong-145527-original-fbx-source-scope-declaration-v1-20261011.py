"""Declare exact additive FBX checkpoint paths; not a closure verifier.
No new metadata leaves, numeric exemptions, geometry or acceptance claims.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BATCH='government-xl-lee-kong-145527-original-fbx-source-scope-declaration-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMES=['government-xl-lee-kong-145527-original-fbx-acquisition-v1-20261011','government-xl-lee-kong-145527-original-raw-fbx-inspection-v1-20261011','government-xl-lee-kong-145527-original-raw-fbx-inspection-v2-20261011','government-xl-lee-kong-145527-original-fbx-gltf-comparison-v1-20261011']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();paths=set()
 for name in NAMES:
  for d in [DOC.parent/name,HERE/'local'/name]:
   if d==DOC.parent/name:assert d.exists()
   if not d.exists():continue
   paths.update(p for p in d.rglob('*')if p.is_file())
 for name in ['xl-lee-kong-145527-original-fbx-acquisition-v1-20261011.py','xl-lee-kong-145527-original-raw-fbx-inspection-v1-20261011.py','xl-lee-kong-145527-original-raw-fbx-inspection-v2-20261011.py','xl-lee-kong-145527-original-fbx-gltf-comparison-v1-20261011.py']:paths.add(HERE/name)
 paths.add(Path(__file__));receipt=read(DOC.parent/NAMES[-1]/'result.json');assert receipt['jobId']=='40e2451c7d0dd2095fb90b12a2b9afd0a7f83969bdafbf5e0bb328a343d323dd'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 # Exact recursively referenced files are explicitly declared when physically
 # present with matching bytes. Historical mismatches remain audit inputs;
 # this declaration never substitutes for root's independent SHA verifier.
 references=receipt['evidenceRefs'];unresolved=[]
 for r in references:
  p=ROOT/r['path']
  if p.is_file()and digest(p.read_bytes())==r['sha256']:paths.add(p)
  else:unresolved.append(r)
 archive=HERE/'local/government-xl-mount-verdant-two-unchanged-installed-v1-20261011/manifest-before-installation.json';assert digest(archive.read_bytes())=='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e';paths.add(archive)
 save(DOC/'declared-scope.json',dict(closedExplicitPaths=sorted(str(p.relative_to(ROOT))for p in paths),presentFileBindings=[ref(p)for p in sorted(paths)],frozenReferenceVersions=references,unresolvedDirectReferenceVersions=unresolved,historicalManifestAliases=[dict(originalPath='3d-viewer/city/data/manifest.json',sha256=ref(archive)['sha256'],archive=ref(archive))],comparisonNeonJob=receipt['jobId'],completeFBXAndGLTFOrderedTriangleEquality=True,coverageOfHistoricalTarget=.8627261209104823,newMetadataLeafPaths=[],newNumericExemptions=0,independentRootClosureRequired=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False))
 (DOC/'README.md').write_text('Additive untouched FBX acquisition, original parser failure, complete successful raw parse and original-format comparison. All584 original triangles exactly equal glTF; the86.27% target coverage hold remains. This is a scope declaration only; root must independently close recursive old/current/provider/source/Neon references. No new metadata leaves or numeric exemptions.\n')
 print(dict(paths=len(paths),unresolvedDirectRefs=len(unresolved),scope=str((DOC/'declared-scope.json').relative_to(ROOT))),flush=True)
if __name__=='__main__':main()
