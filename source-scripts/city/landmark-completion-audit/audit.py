"""Deterministic named-landmark routing from frozen Neon state and actual viewer assets.
Read-only source/runtime/database. No geometry, ledger or publication writes.
"""
import argparse,collections,hashlib,json,pathlib,sys,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/landmark-completion-audit'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def save(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
def capture(snapshot):
 sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));from db import connect
 from psycopg.rows import dict_row
 with connect()as con:
  con.execute('SET TRANSACTION READ ONLY');con.row_factory=dict_row
  rows=con.execute('SELECT snapshot_id,uid,name,landmark_ids,source_state,source_sha256,initial_evidence,review_state,result,updated_at FROM astra_modelling.model_reviews WHERE snapshot_id=%s ORDER BY uid',(snapshot,)).fetchall()
 assert rows,'No review snapshot';rows=json.loads(json.dumps(rows,default=str))
 save(DOC/'neon-snapshot.json',{'snapshotId':snapshot,'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'databaseAccess':'read-only transaction','rows':rows})
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--refresh-neon',action='store_true');parser.add_argument('--snapshot',default='54650d6b59088d6d');a=parser.parse_args()
 if a.refresh_neon:capture(a.snapshot)
 paths={k:ROOT/p for k,p in {'registry':'source-scripts/city/landmark-registry/landmarks.json','preflight':'docs/astra-city/landmark-preflight/report.json','inventory':'docs/astra-city/model-integration-20260909/source-review-inventory.json','identity':'source-scripts/city/landmark-identity/report.json','overlay':'source-scripts/city/landmark-identity/proposed-overlay.json','centre':'docs/astra-city/identity-hold-review/center.json','manifest':'3d-viewer/city/data/manifest.json','neon':'docs/astra-city/landmark-completion-audit/neon-snapshot.json'}.items()}
 inputs={str(p.relative_to(ROOT)):sha(p)for p in paths.values()};d={k:read(p)for k,p in paths.items()};assert d['inventory']['snapshotId']==d['neon']['snapshotId']==a.snapshot
 parts={p['uid']:p for p in d['inventory']['parts']};reviews={p['uid']:p for p in d['neon']['rows']};assert set(parts)==set(reviews),'Inventory and frozen Neon membership differ'
 registry={p['id']:p for p in d['registry']['landmarks']};pre={p['id']:p for p in d['preflight']['landmarks']};assert len(registry)==213 and set(registry)==set(pre)
 identity={p['id']:p for p in d['identity']['rows']};centre={p['uid']:p for p in d['centre']['rows']}
 live={};duplicates=[]
 for url in d['manifest']['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;inputs[str(path.relative_to(ROOT))]=sha(path)
  for m in read(path)['models']:
   if m['uid'] in live:duplicates.append(m['uid'])
   else:live[m['uid']]={**m,'catalogue':url,'assetPath':str((path.parent/m['asset']).relative_to(ROOT))}
 assert not duplicates,'Duplicate live native UID'
 baseline={}
 for tile in d['manifest']['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=read(path)
  selected=[b for b in raw['buildings']if b['uid']in parts]
  if selected:inputs[str(path.relative_to(ROOT))]=sha(path)
  for b in selected:
   assert b['uid']not in baseline,'Duplicate source footprint UID';baseline[b['uid']]={**b,'runtimePath':str(path.relative_to(ROOT))}
 rows=[];old=[];supplement=[]
 for uid,p in sorted(parts.items()):
  r=reviews[uid];m=live.get(uid);b=baseline.get(uid);embedded=b.get('modelGeometry')if b else None;asset=None
  if m:
   assetPath=ROOT/m['assetPath'];actual=sha(assetPath) if assetPath.is_file() else None
   asset={'kind':'native-catalogue','path':m['assetPath'],'sha256':m['sha256'],'actualSHA256':actual,'hashValid':actual==m['sha256'],'modelId':m['modelId'],'bytes':m['bytes'],'placementReviewed':m.get('placementReviewed')is True,'identityReviewApproved':m.get('identityReviewApproved')is True,'publicationApproved':m.get('publicationApproved')is True,'landmarkMembershipApproved':m.get('landmarkMembershipApproved'),'supportDependencies':m.get('supportDependencies',[])}
  elif embedded:
   asset={'kind':'embedded-native-geometry','path':b['runtimePath'],'sha256':hashlib.sha256(canonical(embedded)).hexdigest(),'hashKind':'canonical embedded modelGeometry JSON SHA256; not a gzip asset hash','hashValid':True,'modelId':embedded['modelId'],'bytes':len(canonical(embedded)),'sourceHashes':embedded.get('sourceHashes',{}),'placementReviewed':False,'identityReviewApproved':False,'publicationApproved':False,'supportDependencies':[]}
  installed=bool(asset and asset['hashValid']);verified=installed and r['review_state']=='installed-verified' and (r['source_sha256']==asset['sha256'])
  routes=[]
  if uid in centre:routes.append('resolve-osm-glass-component-overlap')
  elif not b:routes.append('restore-missing-runtime-footprint')
  if asset and not asset['hashValid']:routes.append('repair-runtime-asset-hash-or-file')
  if r['review_state']=='installed-verified' and not verified:routes.append('reconcile-ledger-runtime-source')
  if installed and not verified:
   if not r['source_sha256']:routes.append('seed-existing-source-hash-in-new-ledger-snapshot')
   routes.append('verify-and-record-new-installation' if r['source_sha256']==asset['sha256'] and r['review_state']=='approved-for-integration' else 'reconcile-prior-placement-evidence' if asset['placementReviewed']else'existing-native-source-and-visual-review')
  if not installed and uid not in centre:
   if r['review_state']=='approved-for-integration':routes.append('install-approved-source-and-dependencies')
   elif r['review_state']=='held':routes.append('resolve-documented-source-or-placement-hold')
   elif p['sourceProgress'] in ['exact-source-absent-in-checked-sheets','source-checked-unavailable']:routes.append('checked-source-unavailable-use-alternative-or-reconstruction')
   elif p['candidate']:routes.append('review-prepared-native-model')
   elif p['sourceProgress'] in ['source-match-held','acquired-match-review']:routes.append('resolve-acquired-source-identity-or-coverage')
   else:routes.append('resolve-source-identity-or-acquisition')
  if m and m.get('landmarkMembershipApproved')is False:routes.append('correct-landmark-membership')
  row={'uid':uid,'name':p.get('name'),'landmarkIds':p['landmarkIds'],'relatedLandmarkIds':p.get('relatedLandmarkIds',[]),'supportForUids':p.get('supportForUids',[]),'sourceProgress':p['sourceProgress'],'reviewState':r['review_state'],'reviewSourceSHA256':r['source_sha256'],'reviewResult':r['result'],'originalClassification':p['classification'],'baselinePresent':bool(b),'nativeInstalled':installed,'installedVerified':verified,'asset':asset,'routes':sorted(set(routes)),'centreComponentEvidence':centre.get(uid),'knownHold':p.get('knownHold')}
  rows.append(row)
  if p['sourceProgress']=='installed':
   old.append(row)
   if asset and asset['hashValid']:
    supplement.append({'uid':uid,'objectId':p['objectId'],'name':p.get('name'),'landmarkIds':p['landmarkIds'],'sourceProgress':'installed','classification':['existing-native-needs-evidence-reconciliation'],'knownHold':p.get('knownHold'),'candidate':{'sha256':asset['sha256'],'asset':asset['path'],'assetKind':asset['kind'],'hashKind':asset.get('hashKind','exact compressed asset SHA256')},'sourceHashes':asset.get('sourceHashes'),'sourceEvidence':asset})
 byuid={r['uid']:r for r in rows};landmarks=[]
 for lid,reg in sorted(registry.items()):
  p=pre[lid];members=sorted(set(p['members']));effective=[uid for uid in members if uid not in centre];known=[byuid[uid]for uid in effective if uid in byuid];missing=[uid for uid in effective if uid not in byuid]
  dependencies=set();front=list(effective)
  while front:
   uid=front.pop();m=live.get(uid)
   if not m:continue
   for item in m.get('supportDependencies',[]):
    if isinstance(item,dict)and item.get('state')in['candidate','installed']and item['uid']not in dependencies and item['uid']not in effective:dependencies.add(item['uid']);front.append(item['uid'])
  contextual=[r['uid']for r in rows if lid in r['relatedLandmarkIds']and r['uid']not in dependencies and r['uid']not in effective]
  full=bool(known)and not missing and all(r['nativeInstalled']for r in known)
  allverified=full and all(r['installedVerified']for r in known)
  status=('known-native-parts-installed-awaiting-assembly-signoff'if allverified else 'known-native-parts-installed-review-outstanding'if full else 'partial-known-native-coverage'if any(r['nativeInstalled']for r in known)else 'prepared-or-source-held-no-known-native-parts'if known else 'named-identity-unresolved')
  routes=sorted(set(x for r in known for x in r['routes']))
  if p['identityState']=='proposed-identity-overlay':routes.append('confirm-proposed-named-landmark-membership')
  if not p['componentMembershipComplete']:routes.append('prove-whole-landmark-component-closure')
  if any(uid in centre for uid in members):routes.append('resolve-osm-glass-component-overlap')
  if contextual:routes.append('assess-discovered-support-candidates-with-owning-agent')
  if missing:routes.append('resolve-registry-member-absent-from-inventory')
  if not known:routes.append('map-interior-venue-to-host-building'if reg.get('kind')=='interior-venue'else'resolve-named-landmark-source-identity')
  landmarks.append({'id':lid,'name':reg['name'],'kind':reg.get('kind','building'),'status':status,'wholeLandmarkReady':False,'wholeLandmarkReadinessBasis':'No aggregate architectural/component closure approval is inferred from source-part installation.','componentMembershipComplete':p['componentMembershipComplete'],'identityState':p['identityState'],'registryMemberUIDs':members,'effectiveGovernmentMemberUIDs':effective,'excludedOSMComponentUIDs':[uid for uid in members if uid in centre],'missingInventoryUIDs':missing,'knownNativeParts':len(known),'installedKnownParts':sum(r['nativeInstalled']for r in known),'verifiedInstalledKnownParts':sum(r['installedVerified']for r in known),'installedKnownPartPercent':round(100*sum(r['nativeInstalled']for r in known)/len(known),2)if known else None,'requiredNativeSupportUIDs':sorted(dependencies),'discoveredSupportCandidateUIDs':sorted(contextual),'partRoutes':{r['uid']:r['routes']for r in known if r['routes']},'routes':sorted(set(routes)),'identityEvidence':{k:identity.get(lid,{}).get(k)for k in ['missingDiscoveryNumbers','nearbyUnassignedNames','componentScope','aliasEvidence']},'sourceReferences':reg.get('sources',[]),'unapprovedIdentityCandidates':[{'uid':c.get('uid'),'name':c.get('name'),'decision':c.get('decision'),'nativeCatalogueListed':c.get('uid') in live,'inReviewInventory':c.get('uid')in parts}for c in identity.get(lid,{}).get('weakCandidates',[])]})
 oldSnapshot=hashlib.sha256(canonical(sorted((p['uid'],p['candidate']['sha256'])for p in supplement))).hexdigest()[:16]
 save(DOC/'existing-133-source-supplement.json',{'snapshotId':oldSnapshot,'issue':'HKS-214','parts':supplement,'hashPolicy':'Native catalogue entries use exact gzip SHA256. Three embedded models use canonical modelGeometry JSON SHA256 with source hashes retained separately. Never substitute the whole tile hash for a model hash.','previousSnapshotUnmodified':a.snapshot,'databaseWrites':0})
 routes=collections.defaultdict(list)
 for r in rows:
  for route in r['routes']:routes[route].append(r['uid'])
 summary={'registeredLandmarks':213,'sourcePartsInCurrentSnapshot':len(rows),'originalNamedSourceParts':len(d['preflight']['parts']),'additionalSupportParts':sum(not r['landmarkIds']for r in rows),'nativeInstalledParts':sum(r['nativeInstalled']for r in rows),'installedVerifiedParts':sum(r['installedVerified']for r in rows),'formallyWholeLandmarkReady':0,'landmarkStatusCounts':dict(collections.Counter(r['status']for r in landmarks)),'original133':{'count':len(old),'catalogueNative':sum(bool(r['asset']and r['asset']['kind']=='native-catalogue')for r in old),'embeddedNative':sum(bool(r['asset']and r['asset']['kind']=='embedded-native-geometry')for r in old),'placementFlagTrue':sum(bool(r['asset']and r['asset']['placementReviewed'])for r in old),'missingPlacementFlag':sum(bool(r['asset']and not r['asset']['placementReviewed'])for r in old),'ledgerUnverified':sum(not r['installedVerified']for r in old)},'CentreOSMFacadeComponents':len(centre),'routeCounts':{k:len(v)for k,v in sorted(routes.items())}}
 report={'issue':'HKS-214','reviewSnapshot':a.snapshot,'auditVersion':1,'summary':summary,'landmarks':landmarks,'parts':rows,'routing':dict(sorted(routes.items())),'inputHashes':inputs,'limits':['Runtime installed means referenced by current viewer manifest with verified local asset bytes, not currently visible in camera or production deployment.','Known UID completion is not whole-landmark geometry completion; unnamed/omitted annexes remain outside a proven closed membership set.','Discovered support candidates are context only until reviewed dependency membership is explicit.','Eight Center OSM glass components are excluded from government-building denominator but retained for overlap/identity resolution; no deletions or aliases are performed.','Original source/terrain geometry and1x elevations are unmodified.']}
 report['auditId']=hashlib.sha256(canonical({'inputs':inputs,'summary':summary})).hexdigest()[:16];save(DOC/'report.json',report);save(DOC/'existing-133.json',old)
 lines=['# Landmark routing index','',f"Audit `{report['auditId']}`; frozen Neon capture `{d['neon']['capturedAt']}`. Counts are known native components, not whole-landmark approval.",'','| Landmark | Native installed / known | Installed and verified | Next state |','|---|---:|---:|---|']
 for l in landmarks:lines.append(f"| {l['name'].replace('|','/')} | {l['installedKnownParts']}/{l['knownNativeParts']} | {l['verifiedInstalledKnownParts']} | {l['status']} |")
 (DOC/'landmarks.md').write_text('\n'.join(lines)+'\n')
 # Repeatable routing priority, deliberately no blind physical approval.
 anchors=['ifc','bank-of-china','hsbc','central-plaza','icc','tall-the-center','cheung-kong-centre','space-museum','cultural-centre']
 order={lid:i for i,lid in enumerate(anchors)};eligible=[r for r in old if r['asset']and r['asset']['kind']=='native-catalogue'and not r['asset']['placementReviewed']]
 eligible.sort(key=lambda r:(min((order.get(lid,999)for lid in r['landmarkIds']),default=999),r['uid']))
 batch=eligible[:12];save(DOC/'existing-review-batch.json',{'issue':'HKS-214','scope':'First12 existing native source parts lacking placement flag; prioritise known central landmarks, then deterministic UID. Claim a source lease before new source/visual review. No approval inferred.','assetSnapshot':oldSnapshot,'parts':[{'uid':r['uid'],'name':r['name'],'landmarkIds':r['landmarkIds'],'asset':r['asset']}for r in batch]})
 # Catch files changing during parallel integration; frozen Neon is refreshed explicitly.
 for p,h in inputs.items():assert sha(ROOT/p)==h,'Input changed during audit; rerun: '+p
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
