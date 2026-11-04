"""Fresh complete current raw identity before any Tung Sing named source-envelope interpretation."""
import importlib.util,json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from routed_original_cell_identity import verify_files
BATCH='government-xl-lei-tung-current-full-cell-preflight-v2-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/126434:0'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('lei-tung-current-cell-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  inp=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-support-original-recovery/selection.json.gz';row=next(r for r in read(inp)['rows'] if r['uid']==UID);source=ROOT/'source-scripts/city/government-import/local/xl-terrain-recovery-20261009-support-original-recovery/assets'/('368ec3bcb2b011f8db942a2e294f500043762b15851e55113c95443a48ff5f15.glb.gz');assert digest(source.read_bytes())==row['sourceSHA256'];row['candidate']['path']=str(source.relative_to(ROOT));row['currentReview']=None;row['triangles']=row['native']['model']['triangles']
  dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True);dest.write_bytes(source.read_bytes());row['candidate']['path']=str(dest.relative_to(ROOT))
  second=module('tung_sing_raw_original_decode','xl-second-pass.py');second.LOCAL=LOCAL;tri=second.glb_triangles(row);final=module('tung_sing_raw_current_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form,_,tile=next(x for x in forms if x[0]['uid']==UID);row['source']={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())};manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());context={'uid':UID,'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms}};proof=verify_files(row,context,LOCAL/'raw-cell-replay');assert digest(manifest.read_bytes())==msha
  save(DOC/'selection.json.gz',{'rows':[row],'manifestSHA256':msha});save(DOC/'context.json.gz',{'rows':[context]});save(DOC/'all-current-forms.json.gz',{'forms':[b for b,_,_ in forms],'tileHashes':context['neighbourTileHashes']});save(DOC/'raw-full-cell-proof.json',proof);save(DOC/'input-refs.json',{'inputHashes':{str(inp.relative_to(ROOT)):digest(inp.read_bytes()),str(source.relative_to(ROOT)):digest(source.read_bytes()),str(manifest.relative_to(ROOT)):msha}})
  print(json.dumps({'passed':proof['passed'],'reasons':proof['reasons'],'geographicCell':proof['geographicCell'],'manifestSHA256':msha}),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
