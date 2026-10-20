"""Locate all buried faces against four exact source sheets; diagnostic only."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-china-ferry-full-source-faces-v1-20261020';DOC=BASE/BATCH
GROUND=BASE/'government-xl-china-ferry-adjoining-ground-v1-20261020'
assert not DOC.exists()
r=read(GROUND/'result.json');pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for e in r['evidenceRefs']:
 assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
row=read(BASE/'government-xl-china-ferry-current-foundations-v1-20261020/selection.json.gz')['rows'][0]
t=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes())
g=np.asarray(read(HERE/'local'/GROUND.name/'285642:0-ground.json.gz')['completeAdjoiningTerrain'])
final=module('china_ferry_full_source_final',HERE/'xl-final-script-pass.py');result=face_diagnostics(final,t,g)
faces=result['buriedFaces'];ids=[f['faceIndex']for f in faces];up=[f['faceIndex']for f in faces if f['upward']]
summary=dict(uids=[row['uid']],completeFaces=len(t),completeTerrainFaces=result['completeTerrainTriangles'],buriedFaces=len(ids),buriedUpwardFaces=len(up),buriedHeightRange=[float(t[ids,:,1].min()),float(t[ids,:,1].max())],buriedUpwardHeightRange=[float(t[up,:,1].min()),float(t[up,:,1].max())],sourceRecordedBaseHeight=row['source']['building'].get('baseHeightHKPD'),sourceRecordedTopHeight=row['source']['building'].get('topHeightHKPD'),installationApproved=False)
save(DOC/'complete-face-diagnostic.json.gz',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],**result));save(DOC/'summary.json',summary)
refs=[Path(__file__),HERE/'china_ferry_current_foundations_v1_20261020.py',GROUND/'result.json',*[ROOT/p for p in pins]]
module('china_ferry_full_faces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-complete-terrain-buried-face-location',refs,summary)
print(summary,flush=True)
