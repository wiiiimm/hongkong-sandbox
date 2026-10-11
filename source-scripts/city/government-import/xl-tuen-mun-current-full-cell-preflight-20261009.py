"""Fresh whole-cell/source/current preflight; no hospital identity exception."""
import importlib.util,json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from routed_original_cell_identity import verify_files
BATCH='government-xl-tuen-mun-current-full-cell-preflight-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
UID='landsd/191896:0'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim('tuen-mun-current-cell-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim
 inp=ROOT/'docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006/check-selection.json.gz'
 try:
  row=next(r for r in read(inp)['rows'] if r['uid']==UID)
  ranking=ROOT/'docs/astra-city/government-import/government-xl-identity-primary-spatial-ranking-20261009/ranking.json.gz'
  ranked=next(r for r in read(ranking)['rows'] if r['uid']==UID)
  source=ROOT/ranked['sourcePath'];assert digest(source.read_bytes())==row['sourceSHA256'];row['currentReview']=None
  dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True);dest.write_bytes(source.read_bytes());row['candidate']['path']=str(dest.relative_to(ROOT))
  second=module('hospital_raw_original_decode','xl-second-pass.py');second.LOCAL=LOCAL;tri=second.glb_triangles(row)
  final=module('hospital_raw_current_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form,_,tile=next(x for x in forms if x[0]['uid']==UID)
  row['source']={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())}
  manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes())
  context={'uid':UID,'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms}}
  proof=verify_files(row,context,LOCAL/'raw-cell-replay');assert digest(manifest.read_bytes())==msha
  save(DOC/'selection.json.gz',{'rows':[row],'manifestSHA256':msha});save(DOC/'context.json.gz',{'rows':[context]});save(DOC/'all-current-forms.json.gz',{'forms':[b for b,_,_ in forms],'tileHashes':context['neighbourTileHashes']});save(DOC/'raw-full-cell-proof.json',proof)
  save(DOC/'input-refs.json',{'inputHashes':{str(inp.relative_to(ROOT)):digest(inp.read_bytes()),str(ranking.relative_to(ROOT)):digest(ranking.read_bytes()),str(source.relative_to(ROOT)):digest(source.read_bytes()),str(manifest.relative_to(ROOT)):msha}})
 finally:assert reservations.release(claim['reservation'])['ok']
 paths=[Path(__file__),inp,ranking,source]+[p for p in LOCAL.rglob('*') if p.is_file()]+[ROOT/'3d-viewer'/u for u in context['neighbourTileHashes']]
 fence=module('hospital_current_preflight_fence','xl-popcorn-source-investigations-checkpoints-20261009.py')
 fence.freeze(BATCH,'fresh-unchanged-original-full-cell-current-identity-preflight-v1',paths,dict(uids=[UID],identityAccepted=proof['passed'],rawIdentityReasons=proof['reasons'],scriptFullAcceptancePassed=False,requiresAIModelGeometry=False,requiresHumanDecision=False,nextStep='Apply only a source-specific independently evidenced ownership relationship if every unchanged-source/current own-primary/full-cell guard passes; keep full source and all current physical actors.'))
 print(json.dumps({'passed':proof['passed'],'reasons':proof['reasons'],'geographicCell':proof['geographicCell'],'manifestSHA256':msha}),flush=True)
if __name__=='__main__':main()
