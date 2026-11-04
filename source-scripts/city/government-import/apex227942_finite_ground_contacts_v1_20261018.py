"""Exact source/ground surface intersections across complete coordinate-mode meshes."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-apex227942-four-world-v2-20261018';PHYS=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018';BATCH='government-xl-apex227942-finite-ground-contacts-v1-20261018';DOC=BASE/BATCH;UID='landsd/227942:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 for folder in [CAP,PHYS]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 path=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';ground=np.asarray(read(path)['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);worlds=read(CAP/'world-triangles.json.gz');rows=[];cache={}
 for mode,values in worlds.items():
  t=np.asarray(values[UID],dtype='<f8');key=digest(t.tobytes())+'-'+digest(ground.tobytes())
  if key not in cache:
   print(dict(phase='checking',mode=mode,sourceFaces=len(t),groundFaces=len(ground)),flush=True);proof=exact_finite_contacts(t,list(range(len(t))),ground,list(range(len(ground))));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0;out=DOC/(key+'.json.gz');save(out,proof);cache[key]=dict(proofPath=str(out.relative_to(ROOT)),finiteContacts=len(proof['contacts']),trianglePairsTested=proof['trianglePairsTested'])
  rows.append(dict(mode=mode,**cache[key]));print(rows[-1],flush=True)
 save(DOC/'summary.json',dict(rows=rows,fullAcceptance=False,qualification='Exact geometric intersections only; source identity and interpretation remain separate. No source geometry or numeric support limits altered.'));refs.extend([path,HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']);out=module('apex_finite_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-complete-four-mode-exact-ground-intersections-v1',list(set(refs)),dict(uids=[UID],summary=rows,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
