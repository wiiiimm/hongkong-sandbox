"""Independent read-only overlay invariants and matching-rule regressions."""
import hashlib,json,pathlib,sqlite3
from resolve import ROOT,HERE,DB,read,write,tokens,variants
r=read(HERE/'report.json');o=read(HERE/'proposed-overlay.json')
c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON')
assert r['registryEntries']==213 and len({x['id'] for x in r['rows']})==213
assert sum(r['states'].values())==213
assert len({x['id'] for x in o['landmarks']})==len(o['landmarks'])
for p,h in r['inputHashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
count=0
for g in o['landmarks']:
 assert not g['publicationApproved'] and not g['evidence']['componentMembershipComplete']
 assert len({x['uid'] for x in g['records']})==len(g['records'])
 for x in g['records']:
  b=c.execute('SELECT * FROM buildings WHERE uid=? AND active=1',(x['uid'],)).fetchone();assert b
  assert (b['object_id'],b['csuid'],b['name'])==(x['objectId'],x['csuid'],x['name']);count+=1
for row in r['rows']:
 for p in row['proposedParts']:
  b=c.execute('SELECT x,z FROM buildings WHERE uid=?',(p['uid'],)).fetchone();assert (b['x'],b['z'])==(p['x'],p['z'])
  if p['decision']=='proposed-name-plus-geography':assert p['distanceMetres']<=250 and p['csuid'] and p['governmentEvidence']['inputSHA256']
 if row['state']=='historical-interior-host-unresolved':assert not row['proposedParts']
assert tokens('Sorrento 1')==tokens('Sorrento Tower 1')
assert tokens('Sorrento 1')!=tokens('Villas Sorrento Tower 1')
assert tokens('Metro Town Tower 01')==tokens('Metrotown Tower 1')
assert tokens('LOHAS Park Phase 5A Malibu Tower 1')==tokens('Malibu Tower 1')
assert tokens('Wings at Sea II Tower 5')!=tokens('Wings at Sea Tower 5')
assert tokens('Tai Kwun')!=tokens('Tai Kwun Mansion')
assert variants('Grand Promenade 2–5')[1]==[2,3,4,5]
assert variants('LP6 Towers 1–3, 5')[1]==[1,2,3,5]
byid={x['id']:x for x in r['rows']}
assert all(p['distanceMetres']>250 for name in ['harbourside','central-plaza','tall-manhattan-heights'] for p in byid[name]['rejectedCandidates'])
assert 4 in byid['tall-grand-promenade-2-5']['missingDiscoveryNumbers']
c.close();result=dict(passed=True,registryEntries=213,overlayEntries=len(o['landmarks']),overlayRecords=count,checks=['all input hashes','exact active government UID/CSUID/objectId/name','coordinates unchanged','new proposals geographically corroborated','no historical host fabrication','no automatic component/publication approval','same-name distant aliases excluded','Tower/Block/phase/token regressions','literal range gaps retained'],dbAccess='read-only')
write(HERE/'validation.json',result);write(ROOT/'docs/astra-city/landmark-identity/validation.json',result);print(json.dumps(result))
