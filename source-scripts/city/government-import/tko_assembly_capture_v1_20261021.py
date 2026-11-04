"""Actual production renderer capture for eight unchanged mall assembly originals."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-assembly-capture-v1-20261021';DOC=BASE/BATCH
REC=BASE/'government-xl-tko-tower3-support-layers-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [REC]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];refs.append(p);used[k]=pins[d][k];return read(p)
 selected=sorted(take(REC,REC/'support-inputs.json')['sources'],key=lambda r:r['uid']);uids={r['uid']for r in selected};assert len(uids)==2
 mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);refs.append(mp);forms={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in uids:forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes()));refs.append(p)
 assert set(forms)==uids
 for r in selected:
  assert all(forms[r['uid']][k]==v for k,v in r['source'].items());r['source']=forms[r['uid']];r['triangles']=r['candidate']['entry']['triangles'];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256']==r['candidate']['entry']['sha256'];refs.append(p)
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 save(DOC/'selection.json.gz',dict(rows=selected,manifestSHA256=digest(mp.read_bytes())))
 save(DOC/'input.json.gz',dict(rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in selected],currentManifest=ref(mp),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in manifest['officialModelCatalogues']],evidenceRefs=[ref(p)for p in refs]))
 tool=HERE/'tko_assembly_attributes_v1_20261021.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(DOC/'attributes.json.gz');assert capture['startEndAllInputsVerified']and len(capture['rows'])==2 and not capture['rejected']
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(tool);result=dict(uids=sorted(uids),loaded=len(capture['rows']),rejected=capture['rejected'],installationApproved=False,geometryChanges=0);save(DOC/'summary.json',result);module('yoho_assembly_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-actual-renderer-coordinate-capture',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
