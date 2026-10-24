"""Exact published alias + retained named government tower; no fuzzy matching or publication."""
import hashlib,json,sqlite3,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/landmark-identity-followup'
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
assert reservations.owns(json.load(open('/tmp/astra-identity-alias-review-lease.json')))
references={r['id']:r for r in json.load(open(HERE/'reference-cache-manifest.json'))}
TARGETS=[('tall-the-cullinan-north-tower','The Cullinan North Tower','landsd/203728:0','The Cullinan I','cullinan-i','Union Square Phase 6 North Tower'),('tall-the-cullinan-south-tower','The Cullinan South Tower','landsd/203724:0','The Cullinan II','cullinan-ii','Union Square Phase 6 South Tower'),('tall-china-resources-center','China Resources Center','landsd/37369:0','China Resources Building','china-resources','China Resources Center'),('tall-oak-28','OAK 28','landsd/323059:0','The Oakhill','oakhill','Oak 28')]
c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
rows=[]
for ident,title,uid,name,refid,alias in TARGETS:
 ref=references[refid];raw=(ROOT/ref['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'];text=re.sub(r'<[^>]+>',' ',raw.decode());assert alias in text and name in text
 b=dict(c.execute('select * from buildings where uid=? and active=1',(uid,)).fetchone());assert b['name']==name and b['source_dataset']=='landsd-territory';path=ROOT/'3d-viewer'/b['input_path'];sourcehash=hashlib.sha256(path.read_bytes()).hexdigest()
 source={'uid':uid,'objectId':b['object_id'],'csuid':b['csuid'],'name':b['name'],'retainedViewerInput':b['input_path'],'inputSHA256':sourcehash,'sourceBase':b['source_base'],'sourceTop':b['source_top'],'x':b['x'],'z':b['z']}
 rows.append({'id':ident,'title':title,'publicationApproved':False,'replacePriorIdentity':False,'records':[{'uid':uid,'objectId':b['object_id'],'csuid':b['csuid'],'name':name}],'evidence':{'identityReviewed':True,'decision':'exact-published-alias-and-government-named-tower','alias':alias,'reference':ref,'governmentRecords':[source],'componentMembershipComplete':False,'scope':'Named main tower only. Neighbouring podium/Elements or other components are not added by proximity. Source availability and physical placement still require review.'}})
report={'issue':'HKS-214','areas':[],'landmarks':rows,'qualification':'Identity proposal only; runtime, registry, SQLite and geometry unchanged.'};(HERE/'proposed-overlay.json').write_text(json.dumps(report,indent=2)+'\n');(DOC/'alias-decisions.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'identityProposals':len(rows),'uids':[r['records'][0]['uid'] for r in rows]}))
