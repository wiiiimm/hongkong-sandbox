"""Closed explicit checkpoint handoff; source diagnosis is not acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-ying-hoi-closed-causal-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();checkpoint=BASE/'xl-terrain-recovery-20261010-ying-hoi-current-causal-dispositions-v1';r=read(checkpoint/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 parents=[p for p in BASE.glob('xl-terrain-recovery-20261010-ying-hoi-*') if p.is_dir() and p!=OUT];parents.append(BASE/'government-xl-terrain-recovery-ying-hoi-existing-terrain-current-v1-20261010');paths=set()
 for parent in parents:
  assert not (parent/'partial-diagnostic.json.gz').exists() or (parent/'diagnostic.json.gz').exists(),str(parent)
  paths.update(str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file())
 scripts=['xl-terrain-recovery-20261010-ying-hoi-existing-terrain-current-v1.py','xl-terrain-recovery-20261010-ying-hoi-fresh-original-support-replay-v1.py','xl-terrain-recovery-20261010-ying-hoi-current-causal-dispositions-v1.py','original_local_host_plane_boundary_diagnostic_20261010.py','test_original_local_host_plane_boundary_diagnostic_20261010.py','original_local_host_plane_boundary_diagnostic_v2_20261010.py','test_original_local_host_plane_boundary_diagnostic_v2_20261010.py','original_local_perpendicular_boundary_diagnostic_20261010.py','exact_original_perpendicular_edge_facet_band_20261010.py','test_exact_original_perpendicular_edge_facet_band_20261010.py','test_exact_original_perpendicular_edge_facet_band_actual_ying_hoi_20261010.py','xl-terrain-recovery-20261010-original-local-facade-planes-v1.py','xl-terrain-recovery-20261010-original-local-facade-planes-v2.py','xl-terrain-recovery-20261010-original-local-facade-perpendicular-v1.py'];paths.update(str((HERE/p).relative_to(ROOT)) for p in scripts);paths.add(str(Path(__file__).relative_to(ROOT)))
 # Explicit aliases, independently byte-pinned. Do not recursively expand a
 # whole historical global manifest into unrelated raw territory exports.
 archives=[HERE/'local/government-xl-glorious-peak-two-atomic-installed-v1-20261010/manifest-before-installation.json',BASE/'xl-terrain-recovery-20261010-polyu-current-disjoint-rebind-v1/historical-manifest.json'];aliases=[]
 for p in archives:assert p.exists();paths.add(str(p.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(p.read_bytes()),archive=ref(p)))
 leaf=read(BASE/'xl-terrain-recovery-20261010-glorious-peak-current-role-closed-scope-v1/closed-scope.json')['metadataLeafPaths']
 save(OUT/'closed-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=leaf,causalDispositionsNeon=r['jobId'],scopeType='Closed explicit producer/documents; transitive source and runtime bindings are in the frozen current receipts and require independent closure verification before commit.',currentNumericReplayAuthority='Exact retained205663/candidate207957 source bytes/provider-root streams,11590 original/runtime faces,655 original components,478 exact original contacts, complete byte-bound current drawn ground and whole-facet clearance; independent current identities/foundations/foreign/runtime checks.',remainingOriginalDetailRoles=35,diagnosticPerpendicularBoundaryPasses=165,detachedBeyondExistingBandComponents=[276,277],installationApproved=False,qualification='Checkpoint only. No visual role approval, root/bridge credit, geometry edit, threshold change, runtime/publication or installed count credit. PolyU active compute/proofs excluded. Historical whole-map manifests remain explicit byte-bound metadata leaves.'))
 print(dict(closedExplicitPaths=len(paths),checkpointNeon=r['jobId']))
if __name__=='__main__':main()
