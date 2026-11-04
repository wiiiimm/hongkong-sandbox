"""Acquire untouched official FBX members for four pinned paired-original models.
Fresh provider index, ETag-bound ZIP directories and member checksums; no live changes.
"""
import sys,json,uuid,struct,zipfile,concurrent.futures
from run import ROOT,HERE,read,save,digest,connect,reservations
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
sys.path.insert(0,str(HERE.parent/'citywide-native'));from download import acquire
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BATCH='government-xl-popcorn-station-collection-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query'
def main():
 rows=[{'sourceKey':'e1ecd1820b0be0962427309bd44ba68857f438aef31260ccb2d82314586aa3be/B448271874701063C0','model':{'modelId':'B448271874701063C0','asset':{'sha256':None},'matching':{'viewerMatches':[{'uid':'landsd/295539:0'}]}}}];assert len(rows)==1
 resources=['native-model:'+r['sourceKey'] for r in rows]+['building:'+m['uid'] for r in rows for m in r['model']['matching']['viewerMatches']];claim=reservations.claim('xl-opening-fbx-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');sheets=dict(c.execute('SELECT cache_key,sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=ANY(%s)',([r['sourceKey'].split('/')[0] for r in rows],)).fetchall())
  selected=sorted(set(sheets.values()));params={'f':'json','where':'SHEETNO IN ('+','.join("'"+s+"'" for s in selected)+')','outFields':'*','returnGeometry':'false','resultRecordCount':'1000'};raw,rec=request(URL,params);index=json.loads(raw);assert len(index['features'])==len(selected) and not index.get('exceededTransferLimit');DOC.mkdir(parents=True,exist_ok=True);(DOC/'official-package-index.json').write_bytes(raw);save(DOC/'official-package-index.request.json',rec)
  def work(f):
   a=f['attributes'];sheet=a['SHEETNO'];wanted={r['model']['modelId'] for r in rows if sheets[r['sourceKey'].split('/')[0]]==sheet};folder=LOCAL/'sheets'/sheet;folder.mkdir(parents=True);net=ac.Network(folder/'directory-transfer.json',cap=8_000_000);url=a['Format_FBX'];_,headers=net.get(url,0,method='HEAD');etag=headers['ETag'];size=int(headers['Content-Length']);tail,h=net.get(url,65536,'-65536',etag);end=tail.rfind(b'PK\x05\x06');assert end>=0;fields=struct.unpack('<4s4H2LH',tail[end:end+22]);offset=fields[6];start=int(h['Content-Range'].split()[1].split('-')[0]);assert int(h['Content-Range'].split('/')[-1])==size
   if offset<start:prefix,_=net.get(url,start-offset,f'{offset}-{start-1}',etag);directory=prefix+tail
   else:directory=tail[offset-start:]
   infos,check=ac.parse_directory(directory);(folder/'zip-directory.bin').write_bytes(directory);models=[]
   for mid in sorted(wanted):
    exact=[e for e in infos if e.filename=='BUILDING/'+mid+'/'+mid+'.fbx'];assert len(exact)==1
    models.append({'modelId':mid,'members':[{'name':e.filename,'crc32':e.CRC,'headerOffset':e.header_offset,'compressedBytes':e.compress_size,'decodedBytes':e.file_size} for e in exact]})
   pinned={'sheet':sheet,'sourceURL':url,'etag':etag,'archiveBytes':size,'directorySHA256':digest(directory),'revision':a['REVISIONDATE'],'models':models,'checkedAt':ac.now(),**check};save(folder/'directory.json',pinned);download=acquire(pinned,folder/'zip-directory.bin',folder/'original');out=[]
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
    for m in models:
     member=m['members'][0];value=z.read(member['name']);assert len(value)==member['decodedBytes'];p=LOCAL/'original-fbx'/m['modelId']/(m['modelId']+'.fbx');p.parent.mkdir(parents=True);p.write_bytes(value);row=next(r for r in rows if r['model']['modelId']==m['modelId']);out.append({'modelId':m['modelId'],'uid':row['model']['matching']['viewerMatches'][0]['uid'],'previousGLTFSourceKey':row['sourceKey'],'previousGLTFSourceSHA256':row['model']['asset']['sha256'],'sourceFormat':'FBX','sourceSHA256':digest(value),'sourceBytes':len(value),'sourcePath':str(p.relative_to(ROOT)),'sourceSheet':sheet,'providerArchiveURL':url,'providerRevisionDate':a['REVISIONDATE'],'providerETag':etag,'providerDirectorySHA256':digest(directory),'originalMember':member,'compactArchiveSHA256':download['sha256'],'identityAccepted':False,'installationApproved':False,'geometryChanges':0})
   return out
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:out=[r for result in pool.map(work,index['features']) for r in result]
  assert len(out)==1;save(DOC/'untouched-current-fbx-sources.json',{'rows':out,'qualification':'Unmodified original government FBX member bytes with independent fresh index/archive/directory/member provenance; new-format geometry requires independent identity, coordinate/unit and physical acceptance. No native glTF approval inherited.'});print(json.dumps([{k:r[k] for k in ['modelId','uid','sourceSHA256','sourceBytes','sourceSheet']} for r in out]),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
