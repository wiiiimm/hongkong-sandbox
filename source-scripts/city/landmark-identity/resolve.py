#!/usr/bin/env python3
"""Read-only identity proposals from retained government names and sourced coordinates."""
import collections,hashlib,json,math,pathlib,re,sqlite3,time,unicodedata
from pyproj import Transformer
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/landmark-identity'
DB=ROOT/'source-scripts/city/building-batch/local/buildings.sqlite'
def read(p):return json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c)).replace('centre','center').replace('metro town','metrotown').replace('silver sea','silversea').replace('clear water','clearwater')
 s=re.sub(r'^lohas park phase [0-9]+[a-z]?\s+','',s);s=re.sub(r'\bphase [0-9]+[a-z]?\s*','',s)
 return tuple(sorted(str(int(w)) if w.isdigit() else w for w in re.findall(r'[a-z0-9]+',s) if w not in ('the','tower','towers','block','blocks','hotel')))
def variants(name):
 # Ranges are literal discovery claims, not permission to invent towers or skip4.
 m=re.search(r'(?P<ns>\d+(?:\s*[–−-]\s*\d+)?(?:\s*,\s*\d+)*)$',name)
 if not m:return [(name,None)],[]
 suffix=m['ns'];prefix=name[:m.start()];numbers=[]
 for term in suffix.split(','):
  ends=re.split(r'[–−-]',term)
  if len(ends)==2:numbers+=list(range(int(ends[0]),int(ends[1])+1))
  else:numbers.append(int(term))
 if len(numbers)==1:return [(name,numbers[0])],numbers
 return [(prefix+str(n),n) for n in numbers],numbers

def main():
 started=time.monotonic();regpath=ROOT/'source-scripts/city/landmark-registry/landmarks.json';reg=read(regpath);priorpath=ROOT/'source-scripts/city/landmark-bulk/bulk-report.json';prior={r['id']:r for r in read(priorpath)['rows']}
 c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON')
 buildings={b['uid']:dict(b) for b in c.execute('SELECT uid,name,csuid,object_id,x,z,source_dataset,structure_type,source_base,source_top,embedded,input_path FROM buildings WHERE active=1 ORDER BY uid')}
 detailed={r[0] for r in c.execute('SELECT uid FROM models')};names=collections.defaultdict(list)
 subtowers=collections.defaultdict(list);wholegroups=collections.defaultdict(list)
 for b in buildings.values():
  if b['name']:
   names[tokens(b['name'])].append(b)
   if re.search(r'\b(?:tower|block) \d+[ab]$',b['name'],re.I):subtowers[tokens(re.sub(r'([0-9])[ab]$',r'\1',b['name'],flags=re.I))].append(b)
   if re.search(r'\b(?:tower|block) \d+[ab]?$',b['name'],re.I):wholegroups[tokens(re.sub(r'\b(?:tower|block) \d+[ab]?$', '',b['name'],flags=re.I))].append(b)
 inputHashes=dict(c.execute('SELECT path,sha256 FROM inputs'));sourceGeneration=c.execute("SELECT value FROM settings WHERE key='source_manifest_sha256'").fetchone()[0]
 project=Transformer.from_crs(4326,2326,always_xy=True);inverse=Transformer.from_crs(2326,4326,always_xy=True)
 c.close();rows=[];overlay=[]
 for item in reg['landmarks']:
  old=prior[item['id']];hints=[dict(point=d['locationHintWGS84'],source=d['source'],sourceRow=d.get('sourceRow')) for d in item.get('discoveryMeasurements',[]) if d.get('locationHintWGS84')]
  for h in hints:e,n=project.transform(*h['point']);h['localGrid']=[e-834500,816500-n]
  def distance(b):return min((math.hypot(b['x']-h['localGrid'][0],b['z']-h['localGrid'][1]) for h in hints),default=None)
  candidates={};expected=[];matched_numbers=set()
  for label in [item['name']]+[p for p in item.get('inventoryNamePatterns',[]) if '%' not in p and '_' not in p]:
   vs,nums=variants(label);expected+=nums
   for variant,num in vs:
    options=names.get(tokens(variant),[])+subtowers.get(tokens(variant),[])
    if not nums:options+=wholegroups.get(tokens(variant),[])
    for b in options:
     if b['uid'] in item.get('excludedSourceUids',[]) or b['name'] in item.get('excludedNames',[]):continue
     candidates[b['uid']]=dict(b,matchBasis='exact-canonical-name-and-sourced-location',distanceMetres=distance(b),discoveryNumber=num)
  # Preserve previous explicit component identities; geographic filters only revise held/name-only discovery.
  for p in old['parts']:
   if p['uid'] in buildings:candidates.setdefault(p['uid'],dict(buildings[p['uid']],matchBasis=p['identityBasis'],distanceMetres=distance(buildings[p['uid']]),discoveryNumber=None))
  accepted=[];rejected=[];weak=[]
  has_prior=bool(old['parts']) and old['state']!='ambiguous'
  prior_uids={p['uid'] for p in old['parts']}
  for uid,b in sorted(candidates.items()):
   d=b['distanceMetres'];b['alreadyDetailed']=bool(b['embedded'] or uid in detailed)
   b['governmentEvidence']=dict(sourceDataset=b['source_dataset'],objectId=b['object_id'],csuid=b['csuid'],retainedViewerInput=b['input_path'],inputSHA256=inputHashes.get(b['input_path']),layer='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0')
   b['geographicEvidence']='retained source coordinate hint; government named footprint validates local identity, not source availability'
   if has_prior and uid in prior_uids:
    b['decision']='retained-prior-identity';accepted.append(b)
   elif d is not None and d<=250 and b['source_dataset']=='landsd-territory' and b['csuid']:
    b['decision']='proposed-name-plus-geography';accepted.append(b)
   elif d is not None and d>250:
    b['decision']='rejected-outside-sourced-location';rejected.append(b)
   else:b['decision']='needs-independent-location-or-government-identity';weak.append(b)
  for b in accepted:
   if b['discoveryNumber'] is not None:matched_numbers.add(b['discoveryNumber'])
  expected=sorted(set(expected));missing=sorted(set(expected)-matched_numbers) if len(expected)>1 else []
  old_uids={p['uid'] for p in old['parts']};new_uids={p['uid'] for p in accepted};changed=new_uids!=old_uids
  status='proposed-identity-overlay' if accepted and changed else 'retained-prior-identity' if accepted else 'identity-needs-review' if weak or rejected else 'no-supported-identity'
  if item.get('kind')=='interior-venue':status='historical-interior-host-unresolved';accepted=[]
  # Nearby names are evidence for follow-up, never proximity-only acceptance.
  nearby=[]
  if hints and not accepted:
   nearby=sorted((dict(uid=b['uid'],name=b['name'],csuid=b['csuid'],distanceMetres=round(distance(b),3)) for b in buildings.values() if b['name'] and abs(b['x']-hints[0]['localGrid'][0])<350 and abs(b['z']-hints[0]['localGrid'][1])<350),key=lambda b:(b['distanceMetres'],b['uid']))[:12]
  row=dict(id=item['id'],name=item['name'],priorState=old['state'],state=status,sourceHints=hints,proposedParts=accepted,rejectedCandidates=rejected,weakCandidates=weak,nearbyUnassignedNames=nearby,expectedDiscoveryNumbers=expected,missingDiscoveryNumbers=missing,componentMembershipComplete=False,componentScope='Preserves all previously assigned source parts; new named towers only. Unnamed podium/annexe membership requires source support, not proximity.',identityOnly=True,placementApproved=False,knownHolds=[p['knownHold'] for p in old['parts'] if p.get('knownHold')])
  rows.append(row)
  if accepted and changed and item.get('kind')!='interior-venue':overlay.append(dict(id=item['id'],title=item['name'],replacePriorIdentity=old['state']=='ambiguous',records=[dict(uid=b['uid'],objectId=b['object_id'],csuid=b['csuid'],name=b['name']) for b in accepted],evidence= dict(sourceHints=hints,canonicalRule='Punctuation/accent/case; optional Tower/Block/Hotel word; Metro Town/Silver Sea/Clear Water spacing; explicit phase-prefix removal; native numeric A/B subparts; no fuzzy edit distance.',componentMembershipComplete=False,missingDiscoveryNumbers=missing,governmentRecords=[b['governmentEvidence'] for b in accepted]),publicationApproved=False))
 report=dict(schemaVersion=1,issue='HKS-212',registryEntries=len(rows),seconds=round(time.monotonic()-started,3),networkRequestsDuringScript=0,aiCallsDuringScript=0,dbAccess='read-only',states=dict(collections.Counter(r['state'] for r in rows)),priorNoIdentityEntries=sum(r['priorState']=='no-identity' for r in rows),newlyProposedFromNoIdentity=sum(r['priorState']=='no-identity' and r['state']=='proposed-identity-overlay' for r in rows),ambiguitiesWithProposedGeographicResolution=sum(r['priorState']=='ambiguous' and r['state']=='proposed-identity-overlay' for r in rows),overlayEntries=len(overlay),newUniqueUidProposals=len({p['uid'] for r in rows for p in r['proposedParts']}-{p['uid'] for r in prior.values() for p in r['parts']}),inventorySourceGeneration=sourceGeneration,normalisationVersion=2,inputHashes={str(p.relative_to(ROOT)):sha(p) for p in [regpath,priorpath,HERE/'resolve.py']},rows=rows)
 proposal=dict(schemaVersion=1,name='landmark-identity-proposed-v1',issue=report['issue'],status='identity-proposal-for-review-not-applied',areas=[],landmarks=overlay,provenance=report['inputHashes'],coordinatePolicy='EPSG:4326 source hints projected through existing EPSG:2326 convention, origin834500/816500. No coordinates or model heights changed.')
 report['higherEffortPlacementQueue']=list({h['uid']:h for r in rows for h in r['knownHolds']}.values())
 report['referenceNotes']=read(HERE/'reference-notes.json')
 report['inputHashes'][str((HERE/'reference-notes.json').relative_to(ROOT))]=sha(HERE/'reference-notes.json')
 proposal['provenance']=report['inputHashes']
 write(HERE/'proposed-overlay.json',proposal);write(HERE/'report.json',report);write(DOC/'report.json',report)
 print(json.dumps({k:v for k,v in report.items() if k not in ['rows','inputHashes','referenceNotes','higherEffortPlacementQueue']},indent=2))
 assert len(rows)==213 and len({r['id'] for r in rows})==213
 assert all(p['source_dataset']=='landsd-territory' and p['csuid'] and p['distanceMetres']<=250 for r in rows for p in r['proposedParts'] if p['decision']=='proposed-name-plus-geography')
if __name__=='__main__':main()
