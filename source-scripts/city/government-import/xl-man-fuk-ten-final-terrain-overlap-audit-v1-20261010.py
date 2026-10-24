"""Recompute the final qualified terrain audit; change audit metadata only.

Every position/index, parent-preservation record and source proposal is retained.
The old invalid audit stays immutable. This grants no installation credit.
"""
import copy,importlib.util,json,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import approve_original_overlap,finalize_overlap_evidence
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-man-fuk-ten-final-terrain-overlap-audit-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PHYS=BASE/'government-xl-man-fuk-ten-original-coupled-physical-v3-20261010'
ROLE=BASE/'government-xl-man-fuk-ten-current-complete-typed-role-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not LOCAL.exists()
 role=read(ROLE/'typed-role.json.gz');assert role['currentTypedPhysicalAccepted'] and not role['reasons']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start==role['currentManifest']
 c=read(PHYS/'terrain-candidates.json')[0];source=ROOT/c['path'];assert ref(source)['sha256']==c['sha256']== '422644c1c173dac0bad0a616a9ee9ef10a385a3787eacfa648c500c6986a93cc'
 original=read(source);terrain=copy.deepcopy(original)
 old=read(ROOT/original['nativeMesh']['sourceOverlap']['evidencePath'])
 source_files=old['source']['files']+[ref(source)]
 source_files.extend(ref(ROOT/r['candidate']['path']) for r in read(PHYS/'selection.json.gz')['rows'])
 for r in source_files:assert ref(ROOT/r['path'])==r
 terrain['nativeMesh'].pop('sourceOverlap');path=LOCAL/'government-native-266062-0.json';save(path,terrain)
 audit_path=DOC/'final-native-overlap.json'
 audit=approve_original_overlap(terrain,path,audit_path,source_files)
 terrain['nativeMesh']['sourceOverlap']['evidencePath']=str(audit_path.relative_to(ROOT))
 # Actual production sampler and complete ray geometry provide an additional
 # independent check; retain every barycentric/plane witness separately.
 actual=json.loads(subprocess.check_output(['node',str(HERE/'native_overlap_actual_ray_readonly_20261010.mjs'),str(path),str(audit_path)],cwd=ROOT,text=True))
 audit['independentBarycentricPlaneAgreement']=audit['float32HighestRayAgreement']
 audit['float32HighestRayAgreement']=actual
 audit['qualification']='Final qualified terrain proposal; overlap is measured on complete actual Float32 facets. Terrain modifications occurred in earlier separately qualified proposals, not in this metadata-only audit refresh.'
 save(audit_path,audit);finalize_overlap_evidence(terrain,audit_path)
 original_without=copy.deepcopy(original);original_without['nativeMesh'].pop('sourceOverlap')
 final_without=copy.deepcopy(terrain);final_without['nativeMesh'].pop('sourceOverlap')
 assert final_without==original_without
 save(path,terrain);assert read(path)==terrain and ref(manifest)==start
 proof=dict(metadataOnly=True,allRendererInputFieldsExactlyEqual=True,originalTerrain=ref(source),finalTerrain=ref(path),overlapAudit=ref(audit_path),originalAudit=ref(ROOT/original['nativeMesh']['sourceOverlap']['evidencePath']),currentCompleteRole=ref(ROLE/'typed-role.json.gz'),sourceGeometryChanges=0,terrainNumericGeometryChanges=0,publication=False,newlyInstalled=0)
 save(DOC/'metadata-only-proof.json',proof);save(DOC/'terrain-candidates.json',[{**c,'path':str(path.relative_to(ROOT)),'sha256':ref(path)['sha256']}])
 spec=importlib.util.spec_from_file_location('final_overlap_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'final-qualified-terrain-exact-metadata-only-overlap-audit-v1',[Path(__file__),HERE/'native_patch_resolution.py',HERE/'native_overlap_actual_ray_readonly_20261010.mjs',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/vendor/three.module.js',manifest,ROLE/'result.json',ROLE/'typed-role.json.gz',path,audit_path,DOC/'metadata-only-proof.json',DOC/'terrain-candidates.json',source]+[ROOT/r['path'] for r in source_files],proof)
 print(dict(metadataOnly=True,actualRaySamples=actual['samples'],actualRayMaximumError=actual['maxError'],terrain=ref(path)),flush=True)
if __name__=='__main__':main()
