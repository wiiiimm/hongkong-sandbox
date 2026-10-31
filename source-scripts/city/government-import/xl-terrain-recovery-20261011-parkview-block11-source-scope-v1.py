"""Immutable explicit source closure; no numeric dependency exemptions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'xl-terrain-recovery-20261011-parkview-block11-source-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();oldpath=BASE/'xl-terrain-recovery-20261011-cullinan-west-source-scope-v1/declared-scope.json';old=read(oldpath);leaves=set(old['metadataLeafPaths']);aliases=list(old['historicalManifestAliases']);pointers=list(old.get('metadataLeafJsonPointers',[]));paths={str(Path(__file__).relative_to(ROOT)),str(oldpath.relative_to(ROOT))}
 # Inherited exact historical manifest/catalogue versions only. No Parkview
 # current source/ground/numeric/graph/role/inventory/module becomes a leaf.
 for folder in BASE.iterdir():
  if folder.is_dir()and 'parkview' in folder.name and ('terrain-recovery' in folder.name)and 'stage'not in folder.name and 'installed'not in folder.name and folder!=DOC:
   paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
 for name in ['xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5']:
  paths.update(str(p.relative_to(ROOT))for p in (BASE/name).rglob('*')if p.is_file())
 for pattern in ['xl-terrain-recovery-20261010-parkview-*.py','xl-terrain-recovery-20261011-parkview-*.py','xl-terrain-recovery-20261011-parkview-*.mjs','parkview_original_roof_unit324*.py','test_parkview_original_roof_unit324*.py']:
  paths.update(str(p.relative_to(ROOT))for p in HERE.glob(pattern)if 'stage'not in p.name and 'scope'not in p.name)
 for name in ['xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5.py','actual_float32_model_matrix_bounds_20261011.mjs','test_actual_float32_model_matrix_bounds_20261011.mjs','xl-terrain-recovery-20261010-current-original-literal-actor-bounds-readonly-v4.mjs']:
  paths.add(str((HERE/name).relative_to(ROOT)))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';raw=manifest.read_bytes();assert digest(raw)=='aba0edb60daac0497b98c78d21507461b13b20a4ddcc177ca0526fabeaa86eef';DOC.mkdir();archive=DOC/'historical-current-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));leaves.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)))
 for log in ['parkview-authentic-retained-terrain-proposal-v2-20261011.log','parkview-block11-complete-current-role-v1-20261011.log']:
  p=Path('/tmp')/log
  if p.exists():target=DOC/log;target.write_bytes(p.read_bytes());paths.add(str(target.relative_to(ROOT)))
 unique={(a['originalPath'],a['sha256'],a['archive']['path']):a for a in aliases};save(DOC/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],historicalManifestAliases=list(unique.values()),metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,fullNumericalSourceClosureRequired=True,newMetadataPointerContract=False,sourceGeometryChanges=0,stageAndLiveExcluded=True,qualification='Complete unchanged10679-face Parkview Block11 original/literal/two explicit Float32 representations. Native availability credit only exact finite grade wall60989→exposed shared edge→strict cap57951→owned0; all other native failures and geometry remain uncredited. All80 structural owned parts and72-face visual-only roof appendage independently accounted. Explicit authentic two-sheet terrain candidate retains actual old terrain beneath Block9 and18 strictly disjoint basic footprints. All26 current forms/four full native checks/wholefoundation/identity/runtime remain mandatory. Inherited exact global metadata boundaries only; every Parkview numerical/source/module/current native inventory ref remains fully recursive.'))
 print(dict(paths=len(paths),stageAndLiveExcluded=True),flush=True)
if __name__=='__main__':main()
