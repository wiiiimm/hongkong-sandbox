"""Bind and validate both private original-terrain members under finite shared-edge rules."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import sys
INTEGRATION=HERE.parent/'island-detail-integration'
if str(INTEGRATION)not in sys.path:sys.path.insert(0,str(INTEGRATION))
from coordinated_native_boundary import POLICY,canonical_sha,validate_effective_coordinated_members


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-paired-surface-binding-v5-20261023';out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists();refs=[Path(__file__)]
    prior='government-xl-island-cheong-shing-four-source-terrain-scope-v1-20261023';_,pins=authenticate(base/prior);refs.append(base/prior/'result.json')
    lineagebatch='government-xl-island-industrial-paired-inset-diagnostic-v1-20261023'
    for extra in [lineagebatch,'government-xl-island-industrial-paired-surface-binding-v4-20261023']:
        _,bound=authenticate(base/extra);refs.append(base/extra/'result.json')
        for name,sha in bound.items():
            assert name not in pins or pins[name]==sha
            pins[name]=sha
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    diagnostic=take(base/prior/'summary.json');assert diagnostic['status']=='private-paired-four-source-terrain-scope-metadata'and diagnostic['terrainGeometryUnchanged']and len(diagnostic['coInstallationRequired'])==4
    lineage=take(base/lineagebatch/'lineage.json.gz');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    before={'south':ROOT/'3d-viewer/city/data/government-native-225173-0.json','north':ROOT/'3d-viewer/city/data/government-native-fu-tor-loy-original-v1-20261023.json'}
    originals={};skeletons={};members={}
    for record in diagnostic['members']:
        name=record['member'];candidate=take(ROOT/record['candidate']['path']);originals[name]=candidate
        old=take(before[name]);candidate=copy.deepcopy(candidate);candidate['nativeMesh'].pop('sourceOverlap',None);candidate['nativeMesh']['source'].pop('coordinatedBoundary',None)
        skeletons[name]=candidate;path=local/(name+'-unbound.json');save(path,candidate);refs.append(path)
        members[name]=dict(before=ref(before[name]),candidate=ref(path),canonicalSHA256=canonical_sha(candidate))
    proofpath=out/'finite-boundary-proof.json';save(proofpath,dict(policy=POLICY,parent=ref(parentpath),members=members,editRegionWKT=lineage['outerWKT']))
    refs.append(proofpath);builder=module('paired_surface_validator',HERE/'validated_parent_roundoff_template_v2.py');outputs=[];validated=[]
    for name in ['south','north']:
        candidate=copy.deepcopy(skeletons[name]);candidate['nativeMesh']['source']['coordinatedBoundary']=dict(policy=POLICY,proof=ref(proofpath),member=name)
        overlap=module('paired_bound_overlap_'+name,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/(name+'-overlap');overlap.DOC.mkdir()
        overlap.overlap_proof(candidate,[ROOT/members[name]['candidate']['path'],proofpath,Path(__file__),INTEGRATION/'coordinated_native_boundary.py'])
        assert candidate['nativeMesh']['position']==originals[name]['nativeMesh']['position']and candidate['nativeMesh']['index']==originals[name]['nativeMesh']['index'],'Binding must not alter terrain geometry'
        builder.validate_patch(candidate,parent)
        path=local/(name+'-candidate.json');save(path,candidate);refs.append(path);validated.append(candidate)
        outputs.append(dict(member=name,candidate=ref(path),replaces=dict(url=str(before[name].relative_to(ROOT/'3d-viewer')),sha256=members[name]['before']['sha256'],retainedUids=read(before[name])['meta']['targetUids']),surfaceValidated=True,terrainFaces=len(candidate['nativeMesh']['index'])//3,terrainGeometryChangedSinceDiagnostic=False))
        print(dict(member=name,surfaceValidated=True,terrainFaces=outputs[-1]['terrainFaces']),flush=True)
    validate_effective_coordinated_members(validated)
    current_manifest=ROOT/'3d-viewer/city/data/manifest.json';take(current_manifest)
    result=dict(uids=diagnostic['uids'],members=outputs,currentManifest=ref(current_manifest),finiteBoundaryProof=ref(proofpath),bothEffectiveMembersRequired=True,sourceGeometryChanges=0,installationApproved=False,status='private-coordinated-surface-validator-passed',qualification='Both exact private terrain geometries pass ordinary coverage/overlap/grid/root-edge rules plus hash-bound complete finite shared-edge checks inside the local edit. Publishing either half alone is rejected. This is surface validation only: model identity/support/fourworld/full current native/base/device/browser and publication acceptance remain separate.')
    save(out/'summary.json',result);refs.extend([INTEGRATION/'coordinated_native_boundary.py',INTEGRATION/'native_terrain_validation.py',INTEGRATION/'publish.py',HERE/'coordinated_native_boundary_v1_20261023.py',HERE/'finite_native_boundary_strip_v1_20261023.py',HERE/'test_finite_native_boundary_strip_v1_20261023.py',HERE/'test_coordinated_native_boundary_binding_v1_20261023.py',HERE/'validated_parent_roundoff_template_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    module('paired_surface_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-finite-coordinated-original-terrain-surface-validation-v5',refs,result)
    print(dict(bothSurfacesValidated=True,installationApproved=False),flush=True)


if __name__=='__main__':main()
