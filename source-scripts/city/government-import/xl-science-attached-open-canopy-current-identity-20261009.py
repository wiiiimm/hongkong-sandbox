"""Fresh current Science Museum named ancillary relationship; never publish."""
import importlib.util,json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from science_attached_open_canopy_identity_20261009 import UID,RELATED,verify_files,POLICY
BATCH='government-xl-science-attached-open-canopy-current-identity-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-80343-current-inputs/check-selection.json.gz'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('science-ancillary-identity-'+str(uuid.uuid4()),['building:'+u for u in [UID,RELATED]],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 try:
  save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)));row=next(r for r in read(INPUT)['rows'] if r['uid']==UID);manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());decoder=module('science_fresh_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;final=module('science_fresh_forms','xl-final-script-pass.py')
  source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==row['sourceSHA256'];dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT));tri=decoder.glb_triangles(row);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form,_,tile=next(x for x in forms if x[0]['uid']==UID);row['source']={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())};row['currentReview']=None
  installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};assert UID not in installed
  context={'uid':UID,'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}};proof=verify_files(row,context,LOCAL/'identity-replay');assert digest(manifest.read_bytes())==msha and reservations.owns(lease)
  save(DOC/'selection.json.gz',{'batch':BATCH,'rows':[row],'manifestSHA256':msha});save(DOC/'context.json.gz',{'rows':[context]});save(DOC/'identity-proof.json',proof);save(DOC/'all-current-forms.json.gz',{'forms':[b for b,_,_ in forms],'tileHashes':context['neighbourTileHashes']})
  freezer=module('science_identity_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');paths=[Path(__file__),INPUT,HERE/'science_attached_open_canopy_identity_20261009.py',HERE/'test_science_attached_open_canopy_identity_20261009.py',source,dest,manifest,HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py'];paths+=[ROOT/'3d-viewer'/url for url in context['neighbourTileHashes']]
  freezer.freeze(BATCH,'one-exact-named-open-sided-canopy-current-identity-v1',paths,{'uids':[UID,RELATED],'identityAccepted':proof['passed'],'identityPolicy':POLICY,'sourceIdentityReviewUsedAI':True,'scriptFullAcceptancePassed':False,'currentForms':len(forms),'rawIdentityReasonsRetained':proof['rawUnrelatedOverlapReasonsRetained'],'remainingReason':'complete-original-physical-runtime-neighbours-staged-live-browser-publication','nextStep':'Complete all original physical and runtime gates with actual current canopy and all neighbours retained. Root independently reviews the named identity route before installation.'})
  print(json.dumps({'uid':UID,'passed':proof['passed'],'reasons':proof['reasons'],'manifestSHA256':msha}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
