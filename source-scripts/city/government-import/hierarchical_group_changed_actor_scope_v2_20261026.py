"""Nominate changed actors from exact hierarchical edits, accounting for all assets.

Outside the new child and right-edge expansion, every original grid/child face is
unchanged. No existing actor is reapproved and no intersecting actor is skipped.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from hierarchical_original_terrain_binding_v2_20261026 import verify_successor


def separation(low,high,box):
 gaps=[box[0]-high[0]-.5,low[0]-box[2]-.5,box[1]-high[1]-.5,low[1]-box[3]-.5]
 return dict(strictlyDisjoint=bool(max(gaps)>0),separatingAxisGapsM=gaps,marginM=.5)


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','candidate','inventory']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__),HERE/'hierarchical_original_terrain_binding_v2_20261026.py'];pins={};receipts={}
 def take(name,path):
  if name not in pins:receipts[name],pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 rec=take(a.candidate,base/a.candidate/'summary.json');assert rec['status']=='private-terrain-validator-passed'
 new=take(a.candidate,ROOT/rec['candidate']['path']);oldinfo=rec['replacedNativeTerrain'];assert len(oldinfo)==1;oldinfo=oldinfo[0]
 path=ROOT/'3d-viewer'/oldinfo['url'];assert digest(path.read_bytes())==oldinfo['sha256'];old=read(path);refs.append(path)
 retention=verify_successor(old,new,rec['uids']);assert retention==rec['hierarchicalRetention']
 g=old['meta']['georef'];left=g['bE']-834500+(old['w']-1)*g['aE'];right=g['bE']-834500+(new['w']-1)*g['aE'];top=816500-g['bN'];bottom=top-(old['h']-1)*g['aN']
 child=new['patches'][-1];cg=child['meta']['georef'];x=cg['bE']-834500;z=816500-cg['bN'];boxes=[[x,z,x+(child['w']-1)*cg['aE'],z-(child['h']-1)*cg['aN']],[left,top,right,bottom]]
 v=np.asarray(child['nativeMesh']['position']).reshape(-1,3);assert np.all(v[:,0]>=boxes[0][0])and np.all(v[:,0]<=boxes[0][2])and np.all(v[:,2]>=boxes[0][1])and np.all(v[:,2]<=boxes[0][3])
 inventory=take(a.inventory,base/a.inventory/'complete-bounds.json.gz');by_uid={r['uid']:r for r in inventory['rows']};assert len(by_uid)==len(inventory['rows'])
 mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==pins[a.inventory][str(mp.relative_to(ROOT))];manifest=read(mp);refs.append(mp)
 models={};non_native_dependencies={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;assert digest(p.read_bytes())==pins[a.inventory][str(p.relative_to(ROOT))];refs.append(p)
  for m in read(p)['models']:
   assert m['uid']not in models;models[m['uid']]=m;asset=p.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256']==by_uid[m['uid']]['sourceSHA256'];refs.append(asset)
 assert set(models)==set(by_uid)
 rows=[];affected=[]
 for uid,row in sorted(by_uid.items()):
  values=np.asarray(row['completeFourWorldBounds']).reshape(-1,3);lo,hi=values.min(0)[[0,2]],values.max(0)[[0,2]];proofs=[separation(lo,hi,b)for b in boxes];disjoint=all(p['strictlyDisjoint']for p in proofs)
  rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeFourWorldBounds=row['completeFourWorldBounds'],editRegionSeparations=proofs,wholeSourceOutsideEveryChangedRegion=disjoint))
  if not disjoint:affected.append(uid)
 for uid,m in models.items():
  for dep in m.get('supportDependencies',[]):
   if isinstance(dep,dict):support_uid=dep['uid']
   else:
    assert isinstance(dep,str)and dep.startswith('landsd/')and ':'in dep
    support_uid=dep
   if support_uid not in models:non_native_dependencies.setdefault(support_uid,[]).append(uid)
 forms={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];assert digest(p.read_bytes())==inventory['currentFormTileHashes'][str(p.relative_to(ROOT))]
  found={f['uid']:f for f in read(p)['buildings']if f['uid']in non_native_dependencies}
  if found:refs.append(p);forms.update(found)
 assert set(forms)==set(non_native_dependencies);support_rows=[]
 for uid,f in sorted(forms.items()):
  points=np.asarray([p for ring in f['rings']for p in ring]);lo,hi=points.min(0),points.max(0);proofs=[separation(lo,hi,b)for b in boxes]
  support_rows.append(dict(uid=uid,owners=non_native_dependencies[uid],building=f,editRegionSeparations=proofs,wholeSupportFootprintOutsideEveryChangedRegion=all(p['strictlyDisjoint']for p in proofs)))
 assert digest(mp.read_bytes())==pins[a.inventory][str(mp.relative_to(ROOT))]
 result=dict(uids=rec['uids'],changedClosedXZRegions=boxes,completeInstalledActorsAccounted=len(rows),allCurrentInstalledAssetBytesVerified=True,originalGroupChildrenAndOldGridExact=True,retainedGroupUids=retention['retainedUids'],affectedNativeUids=affected,allRegisteredBasicSupportsAccounted=len(support_rows),affectedRegisteredBasicSupportUids=[r['uid']for r in support_rows if not r['wholeSupportFootprintOutsideEveryChangedRegion']],allExistingNativeWholeSourceTerrainUnaffectedProved=not affected and all(r['wholeSupportFootprintOutsideEveryChangedRegion']for r in support_rows),existingNativeReaccepted=False,rawLegacyApprovalsChanged=False,installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,qualification='Every exact current installed asset/catalogue and all four-world bounds accounted. Every non-installed registered support dependency footprint also tested. Edits are conservatively enclosed by the new child domain and full right-edge expansion; all other root/child terrain triangles have identical geometry by exact retained grid/child construction. Strict closed-bound separation includes0.5m margin. Any intersection remains explicitly affected and needs full checks. This proves terrain non-effect only, never fresh identity/placement approval of existing models or source acceptance of the candidate.')
 save(out/'native-separations.json.gz',rows);save(out/'basic-support-separations.json',support_rows);save(out/'summary.json',result)
 refs.extend([HERE/'expand_rendered_terrain_group_v1_20261026.py',ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/geo.js']);module('hierarchical_changed_actor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-hierarchical-edited-region-installed-actor-scope',list(dict.fromkeys(refs)),result)
 print({k:result[k]for k in ['completeInstalledActorsAccounted','affectedNativeUids','allRegisteredBasicSupportsAccounted','affectedRegisteredBasicSupportUids','allExistingNativeWholeSourceTerrainUnaffectedProved']},flush=True)
if __name__=='__main__':main()
