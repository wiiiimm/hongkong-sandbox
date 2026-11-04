"""Exact original pair renderer-coordinate binding; no installation approval."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-12-15-actual-render-attributes-v1-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-parkview-12-15-shared-runtime-v1-20261021';CAP=BASE/'government-xl-parkview-12-15-shared-runtime-v1-20261021'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 assert reservations.owns(read(LOCAL/'reservation.json'));assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(CAP/'selection.json.gz')['rows'];assert len(rows)==5 and sorted(r['uid'] for r in rows)==['landsd/253980:0', 'landsd/254491:0', 'landsd/255260:0', 'landsd/255440:0', 'landsd/255648:0'];manifest=ROOT/'3d-viewer/city/data/manifest.json'
 save(DOC/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in read(manifest)['officialModelCatalogues']],evidenceRefs=[ref(CAP/'selection.json.gz')],rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in rows]))
 tool=HERE/'parkview_12_15_actual_render_attributes_v1_20261021.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 output=read(DOC/'attributes.json.gz');assert output['startEndAllInputsVerified'];refs=[Path(__file__),tool,SRC/'result.json']
 for p,h in {**pins,**output['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_attributes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-parkview-original-complete-loader-attributes',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],completeFaces=sum(r['candidate']['entry']['triangles']for r in rows),installationApproved=False))
import sys, uuid, json
from run import reservations
LOCAL=HERE/'local'/BATCH
UID='landsd/33396:0'
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/253980:0', 'building:landsd/254491:0', 'building:landsd/255260:0', 'building:landsd/255440:0', 'building:landsd/255648:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

