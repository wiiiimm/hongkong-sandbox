"""Add verified face counts to an acquisition-based capture, without recapturing geometry."""
import argparse,copy,shutil
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--capture',required=True);a=ap.parse_args()
 assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.capture])
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;assert not out.exists()and not local.exists()
 previous,pins=authenticate(base/a.capture);refs=[Path(__file__),base/a.capture/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
 for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
 selection_path=base/a.capture/'selection.json.gz';geometry_path=HERE/'local'/a.capture/'runtime-geometry.json.gz'
 assert digest(selection_path.read_bytes())==pins[str(selection_path.relative_to(ROOT))]
 assert digest(geometry_path.read_bytes())==pins[str(geometry_path.relative_to(ROOT))]
 before=read(selection_path);selection=copy.deepcopy(before);geometry={r['uid']:r for r in read(geometry_path)['rows']}
 assert set(geometry)=={r['uid']for r in selection['rows']}and len(geometry)==len(selection['rows'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 for r,old in zip(selection['rows'],before['rows']):
  uid=r['uid'];path=ROOT/r['candidate']['path'];raw=path.read_bytes();assert digest(raw)==r['sourceSHA256']==r['candidate']['entry']['sha256']==geometry[uid]['sourceSHA256'];refs.append(path)
  count=len(decode_original_world_triangles(raw));g=geometry[uid];assert len(g['index'])%3==0
  assert count==len(g['index'])//3==r['candidate']['entry']['triangles']
  if 'triangles'in r:assert r['triangles']==count
  r['triangles']=count
  assert {k:v for k,v in r.items()if k!='triangles'}=={k:v for k,v in old.items()if k!='triangles'}
 local.mkdir(parents=True);shutil.copyfile(geometry_path,local/'runtime-geometry.json.gz');assert digest((local/'runtime-geometry.json.gz').read_bytes())==digest(geometry_path.read_bytes())
 save(out/'selection.json.gz',selection)
 for name in ['metrics.json','summary.json']:
  path=base/a.capture/name
  if path.exists():
   assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];shutil.copyfile(path,out/name)
 refs.extend([selection_path,geometry_path,local/'runtime-geometry.json.gz'])
 result=dict(uids=sorted(geometry),rows=read(base/a.capture/'summary.json')['rows'],sourceCapture=a.capture,sourceCaptureJobId=previous['jobId'],selectionRowNormalizationOnly=True,completeOriginalAndCapturedFaceCountsVerified=True,runtimeGeometryByteIdentical=True,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False)
 module('normalized_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'verified-source-face-count-normalization-of-completed-capture',refs,result)
if __name__=='__main__':main()
