"""Capture current renderer coordinates; historical selection is source evidence only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'; BATCH='government-xl-manhattan-current-scene-capture-v2-20261021'; DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 src=BASE/'government-xl-next-twenty-current-terrain-v6-20261021'; receipt=read(src/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']}; sp=src/'selection.json.gz'
 assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))]
 manhattan=next(r for r in read(sp)['rows'] if r['uid']=='landsd/276331:0')
 mp=ROOT/'3d-viewer/city/data/manifest.json'; manifest=read(mp); refs=[Path(__file__),src/'result.json',sp,mp]; catalogues=[]; installed=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url; catalogues.append(p); installed.extend((m,p.parent) for m in read(p)['models'])
 assert len(installed)==len({m['uid'] for m,_ in installed})==6791
 k,parent=next((m,p) for m,p in installed if m['uid']=='landsd/115799:0')
 uids={k['uid'],manhattan['uid']}; forms={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid'] in uids: forms[b['uid']]=b;refs.append(p)
 assert set(forms)==uids and forms[manhattan['uid']]==manhattan['source']['building']
 rows=[dict(uid=k['uid'],entry=k,building=forms[k['uid']],path=str((parent/k['asset']).relative_to(ROOT))),dict(uid=manhattan['uid'],entry=manhattan['candidate']['entry'],building=forms[manhattan['uid']],path=manhattan['candidate']['path'])]
 for row in rows:
  p=ROOT/row['path'];assert digest(p.read_bytes())==row['entry']['sha256'];refs.append(p)
 def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 save(DOC/'input.json.gz',dict(rows=rows,currentManifest=ref(mp),currentCatalogueRefs=[ref(p) for p in catalogues],evidenceRefs=[ref(p) for p in refs]))
 tool=HERE/'manhattan_current_scene_attributes_v1_20261021.mjs'
 subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(DOC/'attributes.json.gz');assert capture['startEndAllInputsVerified'] and not capture['rejected'] and len(capture['rows'])==2
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=sorted(uids),loaded=2,currentInstalledModels=6791,installationApproved=False,geometryChanges=0)
 save(DOC/'summary.json',result)
 module('manhattan_current_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-renderer-coordinate-capture',list(dict.fromkeys(refs+[tool])),result)
if __name__=='__main__':main()
