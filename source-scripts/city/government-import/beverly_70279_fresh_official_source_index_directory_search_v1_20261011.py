"""DRAFT fresh bounded official70279 source availability lookup; root review before run.
Official2D exact CSUID+object queries and two reviewed3D index families/four sheets,
GLTF+FBX complete ETag-bound central directories only. No mesh acquisition or edit,
source-substitution, current geometry/capture, held-state change or acceptance.
"""
from pathlib import Path
import concurrent.futures,importlib.util,json,re,struct,sys
from run import ROOT,HERE,read,save,digest,connect
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request,BASE as OUTLINE_BASE
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac,models
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-70279-fresh-official-source-index-directory-search-v1-20261011';DOC=B/BATCH
PRIOR=B/'government-xl-beverly-70279-primary-directory-absence-checkpoint-v1-20261011';REG=B/'government-xl-beverly-podium233218-70279-original-registry-farpoint-attribution-v1-20261011'
UID='landsd/70279:0';CSUID='3716415011T20080220';GEOREF='3716415011';PREFIX='B'+GEOREF;SHEETS=['11-SW-15A','11-SW-15B','11-SW-15C','11-SW-15D']
INDEXES={'package':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query','individualised':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1671676915450_88604/FeatureServer/0/query'};FORMATS=['Format_glTF','Format_FBX']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def query(url,parameters,name):
 raw,rec=request(url,parameters);p=DOC/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);save(DOC/(name+'.request.json'),rec);return json.loads(raw)
def attributes(data):
 assert isinstance(data.get('features'),list)and not data.get('exceededTransferLimit');rows=[f['attributes']for f in data['features']];assert len(rows)==4 and {a['SHEETNO']for a in rows}==set(SHEETS);return sorted(rows,key=lambda a:a['SHEETNO'])
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];errors=[];rows=[]
 for doc in [PRIOR,REG]:
  receipt=read(doc/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(doc/n)for n in ['result.json','diagnostic.json.gz'])
 prior=read(REG/'diagnostic.json.gz');assert not prior['independentExactObjectAndCSUIDCandidateMatches'];old_form=prior['actualCurrentForeignForm']['building'];assert old_form['objectId']==70279 and old_form['buildingCSUID']==CSUID
 outline={}
 for label,where in [('exact-csuid',"BuildingCSUID='"+CSUID+"'"),('exact-object','OBJECTID=70279')]:
  try:
   q=query(OUTLINE_BASE+'/0/query',dict(f='json',where=where,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100'), 'outline-'+label);assert isinstance(q.get('features'),list)and not q.get('exceededTransferLimit');outline[label]=q
  except Exception as e:errors.append(dict(stage='official-outline-'+label,error=type(e).__name__+': '+str(e)[:300]))
 index_attributes={};tasks=[]
 for family,url in INDEXES.items():
  try:
   q=query(url,dict(f='json',where='SHEETNO IN ('+','.join("'"+s+"'"for s in SHEETS)+')',outFields='*',returnGeometry='false',resultRecordCount='100'),family+'-official-package-index-before');aa=attributes(q);index_attributes[family]=aa
   for a in aa:
    assert 'REVISIONDATE'in a
    for fmt in FORMATS:
     source=a.get(fmt)
     if not isinstance(source,str)or not source.startswith('https://download.map.gov.hk/'):
      errors.append(dict(stage='official-format-not-exposed',family=family,sheet=a['SHEETNO'],format=fmt));continue
     tasks.append((family,a,fmt,source))
  except Exception as e:errors.append(dict(stage='official-index-'+family,error=type(e).__name__+': '+str(e)[:300]))
 assert len(tasks)<=16
 def work(t):
  family,a,fmt,url=t;folder=DOC/'directories'/family/a['SHEETNO']/fmt;folder.mkdir(parents=True,exist_ok=True);net=ac.Network(folder/'directory-transfer.json',cap=8_000_000);_,head=net.get(url,0,method='HEAD');etag=head.get('ETag');assert etag;size=int(head['Content-Length']);tail,h=net.get(url,65536,'-65536',etag);end=tail.rfind(b'PK\x05\x06');assert end>=0;fields=struct.unpack('<4s4H2LH',tail[end:end+22]);offset=fields[6];start=int(h['Content-Range'].split()[1].split('-')[0]);assert int(h['Content-Range'].split('/')[-1])==size
  if offset<start:prefix,_=net.get(url,start-offset,f'{offset}-{start-1}',etag);directory=prefix+tail
  else:directory=tail[offset-start:]
  infos,check=ac.parse_directory(directory);assert check['directorySHA256']==digest(directory);(folder/'zip-directory.bin').write_bytes(directory);members=[dict(name=e.filename,crc32=e.CRC,headerOffset=e.header_offset,compressedBytes=e.compress_size,decodedBytes=e.file_size)for e in infos];matches=[m for m in members if any(re.fullmatch(r'[A-Za-z]+'+GEOREF+r'(01|02)06[0-9A-Z]{3}(?:\.[^/]+)?',part,re.I)for part in Path(m['name']).parts)];native=models(infos)if fmt=='Format_glTF'else[];exact_native=[m for m in native if m['geoRefNo']==GEOREF];_,after=net.get(url,0,method='HEAD');assert after.get('ETag')==etag and int(after['Content-Length'])==size
  result=dict(indexFamily=family,format=fmt,sheet=a['SHEETNO'],sourceURL=url,revision=a['REVISIONDATE'],etag=etag,archiveBytes=size,checkedAt=ac.now(),lastModified=head.get('Last-Modified'),completeArchiveMembers=members,nativeGLTFModels=native,exactGeoRefNativeModels=exact_native,exactGeoRefPrefixMembers=matches,sourceModelMembersRequested=0,sourceGeometryAcquired=False,identityAccepted=False,**check);save(folder/'directory.json.gz',result);return result
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures={pool.submit(work,t):t for t in tasks}
  for future in concurrent.futures.as_completed(futures):
   family,a,fmt,url=futures[future]
   try:r=future.result();rows.append(r);print(json.dumps(dict(family=family,sheet=a['SHEETNO'],format=fmt,exactPrefixMembers=len(r['exactGeoRefPrefixMembers']))),flush=True)
   except Exception as e:errors.append(dict(stage='directory',family=family,sheet=a['SHEETNO'],format=fmt,error=type(e).__name__+': '+str(e)[:300]))
 for family,aa in index_attributes.items():
  try:q=query(INDEXES[family],dict(f='json',where='SHEETNO IN ('+','.join("'"+s+"'"for s in SHEETS)+')',outFields='*',returnGeometry='false',resultRecordCount='100'),family+'-official-package-index-after');assert attributes(q)==aa
  except Exception as e:errors.append(dict(stage='official-index-final-fence-'+family,error=type(e).__name__+': '+str(e)[:300]))
 matches=[dict(indexFamily=r['indexFamily'],sheet=r['sheet'],format=r['format'],revision=r['revision'],etag=r['etag'],members=r['exactGeoRefPrefixMembers'],nativeGLTFModels=r['exactGeoRefNativeModels'])for r in rows if r['exactGeoRefPrefixMembers']];complete=not errors and len(rows)==16;outline_identity=[f for q in outline.values()for f in q['features']if f['attributes'].get('OBJECTID')==70279 and f['attributes'].get('BuildingCSUID')==CSUID]
 cached=read(PRIOR/'diagnostic.json.gz')['allFourRelevantCachedPrimaryProviderDirectories'];comparison=[]
 for r in rows:
  if r['format']=='Format_glTF':
   old=next(c for c in cached if c['sheet']==r['sheet']);comparison.append(dict(family=r['indexFamily'],sheet=r['sheet'],cachedDirectorySHA256=old['directorySHA256'],freshDirectorySHA256=r['directorySHA256'],exactDirectoryBytesSame=r['directorySHA256']==old['directorySHA256'],freshRevision=r['revision'],freshETag=r['etag']))
 refs.extend(ref(p)for p in [HERE.parent/'landsd-territory/source.py',HERE.parent/'citywide-source/discover.py',HERE.parent/'landmark-acquisition/acquire.py']);refs.extend(ref(p)for p in sorted(DOC.rglob('*'))if p.is_file());save(DOC/'diagnostic.json.gz',dict(uids=[UID,'landsd/233218:0','landsd/255543:0','landsd/255939:0'],sourceOnly=True,currentAcceptance=False,installationApproved=False,originalSourceGeometryChanges=0,terrainGeometryChanges=0,currentCapturesCreated=False,currentOutlineQueries=outline,exactObjectAndCSUIDCurrentlyReturned=bool(outline_identity),freshDirectoryResults=rows,cached1430AbsenceDistinctFromFreshOfficialSearch=True,cachedVersusFreshDirectoryComparisons=comparison,exactGeoRefSourceCandidates=matches,completeBoundedFreshOfficialSearch=complete,boundedFreshDirectoryAbsence=(complete and not matches),errors=errors,sourceModelMemberRequests=0,sourceGeometryAcquired=False,original70279Recovered=False,boundedSheets=SHEETS,formatsSearched=FORMATS,officialIndexFamilies=INDEXES,authoritativeAbsenceLimitedToListedRevisionsAndDirectories=True,noGlobalOrPermanentSourceAbsenceClaim=True,qualification='Fresh official HTTP query and ETag-bound complete GLTF/FBX directory evidence for exactly four relevant sheets and two reviewed official index families. Zero exactGeoRef matches supports absence only from this explicit complete pinned scope; any request/format/index failure prevents even that bounded absence conclusion. ExactGeoRef member is a candidate, not full CSUID geometry identity. Exact current2D record presence/absence is distinct from3D original availability. No nearby substitute, provider intent/function, geometry/terrain edits, held-state write, current approval or installed credit. K/P existing held1ef9e76176f13d45 and installedJ unchanged by this read-only source search.',evidenceRefs=refs));print(json.dumps(dict(uid=UID,complete=complete,exactGeoRefCandidateDirectories=len(matches),errors=errors,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
