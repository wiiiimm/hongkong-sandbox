"""Diagnose exact original tower wall-to-clear-cap paths on authenticated saved ground.
This is historical source evidence, not current placement or installation approval.
"""
from pathlib import Path
import json
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_strict_clear_cap_wall_paths_20261009 import verify
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-harbourfront-tower-cap-paths-v1-20261021'
DOC=BASE/BATCH
UID='landsd/118230:0'
def main():
 assert not DOC.exists()
 refs=[Path(__file__)];pins={}
 def take(folder,name):
  folder=BASE/folder;r,ps=authenticate(folder);p=folder/name;k=str(p.relative_to(ROOT))
  assert digest(p.read_bytes())==ps[k],k
  pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
 selection=take('government-xl-next-twenty-current-terrain-v6-20261021','selection.json.gz')
 row=next(r for r in selection['rows']if r['uid']==UID)
 saved=take('government-xl-harbourfront-tower-current-grade-v1-20261021','118230:0-original.json.gz')
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==saved['sourceSHA256']
 tri=decode_original_world_triangles(raw);assert digest(tri.tobytes())==saved['completeWorldSHA256']
 canonical=lambda x:digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(saved['faces']),exactOriginalContactListSHA256=canonical([]))
 proof=verify(tri,saved['faces'],[],expected_binding=binding,current_binding=binding)
 save(DOC/'paths.json.gz',dict(uid=UID,sourceSHA256=row['sourceSHA256'],historicalGroundSHA256=saved['completeDrawnGroundSHA256'],binding=binding,proof=proof,installationApproved=False))
 unresolved=[p for p in proof['paths']if not p['hasExactOriginalStrictClearCapRoofPath']]
 exposure=[dict(path=p,vertices=tri[p['sourceFace']].tolist(),context=saved['faces'][p['sourceFace']])for p in proof['paths']if p['sourceFace']in saved['negativeWithoutExposedWitness']]
 save(DOC/'unexposed-face-context.json',dict(uid=UID,faces=exposure,installationApproved=False))
 result=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],affectedFaces=len(proof['paths']),exactCapPaths=sum(p['hasExactOriginalStrictClearCapRoofPath']for p in proof['paths']),missingPathFaces=[p['sourceFace']for p in unresolved],unexposedFaces=proof['rawExposureFailures'],sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,qualification='Exact shared-edge source paths against authenticated historical ground diagnostics. Exposure and finite-ground bounds are not upgraded to certified acceptance. No current-ground, role or installation credit.')
 save(DOC/'summary.json',result)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert digest(asset.read_bytes())==row['sourceSHA256']
 refs.extend([asset,HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 out=module('harbourfront_tower_cap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-tower-clear-cap-path-diagnostic',refs,result)
 print(dict(jobId=out['jobId'],**result),flush=True)
if __name__=='__main__':main()
