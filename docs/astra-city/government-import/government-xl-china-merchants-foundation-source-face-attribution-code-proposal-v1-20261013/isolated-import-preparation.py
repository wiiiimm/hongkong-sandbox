"""Code import and saved metadata/hash checks only; never foundation source math."""
from pathlib import Path
import sys, json, gzip, hashlib, importlib.util
ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'source-scripts/city/government-import'
PROPOSAL=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
def ref(path):
 path=Path(path).resolve();return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
helper=HERE/'foundation_source_face_attribution_adapter_v1_20261013.py'
test=HERE/'test_foundation_source_face_attribution_adapter_v1_20261013.py'
canonical=HERE/'xl-final-script-pass.py'
producer=HERE/'xl-china-merchants-wrapper-foundation-result.py'
base=ROOT/'docs/astra-city/government-import'
wrapper=base/'government-xl-retained-group-central-wrapper-20261009-264206-0'
result=base/'government-xl-china-merchants-wrapper-foundation-result-20261009'
census=base/'government-xl-remaining-20260923/sol-continuation-20261003/components/264206-0.json.gz'
runtime=HERE/'local/government-xl-retained-group-central-wrapper-20261009-264206-0/runtime-geometry.json.gz'
selection=wrapper/'selection.json.gz'
checkselection=HERE/'local/government-xl-retained-group-central-wrapper-20261009-264206-0/frozen-inputs/check-selection.json.gz'
required={canonical:'f0c5a3ff8fb69aaa1493594ca1c2a133452748a65bdf8ab0f429448edfe70d28',producer:'bce7fd7ab3ae94f4ae8f5ac084ed012d20947bbcc2d3f0986cf5d942fe5e5f3d',census:'d86b88502f59365ebb132b6e3ecf0f47c7fe7b46b784d01d63ca9c3ad4712f82',runtime:'57d49718cb864fd075fdb166e642fa81594f63c13a15356fc3ece798b9f3b3dc',selection:'c4a333c0b5ee176d7f2b18ef999f89d6610df152f7b27d73540546627316ce35',checkselection:'cd1de2d887b4024b708fa51996158a30c691a06f8b941b83671235e28ba6722e'}
for path,sha in required.items():assert ref(path)['sha256']==sha,(str(path),ref(path))
paths=[helper,test,canonical,producer,census,runtime,selection,checkselection,wrapper/'result.json',result/'foundation.json',result/'result.json',Path(__file__),PROPOSAL/'METHOD.md',PROPOSAL/'synthetic-tests-attempt-3.log']
before=[ref(path)for path in paths]
spec=importlib.util.spec_from_file_location('isolated_foundation_attribution_canonical',canonical)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
import foundation_source_face_attribution_adapter_v1_20261013 as adapter
pin=adapter.canonical_pin(m.foundation_context)
# No invocation of the foundation function, source decoder or saved geometry.
body=json.loads(gzip.decompress(census.read_bytes()))
assert len(body['components'])==144
ids=[i for row in body['components']for i in row['sourceFaceIndices']]
assert len(ids)==19551 and sorted(ids)==list(range(19551)) and len(set(ids))==19551
foundation=json.loads((result/'foundation.json').read_bytes())['foundation']
assert foundation['triangles']==19551 and foundation['fullyBuriedTriangles']==582 and foundation['fullyBuriedUpwardTriangles']==102 and len(foundation['components'])==6
assert all('sourceFaceIndices'not in row for row in foundation['components'])
imported=set()
for module in [*list(sys.modules.values()),m,m.s,m.s.resolution,m.s.context,m.s.context.shared]:
 filename=getattr(module,'__file__',None)
 if filename:
  path=Path(filename).resolve()
  if path.is_relative_to(ROOT) and path.is_file():imported.add(path)
import_refs=[ref(path)for path in sorted(imported)]
assert before==[ref(path)for path in paths]
assert all(ref(ROOT/r['path'])==r for r in import_refs)
output=dict(scope='isolated code import and literal saved metadata/hash audit only',actualSourceNumericalCalls=0,databaseCalls=0,reservationsClaimed=0,canonicalPin=pin,completeSavedBodies=144,completeSourceFaceSlots=19551,legacySampledFailureGroups=6,legacyFullyBuriedSourceSlots=582,legacyBuriedUpwardSourceSlots=102,legacyFailureGroupsLackSourceIDs=True,inputAndCodeRefsBefore=before,inputAndCodeRefsAfter=[ref(path)for path in paths],actualImportedRepoModuleRefs=import_refs,canonicalScriptUnchanged=True)
(PROPOSAL/'isolated-import-preparation.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(dict(passed=True,codeAndInputPins=len(before),importedRepoFiles=len(import_refs),sourceNumericalCalls=0,databaseCalls=0)))
