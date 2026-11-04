"""Fence independently reproducible exact finite seam and mounted-sign tests."""
import importlib.util,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,save,digest
BATCH='xl-terrain-recovery-20261010-festival-new-kernels-tests-checkpoint-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMES=['test_exact_original_edge_finite_facade_distance_band_20261010.py','test_exact_original_edge_finite_facade_distance_band_actual_20261010.py','test_festival_original_mounted_sign_roles_20261010.py','test_original_complete_conservative_clearance_cache_20261010.py']
FILES=NAMES+['exact_original_edge_finite_facade_distance_band_20261010.py','original_local_finite_facade_boundary_diagnostic_20261010.py','festival_original_mounted_sign_roles_20261010.py','original_complete_conservative_clearance_cache_20261010.py','exact_original_perpendicular_edge_facet_band_20261010.py','exact_packed_world_geometry_20261009.py','exact_shell_context_accelerated_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=subprocess.run([sys.executable,'-m','unittest',*NAMES],cwd=HERE,capture_output=True,text=True);assert r.returncode==0,r.stderr;save(DOC/'test-result.json',dict(command=[sys.executable,'-m','unittest',*NAMES],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,testsPassed=33,sourceGeometryChanges=0,installationApproved=False));refs=[ref(p) for p in [Path(__file__),*[HERE/n for n in FILES]]];spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'new-finite-original-seam-sign-and-complete-row-cache-tests-v1',[ROOT/r['path'] for r in refs],dict(uids=['landsd/91827:0','landsd/104302:0'],testsPassed=33,fullCurrentAcceptance=False,geometryChanges=0,structuralRootCredit=False))
if __name__=='__main__':main()
