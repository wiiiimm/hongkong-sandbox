"""Fresh complete current identity replay for exact Harbourfront boundary role."""
import importlib.util,json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from harbourfront_attached_road_margin_identity_20261009 import UID,verify_files,POLICY,DOC as PRIMARY
BATCH='government-xl-two-harbourfront-attached-boundary-current-identity-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-current-inputs/check-selection.json.gz'
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('harbourfront-boundary-current-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 try:
  save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)));row=next(r for r in read(INPUT)['rows'] if r['uid']==UID);manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());decoder=module('harbourfront_fresh_original','xl-second-pass.py');decoder.LOCAL=LOCAL;final=module('harbourfront_complete_current','xl-final-script-pass.py')
  source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==row['sourceSHA256'];dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT));tri=decoder.glb_triangles(row);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form,_,tile=next(x for x in forms if x[0]['uid']==UID);row['source']={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())};row['currentReview']=None
  installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m.get('placementReviewed') is True};assert UID not in installed
  context={'uid':UID,'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}};proof=verify_files(row,context,LOCAL/'identity-replay');assert digest(manifest.read_bytes())==msha and reservations.owns(lease)
  save(DOC/'selection.json.gz',{'batch':BATCH,'rows':[row],'manifestSHA256':msha});save(DOC/'context.json.gz',{'rows':[context]});save(DOC/'identity-proof.json',proof);save(DOC/'all-current-forms.json.gz',{'forms':[b for b,_,_ in forms],'tileHashes':context['neighbourTileHashes']})
  freezer=module('harbourfront_identity_checkpoint','xl-popcorn-source-investigations-checkpoints-20261009.py');paths=[Path(__file__),INPUT,HERE/'harbourfront_attached_road_margin_identity_20261009.py',HERE/'test_harbourfront_attached_road_margin_identity_20261009.py',source,dest,manifest,HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'source_closed_components.py',PRIMARY/'result.json'];paths +=[ROOT/'3d-viewer'/url for url in context['neighbourTileHashes']]
  freezer.freeze(BATCH,'one-exact-attached-street-front-boundary-current-identity-v1',paths,{'uids':[UID],'identityAccepted':proof['passed'],'identityPolicy':POLICY,'sourceIdentityReviewUsedAI':True,'scriptFullAcceptancePassed':False,'currentForms':len(forms),'rawIdentityReasonsRetained':proof['rawExtentReasonsRetained'],'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'complete-original-wall-cylinder-physical-support-runtime-neighbours-browser-publication','nextStep':'Independently resolve every original wall/cylinder/component physical role and all runtime/foreign/browser gates with complete unchanged original source. No source-specific boundary interpretation gives support credit.'})
  print(json.dumps({'uid':UID,'passed':proof['passed'],'reasons':proof['reasons'],'manifestSHA256':msha}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
