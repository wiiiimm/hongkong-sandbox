"""Exact component low-rim support-layer diagnostic for original Opus assembly."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';GRAPH=BASE/'government-xl-opus-original-component-graph-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-component-layers-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(GRAPH/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 paths=[GRAPH/'graph.json.gz',WORLD/'world-triangles.json.gz']
 for p in paths:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 DOC.mkdir();save(DOC/'input.json',dict(graph=str(paths[0].relative_to(ROOT)),worlds=str(paths[1].relative_to(ROOT))))
 tool=HERE/'opus_component_layers_v1_20261017.mjs'
 with (DOC/'worker.log').open('w') as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 out=read(DOC/'layers.json.gz');refs=[Path(__file__),tool,GRAPH/'result.json',*paths]
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=read(DOC/'summary.json');result=module('opus_component_layers_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-six-component-rim-layer-diagnostic-v1',refs,dict(uids=['landsd/248432:0','landsd/319559:0','landsd/322573:0'],**summary));print(dict(jobId=result['jobId'],**summary),flush=True)
if __name__=='__main__':main()
