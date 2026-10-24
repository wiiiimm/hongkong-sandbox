"""Current identity context and production loader validation, no publication."""
from pathlib import Path
import subprocess,uuid,numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-yoho58849-current-capture-v2-20261017';BATCH='government-xl-yoho58849-current-identity-runtime-v2-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/CAP.name;UID='landsd/58849:0'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  row=read(CAP/'selection.json.gz')['rows'][0];g=read(LOCAL/'runtime-geometry.json.gz')['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));final=module('yoho_identity_context',HERE/'xl-final-script-pass.py');forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);identity=final.identity_context(row,tri,forms);save(DOC/'identity-context.json',identity)
  template=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entry=dict(row['candidate']['entry'],sourceTile=row['native']['sheet'],publicationApproved=False,placementReviewed=False,proceduralWindows=False);template.update(models=[entry],counts=dict(packedModels=1));stage=HERE/'local'/BATCH;asset=stage/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes((ROOT/row['candidate']['path']).read_bytes());assert digest(asset.read_bytes())==row['sourceSHA256']
  save(stage/'catalogue.json',template);save(stage/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(stage/'source-forms.json',{UID:row['source']})
  tool=HERE.parent/'building-batch/validate_candidates.mjs';subprocess.run(['node',str(tool),'--candidates',str(stage),'--source-forms',str((stage/'source-forms.json').relative_to(ROOT)),'--out',str(DOC/'validation.json')],cwd=ROOT,check=True)
  validation=read(DOC/'validation.json');metrics=read(CAP/'metrics.json');profile=metrics.get('profile');save(DOC/'summary.json',dict(uid=UID,identity=identity,validation=validation,fullAcceptance=False,newlyInstalled=0))
  refs=[Path(__file__),CAP/'result.json',HERE/'xl-final-script-pass.py',tool,*[ROOT/p for p in pins],*[p for p in stage.rglob('*')if p.is_file()]]
  for p,h in validation.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert reservations.owns(lease)
  out=module('yoho_identity_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'yoho58849-current-identity-and-runtime-v2',refs,dict(uids=[UID],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
