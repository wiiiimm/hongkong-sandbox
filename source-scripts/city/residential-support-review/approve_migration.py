"""Bind direct assembly inspection and exact seams to five additions plus six metadata changes."""
import json,pathlib,hashlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
 lease=read(pathlib.Path('/tmp/astra-support-migration-approval-lease.json'));assert reservations.owns(lease)
 replacements=read(HERE/'dependency-replacements.json');contact=read(DOC/'migration-support.json');frames=read(DOC/'migration-framing/report.json');facade=read(DOC/'migration-facade/report.json');assert not frames['errors']and not facade['errors'];byuid={r['uid']:r for r in frames['rows']};byuid['landsd/60395:0']=facade['rows'][0];cat=read(HERE/'migration-candidates/catalogue.json');new=set(replacements['requiresNewNativeUids']);old={r['uid']for r in replacements['changes']};assert {'building:'+u for u in new|old}<=set(lease['resources']);assert all(r['allNativeContacts']for r in contact['rows'])
 for c in replacements['catalogues']:assert sha(ROOT/c['source'])==c['oldSHA256']
 observations={
 'landsd/122547:0':'Existing LP6 Tower3 shaft, crown and join to the native podium inspected in complete and isolated views; source geometry unchanged.',
 'landsd/133473:0':'Existing LP6 Tower5 shaft, roof crown and joined native podium inspected; source geometry unchanged.',
 'landsd/156618:0':'Existing LP6 Tower2 stepped crown and shaft inspected over its native support; source geometry unchanged.',
 'landsd/262524:0':'LP6 Tower1 shaft and stepped rooftop crown inspected with the complete native podium assembly.',
 'landsd/272917:0':'Long bent LP6 podium, roof terraces and tower interfaces inspected. All four tower lower rims contact its actual triangles.',
 'landsd/239664:0':'Chungking BlockA rectangular shaft and roof service structures inspected with the shared native podium and all other blocks.',
 'landsd/319006:0':'Chungking BlockB recessed outline and roof structures inspected with the shared native podium.',
 'landsd/319007:0':'Existing Chungking BlockD outline, roof structures and native podium contact inspected; only support metadata changes.',
 'landsd/319008:0':'Existing Chungking BlockC recessed outline and rooftop structures inspected; source geometry unchanged.',
 'landsd/319009:0':'Existing Chungking BlockE native outline and roof structures inspected in the coherent assembly; source geometry unchanged.',
 'landsd/60395:0':'Low shared podium: complete isolated native outline, roof details and facade inspected. Broad rooftop views are occluded by neighbouring buildings; a labelled collision-free street facade view gives14/40 actual wall-triangle hits with the native model active. That normal view is intentionally cropped and does not claim full bounds framing. Its full isolated view gives21/21 hits and frames all bounds. All five tower lower rims contact this podium.'}
 rows=[]
 for m in cat['models']:
  uid=m['uid'];r=byuid[uid];assert len(r['views'])==2
  for v in r['views']:
   assert v['active']and v['nativeGeometryUnchanged']and v['final']['clear']and v['final']['cameraCollisionUid']is None
   if uid!='landsd/60395:0'or v['mode']=='isolated':assert v['final']['fullyFramed']
  folder=DOC/('migration-facade'if uid=='landsd/60395:0'else'migration-framing');rows.append({'uid':uid,'status':'approved-native-addition'if uid in new else'approved-support-metadata-only','modelSHA256':m['sha256'],'observation':observations[uid],'wholeLandmarkComplete':False,'images':[{'path':str((folder/v['file']).relative_to(ROOT)),'sha256':sha(folder/v['file'])}for v in r['views']]})
 inputs=[HERE/'dependency-replacements.json',HERE/'migration-candidates/catalogue.json',DOC/'migration-support.json',DOC/'migration-framing/report.json',DOC/'migration-facade/report.json'];approval={'issue':'HKS-214','status':'approved-for-integration','published':False,'verticalScale':1,'approvedNewUids':sorted(new),'approvedMetadataUids':sorted(old),'nativeRimContacts':sum(r['contacts']for r in contact['rows']),'nativeRimSamples':sum(r['total']for r in contact['rows']),'inputHashes':{str(p.relative_to(ROOT)):sha(p)for p in inputs},'rows':rows,'limits':['Source components and metadata migration only; no whole-landmark or region completion.','Window rows remain illustrative and do not establish surveyed floor counts.','Chungking podium uses a labelled cropped normal facade view plus full isolated geometry; no scene geometry was hidden in the normal view.','Five additions and six dependency replacements must be applied atomically, followed by installed picking/collision/streaming checks.']};save(HERE/'migration-approval.json',approval);save(DOC/'migration-approval.json',approval)
 original=read(DOC/'decisions.json');decision={r['uid']:r for r in original['rows']};out=HERE/'migration-approved';out.mkdir(exist_ok=True);result=[]
 for m in cat['models']:
  if m['uid']not in new:continue
  m=dict(m);asset=HERE/'migration-candidates'/m['asset'];assert sha(asset)==m['sha256'];shutil.copyfile(asset,out/m['asset']);m.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=decision[m['uid']]['landmarkMembershipApproved'],publicationApproved=True,reviewIssue='HKS-214',wholeLandmarkComplete=False,architectureReview=observations[m['uid']]);result.append(m)
 cat['models']=result;cat['counts']['packedModels']=len(result);save(out/'catalogue.json',cat);save(out/'catalogue-index.json',{'models':len(result),'catalogues':['catalogue.json']})
 plan={'areas':[{'area':'Coherent Chungking and LP6 native support assemblies','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/native-support-migration-20260909/catalogue.json'}],'dependencyReviews':[{'path':str((HERE/'dependency-replacements.json').relative_to(ROOT)),'sha256':sha(HERE/'dependency-replacements.json'),'visualApproval':{'path':str((HERE/'migration-approval.json').relative_to(ROOT)),'sha256':sha(HERE/'migration-approval.json')}}]};save(HERE/'migration-publication-plan.json',plan);save(DOC/'migration-publication-plan.json',plan);guard={'issue':'HKS-214','published':False,'newUids':sorted(new),'metadataUids':sorted(old),'models':len(result),'metadataReplacements':len(old),'modelBytes':sum(m['bytes']for m in result),'triangles':sum(m['triangles']for m in result),'planSHA256':sha(HERE/'migration-publication-plan.json'),'catalogueSHA256':sha(out/'catalogue.json'),'approvalSHA256':sha(HERE/'migration-approval.json'),'requiresAtomicDependencyMigration':True,'sourceGeometryAndElevationChanges':0};save(HERE/'migration-guard.json',guard);save(DOC/'migration-guard.json',guard);print(json.dumps(guard,indent=2))
if __name__=='__main__':main()
