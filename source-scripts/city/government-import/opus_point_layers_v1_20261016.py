"""Attribute every remaining exact hotel acceptance sample to original faces."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-point-layers-v1-20261016';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-opus-current-contacts-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 DOC.mkdir();geometry=HERE/'local/government-xl-opus-private-terrain-v2-20261016/runtime-geometry.json.gz';save(DOC/'input.json',dict(geometryPath=str(geometry.relative_to(ROOT)),contactsPath=str((PRIOR/'contacts.json.gz').relative_to(ROOT))))
 tool=HERE/'opus_point_layers_v1_20261016.mjs'
 with(DOC/'worker.log').open('w') as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
 refs += [tool,geometry,PRIOR/'contacts.json.gz',HERE/'support-contact.mjs'];summary=read(DOC/'summary.json')
 result=module('hotel_current_contacts_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-failing-point-other-original-source-layers-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/322573:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
