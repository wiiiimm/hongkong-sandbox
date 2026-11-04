"""Prepare a private expanded group grid; preserve every old node and child."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from expand_rendered_terrain_group_v1_20261026 import extend_right,root_sample


def main():
 base=ROOT/'docs/astra-city/government-import';prefix='government-xl-podium323546-after-beverly-d-';batch=prefix+'expanded-group-parent-v1-20261026';out=base/batch;local=HERE/'local'/batch
 assert not out.exists()and not local.exists();refs=[Path(__file__),HERE/'expand_rendered_terrain_group_v1_20261026.py',HERE/'test_expand_rendered_terrain_group_v1_20261026.py'];owner=base/(prefix+'group-terrain-owner-v1-20261026');r,pins=authenticate(owner);refs.append(owner/'result.json')
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==pins[str(manifestpath.relative_to(ROOT))];manifest=read(manifestpath);refs.append(manifestpath)
 info=r['extraLayerExactOwner'];url=info['url'];path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==info['sha256'];parent=read(path);refs.append(path)
 rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath)
 desired=parent['coarseCells'].copy();desired[2]+=1;others=[]
 for entry in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/entry['url'];node=read(p);refs.append(p)
  if entry['url']!=url:others.append(node['coarseCells'])
 expanded,proof=extend_right(parent,root,root_cells=desired,other_root_cells=others)
 assert proof['unchangedChildren']==13
 pg=expanded['meta']['georef'];width=expanded['w'];maximum=0.;checked=0
 for row in range(parent['h']-1):
  for col in range(parent['w']-1,width-1):
   if any(a<=col<b and d<=row<e for a,d,b,e in expanded.get('patchExclusions',[])):continue
   for x,y in [(col,row),(col,row+1),(col+1,row),(col+1,row+1)]:
    worldx=pg['bE']+x*pg['aE']-834500;worldz=816500-(pg['bN']+y*pg['aN']);height,active,_=root_sample(root,worldx,worldz)
    actual=float(np.float32(expanded['renderedElev'][y*width+x]));maximum=max(maximum,abs(actual-height));checked+=1
 assert checked and maximum<.001
 save(local/'expanded-group.json',expanded)
 result=dict(uids=['landsd/323546:0'],existingGroup=dict(url=url,sha256=info['sha256']),candidateParent=dict(path=str((local/'expanded-group.json').relative_to(ROOT)),sha256=digest((local/'expanded-group.json').read_bytes())),gridExpansion=proof,completeNewUnmaskedVertexChecks=checked,maximumNewCellVertexDifferenceFromRenderedRootM=maximum,newRootCoarseCells=desired,all13OriginalChildrenUnchanged=True,allOldGridValuesUnchanged=True,sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,qualification='Private expanded parent for a later narrowly scoped child inset. Existing thirteen children and every old grid node remain exact. New cells sample the actual rendered Float32 root field and honour root inactivity/other top-level exclusions. No approval of the group, new inset, source identity, actor regression or publication. Full renderer verification remains required.')
 save(out/'summary.json',result);refs.append(local/'expanded-group.json');refs.extend(ROOT/'3d-viewer/city'/n for n in ['world.js','geo.js']);module('podium_expanded_group_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-rendered-group-edge-expansion',refs,result)
 print({k:result[k]for k in ['completeNewUnmaskedVertexChecks','maximumNewCellVertexDifferenceFromRenderedRootM','newRootCoarseCells']},flush=True)
if __name__=='__main__':main()
