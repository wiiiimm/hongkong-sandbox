"""Validate a source-preserving Festival Walk pair terrain candidate; no publication."""
import importlib.util
import sys
from run import ROOT,HERE,read,save,digest

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
checks=module('festival_pair_checks','xl-yoho-mall-ii-acceptance.py')
patches=module('festival_pair_patches','native_patch_resolution.py')
BASE=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC=BASE/'festival-pair-rescue-diagnostic-20260930'
def run():
    old=BASE/'festival-walk-terrain-diagnostic-20260925'
    option=read(BASE/'festival-support-terrain-options-20260930.json')['diagnosticParentRescue']
    source=ROOT/option['candidatePatch']['path'];assert digest(source.read_bytes())==option['candidatePatch']['sha256']
    patch=read(source);bounds=patches._patch_bounds(patch)
    _,_,missing,excess=patches.projected_context(patch,bounds)
    original_excess=patch['nativeMesh']['sourceOverlap']['measuredProjectedExcessM2']
    assert excess<=original_excess+.25 and missing.area<=.25
    patch['nativeMesh']['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','measuredAreaM2':missing.area,'maximumAreaM2':.25,'maximumFraction':1e-3}
    path=HERE/'local/government-xl-festival-pair-rescue-20260930/government-native-91827-0.json'
    evidence=DOC/'native-overlap.json'
    save(path,patch)
    audit=patches.approve_original_overlap(patch,path,evidence,read(old/'native-overlap.json')['source']['files'])
    patch['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT))
    patches.finalize_overlap_evidence(patch,evidence)
    module('festival_validator','../island-detail-integration/publish.py').validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
    save(path,patch)
    result={**read(old/'result.json'),'uids':['landsd/91827:0'],'patchPath':str(path.relative_to(ROOT)),'patchSHA256':digest(path.read_bytes())}
    save(DOC/'result.json',result)
    checks.DOC=DOC;checks.LOCAL=HERE/'local/government-xl-festival-pair-rescue-checks-20260930';checks.STAGE=checks.LOCAL/'candidates';sys.argv=[__file__,'prepare'];checks.run()
if __name__=='__main__':run()
