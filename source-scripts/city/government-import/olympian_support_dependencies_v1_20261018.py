"""Derive native dependency closure from already accepted finite-source contacts."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-support-dependencies-v1-20261018';DOC=BASE/BATCH
NAMES=['government-xl-olympian-two-original-interface-review-v1-20261018','government-xl-olympian-two-park-interface-review-v1-20261018']
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   d=BASE/n;r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 park=read(BASE/'government-xl-olympian-two-park-four-world-contacts-v1-20261018/inputs.json.gz');worlds=park['worlds'];targets=sorted(set(worlds['original'])-set(park['supportUIDs']));assert len(targets)==10
 data=dict(worlds=worlds,targets=targets,towerPaths=read(BASE/'government-xl-olympian-two-four-world-path-bounds-v1-20261018/contacts.json.gz')['rows'],parkContacts=read(BASE/'government-xl-olympian-two-park-four-world-contacts-v1-20261018/contacts.json.gz')['rows']);save(DOC/'inputs.json.gz',data)
 tool=HERE/'olympian_support_dependencies_v1_20261018.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True);out=read(DOC/'provider-checks.json.gz');assert len(out['rows'])==40 and len(out['dependencies'])==10
 save(DOC/'dependencies.json',dict(dependencies=out['dependencies'],qualification='Smallest provider subset covering every existing accepted rim or finite-path endpoint in all four coordinate modes. No new geometry, path or acceptance tolerance. Runtime metadata and browser checks remain.'))
 refs.extend([tool,HERE/'support-contact.mjs',*[ROOT/p for p in pins]])
 module('dependency_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-exact-original-support-provider-map-v1',refs,dict(uids=targets,dependencies=out['dependencies'],fullAcceptance=False))
if __name__=='__main__':main()
