"""Fresh independent identity checks of 21 unchanged overlapping originals.

Acquisition and identity are separate from physical/support/browser acceptance.
"""
import importlib.util, traceback, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from exact_original_georef_cell_identity_20261009 import verify_files

BATCH='government-xl-popcorn-overlapping-original-current-identity-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-current-overlapping-original-recovery-20261009/selection.json.gz'

def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert not (DOC/'result.json').exists()
 selection=read(INPUT);rows=selection['rows'];assert len(rows)==21 and not selection['missing']
 claim=reservations.claim('popcorn-current-identities-'+str(uuid.uuid4()),['building:'+r['uid'] for r in rows],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 final=module('popcorn_overlap_current_forms','xl-final-script-pass.py');decoder=module('popcorn_overlap_original_decode','xl-second-pass.py');decoder.LOCAL=LOCAL
 (LOCAL/'assets').mkdir(parents=True,exist_ok=True);outputs=[];paths=[Path(__file__),INPUT,HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py']
 try:
  for row in rows:
   assert reservations.heartbeat(lease)['ok'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw);row['triangles']=row['native']['model']['triangles'];lo,hi=row['native']['model']['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tri=decoder.glb_triangles(row)
   assert [b for b,_,_ in forms if b['uid']==row['uid']]==[row['source']['building']],'Current source form changed'
   context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}}
   save(DOC/(row['uid'].split('/')[1].replace(':','-')+'-current-context.json.gz'),context)
   try:proof=verify_files(row,context,LOCAL/'identity'/row['uid'].split('/')[1])
   except Exception as error:proof={'uid':row['uid'],'passed':False,'reasons':['identity-adapter-or-source-proof-investigation'],'error':str(error),'traceback':traceback.format_exc(),'installationApproved':False}
   save(DOC/(row['uid'].split('/')[1].replace(':','-')+'-identity.json'),proof);outputs.append({'uid':row['uid'],'passed':proof['passed'],'reasons':proof['reasons']});paths.append(asset);paths.extend(ROOT/'3d-viewer'/u for u in context['neighbourTileHashes']);save(DOC/'partial-summary.json',{'rows':outputs,'installationApproved':False});print(outputs[-1],flush=True)
  module('popcorn_overlap_identity_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-one-fresh-independent-original-identities-v1',paths,{'uids':sorted(r['uid'] for r in rows),'rows':outputs,'independentIdentityPassed':sum(r['passed'] for r in outputs),'humanStatus':'held-unknown','requiresHumanDecision':False,'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'remainingReason':'complete-coupled-original-support-physical-runtime-and-specific-identity-recovery-pending','nextStep':'Continue qualified originals through complete physical/support/current neighbours; retain every failed identity reason for exact source recovery. No identity result grants installation credit.'})
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
