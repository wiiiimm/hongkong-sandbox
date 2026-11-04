"""Compose Academy's private TIN as a disjoint child of its retained regional grid."""
import argparse,copy,sys,uuid,traceback
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from nested_coordinated_parent_contract_v1_20261027 import targets
from disjoint_nested_append_contract_v1_20261029 import POLICY,FIELD,verify_append,private_validator,overlaps
from nested_terrain_patch_validation_v1_20261027 import validate_patch
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-academy69025-nested-parent-composition-v2-20261029';UID='landsd/69025:0'
PARENT='city/data/government-xl-ocean-coordinated-original-qualified-stage-v1-20261027-terrain.json'
PATCH='government-xl-academy69025-stored-floor-return-v2-20261029'
RUNTIME='government-xl-academy69025-stored-return-current-evidence-v1-20261029-69025-0-runtime'
def main():
    p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=HERE/'local'/(BATCH+'-runner')/'reservation.json';assert not out.exists()and not local.exists()
    parentpath=ROOT/'3d-viewer'/PARENT;prior=read(parentpath);resources=['building:'+u for u in sorted(targets(prior)|{UID})]+['terrain:city/data/terrain.json','terrain:'+PARENT]
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('academy-nested-original-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__),parentpath];pins={}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    proposal=take(PATCH,BASE/PATCH/'summary.json');old=take(PATCH,ROOT/proposal['candidate']['path']);selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');take(RUNTIME,BASE/RUNTIME/'metrics.json')
    assert proposal['status']=='private-terrain-validator-passed'and proposal['uids']==[UID]and ref(parentpath)['sha256']==pins[RUNTIME][str(parentpath.relative_to(ROOT))]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=take(PATCH,rootpath);pg=prior['meta']['georef'];g=old['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];x1=x0+(old['w']-1)*g['aE'];z1=z0-(old['h']-1)*g['aN'];bounds=[x0,z0,x1,z1]
    cells=[round((x0+834500-pg['bE'])/pg['aE']),round((816500-z0-pg['bN'])/pg['aN']),round((x1+834500-pg['bE'])/pg['aE']),round((816500-z1-pg['bN'])/pg['aN'])]
    assert not any(overlaps(cells,p['coarseCells'])for p in prior['patches'])and not any(overlaps(cells,c)for c in prior.get('patchExclusions',[]))
    out.mkdir();local.mkdir();save(out/'parent-before.json',prior);result=dict(uids=[UID],sourceSHA256ByUid=proposal['sourceSHA256ByUid'],status='private-nested-parent-investigation',installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,nestedCells=cells,nestedBounds=bounds)
    try:
        builder=module('academy_existing_nested_builder',HERE/'resolve-pass-indexed-parent-clipping.py');mesh=old['nativeMesh'];tri=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
        overlap=module('academy_nested_overlap_proof',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/'overlap';overlap.DOC.mkdir()
        original_validate=builder.validate_patch
        def qualify_overlap_then_validate(node,parent):
            overlap.overlap_proof(node,refs)
            return original_validate(node,parent)
        builder.validate_patch=qualify_overlap_then_validate
        child=builder.make_patch(dict(cells=cells,uids=[UID]),prior,tri,[dict(privateFloorReturn=ref(ROOT/proposal['candidate']['path']),sourceSHA256ByUid=proposal['sourceSHA256ByUid'])],native_core=[x0+10,z0+10,x1-10,z1-10],parent_url=PARENT,parent_sha256=ref(parentpath)['sha256'])
        assert len(child['nativeMesh']['index'])//3<=25000
        builder.validate_patch=original_validate
        save(local/'child.json',child);proof=dict(policy=POLICY,beforeParent=ref(out/'parent-before.json'),child=ref(local/'child.json'),newTargetUids=[UID]);save(out/'append-proof.json',proof)
        successor=copy.deepcopy(prior);successor['patches'].append(child);successor['meta']['targetUids']=sorted(targets(prior)|{UID});successor['meta'][FIELD]=dict(policy=POLICY,proof=ref(out/'append-proof.json'))
        assert verify_append(successor)==prior
        with private_validator():validate_patch(successor,root)
        save(local/'candidate-terrain.json',successor);save(out/'scope.json',dict(bounds=bounds,coarseCells=old['coarseCells'],uids=[UID],nestedCells=cells,retainedParentURL=PARENT))
        result.update(status='private-terrain-validator-passed',candidate=ref(local/'candidate-terrain.json'),terrainTriangles=len(child['nativeMesh']['index'])//3,changedParentFaces=None,allRetainedGridAndChildBodiesUnchanged=True,retainedChildren=len(prior['patches']),replacedNativeTerrain=[dict(url=PARENT,sha256=ref(parentpath)['sha256'],retainedUids=sorted(targets(prior)),coarseCells=prior['coarseCells'])],qualifiedForActualRendererDiagnostics=True)
        refs.extend([local/'child.json',local/'candidate-terrain.json',out/'append-proof.json',out/'parent-before.json'])
    except Exception as e:
        result.update(reason=str(e),errorType=type(e).__name__);save(out/'failure.json',dict(errorType=type(e).__name__,message=str(e),traceback=traceback.format_exc()))
    result['qualification']='Exact old regional parent grid, children/order and unrelated metadata retained. One disjoint source-bound native child only, with existing1m nested builder, ordinary parent-boundary/overlap/height/25k checks. Existing coordinated member proofs see their exact retained old parent only after the complete append contract is verified. No model, identity, neighbour, support, browser or publication acceptance.'
    save(out/'summary.json',result);refs.extend([HERE/'disjoint_nested_append_contract_v1_20261029.py',HERE/'test_disjoint_nested_append_contract_v1_20261029.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'nested_terrain_patch_validation_v1_20261027.py',HERE/'nested_native_terrain_validation_v1_20261027.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py']);assert reservations.owns(lease)
    module('academy_nested_append_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-regional-parent-retention-and-disjoint-original-terrain-child',refs,result);print({k:result.get(k)for k in ['status','reason','terrainTriangles','retainedChildren']},flush=True)
if __name__=='__main__':main()
