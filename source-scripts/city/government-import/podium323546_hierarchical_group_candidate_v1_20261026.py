"""Assemble and ordinarily validate an exact retained-group private successor."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from hierarchical_original_terrain_binding_v1_20261026 import verify_successor,target_uids

def main():
 base=ROOT/'docs/astra-city/government-import';prefix='government-xl-podium323546-after-beverly-d-';batch=prefix+'hierarchical-group-candidate-v1-20261026';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists();refs=[Path(__file__),HERE/'hierarchical_original_terrain_binding_v1_20261026.py'];pins={};receipts={}
 def take(name,path):
  if name not in pins:receipts[name],pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 expanded_name=prefix+'expanded-group-parent-v1-20261026';expanded=take(expanded_name,HERE/'local'/expanded_name/'expanded-group.json')
 child_name=prefix+'group-child-inset-v1-20261026';child=take(child_name,HERE/'local'/child_name/'candidate-terrain.json');assert receipts[child_name]['status']=='private-terrain-validator-passed'
 info=receipts[expanded_name]['existingGroup'];path=ROOT/'3d-viewer'/info['url'];assert digest(path.read_bytes())==info['sha256'];prior=read(path);refs.append(path)
 parent=ROOT/'3d-viewer/city/data/terrain.json';root=read(parent);refs.append(parent)
 validator=module('podium_group_validator',HERE.parent/'island-detail-integration/publish.py')
 validator.validate_patch(prior,root)
 validator.validate_patch(child,expanded)
 validator.check_patch_overlap(child,prior['patches'])
 combined=deepcopy(expanded);combined['patches'].append(child)
 combined['meta']['targetUids']=sorted(target_uids(prior)|{'landsd/323546:0'})
 combined['meta']['scriptedOriginalChildExtension']=dict(existingGroupURL=info['url'],existingGroupSHA256=info['sha256'],expandedParentSHA256=digest((HERE/'local'/expanded_name/'expanded-group.json').read_bytes()),newChildSHA256=digest((HERE/'local'/child_name/'candidate-terrain.json').read_bytes()),policy='Existing children/grid retained; only an explicit disjoint child replaces group fallback. All acceptance remains pending.')
 proof=verify_successor(prior,combined,['landsd/323546:0']);assert proof['retainedChildren']==13
 validator.validate_patch(combined,root)
 save(local/'candidate-terrain.json',combined)
 builder=module('podium_group_extent',HERE/'resolve-pass-indexed-parent-clipping.py');bounds=builder.extent(combined['coarseCells'],root)
 save(out/'scope.json',dict(uids=['landsd/323546:0'],cells=combined['coarseCells'],bounds=bounds))
 result=dict(uids=['landsd/323546:0'],status='private-terrain-validator-passed',candidate=dict(path=str((local/'candidate-terrain.json').relative_to(ROOT)),sha256=digest((local/'candidate-terrain.json').read_bytes())),hierarchicalRetention=proof,replacedNativeTerrain=[dict(url=info['url'],sha256=info['sha256'],retainedUids=proof['retainedUids'],coarseCells=prior['coarseCells'])],sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,qualification='Both original and successor groups pass the unchanged canonical recursive terrain validator. All thirteen original children and old grid nodes are exact, new child has no positive-area coarse overlap with any retained child. Explicit pinned replacement only; full actual renderer, changed-domain neighbours, source identity/support and browser review remain unapproved.')
 save(out/'retention-proof.json',proof);save(out/'summary.json',result);refs.extend([local/'candidate-terrain.json',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',HERE/'resolve-pass-indexed-parent-clipping.py']);module('podium_group_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-canonical-validated-original-hierarchical-group-successor',refs,result)
 print(proof,flush=True)
if __name__=='__main__':main()
