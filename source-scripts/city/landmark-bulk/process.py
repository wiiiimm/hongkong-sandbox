#!/usr/bin/env python3
"""HKS-211: deterministic, retained-cache-only landmark preparation; never publishes."""
import argparse, collections, hashlib, json, math, pathlib, re, sqlite3, sys, time, unicodedata
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DB=ROOT/'source-scripts/city/building-batch/local/buildings.sqlite'
DOC=ROOT/'docs/astra-city/landmark-bulk'
sys.path.insert(0,str(ROOT/'source-scripts/city/building-batch'))
import selection,cached_models
NAME='landmark-bulk-hks211-v1'
def load(p): return json.loads(p.read_text())
def save(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normal(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c)).replace('centre','center')
 return tuple(sorted(str(int(w)) if w.isdigit() else w for w in re.findall(r'[a-z0-9]+',s) if w!='the'))
def discover():
 regpath=ROOT/'source-scripts/city/landmark-registry/landmarks.json';registry=load(regpath)
 c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);c.row_factory=sqlite3.Row
 buildings={r['uid']:dict(r) for r in c.execute('SELECT * FROM buildings WHERE active=1 ORDER BY uid')}
 detailed={r[0] for r in c.execute('SELECT DISTINCT uid FROM models')}
 named=[b for b in buildings.values() if b['name']];norm=collections.defaultdict(list)
 for b in named:norm[normal(b['name'])].append(b)
 rows=[];groups=[]
 audited=load(ROOT/'source-scripts/city/architecture-batch/taikwun-audit.json')['groups']
 for item in registry['landmarks']:
  matches={u:buildings[u] for u in item.get('sourceUidHints',[]) if u in buildings};basis={u:'registry-source-uid' for u in matches}
  patterns=[re.compile('^'+re.escape(p.casefold()).replace('%','.*').replace('_','.')+'$') for p in sorted(set(item.get('inventoryNamePatterns',[])))]
  for b in named:
   if any(p.match(b['name'].casefold()) for p in patterns):matches[b['uid']]=b;basis.setdefault(b['uid'],'declared-name-pattern')
  # Exact token multiset only: spelling, punctuation, token order and numeric zero padding.
  # No fuzzy substring, proximity-only identity, inferred coordinates or grouped tower expansion.
  if not matches:
   for name in [item['name']]+[p for p in item.get('inventoryNamePatterns',[]) if '%' not in p and '_' not in p]:
    for b in norm.get(normal(name),[]):matches[b['uid']]=b;basis[b['uid']]='exact-normalised-name-tokens'
  if item['id'] in audited:
   membership=audited[item['id']]['uids'];matches={u:buildings[u] for u in membership if u in buildings};basis={u:'existing-HKS-208-compound-audit' for u in matches}
  for u,b in list(matches.items()):
   if u in item.get('excludedSourceUids',[]) or b['name'] in item.get('excludedNames',[]):matches.pop(u)
  span=max((math.hypot(a['x']-b['x'],a['z']-b['z']) for a in matches.values() for b in matches.values()),default=0)
  scope=item.get('kind')=='interior-venue'
  ambiguous=span>1000 and not item.get('sourceUidHints')
  parts=[dict(uid=u,name=b['name'],csuid=b['csuid'],objectId=b['object_id'],x=b['x'],z=b['z'],identityBasis=basis[u],alreadyDetailed=bool(b['embedded'] or u in detailed)) for u,b in sorted(matches.items())]
  row=dict(id=item['id'],name=item['name'],origin=item['origin'],kind=item.get('kind','building'),parts=parts,missingHintUids=[u for u in item.get('sourceUidHints',[]) if u not in buildings],candidateSpanMetres=round(span,3),identityHold='historical-interior-host-unverified' if scope else 'same-name-candidates-over-1000m-apart' if ambiguous else None,discoveryStatus=item.get('status'),registryNote=item.get('note'),sources=item.get('sources',[]),discoveryMeasurements=item.get('discoveryMeasurements',[]))
  rows.append(row)
  if parts and not scope and not ambiguous:groups.append(dict(id=item['id'],title=item['name'],records=[{k:p[k] for k in ('uid','objectId','csuid','name')} for p in parts]))
 c.close()
 config=dict(name=NAME,issue='HKS-211',areas=[],landmarks=groups,coordinatePolicy='Native source 1x / HKPD. Discovery measurements are never model dimensions.',networkRequests=0)
 save(HERE/'selection-config.json',config)
 save(HERE/'identity-ledger.json',dict(schemaVersion=1,registrySHA256=sha(regpath),registryEntries=len(rows),rows=rows))
 return config,rows

def report(rows,plan=None,run=None):
 queue=load(ROOT/'source-scripts/city/architecture-followup/queue.json');holds={x['uid']:dict(issue='HKS-209',**x) for x in queue['items']}
 prior=load(ROOT/'docs/astra-city/landmark-pass/screening.json')['held']
 for uid,reason in prior.items():holds.setdefault(uid,dict(issue='HKS-202',uid=uid,classification='known-native-placement-hold',reason=reason))
 c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);c.row_factory=sqlite3.Row
 inventoryStats=dict(activeForms=c.execute('SELECT count(*) FROM buildings WHERE active=1').fetchone()[0],detailedForms=c.execute('SELECT count(*) FROM buildings b WHERE active=1 AND (embedded=1 OR EXISTS(SELECT 1 FROM models m WHERE m.uid=b.uid))').fetchone()[0])
 jobs={r['uid']:dict(r) for r in c.execute('SELECT j.* FROM batch_jobs j JOIN batch_job_sets s ON s.id=j.id WHERE s.name=?',(NAME+':cached-models',))};c.close()
 validation_path=HERE/'compact/validation.json';validation=load(validation_path) if validation_path.exists() else None
 if validation:
  assert {r['uid'] for r in validation['results']}=={r['uid'] for r in load(HERE/'compact/catalogue.json')['models']}, 'Validation stale: rerun the shared validator'
 checks={x['uid']:x for x in (validation or {}).get('results',[])}
 for row in rows:
  states=[]
  for p in row['parts']:
   job=jobs.get(p['uid']);r=json.loads(job['result']) if job and job['result'] else {};outcome=r.get('outcome')
   p.update(outcome=outcome,jobId=job['id'] if job else None,jobStatus=job['status'] if job else None,stagedAsset=r.get('record',{}).get('asset'),sourceModelId=r.get('record',{}).get('modelId'),sha256=r.get('record',{}).get('sha256'),placementApproved=False,validation=checks.get(p['uid']))
   if p['uid'] in holds:p['knownHold']=holds[p['uid']];state='known-placement-holds'
   elif p['alreadyDetailed']:state='already-detailed'
   elif row['identityHold']:state='nonbuilding-scope' if row['kind']=='interior-venue' else 'ambiguous'
   elif 'record' in r:state='candidates-staged'
   elif outcome in ('not-in-retained-staged-models',):state='cache-absent'
   elif outcome=='no-government-identity':state='no-identity'
   elif outcome in ('multiple-source-model-identities','multiple-official-footprint-matches','ambiguous-building-components','conflicting-same-revision-source-bytes','current-footprint-match-failed'):state='ambiguous'
   else:state='processing-exception'
   p['state']=state;states.append(state)
  if row['kind']=='interior-venue':row['state']='nonbuilding-scope'
  elif row['identityHold']:row['state']='ambiguous'
  elif not states:row['state']='no-identity'
  else:row['state']=next(x for x in ['known-placement-holds','processing-exception','ambiguous','cache-absent','no-identity','candidates-staged','already-detailed'] if x in states)
  row['partStateCounts']=dict(collections.Counter(states));row['completeLandmark']=False
 unique={p['uid']:p for row in rows for p in row['parts']}
 catalogue=load(HERE/'compact/catalogue.json');externalCompact={}
 for path in sorted(ROOT.glob('source-scripts/city/*/compact/catalogue.json')):
  if path.parent==HERE/'compact':continue
  for model in load(path).get('models',[]):
   externalCompact.setdefault((model.get('uid'),model.get('sha256')),[]).append(str(path.relative_to(ROOT)))
 reusedFromOtherPasses=[dict(uid=m['uid'],sha256=m['sha256'],catalogues=externalCompact[(m['uid'],m['sha256'])]) for m in catalogue['models'] if (m['uid'],m['sha256']) in externalCompact]
 files=list(HERE.rglob('*'));size=sum(p.stat().st_size for p in files if p.is_file())
 result=dict(schemaVersion=1,issue='HKS-211',scope='All registry entries accounted; staged preparation only. No landmark/region or publication approval.',registryEntries=len(rows),inventory=inventoryStats,separateFeatureTargets=[dict(x,state='nonbuilding-scope',includedIn213=False) for x in load(ROOT/'source-scripts/city/landmark-registry/landmarks.json')['featureTargets']],entryStates=dict(collections.Counter(r['state'] for r in rows)),uniqueIdentityParts=len(unique),partStates=dict(collections.Counter(p['state'] for p in unique.values())),stagedModels=sum(bool(p.get('stagedAsset')) for p in unique.values()),knownArchitectureQueue=dict(issue='HKS-209',items=len(queue['items']),representedUids=sorted({x['uid'] for x in queue['items']}&set(unique))),priorLandmarkHolds=prior,externalCompactReuse=dict(models=len(reusedFromOtherPasses),records=reusedFromOtherPasses),compressedModelBytes=sum(m['bytes'] for m in catalogue['models']),outputBytesAtReport=size,limitBytes=128*1024**2,workers=2,aiCallsDuringProcessing=0,networkRequests=0,newPublishedModels=0,plan=plan or load(HERE/'plan.json'),run=run or load(HERE/'compact/report.json'),validationSummary={k:v for k,v in (validation or {}).items() if k not in ['results','inputHashes']},inputHashes={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'source-scripts/city/landmark-registry/landmarks.json',ROOT/'source-scripts/city/architecture-followup/queue.json',ROOT/'source-scripts/city/architecture-batch/taikwun-audit.json',ROOT/'docs/astra-city/landmark-pass/screening.json',HERE/'selection-config.json',HERE/'process.py']},rows=rows)
 save(HERE/'bulk-report.json',result);save(DOC/'bulk-report.json',result)
 lines=['# Retained-cache landmark bulk preparation — HKS-211','',result['scope'],'',f"All {len(rows)} registry entries were processed. {len(unique)} unique identified source parts; {result['stagedModels']} staged candidates. Zero downloads and zero published replacements.",'','Entry status takes the most restrictive remaining component state; part counts preserve mixed progress. Already detailed means a reference exists, not architectural approval. Historical interiors retain unverified host identities. Name token normalisation never assigns coordinates, expands tower ranges or changes source heights. Same-name sites more than 1 km apart remain ambiguous. Cache absence describes retained staged inputs, not government availability. All 16 HKS-209 queue items and the prior Ngong Ping pagoda hold remain unapproved. Two separate infrastructure/landscape targets are reported outside the 213-entry denominator.','','| State | Entries |','|---|---:|']+[f'| {k} | {v} |' for k,v in sorted(result['entryStates'].items())]
 lines+=['','## Reproduce / resume','','```sh','/tmp/astra-city-venv/bin/python source-scripts/city/landmark-bulk/process.py run','/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/landmark-bulk/compact --out source-scripts/city/landmark-bulk/compact/validation.json','/tmp/astra-city-venv/bin/python source-scripts/city/landmark-bulk/process.py report','```','','Source matching, decoding, exact packing and resumable SQLite jobs reuse building-batch code. Native 1× geometry, source hashes and HKPD are retained. The script reserves 8 MiB of the 128 MiB output ceiling for reports. Resource/failed/deferred jobs remain explicit and are never accepted implicitly. Browser placement and source-component review precede any publication.','']
 (DOC/'README.md').write_text('\n'.join(lines))
 assert len(rows)==213 and len({r['id'] for r in rows})==213
 assert sum(result['entryStates'].values())==213
 assert size<128*1024**2
 print(json.dumps({k:v for k,v in result.items() if k not in ['rows','inputHashes','validationSummary']},indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['run','report']);a=p.parse_args()
 if a.command=='run':
  config,rows=discover();s,_=selection.select(DB,config);save(HERE/'selection.json',s)
  old_validation=HERE/'compact/validation.json'
  if old_validation.exists():old_validation.unlink()
  plan=cached_models.prepare(DB,ROOT,NAME);save(HERE/'plan.json',plan)
  run=cached_models.run_stage(DB,ROOT,HERE/'compact',NAME,workers=2,limit=10000,max_output_bytes=120*1024**2)
  used={x['asset'] for x in load(HERE/'compact/catalogue.json')['models']}
  for asset in (HERE/'compact').glob('*.glb.gz'):
   if asset.name not in used:asset.unlink()
  report(rows,plan,run)
 else:report(load(HERE/'identity-ledger.json')['rows'])
if __name__=='__main__':main()
