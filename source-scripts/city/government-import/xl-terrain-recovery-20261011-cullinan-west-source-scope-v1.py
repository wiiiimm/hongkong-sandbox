"""Read-only explicit Cullinan source scope; root verifies numeric closure."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'xl-terrain-recovery-20261011-cullinan-west-source-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(BASE/'xl-terrain-recovery-20261010-park-hkdi-current-source-scope-v1/declared-scope.json');leaves=set(old['metadataLeafPaths']);aliases=list(old['historicalManifestAliases']);paths={str(Path(__file__).relative_to(ROOT))};pointers=list(old.get('metadataLeafJsonPointers',[]))
 # Retain the existing reviewed global metadata contract. No Cullinan source,
 # numerical context, graph, root, role, inventory or math module is a leaf.
 paths.add(str((BASE/'xl-terrain-recovery-20261010-park-hkdi-current-source-scope-v1/declared-scope.json').relative_to(ROOT)))
 for folder in BASE.iterdir():
  if folder.is_dir()and 'cullinan-west' in folder.name and 'stage'not in folder.name and 'installed'not in folder.name and folder!=DOC:
   paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
 for name in ['xl-terrain-recovery-20261011-complete-current-native-position-inventory-v4']:
  paths.update(str(p.relative_to(ROOT))for p in (BASE/name).rglob('*')if p.is_file())
 for pattern in ['xl-terrain-recovery-20261010-cullinan-west-*.py','xl-terrain-recovery-20261010-cullinan-west-*.mjs','xl-terrain-recovery-20261011-cullinan-west-*.py','cullinan_original_named_visual_details*.py','test_cullinan_original_named_visual_details*.py']:
  paths.update(str(p.relative_to(ROOT))for p in HERE.glob(pattern)if 'stage'not in p.name and 'scope'not in p.name)
 for name in ['exact_original_rational_interface_segment_clearance_20261011.py','test_exact_original_rational_interface_segment_clearance_20261011.py','exact_original_shared_edge_component_census_20261011.py','test_exact_original_shared_edge_component_census_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','test_exact_original_shared_edge_component_census_v2_20261011.py','exact_original_facet_piecewise_finite_facade_band_20261010.py','test_exact_original_facet_piecewise_finite_facade_band_20261010.py','xl-terrain-recovery-20261011-complete-current-native-position-inventory-v4.py']:
  paths.add(str((HERE/name).relative_to(ROOT)))
 for batch in ['government-xl-retained-installed-dependency-metadata-applied-v1-20261010','government-xl-all-installed-dependency-metadata-applied-v1-20261010']:
  folder=BASE/batch;r=read(folder/'result.json');paths.add(str((folder/'result.json').relative_to(ROOT)))
  for p in (folder/'before').rglob('*'):
   if p.is_file():
    original=str(p.relative_to(folder/'before'));aliases.append(dict(originalPath=original,sha256=digest(p.read_bytes()),archive=ref(p)));paths.add(str(p.relative_to(ROOT)));leaves.add(str(p.relative_to(ROOT)))
  for a in r['aliases']:
   p=ROOT/a['archivePath'];assert digest(p.read_bytes())==a['sha256'];aliases.append(dict(originalPath=a['path'],sha256=a['sha256'],archive=ref(p)));paths.add(str(p.relative_to(ROOT)))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';raw=manifest.read_bytes();assert digest(raw)=='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8';DOC.mkdir();archive=DOC/'historical-current-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));leaves.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)))
 for log in ['cullinan-west-complete-current-role-v2-20261011.log','cullinan-west-complete-current-role-v3-20261011.log']:
  p=Path('/tmp')/log;target=DOC/log;target.write_bytes(p.read_bytes());paths.add(str(target.relative_to(ROOT)))
 unique={(a['originalPath'],a['sha256'],a['archive']['path']):a for a in aliases}
 save(DOC/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],historicalManifestAliases=list(unique.values()),metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,fullNumericalSourceClosureRequired=True,newMetadataPointerContract=False,sourceGeometryChanges=0,stageAndLiveExcluded=True,qualification='Two unchanged complete tower sources; complete finite source/literal owned faces, genuine actual root51, exact nonzero edge bodies and whole exposed original/literal carrier interfaces. Visual details add no root or bridge. Current VWalk remains publicationApproved:false with all legacy negatives unchanged. Exact prior catalogue/test versions are archived solely for frozen evidence replay. Inherited reviewed global metadata leaves; no Cullinan numerical/source/ground/kernel/current role or complete POSITION inventory leaf.'))
 print(dict(paths=len(paths),stageAndLiveExcluded=True),flush=True)
if __name__=='__main__':main()
