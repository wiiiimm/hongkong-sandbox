"""Validate frozen Tower3 floor geometry after a caller path-join error.

Reuse the completed terrain work; do not recompute floors or source geometry.
Existing three-member finite boundary and canonical native validators apply.
"""
import argparse,copy,sys,uuid,traceback
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
import three_member_native_boundary_v1_20261027 as chain
BASE=ROOT/'docs/astra-city/government-import'
PRIOR='government-xl-tower3-227380-retained-chain-floor-v2-20261102'
BATCH='government-xl-tower3-227380-retained-chain-validated-v3-20261102'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    out,local=BASE/BATCH,HERE/'local'/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json'
    assert not out.exists()and not local.exists()
    receipt,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    prior=take(BASE/PRIOR/'summary.json');assert prior['status']=='private-three-member-surface-investigation'and prior['errorType']=='TypeError'and prior['reason']=="'PosixPath' object is not subscriptable"
    assert prior['sourceFloorFacets']==81 and prior['changedOldFaces']==6 and prior['newWorkFaces']==771
    scope=take(BASE/PRIOR/'scope.json');resources=scope['leaseResources']
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('tower3-frozen-chain-validation-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==prior['currentManifestSHA256']
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath)
    proofpath=BASE/PRIOR/'three-member-proof.json';proof=take(proofpath)
    _,skeletons,_=chain.load_chain(ref(proofpath),parent)
    assert set(skeletons)=={'south','middle','north'}
    local.mkdir(parents=True);out.mkdir(parents=True)
    save(out/'scope.json',scope)
    for name in ['form-obligations.json.gz','native-obligations.json.gz']:
        path=BASE/PRIOR/name;save(out/name,take(path))
    result={k:v for k,v in prior.items()if k not in {'members','status','reason','errorType'}}
    result.update(members=[],preparedGeometryReusedWithoutRecomputation=True,preparedSource=ref(BASE/PRIOR/'result.json'),fullAffectedForms=scope['intersectingForms'],fullAffectedNativeActors=len(scope['touchingNativeUids']))
    immutable=[Path(__file__),parentpath,proofpath,*[ROOT[m['before']['path']]for m in proof['members'].values()],*[ROOT/m['candidate']['path']for m in proof['members'].values()]]
    try:
        builder=module('tower3_frozen_chain_validator',HERE/'validated_parent_roundoff_template_v2.py');validated=[]
        with chain.private_validator():
            for name in ['south','middle','north']:
                assert reservations.owns(lease)
                node=copy.deepcopy(skeletons[name]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=chain.POLICY,proof=ref(proofpath),member=name)
                overlap=module('tower3_frozen_overlap_'+name,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/(name+'-overlap');overlap.DOC.mkdir()
                overlap.overlap_proof(node,immutable)
                assert node['nativeMesh']['position']==skeletons[name]['nativeMesh']['position']and node['nativeMesh']['index']==skeletons[name]['nativeMesh']['index']
                builder.validate_patch(node,parent)
                path=local/(name+'-candidate.json');save(path,node);refs.append(path);validated.append(node)
                old=proof['members'][name]['before'];before=take(ROOT/old['path'])
                result['members'].append(dict(member=name,candidate=ref(path),replaces=dict(url=str((ROOT/old['path']).relative_to(ROOT/'3d-viewer')),sha256=old['sha256'],retainedUids=before['meta']['targetUids']),surfaceValidated=True,geometryChanges=name=='south'))
                print('Validated frozen member '+name,flush=True)
            chain.validate_effective_coordinated_members(validated)
        result.update(status='private-three-member-chain-surface-validator-passed',allEffectiveMembersRequired=True)
    except Exception as error:
        result.update(status='private-three-member-surface-investigation',reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    assert reservations.owns(lease)
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
    refs.extend([HERE/'three_member_native_boundary_v1_20261027.py',HERE/'validated_parent_roundoff_template_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',chain.INTEGRATION/'coordinated_native_boundary.py',chain.INTEGRATION/'native_terrain_validation.py'])
    save(out/'summary.json',result)
    module('tower3_frozen_chain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-prepared-tower3-three-member-surface-validation',list(dict.fromkeys(refs)),result)
    print(dict(status=result['status'],reason=result.get('reason')),flush=True)


if __name__=='__main__':main()
