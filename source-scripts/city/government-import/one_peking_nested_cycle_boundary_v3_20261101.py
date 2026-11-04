"""Exact two-retained-leaf/one-new-leaf finite cycle, PRIVATE admission only.

All three adjacencies use the existing full finite same-triangle/strip checker.
Every remaining edge uses the ordinary parent-height check. No model acceptance,
publication entry point or canonical validator file is changed.
"""
import copy
from contextlib import contextmanager
from pathlib import Path
import numpy as np
import shapely
import nested_coordinated_native_boundary_v1_20261027 as nested
import nested_terrain_patch_validation_v1_20261027 as validator
from fuying_whole_parent_five_boundary_v1_20261029 import finite_callback
from resolve_pass_indexed_parent_clipping_v2 import terrain
from float32_coverage import approve_roundoff,geometry_sha
from native_patch_resolution import projected_context
_ROUNDOFF_CACHE={}
POLICY='one-peking-exact-nested-three-edge-cycle-v3'
PARENT_SHA='a466bcf3bb748f2f6a60022be6976cdce9e66a3de9681d15e35b9bda13090dab'
COMPOSITION_JOB='f2b82860e8edfd05fb89fc17f254d3f383eafd2f76bab04561e8aa51aa61d54e'
COMPOSITION_SHA='bcd52f10c8ee5ba642c4abc154ce95d555c5a3d32b93f357a5000b9560868637'
NAMES={'retained-12','retained-15','new-root'}
OWNERS={'landsd/233985:0','landsd/240487:0'}
NEW_BOUNDS=(1002.5,-1017.5,1092.5,-967.5)
ORIGINAL_BOUNDARY=nested.coordinated_boundary
ORIGINAL_EFFECTIVE=validator.validate_effective_coordinated_members

def marker(node):return node.get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')

def refined_new_metadata(source,parent):
    """Refine only grid metadata against the unchanged actual parent DEM."""
    node=copy.deepcopy(source);g=parent['meta']['georef'];step=parent['cell']/5
    x,z,X,Z=nested.bounds(source);w=round((X-x)/step)+1;h=round((Z-z)/step)+1
    assert step>0 and (w-1)*step==X-x and (h-1)*step==Z-z
    raw=terrain.fine.DemSampler(parent);rendered=terrain.fine.DemSampler(parent,rendered=True)
    points=[(x+c*step,z+r*step)for r in range(h)for c in range(w)]
    node.update(w=w,h=h,cell=step,elev=[float(raw.ground(a,b))for a,b in points],renderedElev=[float(rendered.ground(a,b))for a,b in points])
    node['vegetation']=[]
    for a,b in points:
        c=min(parent['w']-1,max(0,round((a+834500-g['bE'])/g['aE'])));r=min(parent['h']-1,max(0,round((816500-b-g['bN'])/g['aN'])))
        node['vegetation'].append(parent['vegetation'][r*parent['w']+c])
    node['meta']['georef']={**source['meta']['georef'],'aE':step,'aN':-step,'W':w,'H':h}
    assert node['nativeMesh']==source['nativeMesh']
    return node

def declare_roundoff(node):
    # Memoize only exact immutable geometry/bounds, never an approval state.
    # Reference hashes and canonical node bodies are still checked on every load.
    bounds=nested.bounds(node);key=(geometry_sha(node),bounds)
    if key not in _ROUNDOFF_CACHE:
        _,polygons,_,_=projected_context(node,bounds)
        difference=shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds))
        _ROUNDOFF_CACHE[key]=approve_roundoff(node,bounds)if difference.area>0 else None
    proof=copy.deepcopy(_ROUNDOFF_CACHE[key])
    if proof is not None:
        assert proof['geometrySHA256']==key[0]
        node['nativeMesh']['source']['numericalCoverageGap']=proof
    assert geometry_sha(node)==key[0]
    return proof

def load(ref,parent=None):
    proof=nested.reference(ref)
    assert set(proof)=={'policy','parent','composition','members','retainedOverlapRefresh'}and proof['policy']==POLICY
    assert proof['parent']['sha256']==PARENT_SHA and proof['composition']['sha256']==COMPOSITION_SHA
    prior=nested.reference(proof['parent']);composition=nested.reference(proof['composition'])
    assert composition['jobId']==COMPOSITION_JOB and composition['parentSHA256']==PARENT_SHA
    assert composition['allFiniteSeamsPassed']and set(composition['uids'])==OWNERS
    assert set(composition['members'])==set(proof['members'])==NAMES
    assert prior.get('patches')and len(prior['patches'])==17 and not prior.get('nativeMesh')and not prior.get('hydro')
    refresh=proof['retainedOverlapRefresh'];assert set(refresh)=={'childIndex','candidate'}and refresh['childIndex']==16
    refreshed=nested.reference(refresh['candidate']);old=prior['patches'][16]
    assert old['nativeMesh'].get('sourceOverlap')and refreshed['nativeMesh'].get('sourceOverlap')
    old_without=copy.deepcopy(old);new_without=copy.deepcopy(refreshed)
    old_without['nativeMesh'].pop('sourceOverlap');new_without['nativeMesh'].pop('sourceOverlap')
    assert old_without==new_without,'Retained overlap refresh changed geometry or other metadata'
    assert old['nativeMesh']['sourceOverlap']!=refreshed['nativeMesh']['sourceOverlap']
    # The full unchanged native validator authenticates this new overlap proof;
    # it supplies no boundary, geometry or source-identity exception.
    prior=copy.deepcopy(prior);prior['patches'][16]=refreshed
    candidates={};rectangles={};derived=0
    for name,item in proof['members'].items():
        assert set(item)=={'candidate','canonicalSHA256'}
        source=nested.reference(composition['members'][name]['candidate']);node=nested.reference(item['candidate'])
        assert not marker(node)and not node['nativeMesh'].get('sourceOverlap')and not node.get('patches')and not node.get('hydro')
        assert nested.canonical_sha(node)==item['canonicalSHA256']
        # Exact previously authenticated current-parent/source return, never an
        # arbitrary rehashed candidate. Only the new node's metadata is refined.
        expected=refined_new_metadata(source,prior)if name=='new-root'else copy.deepcopy(source)
        # Fresh complete residue proof under the existing .25m2/2mm policy.
        # Sampling semantics must survive retained Float32 gaps as well as faces.
        declare_roundoff(expected)
        assert node==expected,'Candidate differs from exact source composition or metadata crop'
        assert node['meta']['parentSha256']==PARENT_SHA
        assert all(node['nativeMesh'][field]==source['nativeMesh'][field]for field in ['position','index']),'Rendered terrain geometry changed'
        if name=='new-root':
            assert nested.bounds(node)==NEW_BOUNDS and set(node['meta']['targetUids'])==OWNERS
        else:
            old=prior['patches'][int(name.split('-')[1])]
            assert nested.bounds(node)==nested.bounds(old)and node['coarseCells']==old['coarseCells']
            assert set(node['meta']['targetUids'])==set(old['meta']['targetUids'])|OWNERS
            expected_meta=copy.deepcopy(old)
            expected_meta['id']=node['id'];expected_meta['nativeMesh']=node['nativeMesh']
            for key in ['parentTerrain','parentSha256','targetUids']:expected_meta['meta'][key]=node['meta'][key]
            assert node==expected_meta,'An unrelated retained grid or metadata value changed'
        a,b,c,d=node['coarseCells'];g=prior['meta']['georef'];assert all(type(v)is int for v in [a,b,c,d])and 0<=a<c<prior['w']and 0<=b<d<prior['h']
        assert nested.bounds(node)==(g['bE']+a*g['aE']-834500,816500-g['bN']-b*g['aN'],g['bE']+c*g['aE']-834500,816500-g['bN']-d*g['aN'])
        assert node['meta']['georef']['aE']<g['aE']
        row=composition['members'][name];assert len(nested.triangles(node))==row['afterFaces'];derived+=row['afterFaces']-row['beforeFaces']+row['changedParentFaces']
        candidates[name]=node;rectangles[name]=shapely.box(*nested.bounds(node))
    assert 0<derived<=25000,'Derived terrain work exceeds unchanged constructor budget'
    edges=[]
    for i,a in enumerate(sorted(NAMES)):
        for b in sorted(NAMES)[i+1:]:
            assert rectangles[a].intersection(rectangles[b]).area==0,'Cycle member interiors overlap'
            shared=rectangles[a].boundary.intersection(rectangles[b].boundary)
            assert shared.geom_type=='LineString'and shared.length>0,'Every cycle edge must exist'
            edges.append((a,b))
    assert len(edges)==3
    if parent is not None:verify_parent(prior,parent,proof,candidates,ref)
    return proof,prior,candidates,edges

def verify_parent(prior,successor,proof,candidates,ref):
    expected=copy.deepcopy(prior)
    for name,index in [('retained-12',12),('retained-15',15)]:
        node=copy.deepcopy(candidates[name]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=POLICY,proof=ref,member=name);expected['patches'][index]=node
    node=copy.deepcopy(candidates['new-root']);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=POLICY,proof=ref,member='new-root');expected['patches'].append(node)
    expected['meta']['targetUids']=sorted(set(prior['meta']['targetUids'])|OWNERS)
    assert successor==expected,'Exact parent grid, unrelated children or complete member set changed'
    return dict(retainedChildren=14,metadataOnlyOverlapRefreshChild=16,replacedChildIndices=[12,15],appendedChildren=1,allThreeExactMembersPresent=True,allParentGridValuesUnchanged=True)

def coordinated_boundary(node,parent):
    own=marker(node)
    if own is None or own.get('policy')!=POLICY:return ORIGINAL_BOUNDARY(node,parent)
    assert set(own)=={'policy','proof','member'}
    proof,prior,candidates,edges=load(own['proof'],parent);name=own['member'];assert name in NAMES
    assert nested.canonical_sha(node)==proof['members'][name]['canonicalSHA256']
    callbacks=[finite_callback({n:candidates[n]for n in edge},name)for edge in edges if name in edge]
    assert len(callbacks)==2
    return lambda x,y,z:any(callback(x,y,z)for callback in callbacks)

def validate_effective(nodes):
    ordinary=[n for n in nodes if not marker(n)or marker(n).get('policy')!=POLICY]
    ORIGINAL_EFFECTIVE(ordinary);checked=set()
    for node in nodes:
        own=marker(node)
        if own is None or own.get('policy')!=POLICY:continue
        assert set(own)=={'policy','proof','member'}
        proof,_,candidates,_=load(own['proof']);assert own['member']in NAMES
        assert nested.canonical_sha(node)==proof['members'][own['member']]['canonicalSHA256']
        key=(own['proof']['path'],own['proof']['sha256'])
        if key in checked:continue
        for name,candidate in candidates.items():
            matches=[n for n in nodes if n.get('nativeMesh')and n.get('coarseCells')==candidate['coarseCells']and nested.canonical_sha(n)==proof['members'][name]['canonicalSHA256']]
            assert len(matches)==1 and marker(matches[0])==dict(policy=POLICY,proof=own['proof'],member=name),'Every cycle member must be effective exactly once'
        checked.add(key)

@contextmanager
def private_validator():
    assert nested.coordinated_boundary is ORIGINAL_BOUNDARY and validator.validate_effective_coordinated_members is ORIGINAL_EFFECTIVE
    nested.coordinated_boundary=coordinated_boundary;validator.validate_effective_coordinated_members=validate_effective
    try:yield
    finally:nested.coordinated_boundary=ORIGINAL_BOUNDARY;validator.validate_effective_coordinated_members=ORIGINAL_EFFECTIVE
