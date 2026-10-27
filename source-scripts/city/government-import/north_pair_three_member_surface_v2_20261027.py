"""Validate the North originals' terrain while retaining the installed southern mate.

Reuses frozen prepared faces; no reacquisition, TIN recomputation or model edits.
"""
import copy,traceback
import numpy as np
import shapely
from preserve_original_boundary_facets_v1_20261027 import preserve_boundary_facets
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import three_member_native_boundary_v1_20261027 as chain

def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-west-kowloon-north-pair-after-ocean-'
    batch=prefix+'three-member-surface-v2-20261027';out=base/batch;local=HERE/'local'/batch
    assert not out.exists() and not local.exists()
    refs=[HERE/'north_pair_three_member_surface_v2_20261027.py',HERE/'three_member_native_boundary_v1_20261027.py',HERE/'test_three_member_native_boundary_v1_20261027.py',HERE/'test_coordinated_native_boundary_binding_v1_20261023.py',HERE/'local/government-xl-north-three-member-tests-v1-20261027/test-results.log']
    refs.extend([HERE/'preserve_original_boundary_facets_v1_20261027.py',HERE/'test_preserve_original_boundary_facets_v1_20261027.py',HERE/'local/government-xl-north-three-member-tests-v1-20261027/facet-test-results.log'])
    pins={};receipts={}
    for suffix in ['canonical-surface-v1-20261027','existing-boundary-lineage-v1-20261027','partitioned-inset-v3-20261027']:
        receipt,bound=authenticate(base/(prefix+suffix));receipts[suffix]=receipt;refs.append(base/(prefix+suffix)/'result.json')
        for name,sha in bound.items():assert name not in pins or pins[name]==sha;pins[name]=sha
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    assert receipts['existing-boundary-lineage-v1-20261027']['all44AreExactUnchangedOldBoundaryVertices']
    assert receipts['canonical-surface-v1-20261027']['status']=='private-canonical-surface-investigation'
    proposal=receipts['partitioned-inset-v3-20261027'];assert proposal['status']=='private-partition-faces-coverage-passed'
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    def take(path):assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=take(rootpath)
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';take(manifestpath)
    before={'south':ROOT/'3d-viewer/city/data/government-native-island-cheong-shing-south-v1-20261023.json',
            'middle':ROOT/'3d-viewer/city/data/government-native-island-cheong-shing-north-v1-20261023.json',
            'north':ROOT/'3d-viewer/city/data/government-native-272986-0.json'}
    old={name:take(path)for name,path in before.items()}
    priorlocal=HERE/'local'/(prefix+'canonical-surface-v1-20261027')
    skeletons={'middle':take(priorlocal/'south-unbound.json'),'north':take(priorlocal/'north-unbound.json'),'south':copy.deepcopy(old['south'])}
    old_marker=old['middle']['nativeMesh']['source']['coordinatedBoundary'];oldproofpath=ROOT/old_marker['proof']['path']
    assert digest(oldproofpath.read_bytes())==old_marker['proof']['sha256'];oldproof=read(oldproofpath);refs.append(oldproofpath)
    assert oldproof['parent']==ref(rootpath)
    assert chain.legacy.canonical_sha(old['south'])==oldproof['members']['south']['canonicalSHA256']
    assert chain.legacy.canonical_sha(old['middle'])==oldproof['members']['north']['canonicalSHA256']
    members={};gridchecks=[];restoration=[]
    edit=shapely.from_wkt(proposal['outerWKT'])
    for name,node in skeletons.items():
        node['nativeMesh'].pop('sourceOverlap',None);node['nativeMesh']['source'].pop('coordinatedBoundary',None)
        previous=old[name];step=previous['cell'];assert step==node['cell']
        def faces(item):
            mesh=item['nativeMesh'];return np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
        output,restored=preserve_boundary_facets(faces(previous),faces(node),chain.legacy.bounds(previous),edit)
        if restored:
            assert name=='middle' and [r['originalFace']for r in restored]==[54044,56588,60643,60882]
            mesh=node['nativeMesh'];mesh['position']=output.reshape(-1).tolist();mesh['index']=list(range(output.size//3))
            audit=out/(name+'-restored-original-boundary-facets.json')
            save(audit,dict(member=name,original=ref(before[name]),restored=restored,noOtherTerrainCoordinatesChanged=True,sourceGeometryChanges=0))
            refs.append(audit);mesh['source']['originalBoundaryFacetPreservation']=ref(audit)
            restoration.extend(restored)

        dx=(previous['meta']['georef']['bE']-node['meta']['georef']['bE'])/step
        dz=(node['meta']['georef']['bN']-previous['meta']['georef']['bN'])/step
        assert dx==int(dx) and dz==int(dz) and dx>=0 and dz>=0
        dx,dz=int(dx),int(dz)
        assert previous['w']+dx<=node['w'] and previous['h']+dz<=node['h']
        for key in ['elev','renderedElev','vegetation']:
            for r in range(previous['h']):assert node[key][(r+dz)*node['w']+dx:(r+dz)*node['w']+dx+previous['w']]==previous[key][r*previous['w']:(r+1)*previous['w']]
        if name=='south':
            stripped=copy.deepcopy(previous);stripped['nativeMesh'].pop('sourceOverlap',None);stripped['nativeMesh']['source'].pop('coordinatedBoundary',None)
            assert node==stripped,'Additional southern mate must retain its entire unmarked body'
        gridchecks.append(dict(member=name,oldGridValuesExact=True,retainedGridNodes=previous['w']*previous['h'],sourceFacesUnchanged=name=='south'))
        path=local/(name+'-unbound.json');save(path,node);refs.append(path)
        members[name]=dict(before=ref(before[name]),candidate=ref(path),canonicalSHA256=chain.legacy.canonical_sha(node))
    assert len(restoration)==4
    pairs=[]
    for index,(names,region)in enumerate([(['south','middle'],oldproof['editRegionWKT']),(['middle','north'],proposal['outerWKT'])]):
        path=out/('pair-'+str(index)+'.json');save(path,dict(policy=chain.legacy.POLICY,parent=ref(rootpath),members={name:members[name]for name in names},editRegionWKT=region));refs.append(path);pairs.append(ref(path))
    proofpath=out/'three-member-proof.json';save(proofpath,dict(policy=chain.POLICY,parent=ref(rootpath),members=members,pairs=pairs));refs.append(proofpath)
    result=dict(uids=proposal['uids'],sourceSHA256ByUid=proposal['sourceSHA256ByUid'],members=[],retainedGridChecks=gridchecks,
                installationApproved=False,publication=False,sourceGeometryChanges=0,additionalMateGeometryChanges=0,restoredOriginalBoundaryFacets=len(restoration),
                qualification='Private three-member surface validation only. Unchanged finite-pair kernels check both edges; all other boundaries retain the canonical root-height gate. Original/source identity, four-world neighbours and browser acceptance remain separate.')
    try:
        builder=module('north_chain_surface_validator',HERE/'validated_parent_roundoff_template_v2.py');validated=[]
        with chain.private_validator():
            for name in ['south','middle','north']:
                node=copy.deepcopy(skeletons[name]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=chain.POLICY,proof=ref(proofpath),member=name)
                overlap=module('north_chain_overlap_'+name,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/(name+'-overlap');overlap.DOC.mkdir()
                overlap.overlap_proof(node,[ROOT/members[name]['candidate']['path'],proofpath,HERE/'three_member_native_boundary_v1_20261027.py'])
                assert node['nativeMesh']['position']==skeletons[name]['nativeMesh']['position'] and node['nativeMesh']['index']==skeletons[name]['nativeMesh']['index']
                builder.validate_patch(node,root)
                path=local/(name+'-candidate.json');save(path,node);refs.append(path);validated.append(node)
                result['members'].append(dict(member=name,candidate=ref(path),replaces=dict(url=str(before[name].relative_to(ROOT/'3d-viewer')),sha256=digest(before[name].read_bytes()),retainedUids=old[name]['meta']['targetUids']),surfaceValidated=True,boundaryOnlyRetainedMate=name=='south'))
                print('Validated three-member surface',name,flush=True)
            chain.validate_effective_coordinated_members(validated)
        result.update(status='private-three-member-chain-surface-validator-passed',allEffectiveMembersRequired=True,currentManifest=ref(manifestpath))
    except Exception as error:
        result.update(status='private-three-member-surface-investigation',reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    refs.extend([chain.INTEGRATION/'coordinated_native_boundary.py',chain.INTEGRATION/'native_terrain_validation.py',chain.INTEGRATION/'publish.py',HERE/'validated_parent_roundoff_template_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    save(out/'summary.json',result)
    module('north_three_member_boundary_preserved_surface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-original-three-member-chain-surface-validation',refs,result)
    print(dict(status=result['status'],reason=result.get('reason')),flush=True)

if __name__=='__main__':main()
