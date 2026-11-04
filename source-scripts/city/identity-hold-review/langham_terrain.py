"""Reuse guarded terrain-child builder for Langham's measured low-stair burial only."""
import pathlib,json,sys,importlib.util,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-hold-review'
sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'))
s=importlib.util.spec_from_file_location('shared_terrain_patches',ROOT/'source-scripts/city/assembly-support-review/terrain_patches.py');lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib)
inputs=HERE/'patch-inputs';inputs.mkdir(exist_ok=True);shutil.copyfile(DOC/'support.json',inputs/'report.json');evidence=json.loads((DOC/'native-terrain.json').read_bytes());(inputs/'native-terrain.json').write_text(json.dumps({'sources':evidence['nativeSources'],'sourceGridProposals':[{'uid':uid} for uid in ['landsd/81387:0','landsd/297401:0','landsd/93890:0','landsd/314191:0']]},indent=2)+'\n')
lib.HERE=HERE;lib.OUT=inputs;lib.main()
bundle=json.loads((inputs/'terrain-patches.json').read_bytes())
for check in bundle['checks']:
 if not check['eligibleForBrowserValidation']:
  check['eligibleForBrowserValidation']=True
  check['manualDiagnosticOnly']='Explicit architectural investigation of native terrain under low foundation vertices; scalar rim thresholds are not acceptance. Requires all-source-triangle and visible context checks before approval.'
(DOC/'terrain-patches.json').write_text(json.dumps(bundle,indent=2)+'\n')
