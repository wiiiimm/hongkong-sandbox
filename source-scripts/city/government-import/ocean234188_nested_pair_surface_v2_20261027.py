"""Bind and validate Ocean Centre's private nested original-terrain pair."""
import argparse
import copy
import json
import traceback
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_coverage import approve_roundoff
from nested_coordinated_parent_contract_v1_20261027 import POLICY as PARENT_POLICY,targets,verify_parent
from nested_coordinated_native_boundary_v1_20261027 import POLICY,canonical_sha,reference,validate_effective_coordinated_members
from nested_terrain_patch_validation_v1_20261027 import validate_patch


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);args=parser.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/args.batch;local=HERE/'local'/args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists() and not local.exists()
    prefix='government-xl-after-waterfront-ocean234188-';refs=[Path(__file__)];pins={};receipts={}
    for suffix in ['partitioned-inset-v1-20261027','partitioned-parent-v1-20261027','partitioned-seam-foundation-v1-20261027','retained-group-preflight-v1-20261027']:
        folder=base/(prefix+suffix);receipt,bound=authenticate(folder);receipts[suffix]=receipt;refs.append(folder/'result.json')
        for name,sha in bound.items():
            assert name not in pins or pins[name]==sha; pins[name]=sha
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    proposal=receipts['partitioned-inset-v1-20261027'];parents=receipts['partitioned-parent-v1-20261027'];seams=receipts['partitioned-seam-foundation-v1-20261027']
    assert proposal['status']=='private-partition-faces-coverage-passed' and all(r['passed'] for r in seams['seams'])
    assert all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in seams['foundations'])
    contact=receipts['retained-group-preflight-v1-20261027']['terrainContacts'][0]
    parentpath=ROOT/'3d-viewer'/contact['url'];prior=read(parentpath);assert digest(parentpath.read_bytes())==contact['sha256'];refs.append(parentpath)
    assert len(prior['patches'])==15 and contact['overlappingChildren']==[12]
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath)
    old=prior['patches'][12];assert set(old['meta']['targetUids'])=={'landsd/205767:0','landsd/210032:0','landsd/73140:0'}
    raw=np.asarray(old['nativeMesh']['position'],dtype='float32').astype(float).reshape(-1,3)[np.asarray(old['nativeMesh']['index']).reshape(-1,3)]
    captured_path=ROOT/parents['rows'][0]['capturePath'];captured=np.asarray(read(captured_path)['triangles'],float);refs.append(captured_path)
    # Match world.js makeNativeTerrain's exact Float32 index rewinding.
    delta1,delta2=raw[:,1]-raw[:,0],raw[:,2]-raw[:,0]
    rewound=(delta1[:,2]*delta2[:,0]-delta1[:,0]*delta2[:,2])<0
    raw[rewound]=raw[rewound][:,[0,2,1]]
    assert np.array_equal(raw,captured),'Captured prior differs after exact actual-renderer winding'
    result=dict(uids=proposal['uids'],sourceSHA256=proposal['sourceSHA256'],installationApproved=False,publication=False,
                renderedIndexRewinds=int(rewound.sum()),failedPredecessor='V1 compared raw source winding against actual renderer winding; 390 exact index rewinds accounted for, no changed coordinates or omitted facets.',sourceGeometryChanges=0,qualification='Private nested canonical surface validation only. No original model changes, installation, retained-model acceptance, identity approval or browser approval.')
    try:
        builder=module('ocean_nested_template_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
        south_capture=ROOT/parents['rows'][1]['capturePath'];refs.append(south_capture)
        values=np.asarray(read(south_capture)['triangles'],float)
        g=prior['meta']['georef'];bounds=parents['rows'][1]['bounds']
        cells=[round((bounds[0]+834500-g['bE'])/g['aE']),round((bounds[1]-816500+g['bN'])/g['aE']),
               round((bounds[2]+834500-g['bE'])/g['aE']),round((bounds[3]-816500+g['bN'])/g['aE'])]
        south=builder.make_patch(dict(cells=cells,uids=proposal['uids']),prior,values,[],
              native_core=[bounds[0]+10,bounds[1]+10,bounds[2]-10,bounds[3]-10],parent_url=contact['url'],parent_sha256=contact['sha256'])
        before={'north':copy.deepcopy(old),'south':south}
        before['north']['meta'].update(parentTerrain=contact['url'],parentSha256=contact['sha256'])
        skeletons={};members={}
        def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
        for name,row in zip(['north','south'],proposal['rows']):
            oldpath=local/(name+'-before.json');save(oldpath,before[name]);refs.append(oldpath)
            path=ROOT/row['privateFacesPath'];assert digest(path.read_bytes())==row['privateFacesSHA256'];refs.append(path)
            faces=np.asarray(read(path)['triangles'],float);node=copy.deepcopy(before[name]);mesh=node['nativeMesh']
            mesh['position']=faces.reshape(-1).tolist();mesh['index']=list(range(faces.size//3));mesh.pop('sourceOverlap',None)
            previous=copy.deepcopy(mesh['source']);mesh['source']={k:v for k,v in mesh['source'].items() if k not in ['numericalCoverageGap','protectedParentProjection','coordinatedBoundary','numericalProjectionOverlap']}
            mesh['source']['originalPartitionedInset']=dict(proposal=ref(base/(prefix+'partitioned-inset-v1-20261027')/'result.json'),previousSourceMetadata=previous,sourceModelSHA256=proposal['sourceSHA256'])
            node['meta']['targetUids']=sorted(set(before[name]['meta']['targetUids'])|set(proposal['uids']))
            approve_roundoff(node,row['bounds'])
            path=local/(name+'-unbound.json');save(path,node);refs.append(path);skeletons[name]=node
            members[name]=dict(before=ref(oldpath),candidate=ref(path),canonicalSHA256=canonical_sha(node))
        new_work=proposal['rows'][0]['privateFaces']-proposal['rows'][0]['exactUnchangedParentFaces']+proposal['rows'][1]['privateFaces']
        assert new_work<=25000,'Newly derived terrain runtime budget exceeded'
        proofpath=out/'finite-boundary-proof.json';proof=dict(policy=POLICY,parent=ref(parentpath),members=members,
              editRegionWKT=parents['outerWKT'],parentBinding=dict(policy=PARENT_POLICY,retainedMember='north',retainedChildIndex=12,newMember='south',newTargetUids=proposal['uids']))
        save(proofpath,proof);refs.append(proofpath);marked={}
        for name in ['north','south']:
            node=copy.deepcopy(skeletons[name]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=POLICY,proof=ref(proofpath),member=name)
            overlap=module('ocean_nested_overlap_'+name,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/(name+'-overlap');overlap.DOC.mkdir(parents=True)
            overlap.overlap_proof(node,[ROOT/members[name]['candidate']['path'],proofpath,Path(__file__)])
            assert canonical_sha(node)==members[name]['canonicalSHA256'];marked[name]=node
        successor=copy.deepcopy(prior);successor['patches'][12]=marked['north'];successor['patches'].append(marked['south']);successor['meta']['targetUids']=sorted(targets(prior)|set(proposal['uids']))
        retention=verify_parent(prior,successor,proof,marked['north']['nativeMesh']['source']['coordinatedBoundary'],reference,canonical_sha)
        validate_effective_coordinated_members(successor['patches'])
        validate_patch(successor,root)
        dest=local/'candidate-terrain.json';save(dest,successor);refs.append(dest)
        result.update(status='private-nested-coordinated-surface-validator-passed',candidate=ref(dest),retention=retention,
              newlyDerivedTerrainWorkFaces=new_work,oldRenderedChildFaces=len(raw),bothEffectiveMembersRequired=True,
              replacedNativeTerrain=[dict(url=contact['url'],sha256=contact['sha256'],retainedUids=sorted(targets(prior)),coarseCells=prior['coarseCells'])])
    except Exception as error:
        result.update(status='bounded-nested-surface-investigation',reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    refs.extend(HERE/name for name in ['nested_coordinated_parent_contract_v1_20261027.py','nested_coordinated_native_boundary_v1_20261027.py',
         'nested_native_terrain_validation_v1_20261027.py','nested_terrain_patch_validation_v1_20261027.py','float32_coverage.py','sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    result=json.loads(json.dumps(result));save(out/'summary.json',result)
    module('ocean_nested_surface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'private-exact-nested-coordinated-original-terrain-surface',list(dict.fromkeys(refs)),result)
    print(dict(status=result['status'],reason=result.get('reason')),flush=True)


if __name__=='__main__':main()
