"""HKS-214 mechanical preparation: immutable cached inputs -> exhaustive modelling queue.
No network, database writes, geometry edits, GPU calls or publication.
"""
import argparse,collections,hashlib,json,pathlib,shutil,time,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/landmark-preflight'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def unique(rows,key='uid'):
 out={}
 for row in rows:
  assert row[key] not in out,'Duplicate '+key+': '+row[key]
  out[row[key]]=row
 return out
def support_hints(target,others):
 """Native bounding-box hints only; never claim supporting triangle proof."""
 a,b=target['worldBounds'];out=[]
 for other in others:
  if other['uid']==target['uid']:continue
  c,d=other['worldBounds'];area=max(0,min(b[0],d[0])-max(a[0],c[0]))*max(0,min(b[2],d[2])-max(a[2],c[2]))
  if area and abs(a[1]-d[1])<=2:
   out.append({'uid':other['uid'],'modelId':other['modelId'],'xzBoundingBoxOverlapM2':round(area,3),'topToBottomDifferenceM':round(a[1]-d[1],3),'evidence':'native-bounds-only','supportVerified':False})
 return sorted(out,key=lambda r:r['uid'])
def classify(part,cpu,acquisition_hold=None,source_progress=None):
 state=part['state'];known=part.get('knownHold');tags=[];actions=[]
 if state=='already-detailed':tags.append('already-detailed-not-region-signoff');actions.append('Retain published model; review only as assembly context.')
 elif state=='no-government-identity':tags.append('no-government-identity');actions.append('Resolve an exact government identity; preserve baseline geometry.')
 elif acquisition_hold:tags.append('exact-reference-identity-or-footprint-mismatch');actions.append('Review acquired exact reference against CSUID and footprint; do not relax matching thresholds.')
 elif state!='candidate-staged':
  if source_progress=='exact-source-absent-in-checked-sheets':tags.append('exact-source-absent-in-checked-sheets');actions.append('Review source revision or alternative exact component; checked-sheet absence is not dataset-wide absence.')
  elif source_progress=='acquisition-pending':tags.append('acquisition-pending');actions.append('Finish bounded exact-source download and directory accounting before modelling.')
  else:tags.append('exact-model-not-in-retained-cache');actions.append('Complete bounded exact-source acquisition/directory accounting; cache absence is not dataset-wide absence.')
 if known:tags.append('known-placement-or-source-hold');actions.append(known.get('nextAction')or known.get('reason')or 'Resolve the recorded source/placement hold before browser acceptance.')
 if state=='candidate-staged':
  if not cpu or cpu['outcome']=='validation-exception':tags.append('runtime-validation-exception');actions.append('Repair or inspect the recorded loader/picking/collision exception before visual review.')
  else:
   if 'sampled-highest-roof-below-terrain' in cpu['concerns']:tags.append('sampled-roof-occlusion');actions.append('Review source terrain and native roof intersections at fixed 1x.')
   if 'sampled-terrain-above-model-bottom' in cpu['concerns']:tags.append('foundation-burial-context');actions.append('Review lower native elevations against source terrain and retaining/support geometry.')
   if 'sampled-ground-gap-below-model-bottom' in cpu['concerns']:tags.append('elevated-component-support-context');actions.append('Review exact supporting triangles/podium membership; a bottom gap alone does not prove unsupported geometry.')
   if not cpu['concerns'] and not known:tags.append('cpu-clear-awaiting-visual-review');actions.append('Review source identity, architecture and assembly in the browser after preparation is complete.')
 if part.get('identityProposalGroups'):tags.append('proposed-landmark-membership-unapproved');actions.append('Confirm proposed landmark membership before treating the named source part as an accepted landmark replacement.')
 return tags,actions

def capture(args):
 source=ROOT/args.candidates;paths={'catalogue.json':source/'catalogue.json','validation.json':ROOT/args.validation,'stage-summary.json':ROOT/args.stage_summary,'identity.json':ROOT/args.identity,'progress.json':ROOT/args.progress,'acquisition.json':ROOT/args.acquisition}
 helper_path=ROOT/'source-scripts/city/landmark-progress/report.py';spec=importlib.util.spec_from_file_location('landmark_progress',helper_path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);_,acquisition_paths=helper.acquisition_records(ROOT)
 paths['progress-helper.py']=helper_path
 for path in acquisition_paths:
  batch=read(path);assert batch['completedTiles']==batch['sourceTiles'] and not batch['summary'].get('deferred',0),'Acquisition batch still in flight: '+str(path)
  paths['acquisition-reports/'+str(path.relative_to(ROOT/'docs/astra-city/landmark-acquisition'))]=path
 for rel,h in read(paths['progress.json'])['inputHashes'].items():assert sha(ROOT/rel)==h,'Progress input changed: '+rel
 v=read(paths['validation.json']);c=read(paths['catalogue.json']);models=unique(c['models']);assert len(models)==v['models'];assert set(models)==set(unique(v['results']))
 # Pin only evidence with internally current source/model/terrain hashes.
 for rel,h in v['hashes'].items():assert sha(ROOT/rel)==h,'Validation input changed: '+rel
 manifest=ROOT/'3d-viewer/city/data/manifest.json';paths['manifest.json']=manifest;paths['app.js']=ROOT/'3d-viewer/city/app.js'
 published=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;paths['published/'+path.parent.name+'-'+path.name]=path;published.extend(read(path)['models'])
 initial_hashes={k:sha(p)for k,p in paths.items()};identity=hashlib.sha256(json.dumps(initial_hashes,sort_keys=True).encode()).hexdigest()[:16];dest=HERE/'snapshots'/identity;dest.mkdir(parents=True,exist_ok=True)
 files={}
 for name,path in paths.items():
  target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert sha(target)==sha(path),'Immutable snapshot differs'
  else:shutil.copyfile(path,target)
  assert sha(target)==initial_hashes[name] and sha(path)==initial_hashes[name],'Input changed during snapshot: '+name
  files[name]={'source':str(path.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size}
 for m in models.values():
  path=source/m['asset'];assert sha(path)==m['sha256'] and path.stat().st_size==m['bytes'],'Asset hash/size mismatch'
  target=dest/'assets'/m['asset'];target.parent.mkdir(exist_ok=True)
  if target.exists():assert sha(target)==m['sha256']
  else:shutil.copyfile(path,target)
  files['assets/'+m['asset']]={'source':str(path.relative_to(ROOT)),'sha256':m['sha256'],'bytes':m['bytes']}
 save(dest/'published-models.json',{'models':published});files['published-models.json']={'source':'derived from pinned manifest catalogues','sha256':sha(dest/'published-models.json'),'bytes':(dest/'published-models.json').stat().st_size}
 pin={'id':identity,'files':files,'models':len(models),'cpuValidationInputHashes':v['hashes']};save(dest/'pin.json',pin);save(HERE/'snapshot.json',pin);return dest

def verify_snapshot(snapshot,pin):
 for name,entry in pin['files'].items():assert sha(snapshot/name)==entry['sha256'],'Snapshot changed: '+name

def run(snapshot):
 start=time.perf_counter();pin=read(snapshot/'pin.json');verify_snapshot(snapshot,pin)
 stage=read(snapshot/'stage-summary.json');identity=read(snapshot/'identity.json');validation=read(snapshot/'validation.json');models=unique(read(snapshot/'catalogue.json')['models']);cpus=unique(validation['results']);parts=unique(stage['parts']);landmarks=unique(stage['rows'],'id');identities=unique(identity['rows'],'id')
 assert set(landmarks)==set(identities) and len(landmarks)==stage['allRegistryEntries'];assert set(models)=={u for u,p in parts.items()if p['state']=='candidate-staged'}
 for uid,m in models.items():
  assert m['objectId']==parts[uid]['objectId'] and m['buildingCSUID']==parts[uid]['csuid'],'Staged source identity changed'
  assert m['sha256']==parts[uid]['sha256'] and m['modelId']==parts[uid]['modelId'],'Stage summary differs from model'
  if cpus[uid]['outcome']!='validation-exception':assert cpus[uid]['modelId']==m['modelId'],'CPU result model mismatch'
 progress=read(snapshot/'progress.json');source_progress={}
 for row in progress['rows']:
  for uid,state in row['sourceStates'].items():
   assert uid not in source_progress or source_progress[uid]==state,'Conflicting progress state';source_progress[uid]=state
 acquisition={}
 acquisition_paths=[snapshot/'acquisition.json']+list((snapshot/'acquisition-reports').glob('**/*.json'))
 for path in sorted(acquisition_paths,key=lambda p:(read(p).get('generatedAt',''),str(p))):
  for row in read(path)['rows']:acquisition[row['uid']]=dict(row,report=pin['files'][str(path.relative_to(snapshot))]['source'])
 memberships=collections.defaultdict(list)
 for row in landmarks.values():
  for uid in row['members']:assert uid in parts,'Unaccounted member';memberships[uid].append(row['id'])
 model_context={m['uid']:m for m in read(snapshot/'published-models.json')['models']};model_context.update(models)
 part_rows=[]
 for uid,p in sorted(parts.items()):
  cpu=cpus.get(uid);m=models.get(uid);tags,actions=classify(p,cpu,stage.get('acquisitionHolds',{}).get(uid),source_progress.get(uid));hints=support_hints(m,model_context.values())if m and 'elevated-component-support-context'in tags else []
  part_rows.append({'uid':uid,'name':p.get('name'),'landmarkIds':sorted(memberships[uid]),'sourceState':p['state'],'sourceProgress':source_progress.get(uid),'acquisitionEvidence':acquisition.get(uid),'csuid':p.get('csuid'),'objectId':p.get('objectId'),'identityProposalGroups':p.get('identityProposalGroups',[]),'classification':tags,'nextActions':actions,'knownHold':p.get('knownHold'),'acquisitionHold':stage.get('acquisitionHolds',{}).get(uid),'cpu':cpu,'collisionAndPicking':('passed-source-surface-sample'if cpu and cpu['outcome']!='validation-exception'else'not-established'),'candidate':m,'assemblyHints':hints,'assemblySupportVerified':False,'publicationApproved':False,'reviewEffort':('higher'if any(t in tags for t in ['known-placement-or-source-hold','foundation-burial-context','elevated-component-support-context','sampled-roof-occlusion','exact-reference-identity-or-footprint-mismatch'])else 'standard')})
 indexed={p['uid']:p for p in part_rows};landmark_rows=[]
 for ident,row in sorted(landmarks.items()):
  original=identities[ident];members=[indexed[u]for u in row['members']];tasks=[]
  if original['state']in ['identity-needs-review','no-supported-identity','historical-interior-host-unresolved','historical-source-conflict']:tasks.append('Resolve identity: '+original['state'])
  if not row['componentMembershipComplete']:tasks.append('Confirm full component membership; named towers do not establish unnamed podium/annexe completeness.')
  missing=[m['uid']for m in members if m['sourceState']not in ['candidate-staged','already-detailed']]
  if missing:tasks.append('Resolve missing/unmatched source parts before whole-landmark completion.')
  if original.get('missingDiscoveryNumbers'):tasks.append('Resolve absent numbered towers/components from the discovery list.')
  tasks.extend(sorted({a for m in members for a in m['nextActions']}))
  landmark_rows.append({'id':ident,'name':row['name'],'identityState':original['state'],'identityEvidence':{'componentScope':original.get('componentScope'),'sourceHints':original.get('sourceHints'),'missingDiscoveryNumbers':original.get('missingDiscoveryNumbers'),'weakCandidates':original.get('weakCandidates'),'rejectedCandidates':original.get('rejectedCandidates')},'members':row['members'],'sourceStateCounts':dict(collections.Counter(m['sourceState']for m in members)),'missingOrUnmatchedUIDs':missing,'componentMembershipComplete':row['componentMembershipComplete'],'checklist':tasks,'completeLandmark':False})
 report={'issue':'HKS-214','phase':'supporting-preparation','snapshotId':pin['id'],'registryEntries':len(landmark_rows),'sourceParts':len(part_rows),'stagedModels':len(models),'sourceProgressCounts':dict(collections.Counter(p['sourceProgress']for p in part_rows)),'sourceStateCounts':dict(collections.Counter(p['sourceState']for p in part_rows)),'classificationCounts':dict(collections.Counter(t for p in part_rows for t in p['classification'])),'parts':part_rows,'landmarks':landmark_rows,'inputHashes':{k:v['sha256']for k,v in pin['files'].items()},'validation':{k:validation[k]for k in ['models','checksPassed','exceptions','concerns','seconds','compressedBytes']},'resources':{'preflightSeconds':time.perf_counter()-start,'networkRequests':0,'downloadedBytes':0,'aiCallsInScript':0,'dbWrites':0,'gpuRuns':0},'limits':['Preparation is not modelling completion or publication approval.','Bounding-box assembly hints are not proof of supporting native triangles.','CPU picking/collision checks cover sampled source surfaces, not whole-campus walking/landing routes.','Cache absence is limited to the retained source snapshot.','Unresolved component membership remains explicit for every landmark.']}
 DOC.mkdir(exist_ok=True);save(DOC/'report.json',report);save(DOC/'snapshot.json',pin)
 queue={'issue':'HKS-214','snapshotId':pin['id'],'phase':'preparation-only','parts':[{'uid':p['uid'],'landmarks':p['landmarkIds'],'classification':p['classification'],'actions':p['nextActions'],'reviewEffort':p['reviewEffort'],'mayPublish':False}for p in part_rows],'landmarks':[{'id':r['id'],'members':r['members'],'checklist':r['checklist'],'complete':False}for r in landmark_rows]};save(DOC/'queue.json',queue)
 overview={k:report[k]for k in ['issue','phase','snapshotId','registryEntries','sourceParts','stagedModels','sourceStateCounts','sourceProgressCounts','classificationCounts','validation','resources','limits']};save(DOC/'summary.json',overview);print(json.dumps(overview,indent=2));return report

def main():
 p=argparse.ArgumentParser();p.add_argument('--capture',action='store_true');p.add_argument('--snapshot');p.add_argument('--candidates',default='source-scripts/city/landmark-identity/prepared');p.add_argument('--validation',default='docs/astra-city/landmark-identity/prepared-validation.json');p.add_argument('--stage-summary',default='docs/astra-city/landmark-identity/stage-summary.json');p.add_argument('--identity',default='source-scripts/city/landmark-identity/report.json');p.add_argument('--progress',default='docs/astra-city/landmark-progress/progress.json');p.add_argument('--acquisition',default='docs/astra-city/landmark-acquisition/report.json');a=p.parse_args()
 snapshot=capture(a)if a.capture else HERE/'snapshots'/(a.snapshot or read(HERE/'snapshot.json')['id']);run(snapshot)
if __name__=='__main__':main()
