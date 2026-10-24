"""Capture unchanged museum geometry using current production renderer arithmetic."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-actual-render-attributes-v1-20261016';DOC=BASE/BATCH
UID='landsd/4759:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();prior=BASE/'government-xl-history-museum-loader-validation-v1-20261016';receipt=read(prior/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert ref(ROOT/q['path'])==q
 local=HERE/'local'/prior.name;catpath=local/'catalogue.json';cat=read(catpath);entry=cat['models'][0];form=read(local/'source-forms.json')[UID];tile=ROOT/'3d-viewer'/form['tile'];assert ref(tile)['sha256']==form['tileSHA256'];assert form['building'] in read(tile)['buildings'];asset=local/entry['asset'];assert ref(asset)['sha256']==entry['sha256'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
 DOC.mkdir();save(DOC/'input.json.gz',dict(currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u) for u in manifest['officialModelCatalogues']],evidenceRefs=[ref(tile),ref(catpath),ref(prior/'result.json')],rows=[dict(uid=UID,entry=entry,building=form['building'],path=str(asset.relative_to(ROOT)))],qualification='Immutable museum original; no publication.'))
 tool=HERE/'history_museum_actual_render_attributes_v1_20261016.mjs'
 with (DOC/'capture.log').open('w') as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 out=read(DOC/'attributes.json.gz');assert out['startEndAllInputsVerified'];refs=[Path(__file__),tool,prior/'result.json']
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 r=module('museum_attribute_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-museum-complete-production-attributes-v1',refs,dict(uids=[UID],completeFaces=22125,fullAcceptance=False));print(dict(jobId=r['jobId'],completeFaces=22125),flush=True)
if __name__=='__main__':main()
