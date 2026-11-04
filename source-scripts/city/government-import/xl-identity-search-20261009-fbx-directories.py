"""Fresh ETag-bound alternate-format directory search; no FBX model downloads."""
import struct,sys,json,concurrent.futures
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009';LOCAL=HERE/'local/government-xl-identity-search-20261009'
def main():
 features=read(DOC/'current-package-index.json')['features'];old=read(DOC/'unmapped-context.json.gz')['rows'];by_sheet={r['sheet']:r['modelId'] for r in read(DOC/'current-package-research.json.gz')['rows']}
 def work(f):
  a=f['attributes'];sheet=a['SHEETNO'];mid=by_sheet[sheet];near=next(r for r in old if r['modelId']==mid);refs={str(x['GeoRefNo']) for x in near['nearbyFeatures']}|{mid[1:11]};url=a['Format_FBX'];folder=LOCAL/'fbx-directories'/sheet;folder.mkdir(parents=True,exist_ok=True);net=ac.Network(folder/'transfer.json',cap=8_000_000)
  _,headers=net.get(url,0,method='HEAD');etag=headers['ETag'];size=int(headers['Content-Length']);tail,h=net.get(url,65536,'-65536',etag);end=tail.rfind(b'PK\x05\x06');assert end>=0;fields=struct.unpack('<4s4H2LH',tail[end:end+22]);offset=fields[6];start=int(h['Content-Range'].split()[1].split('-')[0]);assert int(h['Content-Range'].split('/')[-1])==size
  if offset<start:prefix,_=net.get(url,start-offset,f'{offset}-{start-1}',etag);raw=prefix+tail
  else:raw=tail[offset-start:]
  infos,check=ac.parse_directory(raw);(folder/'zip-directory.bin').write_bytes(raw)
  members=[{'name':e.filename,'crc32':e.CRC,'decodedBytes':e.file_size} for e in infos if any('B'+ref in e.filename for ref in refs)];r={'sheet':sheet,'sourceURL':url,'etag':etag,'archiveBytes':size,'directorySHA256':digest(raw),'checkedAt':ac.now(),'revision':a['REVISIONDATE'],'modelId':mid,'relatedMembers':members,'exactModelMembers':[m for m in members if mid in m['name']],'sourcePayloadsDownloaded':0,'identityAccepted':False,'installationApproved':False,**check};save(folder/'result.json',r);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(work,features))
 save(DOC/'fbx-package-research.json.gz',{'rows':rows,'qualification':'Current provider index exposes FBX and MAX alternatives, not a 3DS URL. Fresh FBX directories are bounded range downloads; source payload and conversion were not acquired. Naming alone is not full identity proof.'});print(json.dumps([{k:r[k] for k in ('sheet','modelId','exactModelMembers')} for r in rows]),flush=True)
if __name__=='__main__':main()
