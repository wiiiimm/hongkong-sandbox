"""Current exact-source identity context and production runtime checks for nine originals."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from wave_verdant_private_browser_v5_20261018 import UIDS
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-private-browser-v5-20261018';BATCH='government-xl-wave-verdant-current-identity-runtime-v1-20261018';DOC=BASE/BATCH;STAGE=HERE/'local'/BATCH

def main():
 assert not DOC.exists() and not STAGE.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sources={}
 for name,file,key in [('government-xl-wave-all-original-support-distance-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-podium-support-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-block2-original-recovery-v1-20261017','selection.json.gz','rows'),('government-xl-wave-verdant-194544-original-recovery-v1-20261017','selection.json.gz','rows')]:
  p=BASE/name/file;refs.append(p);sources.update({x['uid']:x for x in read(p)[key]})
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 try:
  final=module('wave_current_identity',HERE/'xl-final-script-pass.py');cat=read(HERE/'local'/PRIOR.name/'catalogue.json');contexts=[];formrefs={}
  for entry in cat['models']:
   uid=entry['uid'];row=sources[uid];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==entry['sha256']==row['sourceSHA256'];tri=decode_original_world_triangles(raw);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);matches=[b for b,_,_ in forms if b['uid']==uid];assert len(matches)==1 and matches[0]==row['source']['building'],('current source form mismatch',uid)
   identity=final.identity_context(row,tri,forms);contexts.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],identity=identity,currentSourceFormExact=True));asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
   for _,_,tile in forms:formrefs[tile]=digest((ROOT/'3d-viewer'/tile).read_bytes())
   print(uid,identity,flush=True)
  save(DOC/'identity-context.json',dict(rows=contexts,neighbourTileHashes=formrefs));save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=len(UIDS),catalogues=['catalogue.json']));save(STAGE/'source-forms.json',{u:sources[u]['source'] for u in UIDS})
  tool=HERE.parent/'building-batch/validate_candidates.mjs';subprocess.run(['node',str(tool),'--candidates',str(STAGE),'--source-forms',str((STAGE/'source-forms.json').relative_to(ROOT)),'--out',str(DOC/'validation.json')],cwd=ROOT,check=True)
  validation=read(DOC/'validation.json');save(DOC/'summary.json',dict(rows=contexts,validation=validation,fullAcceptance=False,newlyInstalled=0))
  refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',tool,*[ROOT/p for p in pins],*[p for p in STAGE.rglob('*')if p.is_file()]])
  for p,h in validation.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
  for tile,h in formrefs.items():p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==h;refs.append(p)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert reservations.owns(lease)
  out=module('wave_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-current-source-identity-runtime-v1',list(set(refs)),dict(uids=UIDS,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
