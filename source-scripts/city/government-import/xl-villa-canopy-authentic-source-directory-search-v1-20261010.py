"""Fresh official-sheet alternate-format search for exact current canopy lineage.

Directory research only: no source geometry, current actor, or approval changes.
"""
import concurrent.futures,importlib.util,json,struct,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac,models
BATCH='government-xl-villa-canopy-authentic-source-directory-search-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
INDEX='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query'
PREFIX='B2162233384';UID='landsd/325786:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not (DOC/'diagnostic.json.gz').exists();DOC.mkdir(parents=True,exist_ok=True)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  cached=c.execute("SELECT DISTINCT r.cache_key,m->>'modelId',m->'asset'->>'sha256' FROM astra_modelling.native_stage_results r,LATERAL jsonb_array_elements(r.result->'models')m WHERE m->>'modelId' LIKE %s ORDER BY 1,2",(PREFIX+'%',)).fetchall()
 save(DOC/'all-historical-exact-prefix-cache-query.json',dict(prefix=PREFIX,rows=cached,availabilityAbsenceNotClaimed=True))
 raw,rec=request(INDEX,dict(f='json',where="SHEETNO='6-NW-15A'",outFields='*',returnGeometry='false',resultRecordCount='1000'))
 (DOC/'official-package-index.json').write_bytes(raw);save(DOC/'official-package-index.request.json',rec)
 data=json.loads(raw);assert len(data['features'])==1 and not data.get('exceededTransferLimit');a=data['features'][0]['attributes'];assert a['SHEETNO']=='6-NW-15A'
 formats={k:v for k,v in a.items() if k.startswith('Format_') and isinstance(v,str) and v.startswith('https://download.map.gov.hk/')}
 assert 'Format_glTF' in formats and 'Format_FBX' in formats
 def work(item):
  fmt,url=item;folder=DOC/fmt;folder.mkdir(exist_ok=True);net=ac.Network(folder/'directory-transfer.json',cap=8_000_000)
  _,head=net.get(url,0,method='HEAD');etag=head['ETag'];size=int(head['Content-Length']);tail,h=net.get(url,65536,'-65536',etag);end=tail.rfind(b'PK\x05\x06');assert end>=0
  fields=struct.unpack('<4s4H2LH',tail[end:end+22]);offset=fields[6];start=int(h['Content-Range'].split()[1].split('-')[0]);assert int(h['Content-Range'].split('/')[-1])==size
  if offset<start:prefix,_=net.get(url,start-offset,f'{offset}-{start-1}',etag);directory=prefix+tail
  else:directory=tail[offset-start:]
  infos,check=ac.parse_directory(directory);(folder/'zip-directory.bin').write_bytes(directory)
  matches=[dict(name=e.filename,crc32=e.CRC,headerOffset=e.header_offset,compressedBytes=e.compress_size,decodedBytes=e.file_size) for e in infos if PREFIX in e.filename]
  # Complete current building inventory enables exact adjacent-source follow-up;
  # proximity or inventory membership is never identity approval.
  building=[dict(name=e.filename,crc32=e.CRC,headerOffset=e.header_offset,compressedBytes=e.compress_size,decodedBytes=e.file_size) for e in infos if e.filename.startswith('BUILDING/')]
  assert check['directorySHA256']==digest(directory)
  result=dict(format=fmt,sheet=a['SHEETNO'],sourceURL=url,revision=a['REVISIONDATE'],etag=etag,archiveBytes=size,checkedAt=ac.now(),exactCurrentCanopyPrefix=PREFIX,exactPrefixMembers=matches,completeBuildingMembers=building,nativeGLTFModels=models(infos) if fmt=='Format_glTF' else [],sourcePayloadsDownloaded=0,identityAccepted=False,**check)
  save(folder/'directory.json.gz',result);print(dict(format=fmt,exactPrefixMembers=len(matches),allBuildingMembers=len(building)),flush=True);return result
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(work,formats.items()))
 out=dict(uid=UID,csuid='2162233384T20211022',buildingID='1910216544',sourceSheet='6-NW-15A',formats=rows,allHistoricalCacheExactPrefixMatches=cached,exactCurrentPrefixFound=any(r['exactPrefixMembers'] for r in rows),geometryChanges=0,identityAccepted=False,physicalAccepted=False,installation=False,qualification='Fresh ETag-bound complete directories of all official formats exposed for this one current source sheet. Zero exact-prefix matches proves only this pinned sheet/format/revision search negative, not territory-wide or permanent government-source absence. Adjacent model naming grants no identity/support credit.')
 save(DOC/'diagnostic.json.gz',out)
 paths=[Path(__file__),DOC/'official-package-index.json',DOC/'official-package-index.request.json',DOC/'all-historical-exact-prefix-cache-query.json',HERE.parent/'citywide-source/discover.py',ROOT/'source-scripts/city/landmark-acquisition/acquire.py']
 paths += [p for p in DOC.rglob('*') if p.is_file()]
 s=importlib.util.spec_from_file_location('canopy_directory_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'exact-current-canopy-lineage-fresh-official-sheet-all-format-directory-search-v1',sorted(set(paths)),dict(uids=[UID,'landsd/89917:0'],exactPrefixFound=out['exactCurrentPrefixFound'],sourceGeometryChanges=0,identityAccepted=False,fullAcceptance=False,humanDecisionRequired=False,humanStatus='authentic-canopy-source-search-only',availabilityAbsenceNotClaimed=True))
 print(dict(exactCurrentPrefixFound=out['exactCurrentPrefixFound'],formats=list(formats)),flush=True)
if __name__=='__main__':main()
