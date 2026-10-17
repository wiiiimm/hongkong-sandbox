"""Declare No1 roots for independent existing recursive verification.
This is not successful closure or provenance waiver. Every numeric root remains.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-no1-garden-source-scope-declaration-v1';assert not OUT.exists();OUT.mkdir()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
paths=set()
def add(p):
 assert p.is_file();paths.add(str(p.relative_to(ROOT)))
for d in BASE.glob('*no1-garden*'):
 if (d/'result.json').is_file() and not any(s in d.name for s in ['typed-stage','installed-','closed-scope']):
  for p in d.rglob('*'):
   if p.is_file():add(p)
for d in [BASE/'xl-terrain-recovery-20261010-no1-garden-exact-historical-tin-restore-v1']:
 for p in d.rglob('*'):
  if p.is_file():add(p)
for p in HERE.glob('xl-terrain-recovery-20261010-no1-garden*'):
 if p.is_file() and not any(s in p.name for s in ['stage-install','live-install','source-closed-scope']):add(p)
for n in ['current_installed_recorded_native_dependency_20261010.mjs','test_current_installed_recorded_native_dependency_20261010.mjs','no1_preserved_parent_child_provenance_scope_v2_20261010.py','test_no1_preserved_parent_child_provenance_scope_v2_20261010.py']:add(HERE/n)
prior=read(BASE/'xl-terrain-recovery-20261010-festival-stage-live-closure-v4/closed-scope.json');aliases=list(prior['historicalManifestAliases']);leaf=list(prior['metadataLeafPaths']);archive=OUT/'acceptance-manifest.json';archive.write_bytes((ROOT/'3d-viewer/city/data/manifest.json').read_bytes());assert digest(archive.read_bytes())=='a3a28145511e3ce6f0b0255d490e1219ad05c643030d00f3e4d9844cdf784b64';add(archive);leaf.append(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(archive.read_bytes()),archive=ref(archive)))
for d in BASE.glob('xl-terrain-recovery-20261010-no1-garden-source-closed-scope-v*'):
 for p in (d/'historical-evidence').glob('*'):
  if not p.is_file():continue
  sha=p.name.split('-',1)[0];assert digest(p.read_bytes())==sha
  # Original paths are recovered by independently verified byte lookup; the
  # successful previous alias list already provides historical manifest aliases.
  add(p)
add(Path(__file__))
save(OUT/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=leaf,metadataLeafJsonPointers=[],declarationOnly=True,rootIndependentRecursiveVerificationRequired=True,sourceGeometryChanges=0,terrainProposalChanged=True,lastUnresolvedReference=dict(path='source-scripts/city/landmark-acquisition/batches/terrain-prerequisites/staged/11-SW-10D/TERRAIN(TB)/T36750156000106E11/T36750156000106E11-geometry.gltf',origin='source-scripts/city/government-import/local/government-xl-festival-two-atomic-installed-v1-20261010/manifest-before-installation.json'),qualification='Immutable source/current numeric roots declared only; original/runtime821facets, source/TIN/current terrain,14forms/12native meshes and exact source roots remain recursive. Existing root verifier must independently resolve complete dependency closure; this declaration grants no provenance exception or installation approval.'))
print(len(paths))
