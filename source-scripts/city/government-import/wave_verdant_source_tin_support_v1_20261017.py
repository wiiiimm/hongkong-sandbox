"""Check recovered unchanged Verdant Villa original contact against the private original-terrain and podium assembly."""
from pathlib import Path
import numpy as np,subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-wave-basic-ground-capture-v1-20261017';WORLD=BASE/'government-xl-wave-four-world-paths-v1-20261017';BATCH='government-xl-wave-verdant-source-tin-support-v1-20261017';DOC=BASE/BATCH
UIDS=['landsd/195000:0']
def source_ground(refs):
 terrain=BASE/'government-xl-four-qualified-original-podiums-physical-20261007-301560-0/source-recovery.json'
 refs.append(terrain);decoder=module('verdant_source_terrain_decode',HERE/'xl-second-pass.py');decoder.LOCAL=HERE/'local'/BATCH;surfaces=[]
 for sheet in read(terrain)['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for entry in sheet['terrainFiles']:
   path=folder/'terrain'/entry['name'];assert digest(path.read_bytes())==entry['sha256'];refs.append(path)
   if path.suffix=='.gltf':surfaces.append(decoder.terrain_triangles(path))
 refs.append(HERE/'xl-second-pass.py');return np.concatenate(surfaces)
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for d in [CAP,WORLD,BASE/'government-xl-wave-neighbours-terrain-capture-v1-20261017']:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 rec=BASE/'government-xl-wave-neighbours-terrain-capture-v1-20261017';sources={r['uid']:r for r in read(rec/'selection.json.gz')['rows']};rows=[dict(r,building=sources[r['uid']]['source']['building']) for r in read(HERE/'local'/rec.name/'runtime-geometry.json.gz')['rows'] if r['uid'] in UIDS];assert {r['uid']for r in rows}==set(UIDS);worlds=read(WORLD/'worlds.json.gz');podium=np.array(worlds['literal']['landsd/301560:0']);ground=source_ground(refs);save(DOC/'input.json.gz',dict(rows=rows,podium=np.concatenate([ground,podium]).tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);proofs=read(DOC/'support.json.gz');ground=ground;final=module('wave_retained_basic_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  t=np.array(r['position']).reshape(-1,3)[np.array(r['index']).reshape(-1,3)];b=r['building'];f=final.foundation_context(t,np.concatenate([ground,podium]),Polygon(b['rings'][0],b['rings'][1:]));proof=next(x['proof']for x in proofs['rows']if x['uid']==r['uid']);item=dict(uid=r['uid'],actualOriginalFaces=len(t),supportPassed=proof['passed'],strictContacts=proof['strictContacts'],samples=proof['samples'],compoundBuried=f['fullyBuriedTriangles'],compoundUpwardBuried=f['fullyBuriedUpwardTriangles'],complete=f['completeTerrainTriangles']==f['triangles']);summary.append(item);save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);print(item,flush=True)
 for p,h in proofs['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([tool,HERE/'xl-final-script-pass.py']);save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,qualification='Recovered original source geometry preserved exactly; current captured coordinate mode against authenticated full source TIN and podium, diagnostic only; not a candidate terrain change. Other arithmetic modes and full identity/runtime checks remain. No source model installed, deleted or deemed corrupt. Rendering dependency and complete neighbour acceptance remain required.'))
 out=module('wave_retained_basic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-verdant-authenticated-source-tin-contact-v1',list(set(refs)),dict(uids=UIDS,summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
