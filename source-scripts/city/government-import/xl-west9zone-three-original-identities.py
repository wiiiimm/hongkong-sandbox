"""Fresh original identity evidence for WEST9ZONE and its two tower originals."""
import importlib.util,json,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from government_georef_cell_identity import verify_files as individual_verify
from retained_component_geographic_identity import verify_files as group_verify
DOC=ROOT/'docs/astra-city/government-import/government-xl-west9zone-three-original-identities-20261008';LOCAL=HERE/'local'/DOC.name
OLD=ROOT/'docs/astra-city/government-import/government-xl-west9zone-original-support-group-20261005'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();rows=read(OLD/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}=={'landsd/81972:0','landsd/83691:0'}
 primary=next(r for r in read(ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/physical-selection.json.gz')['rows'] if r['uid']=='landsd/227099:0');rows.append(primary)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestSHA=digest(manifest.read_bytes());final=module('west_fresh_context','xl-final-script-pass.py');decoder=module('west_fresh_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;contexts=[];proofs=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in rows:
   review=c.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(r['uid'],)).fetchone();r['currentReview']=None if review is None else {'state':review[0],'sourceSHA256':review[1],'result':review[2]}
 for row in rows:
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  lo,hi=row['native']['model']['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tri=decoder.glb_triangles(row);context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}};contexts.append(context)
  proof=(group_verify if row['uid']==primary['uid'] else individual_verify)(row,context,LOCAL/'identity'/row['uid'].split('/')[1]);proofs.append(proof);save(DOC/(row['uid'].split('/')[1].replace(':','-')+'.json'),proof);print(json.dumps({'uid':row['uid'],'passed':proof['passed'],'reasons':proof['reasons'],'currentReview':row['currentReview']}),flush=True)
 assert digest(manifest.read_bytes())==manifestSHA;save(DOC/'selection.json.gz',{'rows':rows,'manifestSHA256':manifestSHA});save(DOC/'context.json.gz',{'rows':contexts});save(DOC/'summary.json',{'rows':[{'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'passed':p['passed'],'reasons':p['reasons']} for r,p in zip(rows,proofs)],'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'manifestSHA256':manifestSHA})
if __name__=='__main__':main()
