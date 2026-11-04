"""Compare unchanged BASIC support against old BASIC/new original plus actual ground.

This diagnoses terrain-only gap warnings on actors resting on a podium. Every
canonical support result, including old failures and new unresolved points, is
retained; this is not a physical review, source exception or publication tool.
"""
import argparse,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','before-runtime','after-runtime','attributes','scope','uid']:p.add_argument('--'+k,required=True)
 p.add_argument('--basic-uid',action='append',required=True);a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()and a.batch.startswith('government-xl-')and'/'not in a.batch;assert len(a.basic_uid)==len(set(a.basic_uid))and a.uid not in a.basic_uid
 refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 def take(n,path):
  if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 sources=[];geometries=[]
 for n in [a.before_runtime,a.after_runtime]:
  selection=take(n,base/n/'selection.json.gz');sources.append(next(r for r in selection['rows']if r['uid']==a.uid));geometries.append(next(r for r in take(n,HERE/'local'/n/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid))
 assert sources[0]['source']==sources[1]['source']and sources[0]['sourceSHA256']==sources[1]['sourceSHA256']==geometries[0]['sourceSHA256']==geometries[1]['sourceSHA256']
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);assert digest(manifestpath.read_bytes())==selection['manifestSHA256'];refs.append(manifestpath)
 forms={b['uid']:b for b in take(a.scope,base/a.scope/'form-obligations.json.gz')};assert {a.uid,*a.basic_uid}<=forms.keys();tiles={t['id']:'3d-viewer/'+t['url']for t in manifest['tiles']}
 rows=[];hashes={str(manifestpath.relative_to(ROOT)):digest(manifestpath.read_bytes())}
 for uid in [a.uid,*a.basic_uid]:
  b=forms[uid];tile=ROOT/tiles[b['tile']];assert next(f for f in read(tile)['buildings']if f['uid']==uid)==b;refs.append(tile);hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());rows.append(dict(building=b,tile=str(tile.relative_to(ROOT))))
 save(out/'basic-input.json',dict(manifestSHA256=hashes[str(manifestpath.relative_to(ROOT))],currentInputHashes=hashes,rows=rows));capture=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';subprocess.run(['node',str(capture),str((out/'basic-input.json').relative_to(ROOT)),str((out/'basic-geometry.json').relative_to(ROOT))],cwd=ROOT,check=True);basic=read(out/'basic-geometry.json');byuid={r['uid']:r for r in basic['rows']};assert set(byuid)=={a.uid,*a.basic_uid}
 old=byuid[a.uid];before=np.asarray(old['position']).reshape(-1,3)[np.asarray(old['index']).reshape(-1,3)];asset=ROOT/sources[1]['candidate']['path'];assert digest(asset.read_bytes())==sources[1]['sourceSHA256'];refs.append(asset)
 attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid);assert attr['sourceSHA256']==sources[1]['sourceSHA256'];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 modes={'beforeBasic':(before,geometries[0]),'afterOriginal':(decode_original_world_triangles(asset.read_bytes()),geometries[1])}
 for mode,key in [('afterLiteral','completeLiteralWorldPosition'),('afterLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('afterBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:modes[mode]=(np.asarray(attr[key]).reshape(-1,3)[ix],geometries[1])
 tool=HERE/'plaza_ascot_basic_combined_support_v1_20261020.mjs';refs.extend([capture,tool]);reports={}
 for mode,(support,g)in modes.items():
  folder=out/mode;inputs=[dict(**byuid[uid],drawnGroundGeometry=g['drawnGroundGeometry'])for uid in a.basic_uid];save(folder/'input.json.gz',dict(podium=support.tolist(),rows=inputs));subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True);report=read(folder/'support.json.gz');reports[mode]={r['uid']:r['proof']for r in report['rows']}
  for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 for path,sha in basic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 summary=[]
 for uid in a.basic_uid:
  old=reports['beforeBasic'][uid];oldpoints={tuple(r['position'])for r in old['unresolved']};after=[]
  for mode in modes:
   if mode=='beforeBasic':continue
   proof=reports[mode][uid];assert proof['samples']==old['samples'];points={tuple(r['position'])for r in proof['unresolved']};after.append(dict(mode=mode,passed=proof['passed'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(points),newUnresolvedPositions=len(points-oldpoints)))
  summary.append(dict(uid=uid,beforePassed=old['passed'],beforeUnresolved=len(oldpoints),allFourAfterModesPassed=all(r['passed']for r in after),modes=after))
 result=dict(uids=[a.uid],rows=summary,unchangedBasicUids=a.basic_uid,allBasicGeometryUnchanged=True,governmentGeometryChanges=0,productionChanges=0,installationApproved=False,publication=False,qualification=__doc__);save(out/'summary.json',result);module('retained_basic_combined_support',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-retained-basic-before-after-actual-compound-support',refs,result);print(summary,flush=True)
if __name__=='__main__':main()
