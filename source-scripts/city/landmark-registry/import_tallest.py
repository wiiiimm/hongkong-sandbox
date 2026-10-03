"""Extract factual discovery fields from the user-requested Wikipedia table.
No article prose, images, model geometry or surveyed elevations are imported.
"""
import argparse,hashlib,json,pathlib,re,urllib.request
from html.parser import HTMLParser
HERE=pathlib.Path(__file__).resolve().parent
URL='https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_Hong_Kong'
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.depth=0;self.cell=None;self.row=None;self.ignored=0
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='table':
   self.depth+=1
   if self.depth==1:self.table=[]
  if self.depth!=1:return
  if t in ('sup','style','script'):self.ignored+=1
  if t=='tr':self.row=[]
  if t in ('td','th'):self.cell={'text':'','attrs':a}
  if t=='br' and self.cell is not None:self.cell['text']+=' '
 def handle_data(self,d):
  if self.depth==1 and self.cell is not None and not self.ignored:self.cell['text']+=d
 def handle_endtag(self,t):
  if self.depth==1:
   if t in ('sup','style','script'):self.ignored=max(0,self.ignored-1)
   if t in ('td','th') and self.cell is not None:
    if self.row is not None:self.row.append(self.cell)
    self.cell=None
   if t=='tr' and self.row is not None:self.table.append(self.row);self.row=None
   if t=='table':self.tables.append(self.table)
  if t=='table':self.depth-=1

def expand(rows):
 pending={};out=[]
 for raw in rows:
  row={i:v[1] for i,v in pending.items()};pending={i:(n-1,c) for i,(n,c) in pending.items() if n>1};col=0
  for c in raw:
   while col in row:col+=1
   for j in range(int(c['attrs'].get('colspan',1))):
    assert col+j not in row,'Overlapping table cells';row[col+j]=c
    n=int(c['attrs'].get('rowspan',1))
    if n>1:pending[col+j]=(n-1,c)
   col+=int(c['attrs'].get('colspan',1))
  out.append([row[i] for i in range(max(row)+1)] if row else [])
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--html',type=pathlib.Path);a=ap.parse_args()
 raw=a.html.read_bytes() if a.html else urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'HongKongSandboxLandmarkAudit/1.0'}),timeout=45).read()
 p=Tables();p.feed(raw.decode());tables=[expand(t) for t in p.tables]
 clean=lambda c:re.sub(r'\s+',' ',c['text']).strip()
 matches=[t for t in tables if t and [clean(c) for c in t[0]][:3]==['Rank','Name','Image']];assert len(matches)==1,'Main table changed; review importer'
 rows=matches[0];records=[]
 for i,row in enumerate(rows[1:],1):
  assert len(row) in (8,9),(i,len(row)) # Some source rows omit the trailing Notes cell.
  name=clean(row[1]);height=clean(row[3]);floors=clean(row[4]);year=clean(row[6]);coords=clean(row[7])
  assert name and re.match(r'\d',height),(i,name,height)
  loc=re.search(r'([\d.]+)°N\s+([\d.]+)°E',coords)
  records.append({'name':name,'listedHeightMetres':float(re.match(r'[\d.]+',height)[0]),'listedFloors':int(floors) if floors.isdigit() else floors,'listedYear':year,'locationHintWGS84':[float(loc[2]),float(loc[1])] if loc else None,'sourceRow':i,'source':URL+'#Tallest_buildings','status':'main-table-entry-current-status-unverified'})
 assert len(records)>100
 duplicates=sorted({r['name'] for r in records if sum(x['name']==r['name'] for x in records)>1})
 for r in records:
  r['sourceWarnings']=(["duplicate-name-conflicting-source-rows"] if r['name'] in duplicates else [])+(["below-table-advertised180m-threshold"] if r['listedHeightMetres']<180 else [])
 # The main table itself can contain topped-out projects. No entry is thereby approved for present-day modelling.
 excluded=[]
 for t in tables:
  if not t:continue
  headers=[clean(c) for c in t[0]]
  if headers[:1]!=['Name']:continue
  if 'Status' in headers:kind='under-construction-or-proposed'
  elif 'Years existed' in headers:kind='demolished'
  elif 'Floors*' in headers:kind='cancelled-or-vision'
  else:continue
  excluded.append({'kind':kind,'names':[clean(r[0]) for r in t[1:] if r]})
 out={'schemaVersion':1,'source':URL,'retrievedDate':'2026-09-07','htmlSHA256':hashlib.sha256(raw).hexdigest(),'sourceMinimumMetres':180,'count':len(records),'uniqueNames':len({r['name'] for r in records}),'duplicateNames':duplicates,'records':records,'excludedTables':excluded,'notes':['Factual discovery fields only; article text/images omitted. Wikipedia attribution retained.','This180m list is not exhaustive for the user\'s >35-floor criterion. Use government inventory heights for the remaining tall-building queue.','Listed height/floors/year are unverified discovery hints, never overwrite LandsD survey/native geometry.','Main table includes topped-out entries; verify current existence/status and all component IDs before acquisition.']}
 (HERE/'tallest-source.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'rows':len(records),'first':records[0]['name'],'last':records[-1]['name'],'excluded':[(g['kind'],len(g['names'])) for g in excluded]}))
if __name__=='__main__':main()
