"""Complete original eight-model renderer capture. Private, no installation."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';DOC=BASE/BATCH
SOURCES=[BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v3-20261019',BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];rows=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in SOURCES:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');rows+=read(folder/'selection.json.gz')['rows']
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert len(rows)==8 and len({r['uid']for r in rows})==8
 manifest=ROOT/'3d-viewer/city/data/manifest.json';save(DOC/'selection.json.gz',dict(rows=rows))
 save(DOC/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in read(manifest)['officialModelCatalogues']],evidenceRefs=[ref(f/'selection.json.gz')for f in SOURCES],rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in rows]))
 tool=HERE/'lai_chi_kok_eight_render_attributes_v1_20261019.mjs';subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 out=read(DOC/'attributes.json.gz');assert out['startEndAllInputsVerified']and len(out['rows'])==8;refs.append(tool)
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 module('eight_render_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-models-complete-renderer-attributes',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],completeFaces=sum(r['triangles']for r in rows),installationApproved=False))
if __name__=='__main__':main()
