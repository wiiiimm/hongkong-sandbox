"""Capture complete original pool/tower attributes in all renderer arithmetic modes."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-actual-render-attributes-v1-20261017';DOC=BASE/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();prior=BASE/'government-xl-sham-shui-po-pool-original-group-v1-20261016';receipt=read(prior/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert ref(ROOT/q['path'])==q
 rows=[];evidence=[ref(prior/'result.json')]
 for row in read(prior/'selection.json.gz')['rows']:
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert row['source']['building'] in read(tile)['buildings'];asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];evidence.append(ref(tile));rows.append(dict(uid=row['uid'],entry=row['candidate']['entry'],building=row['source']['building'],path=str(asset.relative_to(ROOT))))
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);DOC.mkdir();save(DOC/'input.json.gz',dict(currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u) for u in manifest['officialModelCatalogues']],evidenceRefs=evidence,rows=rows,qualification='Original pool sources, diagnostic only.'))
 tool=HERE/'pool_actual_render_attributes_v1_20261017.mjs'
 with (DOC/'capture.log').open('w') as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 out=read(DOC/'attributes.json.gz');assert out['startEndAllInputsVerified'];refs=[Path(__file__),tool,prior/'result.json']
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 r=module('pool_attribute_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pool-complete-production-attributes-v1',refs,dict(uids=[r['uid'] for r in rows],completeFaces=15899,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],completeFaces=15899),flush=True)
if __name__=='__main__':main()
