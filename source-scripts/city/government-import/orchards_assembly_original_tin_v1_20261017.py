"""Check all three unchanged Orchards originals against authenticated source terrain."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-assembly-original-tin-v1-20261017';DOC=BASE/BATCH
TERRAIN=BASE/'government-xl-orchards-connection-overlap-terrain-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};rows=[]
 for name in ['government-xl-orchards-connection-overlap-terrain-v1-20261017','government-xl-orchards-podium-current-checks-v1-20261017','government-xl-orchards-community-current-checks-v1-20261017']:
  d=BASE/name;r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.extend([d/'result.json',d/'selection.json.gz']);rows.extend(read(d/'selection.json.gz')['rows'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 assert {r['uid']for r in rows}=={'landsd/254629:0','landsd/233002:0','landsd/256434:0'}
 meshes={}
 for r in rows:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];meshes[r['uid']]=decode_original_world_triangles(p.read_bytes());assert len(meshes[r['uid']])==r['native']['model']['triangles'];refs.append(p)
 second=module('orchards_assembly_terrain_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH;sources=[]
 for sheet in read(TERRAIN/'source-recovery.json')['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':sources.append(second.terrain_triangles(p))
 ground=np.concatenate(sources);final=module('orchards_assembly_foundation',HERE/'xl-final-script-pass.py');results=[]
 for r in rows:
  uid=r['uid'];supports=['landsd/233002:0']if uid=='landsd/254629:0'else[];surface=np.concatenate([ground]+[meshes[u]for u in supports]);b=r['source']['building'];f=final.foundation_context(meshes[uid],surface,Polygon(b['rings'][0],b['rings'][1:]));ok=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0
  result=dict(uid=uid,sourceSHA256=r['sourceSHA256'],supportUids=supports,foundation=f,strictFoundationAccepted=ok);results.append(result);save(DOC/(uid.split('/')[1]+'-foundation.json'),result);print(dict(uid=uid,passed=ok,buried=f['fullyBuriedTriangles']),flush=True)
 summary=dict(rows=[dict(uid=r['uid'],passed=r['strictFoundationAccepted'],buried=r['foundation']['fullyBuriedTriangles'])for r in results],originalTerrainFaces=len(ground),allWholeFoundationsPass=all(r['strictFoundationAccepted']for r in results),installationApproved=False)
 save(DOC/'summary.json',summary);save(DOC/'selection.json.gz',dict(rows=rows));refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 out=module('orchards_assembly_tin_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-original-assembly-authentic-tin-complete-foundation-v1',list(set(refs)),dict(uids=sorted(meshes),summary=summary,fullAcceptance=False,nextStep='Construct complete candidate terrain preserving current installed Tower 1 and qualify composite footprint identity; these source-TIN results alone do not approve the candidate or resolve canonical support.'));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
