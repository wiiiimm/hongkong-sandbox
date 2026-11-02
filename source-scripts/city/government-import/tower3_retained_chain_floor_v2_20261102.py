"""Private source-floor repair strictly inside the existing southern chain member.

No model edits or installation approval. All old member extents, targets, grids
and finite shared-boundary checks remain; middle/north indexed geometry stays
literal. Complete current actor scope is reserved before candidate work.
"""
import argparse, copy, sys, uuid, traceback
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from retained_native_floor_domains_v3_20261102 import inset
import three_member_native_boundary_v1_20261027 as chain
BASE=ROOT/'docs/astra-city/government-import'; UID='landsd/227380:0'
P='government-xl-tower3-227380-after-observatory-v1-20261102'
BATCH='government-xl-tower3-227380-retained-chain-floor-v2-20261102'
INVENTORY='government-xl-after-observatory-current-native-bounds-v1-20261102'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out,local=BASE/BATCH,HERE/'local'/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json'
    assert not out.exists() and not local.exists()
    refs,pins=[Path(__file__)],{}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(batch,name,private=False):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=(HERE/'local'/batch if private else BASE/batch)/name
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    inventory=take(INVENTORY,'complete-bounds.json.gz')
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
    assert digest(manifestpath.read_bytes())==pins[INVENTORY][str(manifestpath.relative_to(ROOT))];refs.append(manifestpath);mh=digest(manifestpath.read_bytes())
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath)
    before={};nodes={}
    for name in ['south','middle','north']:
        path=ROOT/f'3d-viewer/city/data/government-native-north-pair-{name}-v1-20261027.json'
        assert str(path.relative_to(ROOT/'3d-viewer')) in {r['url']for r in manifest['terrainPatches']}
        before[name]=path;nodes[name]=read(path);refs.append(path)
    oldmarker=nodes['south']['nativeMesh']['source']['coordinatedBoundary'];proofpath=ROOT/oldmarker['proof']['path']
    assert digest(proofpath.read_bytes())==oldmarker['proof']['sha256'];oldproof=read(proofpath);refs.append(proofpath)
    assert oldproof['policy']==chain.POLICY and oldproof['parent']==ref(parentpath)
    assert set(oldproof['members'])==set(nodes)
    for name,node in nodes.items():
        assert node['nativeMesh']['source']['coordinatedBoundary']==dict(oldmarker,member=name)
        assert chain.legacy.canonical_sha(node)==oldproof['members'][name]['canonicalSHA256']
    domain=shapely.union_all([shapely.box(*chain.legacy.bounds(n))for n in nodes.values()])
    forms=[]
    for entry in manifest['tiles']:
        path=ROOT/'3d-viewer'/entry['url'];assert digest(path.read_bytes())==inventory['currentFormTileHashes'][str(path.relative_to(ROOT))];refs.append(path)
        for form in read(path)['buildings']:
            points=[q for ring in form.get('rings',[])for q in ring]
            if points:
                t=np.asarray(points);lo,hi=t.min(0),t.max(0)
                if domain.intersects(shapely.box(*lo,*hi)):forms.append(form)
    assert len(forms)==len({f['uid']for f in forms})
    native=[]
    for row in inventory['rows']:
        boxes=row['completeFourWorldBounds'];assert len(boxes)==4
        if any(domain.intersects(shapely.box(lo[0],lo[2],hi[0],hi[2]))for lo,hi in boxes):native.append(row)
    resources={'terrain:city/data/terrain.json','building:'+UID}
    resources.update('terrain:'+str(path.relative_to(ROOT/'3d-viewer'))for path in before.values())
    resources.update(('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms)
    resources.update('building:'+r['uid']for r in native)
    resources.update('building:'+u for node in nodes.values()for u in node['meta']['targetUids'])
    initial={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('tower3-retained-chain-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
    assert digest(manifestpath.read_bytes())==mh
    selection=take(P+'-runtime','selection.json.gz');assert selection['manifestSHA256']==mh
    source=selection['rows'][0];assert source['uid']==UID and source['triangles']==12038
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes())
    ground=take(P+'-runtime','runtime-geometry.json.gz',True)['rows'][0]
    low=take(P+'-low-faces','original.json.gz')
    assert low['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes()) and low['completeSourceFaces']==len(tri)
    assert low['groundSHA256']==digest(np.asarray(ground['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3).tobytes())
    ids=[]
    for row in low['rows']:
        face=tri[row['sourceFace']];assert np.array_equal(face,np.asarray(row['vertices']))
        n=np.cross(face[1]-face[0],face[2]-face[0]);size=np.linalg.norm(n)
        if size and n[1]>=.25*size:ids.append(row['sourceFace'])
    assert len(ids)==len(set(ids))==81
    floors=tri[ids];outer=shapely.union_all(shapely.polygons(floors[:,:,[0,2]])).buffer(1.,join_style='mitre').buffer(3.,join_style='mitre')
    south=shapely.box(*chain.legacy.bounds(nodes['south']));assert south.covers(outer) and outer.distance(south.boundary)>0
    assert all(outer.disjoint(shapely.box(*chain.legacy.bounds(nodes[n])))for n in ['middle','north'])
    local.mkdir(parents=True);out.mkdir(parents=True)
    save(out/'form-obligations.json.gz',forms);save(out/'native-obligations.json.gz',native)
    save(out/'scope.json',dict(uids=[UID],domainWKT=domain.wkt,intersectingForms=len(forms),touchingNativeUids=[r['uid']for r in native],currentNativeActors=len(inventory['rows']),leaseResources=sorted(resources),installationApproved=False))
    baseline=chain.legacy.triangles(nodes['south']);after,work=inset(baseline,floors)
    assert work['retainedWorkBudget']['newWorkFaces']<=25000
    assert work['sourceClearanceM']==.05 and work['coreMarginM']==1. and work['returnWidthM']==3.
    save(out/'source-floor-proof.json.gz',work)
    save(out/'source-floor-facets.json',dict(uid=UID,sourceSHA256=source['sourceSHA256'],faces=[dict(sourceFace=i,vertices=tri[i].tolist())for i in ids],outerWKT=outer.wkt,minimumDistanceToSouthBoundaryM=outer.distance(south.boundary)))
    skeletons=copy.deepcopy(nodes);members={};result=dict(uids=[UID],sourceSHA256ByUid={UID:source['sourceSHA256']},members=[],sourceGeometryChanges=0,sourcePoseChanges=0,publication=False,installationApproved=False,neighboursChecked=False,currentManifestSHA256=mh)
    for name,node in skeletons.items():
        node['nativeMesh'].pop('sourceOverlap',None);node['nativeMesh']['source'].pop('coordinatedBoundary',None)
        if name=='south':
            node['nativeMesh']['position']=after.reshape(-1).tolist();node['nativeMesh']['index']=list(range(after.size//3));node['meta']['targetUids']=sorted(set(node['meta']['targetUids'])|{UID})
            node['nativeMesh']['source']['boundedOriginalFloorReturn']=dict(source=ref(asset),sourceFaceIds=ids,proof=ref(out/'source-floor-proof.json.gz'),policy='Existing fixed1m core/3m return/0.05m clearance; original indexed government building unchanged.')
        else:
            assert node['nativeMesh']['position']==nodes[name]['nativeMesh']['position'] and node['nativeMesh']['index']==nodes[name]['nativeMesh']['index']
            assert chain.legacy.canonical_sha(node)==chain.legacy.canonical_sha(nodes[name])
        for key in ['w','h','cell','coarseCells','elev','renderedElev','vegetation']:assert node[key]==nodes[name][key]
        path=local/(name+'-unbound.json');save(path,node);refs.append(path)
        members[name]=dict(before=ref(before[name]),candidate=ref(path),canonicalSHA256=chain.legacy.canonical_sha(node))
    pairrefs=[]
    for i,oldref in enumerate(oldproof['pairs']):
        path=ROOT/oldref['path'];assert digest(path.read_bytes())==oldref['sha256'];pair=read(path);refs.append(path)
        assert pair['policy']==chain.legacy.POLICY and pair['parent']==ref(parentpath)
        newpath=out/('pair-'+str(i)+'.json');save(newpath,dict(policy=pair['policy'],parent=ref(parentpath),members={n:members[n]for n in pair['members']},editRegionWKT=pair['editRegionWKT']));refs.append(newpath);pairrefs.append(ref(newpath))
    newproof=out/'three-member-proof.json';save(newproof,dict(policy=chain.POLICY,parent=ref(parentpath),members=members,pairs=pairrefs));refs.append(newproof)
    try:
        builder=module('tower3_chain_validator',HERE/'validated_parent_roundoff_template_v2.py');validated=[]
        with chain.private_validator():
            for name in ['south','middle','north']:
                assert reservations.owns(lease)
                node=copy.deepcopy(skeletons[name]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=chain.POLICY,proof=ref(newproof),member=name)
                overlap=module('tower3_overlap_'+name,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/(name+'-overlap');overlap.DOC.mkdir()
                # Geometry evidence depends on immutable originals/candidates, not the mutable map manifest.
                overlap.overlap_proof(node,[Path(__file__),parentpath,asset,*before.values(),*(ROOT[m['candidate']['path']]for m in members.values()),newproof])
                builder.validate_patch(node,parent)
                path=local/(name+'-candidate.json');save(path,node);refs.append(path);validated.append(node)
                result['members'].append(dict(member=name,candidate=ref(path),replaces=dict(url=str(before[name].relative_to(ROOT/'3d-viewer')),sha256=digest(before[name].read_bytes()),retainedUids=nodes[name]['meta']['targetUids']),surfaceValidated=True,geometryChanges=name=='south'))
                print('Validated chain member '+name,flush=True)
            chain.validate_effective_coordinated_members(validated)
        result.update(status='private-three-member-chain-surface-validator-passed',allEffectiveMembersRequired=True)
    except Exception as error:
        result.update(status='private-three-member-surface-investigation',reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    assert digest(manifestpath.read_bytes())==mh and reservations.owns(lease)
    for path,sha in initial.items():assert digest((ROOT/path).read_bytes())==sha,path
    result.update(fullAffectedForms=len(forms),fullAffectedNativeActors=len(native),changedOldFaces=len(work['changedTerrainFaceIndices']),newWorkFaces=work['retainedWorkBudget']['newWorkFaces'],sourceFloorFacets=len(ids),middleAndNorthGeometryLiteral=True,allExistingFallbackGridValuesLiteral=True,qualification=__doc__)
    save(out/'summary.json',result)
    refs.extend([HERE/'retained_native_floor_domains_v3_20261102.py',HERE/'retained_bounded_floor_work_v1_20261102.py',HERE/'retained_inset_work_budget_v1_20261026.py',HERE/'three_member_native_boundary_v1_20261027.py',HERE/'validated_parent_roundoff_template_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',chain.INTEGRATION/'coordinated_native_boundary.py',chain.INTEGRATION/'native_terrain_validation.py'])
    module('tower3_chain_floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-floor-return-inside-existing-coordinated-chain',list(dict.fromkeys(refs)),result)
    print(dict(status=result['status'],reason=result.get('reason'),forms=len(forms),natives=len(native)),flush=True)


if __name__=='__main__':main()
