"""Verify original companion support on the unchanged original Opus podium."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-assembly-layers-v1-20261016';DOC=BASE/BATCH
CAP=BASE/'government-xl-opus-companion-original-v1-20261016'
PAIR=BASE/'government-xl-opus-preserved-neighbours-v1-20261016'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,PAIR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for ref in r['evidenceRefs']:
    assert ref['path']not in pins or pins[ref['path']]==ref['sha256'];pins[ref['path']]=ref['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 DOC.mkdir();geometry=HERE/'local'/PAIR.name/'runtime-geometry.json.gz';actors=CAP/'original-geometry.json.gz';save(DOC/'input.json',dict(geometryPath=str(geometry.relative_to(ROOT)),actorsPath=str(actors.relative_to(ROOT))))
 tool=HERE/'opus_assembly_layers_v1_20261016.mjs'
 with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 summary=read(DOC/'summary.json');refs += [tool,geometry,actors,HERE/'support-contact.mjs']
 out=module('opus_neighbour_support_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-two-original-towers-complete-podium-layer-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/319559:0','landsd/248432:0','landsd/322573:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
