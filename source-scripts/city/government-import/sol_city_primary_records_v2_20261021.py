"""Fresh government footprint and structure records for seven original candidates."""
from pathlib import Path
import sys,gzip
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-primary-records-v2-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-sol-city-companion-sources-v1-20261021';URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};p=SRC/'nominations.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
tile=ROOT/'3d-viewer/city/data/tiles/-7_-9.json';tileSHA=digest(tile.read_bytes());wanted={'landsd/273080:0','landsd/273271:0','landsd/260034:0','landsd/251569:0','landsd/268424:0','landsd/170270:0'};rows=[dict(uid=b['uid'],source=dict(building=b,tile='city/data/tiles/-7_-9.json'))for b in read(tile)['buildings']if b['uid']in wanted];assert {r['uid']for r in rows}==wanted;save(DOC/'selected-forms.json',dict(rows=rows,tileSHA256=tileSHA));csuids=[x['source']['building']['buildingCSUID']for x in rows];assert all(x.isalnum()for x in csuids);where='BuildingCSUID IN ('+','.join("'"+x+"'"for x in csuids)+')';DOC.mkdir(exist_ok=True)
def query(name,table,where,geom):
 params=dict(f='json',where=where,outFields='*',returnGeometry='true'if geom else'false',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID');raw,rec=request(URL+'/'+str(table)+'/query',params,json_expected=False);decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw;(DOC/(name+'.json')).write_bytes(decoded);rec.update(decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded);save(DOC/(name+'-request.json'),rec)
 if raw!=decoded:(DOC/(name+'-original.gz')).write_bytes(raw)
 d=read(DOC/(name+'.json'));assert not d.get('error') and not d.get('exceededTransferLimit');return d['features']
features=query('footprints',0,where,True);relations=query('relations',1002,where,False);ids=sorted({int(x['attributes']['BuildingStructureID'])for x in relations});details=query('structures',1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')',False)if ids else[]
summary=dict(uids=[x['uid']for x in rows],footprints=len(features),relations=len(relations),structures=len(details),installationApproved=False);save(DOC/'summary.json',summary);module('yoho_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-government-source-identity-records',[Path(__file__),SRC/'result.json',p,tile,HERE.parent/'landsd-territory/source.py'],summary);print(summary,flush=True)
