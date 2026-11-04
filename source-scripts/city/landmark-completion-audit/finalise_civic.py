"""Exact existing civic asset review and narrowly guarded metadata migrations."""
import json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;D=ROOT/'docs/astra-city/landmark-completion-audit'
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 batch=read(D/'civic12-batch.json');uids={p['uid'] for p in batch['parts']};priority=read(HERE/'civic-priority-review.json');priorityUIDs={p['uid'] for p in priority['rows']};views={};reports=[]
 for folder in ['civic12-browser','civic12-reframed','civic12-mobile-completion','civic-priority-browser']:
  f=D/folder/'report.json';r=read(f);assert not r['errors'];reports.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'runtimeHashes':r['runtimeHashes'],'stagedPriorityOnly':r['staged']})
  for v in r['views']:
   uid=v['uids'][0]
   if uid in priorityUIDs and folder!='civic-priority-browser':continue
   assert sha(f.parent/v['file'])==v['sha256'];assert not v['cameraCollision'] and not v['uiOverflow'] and v['boxInsideView'];assert v['activeUIDs']==v['uids'];assert all(p['uid']==p['hitUid'] for p in v['picking']);assert all(p['hits'] and any(abs(h-p['sampler'])<.003 for h in p['hits']) for p in v['terrainProbes']);views[(uid,v['mobile'],v['time'])]={**v,'folder':folder,'stagedPriorityOnly':uid in priorityUIDs}
 assert len(views)==48,(len(views),sorted({(u,m,t) for u in uids for m in [False,True] for t in [15,22]}-set(views)))
 for uid in uids:assert {(m,t) for u,m,t in views if u==uid}=={(False,15),(False,22),(True,15),(True,22)}
 save(D/'civic12-browser-accepted.json',{'issue':'HKS-214','views':list(views.values()),'reports':reports,'count':48,'nativeAssetsChanged':False,'priorityOnlyStagedUIDs':sorted(priorityUIDs),'qualification':'Only three named civic metadata priorities are intercepted for staged review; all other models, source assets, terrain and budgets are actual viewer values. Source-part acceptance is not whole-landmark closure.'})
 models={m['uid']:m for m in read(HERE/'civic12-catalogue.json')['models']};proofs={};manifests=[ROOT/'source-scripts/city/landmark-pass/existing-work-grandhall/staged/9-SE-21B/manifest.json',*(ROOT/'source-scripts/city/central-completion/staged').glob('*/manifest.json')]
 for f in manifests:
  manifest=read(f)
  for spec in manifest.get('models',[]):
   for uid,m in models.items():
    if spec['id']!=m['modelId'] or uid in proofs:continue
    match=next((r for r in spec.get('officialMatches',[]) if r['objectId']==int(uid.split('/')[1].split(':')[0])),None)
    if not match:continue
    assert match['buildingCSUID']==m['buildingCSUID'];files=[]
    for path,h in spec['sourceHashes'].items():assert sha(f.parent/path)==h;files.append({'path':str((f.parent/path).relative_to(ROOT)),'sha256':h})
    proofs[uid]={'manifest':str(f.relative_to(ROOT)),'manifestSHA256':sha(f),'match':match,'files':files,'modelId':m['modelId']}
 corridor=ROOT/'docs/astra-city/central-completion/corridor-models.json'
 for r in read(corridor)['assets']:
  uid=r['uid']
  if uid not in uids or uid in proofs:continue
  m=models[uid];assert r['compressedSha256']==m['sha256'] and r['sourceMatch']['buildingCSUID']==m['buildingCSUID'];folder=(ROOT/r['sourceEntry']).parents[2];files=[]
  for path,h in r['sourceHashes'].items():assert sha(folder/path)==h;files.append({'path':str((folder/path).relative_to(ROOT)),'sha256':h})
  proofs[uid]={'priorMatchReport':str(corridor.relative_to(ROOT)),'priorMatchReportSHA256':sha(corridor),'match':r['sourceMatch'],'files':files,'modelId':m['modelId'],'qualification':'Current selective staged manifest omits this previously packed corridor target; retained exact source files and prior exact-GeoRef match report remain checked.'}
 assert set(proofs)==uids
 save(D/'civic12-identity-proofs.json',{'issue':'HKS-214','rows':proofs,'qualification':'Exact source component identities, not whole tourist-assembly or photographic-material approval.'})
 supports={r['uid']:r for r in read(D/'civic12-support.json')['rows']};surfaces={r['uid']:r['stats']['patched'] for r in read(D/'civic12-surfaces.json')['rows']};pairs=[read(D/'grandhall-podium-support.json'),read(D/'hopewell-podium-support.json')];assert all(p['remainingAllConnected'] for p in pairs)
 evidence=[D/'civic12-support.json',D/'civic12-surfaces.json',D/'civic12-native-burial.json',D/'civic12-browser-accepted.json',D/'civic12-identity-proofs.json',D/'grandhall-podium-support.json',D/'hopewell-podium-support.json'];hashes={str(p.relative_to(ROOT)):sha(p) for p in evidence};notes={
 'landsd/238482:0':'Grand Hall of Ten Thousand Buddhas was already present but omitted from the529 review inventory. Native multi-storey roof/form verified. Two of four low-rim vertices directly contact native podium238483; all four are in mesh components connected to measured contacts, maximum seam0.616m. No buried faces. Requires native podium retention metadata.',
 'landsd/265525:0':'Hopewell circular tower and crown remain visible at native source heights.169/170 low-rim vertices touch installed native podium334311 within0.5m; remaining vertex belongs to a connected source component, nearest distance0.631m. No buried faces. Requires native podium retention.',
 'landsd/124803:0':'HKCEC native curved harbour roof, full source envelope and roof details visible.55 small below-grade faces total17.145m² (0.00936%), including51 upward triangles at4.516–5.383m HKPD; original native TIN reproduces all55 with0.284–0.627m burial. Preserve surveyed source geometry rather than shift the complex for local foundation/paving detail.',
 'landsd/180905:0':'This THREE GARDEN ROAD UID is a small ancillary connector, roughly11.5x14.8m and7.03m high, not either complete tower. Its exact source form, local position and terrain contact pass. Keep priority detail and preserve component-versus-landmark distinction.',
 'landsd/322270:0':'Central Government Offices source form and roof/connecting volume verified. Existing detail priority has only300m mobile range and cannot retain the native model at the full-building portrait review distance. Narrow staged landmark priority succeeds using unchanged1800m landmark range and current budgets; requires guarded metadata integration.',
 'landsd/4447:0':'AIA Central exact native tower retained. Initial southwest camera was occluded by a neighbouring building; exact source/terrain visibility search provides a clear frame. Narrow staged landmark priority supports whole-tower mobile framing under unchanged budgets; requires guarded metadata integration.',
 'landsd/320038:0':'Chief Executive Office native block verified as its own source component. Promote this explicitly named civic landmark to the existing landmark range, keeping geometry/support/budget settings unchanged; staged desktop/mobile frames pass.'}
 live={};manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']:
  f=ROOT/'3d-viewer'/url
  for m in read(f)['models']:live[m['uid']]=(f,url,m)
 pending=priorityUIDs|{'landsd/238482:0','landsd/265525:0'};rows=[]
 for p in batch['parts']:
  uid=p['uid'];f,url,m=live[uid];assert m['sha256']==sha(ROOT/p['asset']['path'])==p['asset']['sha256']==supports[uid]['sha256'];rows.append({'uid':uid,'name':p['name'],'status':'approved-for-integration' if uid in pending else 'installed-verified','sourceSHA256':m['sha256'],'modelId':m['modelId'],'observation':notes.get(uid,'Exact native source identity, full building/roof form, current terrain contact, roof picking and day/night desktop/mobile visibility checked. No wholly buried source face. Preserve original government geometry and heights.'),'wholeLandmarkComplete':False,'evidenceHashes':hashes,'surface':{k:v for k,v in surfaces[uid].items() if k!='buriedTriangleEvidence'}})
 decision={'issue':'HKS-214','reviewSnapshot':read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId'],'existingNativeParts':12,'newModelsAdded':0,'installedVerified':7,'pendingMetadata':5,'rows':rows,'sourceGeometryChanged':False,'verticalScale':1,'limits':['Government geometry is simplified native form; procedural windows, colours and facade materials are not surveyed textures or interiors.','Whole landmark membership/architecture closure is separate from verified source parts.','Three Garden Road180905 is only an ancillary connector.','Grand Hall238482 is an existing asset recovered into the ledger, not a newly added model.','Three staged priority overrides require actual-runtime integration checks before installed verification.']};save(D/'civic12-decisions.json',decision)
 contact=D/'civic12-support.json';changes=[];catalogues={}
 for pair in pairs:
  uid=pair['tower'];f,url,m=live[uid];podium=live[pair['podium']][2];catalogues.setdefault(url,{'url':url,'source':str(f.relative_to(ROOT)),'oldSHA256':sha(f),'models':[]})['models'].append(uid);changes.append({'uid':uid,'catalogue':str(f.relative_to(ROOT)),'modelSHA256':m['sha256'],'modelId':m['modelId'],'buildingCSUID':m['buildingCSUID'],'oldSupportDependencies':m.get('supportDependencies',[]),'supportDependencies':[{'uid':podium['uid'],'state':'installed','csuid':podium['buildingCSUID']}],'contactEvidenceSHA256':sha(contact)})
 save(HERE/'dependency-replacements-civic.json',{'issue':'HKS-214','version':1,'published':False,'scope':'Retain existing native Grand Hall and Hopewell podiums; all geometry and other metadata unchanged.','catalogues':list(catalogues.values()),'changes':changes,'contactReport':str(contact.relative_to(ROOT)),'contactReportSHA256':sha(contact),'requiresNewNativeUids':[],'requiredExistingNativeUids':[p['podium'] for p in pairs],'requiresVisualApproval':True,'visualApproval':{'status':'approved-for-integration','evidence':str((D/'civic12-decisions.json').relative_to(ROOT)),'evidenceSHA256':sha(D/'civic12-decisions.json'),'scope':'Exact connected native tower/podium source surfaces and inspected desktop/mobile day/night views.'}})
 cats={};changes=[]
 for row in priority['rows']:
  uid=row['uid'];f,url,m=live[uid];assert m['priority']==row['oldPriority'] and sha(f)==row['catalogueSHA256'];cats.setdefault(url,{'url':url,'source':str(f.relative_to(ROOT)),'oldSHA256':sha(f),'models':[]})['models'].append(uid);changes.append({'uid':uid,'catalogue':str(f.relative_to(ROOT)),'modelSHA256':m['sha256'],'modelId':m['modelId'],'buildingCSUID':m['buildingCSUID'],'oldPriority':m['priority'],'priority':'landmark'})
 approval={'issue':'HKS-214','status':'approved-for-integration','scope':'Three explicitly named civic landmarks use the already configured landmark distance. No budget, range, source or support changes.','uids':sorted(priorityUIDs),'evidence':str((D/'civic12-decisions.json').relative_to(ROOT)),'evidenceSHA256':sha(D/'civic12-decisions.json')};save(D/'civic-priority-approval.json',approval)
 review={'issue':'HKS-214','catalogues':list(cats.values()),'changes':changes,'evidence':{'path':str((D/'civic12-decisions.json').relative_to(ROOT)),'sha256':sha(D/'civic12-decisions.json')}};save(HERE/'priority-replacements-civic.json',review);save(HERE/'priority-replacements-civic-plan-entry.json',{'path':str((HERE/'priority-replacements-civic.json').relative_to(ROOT)),'sha256':sha(HERE/'priority-replacements-civic.json'),'visualApproval':{'path':str((D/'civic-priority-approval.json').relative_to(ROOT)),'sha256':sha(D/'civic-priority-approval.json')}});print(json.dumps({'verifiedExisting':7,'metadataPending':5,'newModels':0,'views':48}))
if __name__=='__main__':main()
