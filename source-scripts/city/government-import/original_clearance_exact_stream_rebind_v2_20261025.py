"""Reuse complete original/ground proofs only for exactly identical current streams.

No approval transfers: all prior negative faces and support/cap failures remain.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def verify_stream(tri,ground,proof):
 assert tri.ndim==ground.ndim==3 and tri.shape[1:]==ground.shape[1:]==(3,3)
 assert np.isfinite(tri).all()and np.isfinite(ground).all()
 assert len(tri)==proof['completeSourceFaces']
 assert digest(tri.tobytes())==proof['sourceWorldSHA256'],'Changed complete source stream'
 assert digest(ground.tobytes())==proof['groundSHA256'],'Changed complete drawn ground stream'
 return True


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','previous','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
 a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.previous,a.runtime,a.attributes]);base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(n,path):
  if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selected['rows']if r['uid']==a.uid)
 g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
 attributes=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attr=next(r for r in attributes['rows']if r['uid']==a.uid)
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
 previous=take(a.previous,base/a.previous/'summary.json');assert previous['uids']==[a.uid]and previous['sourceSHA256']==row['sourceSHA256']and not previous['installationApproved']
 ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 worlds={'original':decode_original_world_triangles(raw),**{m:np.asarray(attr[k],dtype='<f8').reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
 ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);bindings=[]
 for mode,tri in worlds.items():
  proofpath=base/a.previous/(mode+'.json.gz');proof=take(a.previous,proofpath);assert verify_stream(tri,ground,proof)
  dest=out/proofpath.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(proofpath.read_bytes())
  cap_path=base/a.previous/(mode+'-cap-paths.json.gz');cap=take(a.previous,cap_path)
  assert cap['sourceWorldSHA256']==proof['sourceWorldSHA256']and cap['actualGroundSHA256']==cap['compoundGroundSHA256']==proof['groundSHA256']
  assert cap['proof']['completeSourceFaces']==len(tri)and set(cap['proof']['negativeSourceFaces'])=={r['sourceFace']for r in proof['rows']}
  (out/cap_path.name).write_bytes(cap_path.read_bytes())
  bindings.append(dict(mode=mode,sourceWorldSHA256=proof['sourceWorldSHA256'],drawnGroundSHA256=proof['groundSHA256'],completeSourceFaces=len(tri),allPriorNegativeFacesRetained=[r['sourceFace']for r in proof['rows']],exactCapProofSHA256=digest(cap_path.read_bytes())))
 for path,sha in pins[a.previous].items():
  if path.endswith('.py'):assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 save(out/'summary.json',previous)
 binding=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],currentManifestSHA256=selected['manifestSHA256'],rows=bindings,allFourCompleteSourceAndGroundStreamsExactlyIdentical=True,allPriorRawFailuresPreserved=True,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0)
 save(out/'current-stream-binding.json',binding);refs.append(out/'summary.json')
 module('original_exact_stream_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-original-and-drawn-ground-stream-proof-rebind',refs,binding)


if __name__=='__main__':main()
