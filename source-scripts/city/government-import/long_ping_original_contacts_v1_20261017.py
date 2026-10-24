"""Authenticate source terrain and persist exact original-vs-candidate contacts."""
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-long-ping-original-contacts-v1-20261017'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
prior=[BASE/'government-xl-long-ping-source-terrain-v1-20261017',BASE/'government-xl-long-ping-candidate-physical-v2-20261017']
def main():
 assert not DOC.exists()
 pins={};refs=[Path(__file__),HERE/'long_ping_original_contacts_v1_20261017.mjs',HERE/'support-contact.mjs',HERE/'support-interface.mjs',HERE/'triangle-point-index.mjs']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in prior:
   r=read(p/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sourceReceipt=read(prior[0]/'result.json');paths=[ROOT/e['path']for e in sourceReceipt['evidenceRefs']if '/terrain/'in e['path']and e['path'].endswith('.gltf')];assert len(paths)==1
 decoder=module('long_ping_contacts_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;terrain=np.concatenate([decoder.terrain_triangles(p)for p in paths]);save(LOCAL/'original-terrain.json.gz',terrain.tolist())
 runtime=HERE/'local'/prior[1].name/'runtime-geometry.json.gz';assert str(runtime.relative_to(ROOT))in pins
 DOC.mkdir(parents=True)
 subprocess.run(['node',str(HERE/'long_ping_original_contacts_v1_20261017.mjs'),str(runtime),str(LOCAL/'original-terrain.json.gz'),str(DOC/'contacts.json')],cwd=ROOT,check=True)
 data=read(DOC/'contacts.json');refs += [p for p in LOCAL.rglob('*')if p.is_file()]+[ROOT/p for p in pins]+[runtime,LOCAL/'original-terrain.json.gz',HERE/'xl-second-pass.py']
 out=module('long_ping_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-original-tin-contact-comparison-v1',list(set(refs)),dict(uids=[data['uid']],samples=len(data['comparison']),sourceFailures=len(data['originalCheck']['failed']),remainingContacts=len(data['failures']),maximumTerrainDifferenceM=data['maxTerrainDelta'],missingOriginal=data['missingOriginal'],nextStep='Interpret exact failing original source contacts and incident architectural surfaces; no threshold or placement override.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
