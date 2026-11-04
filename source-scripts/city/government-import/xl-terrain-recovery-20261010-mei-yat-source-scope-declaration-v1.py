"""Declare complete Mei Yat immutable source/current roots for root verification.
No dependency exception or installed credit is granted by this declaration.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-mei-yat-source-scope-declaration-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();role=BASE/'xl-terrain-recovery-20261010-mei-yat-current-complete-visual-support-v1';r=read(role/'result.json');typed=read(role/'typed-role.json.gz');assert typed['independentPhysicalChecksPassed'] and not typed['unresolvedIndependentPhysicalReasons']
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 paths=set()
 def add(p):assert p.is_file();paths.add(str(p.relative_to(ROOT)))
 for d in BASE.glob('*mei-yat*'):
  if (d/'result.json').is_file() and not any(s in d.name for s in ['typed-stage','installed-','closed-scope','scope-declaration']):
   for p in d.rglob('*'):
    if p.is_file():add(p)
 for d in [BASE/'xl-terrain-recovery-20261010-mei-yat-original-facade-visual-v2',BASE/'xl-terrain-recovery-20261010-mei-yat-remaining-three-facade-visual-v1',BASE/'xl-terrain-recovery-20261010-mei-yat-plain-stage-config-v1']:
  for p in d.rglob('*'):
   if p.is_file():add(p)
 for p in HERE.glob('*mei_yat*'):
  if p.is_file():add(p)
 for p in HERE.glob('xl-terrain-recovery-20261010-mei-yat*'):
  if p.is_file() and not any(s in p.name for s in ['scope-declaration','closed-scope']):add(p)
 for n in ['exact_original_facet_orthogonal_finite_facade_band_20261010.py','test_exact_original_facet_orthogonal_finite_facade_band_20261010.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','test_exact_original_edge_finite_facade_distance_band_v2_20261010.py','xl-terrain-recovery-20261010-plain-single-source-stage-v1.py','xl-terrain-recovery-20261010-plain-single-source-live-v1.py','test_plain_single_source_stage_interface_20261010.py']:add(HERE/n)
 prior=read(BASE/'xl-terrain-recovery-20261010-no1-garden-source-scope-declaration-v1/declared-scope.json');aliases=list(prior['historicalManifestAliases']);leaf=set(prior['metadataLeafPaths']);raw=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(raw)==typed['manifestSHA256'];archive=OUT/'acceptance-manifest.json';archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(raw);add(archive);leaf.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)));add(Path(__file__))
 save(OUT/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),metadataLeafJsonPointers=[],currentRoleNeon=r['jobId'],declarationOnly=True,rootIndependentRecursiveVerificationRequired=True,sourceGeometryChanges=0,terrainProposalChanged=False,stageAndLiveExcluded=True,currentNumericReplayAuthority='All 10209 unchanged original and literal rendered faces, complete413-face source-authentic terrain proposal/full drawn-ground facets, 878 complete source parts with genuine root124 and1380 exact source contacts,757 independently structural parts plus121 individually bound visual-only mounts, complete current19forms/native whole bounds/identity/foundation/runtime/provider streams.',qualification='No numeric source, ground, host, component, terrain proposal or actor dependency is a metadata leaf. Prior global catalogues/manifests remain exact byte-bound scoped metadata under previously reviewed closure semantics. Original121 no-contact failures and all failed diagnostic contracts remain immutable. Independent root dependency verification and staged/live browsers remain mandatory.'))
 print(dict(paths=len(paths),roleNeon=r['jobId']))
if __name__=='__main__':main()
