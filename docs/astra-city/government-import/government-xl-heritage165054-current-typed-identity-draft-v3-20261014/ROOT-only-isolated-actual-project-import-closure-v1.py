"""ROOT-only isolated imports, no source arrays/proofs/DB/lease/test execution."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[3];HERE=ROOT/'source-scripts/city/government-import'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()and a.output.resolve().is_relative_to(D)
cpath=D/'input-contract.json';raw=cpath.read_bytes();c=json.loads(raw);before={q:sha(ROOT/q)for q in c['filePins']}
assert before==c['filePins'];assert sha(ROOT/'3d-viewer/city/data/manifest.json')==c['currentManifestSHA256']
executed={str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__).resolve())}
def audit(event,args):
 if event!='exec':return
 path=Path(args[0].co_filename).resolve()
 if path.suffix!='.py'or not path.is_file()or not path.is_relative_to(ROOT):return
 key=str(path.relative_to(ROOT));h=sha(path)
 if key in executed:assert executed[key]==h,key
 executed[key]=h
sys.addaudithook(audit);sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import government_georef_cell_identity
import exact_original_georef_cell_identity_20261009
spec=importlib.util.spec_from_file_location('heritage_actual_import_only_final',HERE/'xl-final-script-pass.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
# The exec audit also records dynamic spec modules not inserted in sys.modules.
for module in list(sys.modules.values()):
 name=getattr(module,'__file__',None)
 if name is None:continue
 path=Path(name).resolve()
 if path.suffix=='.py'and path.is_file()and path.is_relative_to(ROOT):
  key=str(path.relative_to(ROOT));h=sha(path)
  if key in executed:assert executed[key]==h,key
  executed[key]=h
assert sha(cpath)==hashlib.sha256(raw).hexdigest();assert {q:sha(ROOT/q)for q in before}==before
assert all(sha(ROOT/q)==h for q,h in executed.items())
out={'completeActualProjectImportClosure':True,'actualImportedLocalFileHashes':executed,'inputContractSHA256AtCollection':hashlib.sha256(raw).hexdigest(),'currentManifestSHA256':c['currentManifestSHA256'],'entryImports':['government_georef_cell_identity','exact_original_georef_cell_identity_20261009','xl-final-script-pass.py'],'dynamicExecFilesAlsoRecorded':True,'isolatedProcessRequired':True,'noSourceArraysLoadedOrGeometryProofFunctionsCalled':True,'noDBOrLeaseOrTestExecution':True,'allBeforeEndPinsVerified':True,'newLocalFilesToBind':{q:h for q,h in executed.items()if q not in c['filePins']}}
with a.output.open('x')as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'passed':True,'actualLocalFileCount':len(executed),'newLocalFilesToBind':out['newLocalFilesToBind'],'outputSHA256':sha(a.output),'noGeometryDBLeaseTests':True}),flush=True)
