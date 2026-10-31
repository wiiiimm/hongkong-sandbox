"""Build a disjoint private source-terrain child while retaining its entire live group."""
from copy import deepcopy
from pathlib import Path
import argparse
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from hierarchical_original_terrain_binding_v1_20261026 import verify_successor,target_uids


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','terrain','scope','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists() and not local.exists()
    refs=[Path(__file__),HERE/'hierarchical_original_terrain_binding_v1_20261026.py'];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selection['rows'] if r['uid']==a.uid)
    scope=take(a.scope,base/a.scope/'scope.json');assert scope['uids']==[a.uid] and len(scope['terrainContacts'])==1
    contact=scope['terrainContacts'][0];group_path=ROOT/'3d-viewer'/contact['url'];prior=take(a.scope,group_path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    assert any(e['url']==contact['url'] for e in read(manifest)['terrainPatches'])
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';root=take(a.scope,parentpath)
    sources=take(a.terrain,base/a.terrain/'summary.json');terrainrow=next(r for r in sources['rows'] if r['uid']==a.uid)
    assert terrainrow['sourceSHA256']==row['sourceSHA256'] and terrainrow['status']=='original-terrain-checked'
    second=module('retained_group_child_geometry',HERE/'xl-second-pass.py');builder=module('retained_group_child_builder',HERE/'resolve-pass-indexed-parent-clipping.py')
    cells=builder.rectangle_for(row['native']['model']['worldBounds'],prior)
    assert 0<=cells[0]<cells[2]<prior['w'] and 0<=cells[1]<cells[3]<prior['h']
    validator=module('retained_group_child_validator',HERE.parent/'island-detail-integration/publish.py')
    validator.validate_patch(prior,root)
    for old in prior['patches']:
        x,y,z,w=old['coarseCells'];aa,bb,cc,dd=cells
        assert cc<=x or aa>=z or dd<=y or bb>=w,'New child overlaps retained original terrain'
    terrainparts=[];source_files=[];native_sources=[]
    for name in terrainrow['sourceTerrainPaths']:
        path=ROOT/name;gltf=take(a.terrain,path)
        binding=dict(path=name,sha256=digest(path.read_bytes()));native_sources.append(binding);source_files.append(binding)
        for buffer in gltf.get('buffers',[]):
            member=path.parent/buffer['uri'];assert digest(member.read_bytes())==pins[a.terrain][str(member.relative_to(ROOT))]
            refs.append(member);source_files.append(dict(path=str(member.relative_to(ROOT)),sha256=digest(member.read_bytes())))
        terrainparts.append(second.terrain_triangles(path))
    terrain=np.concatenate(terrainparts);bounds=builder.extent(cells,prior)
    terrain=terrain[(terrain[:,:,0].max(1)>=bounds[0])&(terrain[:,:,0].min(1)<=bounds[2])&(terrain[:,:,2].max(1)>=bounds[1])&(terrain[:,:,2].min(1)<=bounds[3])]
    low,high=row['native']['model']['worldBounds'];core=[low[0]-1,low[2]-1,high[0]+1,high[2]+1]
    captured=[];original_validator=builder.validate_patch
    def capture(patch,parent):
        captured.append(patch);return original_validator(patch,parent)
    builder.validate_patch=capture
    try:child=builder.make_patch(dict(cells=cells,uids=[a.uid]),prior,terrain,native_sources,native_core=core,parent_url=contact['url'],parent_sha256=digest(group_path.read_bytes()))
    except AssertionError as error:
        assert str(error)=='Native terrain contains overlapping height surfaces' and len(captured)==1
        child=captured[0];assert len(child['nativeMesh']['index'])//3<=25000,'terrain-runtime-budget'
        raw=local/'unvalidated-child.json';save(raw,child);refs.append(raw)
        helper=module('retained_group_child_overlap',HERE/'native_patch_resolution.py');evidence=out/'highest-surface-evidence.json'
        helper.approve_original_overlap(child,raw,evidence,source_files)
        child['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT));helper.finalize_overlap_evidence(child,evidence);refs.extend([evidence,HERE/'native_patch_resolution.py'])
    validator.validate_patch(child,prior);validator.check_patch_overlap(child,prior['patches'])
    combined=deepcopy(prior);combined['patches'].append(child);combined['meta']['targetUids']=sorted(target_uids(prior)|{a.uid})
    combined['meta']['scriptedOriginalChildExtension']=dict(existingGroupURL=contact['url'],existingGroupSHA256=digest(group_path.read_bytes()),policy='All live children and every group grid node retained exactly; one disjoint original terrain child added privately.')
    proof=verify_successor(prior,combined,[a.uid]);validator.validate_patch(combined,root)
    dest=local/'candidate-terrain.json';save(dest,combined);refs.append(dest)
    save(out/'retention-proof.json',proof);save(out/'scope.json',dict(uids=[a.uid],cells=combined['coarseCells'],bounds=builder.extent(combined['coarseCells'],root)))
    result=dict(uids=[a.uid],status='private-terrain-validator-passed',candidate=dict(path=str(dest.relative_to(ROOT)),sha256=digest(dest.read_bytes())),hierarchicalRetention=proof,replacedNativeTerrain=[dict(url=contact['url'],sha256=digest(group_path.read_bytes()),retainedUids=proof['retainedUids'],coarseCells=prior['coarseCells'])],sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,newlyInstalled=0,qualification='Canonical recursive validation of an unchanged live terrain group plus one disjoint source-terrain child. Every old child/grid value retained exactly. Current model placement, changed-domain regression, source identity and browser acceptance remain unapproved.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-second-pass.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py'])
    module('retained_group_child_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-original-disjoint-retained-group-child',refs,result)
    print(proof,flush=True)


if __name__=='__main__':main()
