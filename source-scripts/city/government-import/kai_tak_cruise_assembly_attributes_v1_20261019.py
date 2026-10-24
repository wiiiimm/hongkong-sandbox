"""Exact original pair renderer-coordinate binding; no installation approval."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-assembly-attributes-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-kai-tak-cruise-original-component-checks-v2-20261019';CAP=BASE/'government-xl-kai-tak-cruise-expanded-parent-v3-20261019'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(SRC/'selection.json.gz')['rows']+read(CAP/'selection.json.gz')['rows'];assert len(rows)==14;manifest=ROOT/'3d-viewer/city/data/manifest.json'
 save(DOC/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in read(manifest)['officialModelCatalogues']],evidenceRefs=[ref(SRC/'selection.json.gz'),ref(CAP/'selection.json.gz')],rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in rows]))
 tool=HERE/'kai_tak_cruise_assembly_attributes_v1_20261019.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 output=read(DOC/'attributes.json.gz');assert output['startEndAllInputsVerified'];refs=[Path(__file__),tool,SRC/'result.json']
 for p,h in {**pins,**output['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_attributes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-complete-loader-attributes',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],completeFaces=48246,installationApproved=False))
if __name__=='__main__':main()
