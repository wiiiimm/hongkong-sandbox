"""Recover two exact pinned counterpart originals for OP component diagnostics."""
import sys,json,uuid,zipfile,concurrent.futures
from run import ROOT,HERE,read,save,digest,connect,reservations
sys.path.insert(0,str(HERE.parent/'enhancement-screening'));from shape_prepare import scan,acquire,canonical_bytes
from convert import _convert_one
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009';LOCAL=HERE/'local/government-xl-identity-search-op-structures-20261009-counterparts'
def main():
 rows=[r for r in read(HERE/'local/government-xl-identity-search-op-structures-20261009/paired-physical-source-candidates.json.gz')['rows'] if r['model']['modelId'] in ['B350302046901063C0','B355371858701063C0']];assert len(rows)==2
 resources=['native-model:'+r['sourceKey'] for r in rows]+['building:'+m['uid'] for r in rows for m in r['model']['matching']['viewerMatches']];claim=reservations.claim('xl-op-original-counterparts-'+str(uuid.uuid4()),resources,batch='government-xl-identity-search-op-structures-20261009',ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');sheets=dict(c.execute('SELECT cache_key,sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=ANY(%s)',([r['sourceKey'].split('/')[0] for r in rows],)).fetchall());dirs=dict(c.execute('SELECT DISTINCT ON(sheet) sheet,result FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC',(list(sheets.values()),)).fetchall())
  def work(r):
   sheet=sheets[r['sourceKey'].split('/')[0]];prior=dirs[sheet];folder=LOCAL/sheet;m=r['model'];mid=m['modelId'];cur,_=scan({'SHEETNO':sheet,'Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},folder/'directory',refresh=True);assert cur['etag']==prior['etag'] and cur['directorySHA256']==prior['directorySHA256'],'Pinned revision changed';cur['models']=[x for x in cur['models'] if x['modelId']==mid];assert len(cur['models'])==1
   acquired=acquire(cur,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True)
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:converted=_convert_one(z,z.getinfo(m['sourceEntry']),folder/'decoded',packed,{}, {'modelId':mid})
   raw=canonical_bytes((packed/converted['asset']['asset']).read_bytes(),m['asset']['sha256']);assert len(raw)==m['asset']['bytes'];p=LOCAL/'assets'/(m['asset']['sha256']+'.glb.gz');p.parent.mkdir(exist_ok=True);p.write_bytes(raw);return {'sourceKey':r['sourceKey'],'sourceSHA256':m['asset']['sha256'],'modelId':mid,'path':str(p.relative_to(ROOT)),'sourceETag':cur['etag'],'directorySHA256':cur['directorySHA256'],'sheet':sheet,'archive':acquired,'modelGeometryChanges':0}
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(work,rows))
  save(DOC/'counterpart-original-recovery.json.gz',{'rows':out,'qualification':'Exact native-stage SHA and byte count recovered from fresh government range ZIP with pinned matching directory/ETag, deterministic original packing only. No geometry/pose modifications or identity approval.'});print(json.dumps([{'modelId':r['modelId'],'sha':r['sourceSHA256']} for r in out]),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
