#!/usr/bin/env python3
"""HKS-212 overlay-to-staging adapter. No source acquisition or publication."""
import argparse,collections,hashlib,json,os,pathlib,sqlite3,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/landmark-identity';OUT=HERE/'prepared';DB=ROOT/'source-scripts/city/building-batch/local/buildings.sqlite'
sys.path.insert(0,str(ROOT/'source-scripts/city/building-batch'))
import cached_models,selection
NAME='landmark-identity-hks212-preparation-v2'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def readonly():
 c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON');return c

def validate_overlay():
 overlay=read(HERE/'proposed-overlay.json');base=read(ROOT/'source-scripts/city/landmark-bulk/selection-config.json');identity=read(HERE/'report.json')
 assert overlay['status']=='identity-proposal-for-review-not-applied'
 assert len(identity['rows'])==213 and len({r['id'] for r in identity['rows']})==213
 for path,digest in overlay['provenance'].items():
  p=(ROOT/path).resolve();assert p.is_relative_to(ROOT) and sha(p)==digest,'Overlay evidence changed: '+path
 groups={g['id']:dict(g,records=list(g['records'])) for g in base['landmarks']};proposed={};replaced=[];c=readonly()
 try:
  for g in overlay['landmarks']:
   assert not g['publicationApproved'] and not g['evidence']['componentMembershipComplete']
   old=groups.get(g['id'],dict(id=g['id'],title=g['title'],records=[]))
   parts={} if g.get('replacePriorIdentity') else {p['uid']:p for p in old['records']}
   if g.get('replacePriorIdentity'):replaced.append(g['id'])
   proposed[g['id']]=set()
   for p in g['records']:
    b=c.execute('SELECT * FROM buildings WHERE uid=? AND active=1',(p['uid'],)).fetchone();assert b,'Missing active UID: '+p['uid']
    assert (b['object_id'],b['csuid'],b['name'])==(p['objectId'],p['csuid'],p['name']),'Identity changed: '+p['uid']
    for evidence in g['evidence']['governmentRecords']:
     if evidence['objectId']==p['objectId'] and evidence['csuid']==p['csuid']:
      assert evidence['retainedViewerInput']==b['input_path']
      inp=c.execute('SELECT sha256 FROM inputs WHERE path=?',(b['input_path'],)).fetchone();assert inp and inp[0]==evidence['inputSHA256']
      assert sha(ROOT/'3d-viewer'/b['input_path'])==evidence['inputSHA256'];break
    else:raise AssertionError('No exact input evidence for '+p['uid'])
    if p['uid'] in parts:assert parts[p['uid']]==p,'Conflicting duplicate UID in group'
    parts[p['uid']]=p;proposed[g['id']].add(p['uid'])
   groups[g['id']]=dict(id=g['id'],title=g['title'],records=[parts[u] for u in sorted(parts)])
  unique={}
  for g in groups.values():
   for p in g['records']:
    if p['uid'] in unique:assert unique[p['uid']]==p,'Conflicting duplicate UID across groups'
    b=c.execute('SELECT object_id,csuid,name FROM buildings WHERE uid=? AND active=1',(p['uid'],)).fetchone();assert b and tuple(b)==(p['objectId'],p['csuid'],p['name'])
    unique[p['uid']]=p
 finally:c.close()
 config=dict(name=NAME,issue='HKS-212',areas=[],landmarks=[groups[g] for g in sorted(groups)],identityApproved=False,placementApproved=False,sourceOverlaySHA256=sha(HERE/'proposed-overlay.json'),coordinatePolicy='Native1x/HKPD; identity overlay only. All model/placement holds retained.')
 holds={h['uid']:h for h in identity['higherEffortPlacementQueue']};assert len(holds)==17 and set(holds)<=set(unique)
 return config,identity,proposed,holds,dict(overlayEntries=len(overlay['landmarks']),selectedGroups=len(groups),uniqueSelectedUIDs=len(unique),replacePriorIdentityGroups=sorted(replaced),knownHolds=len(holds),inputSHA256={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'proposed-overlay.json',HERE/'report.json',ROOT/'source-scripts/city/landmark-bulk/selection-config.json',HERE/'stage_proposals.py']})

def summaries(config,identity,proposed,holds,verification,plan,run,validation,elapsed):
 c=readonly();jobs={r['uid']:dict(r) for r in c.execute('SELECT j.* FROM batch_jobs j JOIN batch_job_sets s ON j.id=s.id WHERE s.name=?',(NAME+':cached-models',))};detailed={r[0] for r in c.execute('SELECT uid FROM buildings b WHERE active=1 AND (embedded=1 OR EXISTS(SELECT 1 FROM models m WHERE m.uid=b.uid))')};c.close()
 cat=read(OUT/'catalogue.json');models={m['uid']:m for m in cat['models']};cpu={r['uid']:r for r in validation.get('results',[])};parts={};bygroup={g['id']:g for g in config['landmarks']}
 oldmodels={m['uid'] for m in read(ROOT/'source-scripts/city/landmark-bulk/compact/catalogue.json')['models']}
 for g in config['landmarks']:
  for p in g['records']:
   uid=p['uid'];j=jobs.get(uid);result=json.loads(j['result']) if j and j['result'] else {}
   state='already-detailed' if uid in detailed else 'candidate-staged' if uid in models else result.get('outcome',j['status'] if j else 'no-job')
   parts.setdefault(uid,dict(**p,state=state,jobStatus=j['status'] if j else None,modelId=models.get(uid,{}).get('modelId'),sha256=models.get(uid,{}).get('sha256'),identityProposalGroups=[],placementApproved=False,identityApproved=False,knownHold=holds.get(uid),cpu=cpu.get(uid),stagedBeforeIdentityPass=uid in oldmodels)).get('identityProposalGroups').extend([g['id']] if uid in proposed.get(g['id'],set()) else [])
 rows=[]
 for r in identity['rows']:
  members=[p['uid'] for p in bygroup.get(r['id'],{}).get('records',[])];rows.append(dict(id=r['id'],name=r['name'],identityState=r['state'],members=members,componentMembershipComplete=False,states=dict(collections.Counter(parts[u]['state'] for u in members)),heldUIDs=[u for u in members if u in holds],noSelectionReason=r['state'] if not members else None))
 acquisitionHolds={}
 for path in acquisition_reports():
  for r in read(path)['rows']:
   if r['models'] and not r['standardMatch']:
    acquisitionHolds.setdefault(r['uid'],dict(issue='HKS-213',reason='Exact reference acquired but conservative footprint/CSUID match failed; identity and placement remain held',reports=[],models=[]))
    acquisitionHolds[r['uid']]['reports'].append(str(path.relative_to(ROOT)))
    acquisitionHolds[r['uid']]['models'].extend(r['models'])
 for uid,part in parts.items():
  if uid in acquisitionHolds:part['acquisitionHold']=acquisitionHolds[uid]
 report=dict(schemaVersion=1,issue='HKS-212',selection=NAME,scope='Mechanical identity overlay preparation only; no publication, architectural acceptance or completed-region claim.',verification=verification,allRegistryEntries=len(rows),uniqueSelectedUIDs=len(parts),partStates=dict(collections.Counter(p['state'] for p in parts.values())),stagedModels=len(models),stagedInPriorBulk=len(set(models)&oldmodels),additionalStagedSincePriorBulk=len(set(models)-oldmodels),proposedIdentityStaged=len({u for us in proposed.values() for u in us}&set(models)),knownHolds=holds,acquisitionHolds=acquisitionHolds,knownHeldModelsStaged=sorted(set(holds)&set(models)),compressedModelBytes=sum(m['bytes'] for m in models.values()),workers=2,outputLimitBytes=128*1024**2,networkRequests=0,newPublishedModels=0,plan=plan,run=run,validation={k:v for k,v in validation.items() if k not in ['results','hashes']},seconds=round(elapsed,3),parts=[parts[u] for u in sorted(parts)],rows=rows)
 assert len(rows)==213 and sum(report['partStates'].values())==len(parts)
 assert not (set(models)&detailed),'Already detailed model was staged twice'
 write(OUT/'stage-summary.json',report);write(DOC/'stage-summary.json',report);write(DOC/'prepared-validation.json',validation)
 total=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());assert total<=128*1024**2,'Combined output budget exceeded'
 print(json.dumps({k:v for k,v in report.items() if k not in ['parts','rows','knownHolds','plan','run']},indent=2))

def acquisition_reports():
 base=ROOT/'docs/astra-city/landmark-acquisition'
 return [path for path in [base/'report.json']+sorted(base.glob('batches/*/report.json')) if 'completedTiles' in read(path) and 'rows' in read(path)]

def stable_acquisition():
 evidence=[]
 for report in acquisition_reports():
  verification=report.with_name('verification.json');v=read(verification)
  assert v['result']=='passed' and not v['errors'], 'Acquisition not verified: '+str(report)
  r=read(report);assert r['completedTiles']==r['sourceTiles'], 'Incomplete acquisition: '+str(report)
  evidence.append(dict(report=str(report.relative_to(ROOT)),reportSHA256=sha(report),verificationSHA256=sha(verification)))
 # Adapter links expose nested source batches to the unchanged cache scanner.
 # Links are local ignored intermediates. Published/source manifests stay untouched.
 staged=HERE/'staged';staged.mkdir(exist_ok=True)
 for path in staged.iterdir():
  assert path.is_symlink(), 'Unexpected non-symlink adapter member: '+str(path)
  path.unlink()
 for manifest in sorted((ROOT/'source-scripts/city/landmark-acquisition/batches').glob('*/staged/*/manifest.json')):
  target=manifest.parent;assert target.resolve().is_relative_to(ROOT)
  link=staged/(manifest.parents[2].name+'--'+target.name)
  link.symlink_to(os.path.relpath(target,staged),target_is_directory=True)
 return evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['check','run']);p.add_argument('--sources-stable',action='store_true',help='Required acknowledgement from coordinating acquisition agent/root before scanning staged manifests');p.add_argument('--node',default='/Users/williamli/.nvm/versions/node/v24.17.0/bin/node');a=p.parse_args();started=time.monotonic()
 config,identity,proposed,holds,verification=validate_overlay()
 if a.command=='check':print(json.dumps(verification,indent=2));return
 if not a.sources_stable:p.error('Wait for acquisition/root confirmation, then supply --sources-stable')
 verification['stableAcquisition']=stable_acquisition()
 write(OUT/'selection-config.json',config);s,_=selection.select(DB,config);assert not s['exceptions'];write(OUT/'selection.json',s)
 plan=cached_models.prepare(DB,ROOT,NAME);write(OUT/'plan.json',plan)
 run=cached_models.run_stage(DB,ROOT,OUT,NAME,workers=2,limit=10000,max_output_bytes=120*1024**2);write(OUT/'run.json',run)
 allproposed={u for us in proposed.values() for u in us}
 for name in ['catalogue.json']+read(OUT/'catalogue-index.json')['catalogues']:
  catalogue=read(OUT/name)
  for m in catalogue['models']:
   assert m.get('placementReviewed') is False
   if m.get('sourceManifest'):m['sourceManifest']=str((ROOT/m['sourceManifest']).resolve().relative_to(ROOT))
   m.update(identityReviewApproved=False,proposedIdentity=m['uid'] in allproposed,knownPlacementHold=holds.get(m['uid']),publicationApproved=False)
  write(OUT/name,catalogue)
 used={m['asset'] for m in read(OUT/'catalogue.json')['models']}
 for asset in OUT.glob('*.glb.gz'):
  if asset.name not in used:asset.unlink()
 previous_validation=OUT/'validation.json'
 if previous_validation.exists():previous_validation.unlink()
 check=subprocess.run([a.node,str(ROOT/'source-scripts/city/building-batch/validate_candidates.mjs'),'--candidates',str(OUT),'--out',str(OUT/'validation.json')],cwd=ROOT,capture_output=True,text=True)
 assert (OUT/'validation.json').exists(),check.stderr
 validation=read(OUT/'validation.json');assert {r['uid'] for r in validation['results']}=={m['uid'] for m in read(OUT/'catalogue.json')['models']},'Stale/incomplete validation'
 summaries(config,identity,proposed,holds,verification,plan,run,validation,time.monotonic()-started)
 if check.returncode:sys.exit(check.returncode)
if __name__=='__main__':main()
