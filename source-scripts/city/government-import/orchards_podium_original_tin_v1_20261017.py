"""Compare the complete original podium against authentic original terrain sheets."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';CURRENT=BASE/'government-xl-orchards-podium-current-checks-v1-20261017';TERRAIN=BASE/'government-xl-orchards-connection-overlap-terrain-v1-20261017';BATCH='government-xl-orchards-podium-original-tin-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)]
 for folder in [CURRENT,TERRAIN]:
  r=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
  refs.append(folder/'result.json')
 row=read(CURRENT/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());second=module('orchards_original_terrain_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH;sources=[]
 for sheet in read(TERRAIN/'source-recovery.json')['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':sources.append(second.terrain_triangles(p))
 ground=np.concatenate(sources);b=row['source']['building'];final=module('orchards_original_tin_foundation',HERE/'xl-final-script-pass.py');f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));passed=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0
 summary=dict(completeOriginalPodiumFaces=len(tri),originalTerrainFaces=len(ground),completeTerrainTriangles=f['completeTerrainTriangles'],originalTINBuriedFaces=f['fullyBuriedTriangles'],originalTINBuriedUpwardFaces=f['fullyBuriedUpwardTriangles'],originalTINBuriedAreaM2=f['fullyBuriedAreaM2'],currentDrawnBuriedFaces=read(CURRENT/'foundations.json')['rows'][0]['foundation']['fullyBuriedTriangles'],originalTINFoundationPassed=passed,fullAcceptance=False)
 save(DOC/'foundation.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],foundation=f,summary=summary,qualification='Unchanged complete original source and authenticated original TIN only. This does not construct or approve a terrain replacement.'))
 refs.extend([asset,HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 out=module('orchards_original_tin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-original-podium-complete-authentic-tin-foundation-v1',list(set(refs)),dict(uids=[row['uid']],summary=summary,fullAcceptance=False,nextStep='Use authentic original-TIN comparison to distinguish existing patch transition failures from authored below-grade faces before choosing a complete original assembly candidate.'));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
