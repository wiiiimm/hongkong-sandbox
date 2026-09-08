"""HKS-213: restartable exact-ID source acquisition; no runtime/registry/DB writes.
Selective ZIP range mechanics follow mui-wo-models/fetch.py. Only selected native
members are retained; no monolithic source archive or source transforms change.
"""
import argparse,concurrent.futures,datetime,gzip,hashlib,importlib.util,io,json,pathlib,re,sqlite3,struct,sys,tempfile,threading,time,urllib.parse,urllib.request,zipfile,zlib

BASE=pathlib.Path(__file__).resolve().parent
HERE=BASE
ROOT=BASE.parents[2]
DOCS=ROOT/'docs/astra-city/landmark-acquisition'
SERVICE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0'
CAP=100_000_000
sys.dont_write_bytecode=True

PROVENANCE_HEADERS={name.lower():name for name in ('ETag','Last-Modified','Content-Length','Content-Range','Content-Type','Accept-Ranges','Date')}
def provenance_headers(headers):return {PROVENANCE_HEADERS[key.lower()]:value for key,value in headers.items()if key.lower()in PROVENANCE_HEADERS}

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,prefix=path.name+'.',suffix='.part',delete=False)as stream:
  temporary=pathlib.Path(stream.name);stream.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 try:temporary.replace(path)
 finally:temporary.unlink(missing_ok=True)
def relative(path):return str(path.relative_to(ROOT))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

class BudgetExceeded(RuntimeError):pass
class Network:
 """Reserve before dispatch; an interrupted/uncertain request keeps its full charge.
 A restart uses the same pinned batch envelope, not a fresh allowance.
 """
 def __init__(self,path,cap=CAP):
  self.lock=threading.RLock();self.path=path;self.data=read(path)if path.exists()else {'schemaVersion':1,'issue':'HKS-213','startedAt':now(),'chargedBytes':0,'receivedBytes':0,'requests':[]}
  self.cap=cap;self.initial=self.data['receivedBytes'];self.data['capBytes']=cap;write(path,self.data)
 def get(self,url,maximum,span=None,etag=None,method='GET'):
  headers={}
  if span:headers['Range']='bytes='+span
  if etag:headers['If-Match']=etag
  row={'url':url,'method':method,'range':span,'reservedBytes':maximum,'startedAt':now(),'status':'reserved'}
  with self.lock:
   if self.data['chargedBytes']+maximum>self.cap:raise BudgetExceeded(f'Cumulative byte cap: {self.data["chargedBytes"]} charged; next reservation {maximum}; cap {self.cap}')
   self.data['requests'].append(row);self.data['chargedBytes']+=maximum;write(self.path,self.data)
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers,method=method),timeout=60)as response:
    received=provenance_headers(response.headers);status=response.status
    if span and status!=206:raise ValueError('Server refused bounded byte range; full archive body not read')
    raw=response.read(maximum+1)if method!='HEAD'else b''
    if len(raw)>maximum:raise ValueError('Response exceeds reserved byte limit')
    if span:
     content_range=received.get('Content-Range','');assert content_range.startswith('bytes '),content_range
     actual_start,actual_end=map(int,content_range.split()[1].split('/')[0].split('-'));assert actual_end-actual_start+1==len(raw)
     if not span.startswith('-'):assert [actual_start,actual_end]==list(map(int,span.split('-')))
     if etag:assert received.get('ETag')==etag,'Source revision changed during ranges'
    with self.lock:
     row.update(status='complete',finishedAt=now(),httpStatus=status,receivedBytes=len(raw),sha256=sha(raw),headers=received)
     self.data['receivedBytes']+=len(raw);self.data['chargedBytes']-=maximum-len(raw);write(self.path,self.data)
    return raw,received
  except Exception as error:
   with self.lock:
    row.update(status='failed-reservation-retained',finishedAt=now(),error=f'{type(error).__name__}: {error}');write(self.path,self.data)
   raise
 def json(self,url,maximum=3_000_000):
  raw,headers=self.get(url,maximum);data=json.loads(raw);assert not data.get('error'),data;return data


def parse_directory(raw):
 """Validate a complete non-ZIP64 single-disk directory without archive allocation."""
 end=raw.rfind(b'PK\x05\x06');assert end>=0 and end+22<=len(raw),'No complete end-of-directory record'
 fields=list(struct.unpack('<4s4H2LH',raw[end:end+22]));_,disk,cd_disk,disk_count,total,cd_size,cd_offset,comment=fields
 assert disk==cd_disk==0 and disk_count==total and total!=65535,'Unsupported split/ZIP64 source'
 assert end+22+comment==len(raw) and end==cd_size,'Directory must be complete, with exact comment length'
 fields[6]=0
 compact=raw[:cd_size]+struct.pack('<4s4H2LH',*fields)+raw[end+22:]
 with zipfile.ZipFile(io.BytesIO(compact))as archive:infos=sorted(archive.infolist(),key=lambda entry:entry.header_offset)
 assert len(infos)==total and len({i.filename for i in infos})==total,'Directory count/duplicate mismatch'
 assert all(0<=i.header_offset<cd_offset for i in infos),'Invalid local header offset'
 return infos,{'completeEntries':total,'centralDirectoryBytes':cd_size,'centralDirectoryOffset':cd_offset,'directorySHA256':sha(raw)}


def unpack_member(raw,entry):
 assert len(raw)>=30
 fields=struct.unpack('<4s5H3L2H',raw[:30]);signature,version,flags,method,mtime,mdate,crc,packed,size,name_len,extra_len=fields
 assert signature==b'PK\x03\x04'and not flags&1 and method==entry.compress_type
 name=raw[30:30+name_len].decode('utf-8'if flags&2048 else 'cp437');assert name==entry.filename
 offset=30+name_len+extra_len;compressed=raw[offset:offset+entry.compress_size];assert len(compressed)==entry.compress_size
 if method==zipfile.ZIP_STORED:value=compressed
 elif method==zipfile.ZIP_DEFLATED:value=zlib.decompress(compressed,-15)
 else:raise ValueError('Unsupported ZIP compression '+str(method))
 assert len(value)==entry.file_size and zlib.crc32(value)&0xffffffff==entry.CRC,'Native member length/CRC mismatch'
 return value


def configure_batch(batch=None,targets_source=None,budget_mb=None):
 global HERE,DOCS
 if not batch:
  if targets_source or budget_mb is not None:raise ValueError('New targets/budget require a named batch; original checkpoint is immutable')
  HERE=BASE;DOCS=ROOT/'docs/astra-city/landmark-acquisition';return None
 if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}',batch):raise ValueError('Invalid batch name')
 HERE=BASE/'batches'/batch;DOCS=ROOT/'docs/astra-city/landmark-acquisition/batches'/batch
 config_path=HERE/'batch.json'
 if config_path.exists():
  config=read(config_path)
  if targets_source and sha(pathlib.Path(targets_source).resolve().read_bytes())!=config['targetSnapshotSHA256']:raise ValueError('Target snapshot changed; use a new pinned batch')
  if budget_mb is not None and budget_mb*1_000_000!=config['capBytes']:raise ValueError('Pinned batch budget differs; preserve its ledger and use a recorded follow-up batch')
  assert sha((HERE/'target-input.json').read_bytes())==config['targetSnapshotSHA256'];return config
 if not targets_source:raise ValueError('New batch requires --targets-source')
 source=pathlib.Path(targets_source).resolve();raw=source.read_bytes();json.loads(raw)
 cap=(budget_mb if budget_mb is not None else 500)*1_000_000
 if cap<=0:raise ValueError('Budget must be positive')
 HERE.mkdir(parents=True,exist_ok=True);(HERE/'target-input.json').write_bytes(raw)
 config={'schemaVersion':1,'issue':'HKS-213','batchId':batch,'createdAt':now(),'targetsSource':relative(source),'targetSnapshotSHA256':sha(raw),'targetSnapshot':relative(HERE/'target-input.json'),'capBytes':cap,'budgetBasis':'User authorised all remaining mechanical landmark acquisition; bounded parallel selective ranges, independent pinned ledger, no original100MB restriction.','originalCheckpointPreserved':True}
 write(config_path,config);return config


def target_entries(data):
 # Identity stage summaries have BOTH top-level parts and per-landmark rows.
 # Their rows contain members rather than the original bulk report's row.parts.
 if 'targets'not in data and'parts'not in data and'rows'in data:
  return [(part,[row['id']])for row in data['rows']for part in row.get('parts',[])if part.get('state')=='cache-absent'and part.get('csuid')]
 entries=[]
 for part in data.get('targets',data.get('parts',[])):
  if isinstance(part,str):part={'uid':part}
  if 'targets'not in data and part.get('state')!='not-in-retained-staged-models':continue
  entries.append((part,part.get('landmarks',part.get('identityProposalGroups',[]))))
 return entries


def target_records(source_path):
 data=read(source_path);targets={};entries=target_entries(data)
 connection=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);connection.row_factory=sqlite3.Row
 try:
  for part,landmarks in entries:
   uid=part['uid'];assert re.fullmatch(r'landsd/\d+:\d+',uid),'No source identity: '+str(uid)
   record=connection.execute('select uid,object_id,csuid,name,x,z from buildings where uid=? and active=1',(uid,)).fetchone();assert record,'No retained active footprint for '+uid
   assert not part.get('csuid')or part['csuid']==record['csuid'],'CSUID changed: '+uid
   assert part.get('objectId')in(None,record['object_id']),'Object identity changed: '+uid
   target=targets.setdefault(uid,{'uid':uid,'objectId':record['object_id'],'csuid':record['csuid'],'name':part.get('name')or record['name'],'x':record['x'],'z':record['z'],'landmarks':[],'identityApproved':part.get('identityApproved',False)})
   for landmark in landmarks:
    if landmark not in target['landmarks']:target['landmarks'].append(landmark)
 finally:connection.close()
 return data,targets


def prepare(network):
 from shapely.geometry import Polygon
 from shapely.ops import unary_union
 from shapely.strtree import STRtree
 from pyproj import Transformer
 config=read(HERE/'batch.json')if(HERE/'batch.json').exists()else None
 source_report=HERE/'target-input.json'if config else ROOT/'docs/astra-city/landmark-bulk/bulk-report.json'
 bulk,targets=target_records(source_report)
 if not targets:raise ValueError('No exact-ID acquisition targets in pinned input; refusing an empty success report')
 metadata_path=HERE/'service.json';index_path=HERE/'index.json'
 if not metadata_path.exists():write(metadata_path,{'checkedAt':now(),'url':SERVICE+'?f=json','service':network.json(SERVICE+'?f=json')})
 service=read(metadata_path)['service'];assert service['type']=='Feature Layer'and'Query'in service['capabilities']
 if not index_path.exists():
  features=[];requests=[];offset=0
  while True:
   params={'f':'json','where':'1=1','outFields':'OBJECTID,SHEETNO,REVISIONDATE,Format_glTF','outSR':2326,'returnGeometry':'true','orderByFields':'OBJECTID','resultOffset':offset,'resultRecordCount':service['maxRecordCount']}
   url=SERVICE+'/query?'+urllib.parse.urlencode(params);page=network.json(url,5_000_000);features.extend(page['features']);requests.append(url)
   if not page.get('exceededTransferLimit'):break
   assert page['features'];offset+=len(page['features'])
  assert len({f['attributes']['SHEETNO']for f in features})==len(features)
  write(index_path,{'checkedAt':now(),'spatialReference':{'wkid':2326},'completePagination':True,'requests':requests,'features':features})
 index=read(index_path)
 # Use native retained official footprint records for the unchanged decoder.
 source=ROOT/'source-scripts/city/landsd-territory/landsd-hong-kong-source.geojson.gz';official_path=HERE/'official-selection.json.gz'
 if not official_path.exists():
  sys.path.insert(0,str(source.parent));from retain import iter_features
  georefs={t['csuid'][:10]for t in targets.values()};projection=Transformer.from_crs(4326,2326,always_xy=True);features=[]
  for feature in iter_features(source):
   attrs=feature['properties']
   if str(attrs.get('GeoRefNo',''))not in georefs:continue
   polygons=[feature['geometry']['coordinates']]if feature['geometry']['type']=='Polygon'else feature['geometry']['coordinates']
   features.append({'attributes':attrs,'geometry':{'rings':[[list(projection.transform(*point))for point in ring]for polygon in polygons for ring in polygon]}})
  raw=json.dumps({'datasetVersion':'Building_Outline_Public_v20260819','source':relative(source),'sourceSHA256':sha(source.read_bytes()),'features':features},separators=(',',':')).encode();official_path.write_bytes(gzip.compress(raw,mtime=0))
 official=json.loads(gzip.decompress(official_path.read_bytes()));shapes={}
 for feature in official['features']:
  key=feature['attributes']['OBJECTID'];shapes[key]=unary_union([Polygon(ring).buffer(0)for ring in feature['geometry']['rings']])
 tiles={};tile_shapes=[Polygon(feature['geometry']['rings'][0]).buffer(0)for feature in index['features']];tree=STRtree(tile_shapes)
 for target in targets.values():
  if target['objectId']not in shapes:continue
  for i in sorted(tree.query(shapes[target['objectId']].buffer(1),predicate='intersects')):
   attrs=index['features'][int(i)]['attributes'];target.setdefault('sheets',[]).append(attrs['SHEETNO']);tile=tiles.setdefault(attrs['SHEETNO'],{'attributes':attrs,'uids':[]});tile['uids'].append(target['uid'])
 plan={'issue':'HKS-213','batchId':config['batchId']if config else'original-115','createdAt':now(),'sourceReport':relative(source_report),'sourceReportSHA256':sha(source_report.read_bytes()),'sourceIndexSHA256':sha(index_path.read_bytes()),'registryEntries':bulk.get('registryEntries',bulk.get('allRegistryEntries',213)),'targetParts':len(targets),'officialTiles':len(tiles),'targets':list(targets.values()),'tiles':tiles,'policy':'Exact ten-digit GeoRefNo only; all current official sheets intersecting retained footprint +1m. No identity invention, coordinate change or publication.'}
 write(HERE/'plan.json',plan);return plan


def retained_caches():
 caches={}
 for path in (ROOT/'source-scripts/city').glob('**/download.json'):
  if HERE in path.parents:continue
  try:
   record=read(path)
   if record.get('sheet')and record.get('sourceETag'):caches.setdefault(record['sheet'],[]).append((path,record))
  except (ValueError,OSError):pass
 return caches


def acquire_tile(network,sheet,tile,targets,caches,head_refresh=False,exact_members=None):
 attrs=tile['attributes'];url=attrs['Format_glTF'];folder=HERE/'sources'/sheet;folder.mkdir(parents=True,exist_ok=True)
 state_path=folder/'state.json';state=read(state_path)if state_path.exists()else {'sheet':sheet,'status':'planned','members':{},'prefixes':[]}
 # Stable official URL + revision + ETag prove cache provenance; HEAD reads no body.
 head_path=folder/'head.json'
 if head_refresh or not head_path.exists():
  _,headers=network.get(url,0,method='HEAD');write(head_path,{'checkedAt':now(),'url':url,'headers':headers})
 head=read(head_path);headers=head['headers'];etag=headers.get('ETag');assert etag,'Missing stable source ETag';archive_size=int(headers['Content-Length'])
 revision=datetime.datetime.fromtimestamp(attrs['REVISIONDATE']/1000,datetime.timezone.utc).isoformat()
 if state.get('sourceETag')and state['sourceETag']!=etag:raise ValueError('Source changed; start a separate acquisition run rather than overwrite retained native evidence')
 state.update(source=url,sourceETag=etag,sourceArchiveBytes=archive_size,revisionDate=revision)
 valid=[(path,record)for path,record in caches.get(sheet,[])if record.get('source')==url and record.get('sourceETag')==etag and record.get('revisionDate')==revision]
 directory_path=folder/'zip-directory.bin'
 if not directory_path.exists():
  reused=False
  for path,record in valid:
   retained=path.parent/'zip-directory.bin'
   if retained.exists():
    raw=retained.read_bytes();parse_directory(raw);directory_path.write_bytes(raw);state['directoryReusedFrom']=relative(retained);reused=True;break
  if not reused:
   tail,received=network.get(url,65536,'-65536',etag);end=tail.rfind(b'PK\x05\x06');assert end>=0
   fields=struct.unpack('<4s4H2LH',tail[end:end+22]);cd_offset=fields[6];tail_start=int(received['Content-Range'].split()[1].split('-')[0]);assert int(received['Content-Range'].split('/')[-1])==archive_size
   if cd_offset<tail_start:
    prefix,_=network.get(url,tail_start-cd_offset,f'{cd_offset}-{tail_start-1}',etag);raw=prefix+tail
   else:raw=tail[cd_offset-tail_start:]
   parse_directory(raw);directory_path.write_bytes(raw)
 infos,check=parse_directory(directory_path.read_bytes());state['directoryCheck']=check;by_name={entry.filename:entry for entry in infos}
 prefixes=sorted({'BUILDING/B'+targets[uid]['csuid'][:10]for uid in tile['uids']})if exact_members is None else sorted(exact_members)
 selected=[entry for entry in infos if (entry.filename.startswith(tuple(prefixes))if exact_members is None else entry.filename in exact_members)and entry.filename.endswith(('.gltf','.bin'))]
 if exact_members is not None:
  assert {entry.filename for entry in selected}==set(exact_members),'Pinned native member absent from current source'
  for entry in selected:
   expected=exact_members[entry.filename];assert (entry.header_offset,entry.CRC,entry.compress_size,entry.file_size)==(expected['headerOffset'],expected['crc32'],expected['compressedBytes'],expected['decodedBytes']),'Pinned native member metadata changed'
 assert all(not pathlib.PurePosixPath(entry.filename).is_absolute()and'..'not in pathlib.PurePosixPath(entry.filename).parts for entry in selected),'Unsafe source member path'
 state['prefixes']=prefixes;state['exactGLTFEntries']=[entry.filename for entry in selected if entry.filename.endswith('.gltf')];state['status']='directory-verified';write(state_path,state)
 # Reuse native retained members only after compact-cache SHA and member CRC/SHA.
 missing={entry.filename:entry for entry in selected}
 for name in list(missing):
  existing=folder/'members'/name;record=state['members'].get(name)
  if existing.exists()and record:
   raw=existing.read_bytes();entry=missing[name]
   if sha(raw)==record['sha256']and len(raw)==entry.file_size and zlib.crc32(raw)&0xffffffff==entry.CRC:del missing[name]
 for path,record in valid:
  names={entry['name']:entry for entry in record.get('entries',[])};wanted=set(missing)&set(names)
  if not wanted:continue
  archive=path.parent/(sheet+'.zip')
  if not archive.exists()or sha(archive.read_bytes())!=record['sha256']:continue
  with zipfile.ZipFile(archive)as retained:
   for name in sorted(wanted):
    raw=retained.read(name);entry=missing[name];assert sha(raw)==names[name]['sha256']and len(raw)==entry.file_size and zlib.crc32(raw)&0xffffffff==entry.CRC
    dest=folder/'members'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);state['members'][name]={'sha256':sha(raw),'bytes':len(raw),'sourceCRC32':entry.CRC,'reusedFrom':relative(archive)};del missing[name]
  write(state_path,state)
 positions={entry.filename:i for i,entry in enumerate(infos)}
 for name,entry in missing.items():
  assert not pathlib.PurePosixPath(name).is_absolute()and'..'not in pathlib.PurePosixPath(name).parts
  i=positions[name];stop=(infos[i+1].header_offset if i+1<len(infos)else check['centralDirectoryOffset'])-1
  raw,_=network.get(url,stop-entry.header_offset+1,f'{entry.header_offset}-{stop}',etag);value=unpack_member(raw,entry);dest=folder/'members'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
  state['members'][name]={'sha256':sha(value),'bytes':len(value),'sourceCRC32':entry.CRC,'range':[entry.header_offset,stop]};write(state_path,state)
 # Every glTF buffer URI must be covered; partial/unsupported dependencies stay held.
 for name in state['exactGLTFEntries']:
  gltf=read(folder/'members'/name)
  for buffer in gltf.get('buffers',[]):
   dependency=pathlib.PurePosixPath(name).parent/buffer['uri'];assert not dependency.is_absolute()and'..'not in dependency.parts
   assert str(dependency)in state['members'],'Missing exact buffer dependency: '+str(dependency)
 archive=folder/(sheet+'.zip');temporary=archive.with_suffix('.zip.part')
 with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as compact:
  for entry in selected:compact.write(folder/'members'/entry.filename,entry.filename)
 temporary.replace(archive)
 record={'source':url,'sheet':sheet,'revisionDate':revision,'retrievedAt':now(),'sourceETag':etag,'sourceLastModified':headers.get('Last-Modified'),'sourceArchiveBytes':archive_size,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'archiveSha256':None,'cacheKind':'Derived compact ZIP of selected original glTF/bin entries; never a complete source archive','memberPrefixes':prefixes,'entries':[{'name':entry.filename,'sourceCompressedBytes':entry.compress_size,**state['members'][entry.filename]}for entry in selected],'indexAttributes':attrs,'transferredBytes':sum(r.get('receivedBytes',0)for r in network.data['requests']if r['url']==url)}
 write(folder/'download.json',record)
 stage=module('landmark_acquisition_stage',ROOT/'docs/astra-city/mui-wo-buildings/review/prepare_model_sample.py').stage
 manifest=stage(archive,record,HERE/'official-selection.json.gz',HERE/'staged'/sheet)
 state.update(status='staged'if manifest['models']else'complete-directory-no-exact-model',manifest=relative(HERE/'staged'/sheet/'manifest.json'),counts=manifest['counts'],finishedAt=now());write(state_path,state)
 return state


def report(plan,network):
 states={sheet:read(HERE/'sources'/sheet/'state.json')for sheet in plan['tiles']if (HERE/'sources'/sheet/'state.json').exists()};rows=[]
 for target in plan['targets']:
  parts=[];models=[];complete=True
  for sheet in target.get('sheets',[]):
   state=states.get(sheet,{});entries=[name for name in state.get('exactGLTFEntries',[])if name.startswith('BUILDING/B'+target['csuid'][:10])]
   part={'sheet':sheet,'status':state.get('status','deferred-not-run'),'exactEntries':entries,'directory':state.get('directoryCheck'),'error':state.get('error')};parts.append(part)
   if state.get('status')not in ('staged','complete-directory-no-exact-model'):complete=False
   if state.get('manifest'):
    for model in read(ROOT/state['manifest'])['models']:
     if model['geoRefNo']==target['csuid'][:10]:models.append({'sheet':sheet,'modelId':model['id'],'manifest':state['manifest'],'exactCSUIDMatch':target['csuid']in model['officialBuildingCSUIDs'],'officialBuildingCSUIDs':model['officialBuildingCSUIDs'],'sourceHashes':model['sourceHashes'],'nativeBounds':model['worldBounds'],'triangles':model['triangles']})
  outcome='acquired-and-staged'if models else'no-exact-model-in-complete-checked-sheets'if complete and parts else'deferred'
  rows.append({**target,'outcome':outcome,'standardMatch':any(model['exactCSUIDMatch']for model in models),'models':models,'sheetsChecked':parts})
 summary={key:sum(row['outcome']==key for row in rows)for key in ('acquired-and-staged','no-exact-model-in-complete-checked-sheets','deferred')}
 result={'issue':'HKS-213','batchId':plan.get('batchId','original-115'),'generatedAt':now(),'plan':relative(HERE/'plan.json'),'planSHA256':sha((HERE/'plan.json').read_bytes()),'serviceMetadata':relative(HERE/'service.json'),'sourceIndex':relative(HERE/'index.json'),'summary':summary,'nativeModelParts':sum(len(row['models'])for row in rows),'exactCSUIDMatchedTargets':sum(row['standardMatch']for row in rows),'sourceTiles':len(plan['tiles']),'completedTiles':sum(state.get('status')in('staged','complete-directory-no-exact-model')for state in states.values()),'reusedDirectories':sum(bool(state.get('directoryReusedFrom'))for state in states.values()),'reusedNativeMembers':sum(bool(member.get('reusedFrom'))for state in states.values()for member in state.get('members',{}).values()),'newNativeMembers':sum(bool(member.get('range'))for state in states.values()for member in state.get('members',{}).values()),'transfer':{'receivedBytes':network.data['receivedBytes'],'newThisInvocationBytes':network.data['receivedBytes']-network.initial,'chargedBytes':network.data['chargedBytes'],'capBytes':network.cap,'requests':len(network.data['requests']),'ledger':relative(network.path)},'rows':rows,'qualification':'No-exact-model is only for complete current checked official sheet directories, not a territory-wide absence claim. Source acquisition/staging is not placement acceptance or publication. Native source geometry remains 1x HKPD; no modelling or terrain fixes.','aiCalls':0}
 write(DOCS/'report.json',result);return result


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan-only',action='store_true');parser.add_argument('--limit-tiles',type=int);parser.add_argument('--refresh-head',action='store_true');parser.add_argument('--batch');parser.add_argument('--targets-source');parser.add_argument('--budget-mb',type=int);parser.add_argument('--workers',type=int);args=parser.parse_args()
 config=configure_batch(args.batch,args.targets_source,args.budget_mb)
 HERE.mkdir(parents=True,exist_ok=True);network=Network(HERE/'transfer-ledger.json',cap=config['capBytes']if config else CAP)
 plan=read(HERE/'plan.json')if (HERE/'plan.json').exists()else prepare(network)
 print(f'Plan: {plan["targetParts"]} exact-ID parts across {plan["officialTiles"]} official sheets',flush=True)
 if args.plan_only:print(json.dumps(report(plan,network)['summary']));return
 targets={target['uid']:target for target in plan['targets']};caches=retained_caches()
 workers=args.workers if args.workers is not None else(4 if config else 1)
 if not 1<=workers<=8:raise ValueError('Workers must be between1 and8')
 network.data['maxConcurrentSheetWorkers']=workers;write(network.path,network.data)
 priority={target['uid']:i for i,target in enumerate(plan['targets'])}
 ordered=sorted(plan['tiles'].items(),key=lambda item:(item[0]not in caches,min(priority[uid]for uid in item[1]['uids'])))
 pending=[]
 for sheet,tile in ordered:
  previous=HERE/'sources'/sheet/'state.json'
  if previous.exists()and read(previous).get('status')in('staged','complete-directory-no-exact-model')and not args.refresh_head:continue
  pending.append((sheet,tile))
 if args.limit_tiles is not None:pending=pending[:args.limit_tiles]
 def work(item):
  sheet,tile=item;previous=HERE/'sources'/sheet/'state.json'
  try:
   state=acquire_tile(network,sheet,tile,targets,caches,args.refresh_head)
   return sheet,state,None
  except Exception as error:
   state=read(previous)if previous.exists()else{'sheet':sheet,'members':{}};state.update(status='deferred-byte-cap'if isinstance(error,BudgetExceeded)else'deferred-error',error=f'{type(error).__name__}: {error}');write(previous,state)
   return sheet,state,error
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers)as pool:
  futures={pool.submit(work,item):item[0]for item in pending}
  for future in concurrent.futures.as_completed(futures):
   sheet,state,error=future.result()
   print(sheet,state['status'],state.get('error')if error else str(len(state.get('exactGLTFEntries',[])))+' model entries',network.data['receivedBytes'],'bytes cumulative',flush=True)
   report(plan,network)
 result=report(plan,network);print(json.dumps({'summary':result['summary'],'transfer':result['transfer'],'nativeModelParts':result['nativeModelParts']},indent=2))
if __name__=='__main__':main()
