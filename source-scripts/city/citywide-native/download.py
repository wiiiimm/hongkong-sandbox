"""HKS-222 grouped, checksum-verified acquisition of original government members."""
import hashlib,importlib.util,json,pathlib,urllib.parse,zipfile,zlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('native_acquisition',HERE.parent/'landmark-acquisition/acquire.py');ac=importlib.util.module_from_spec(spec);spec.loader.exec_module(ac)
def spans(infos,selected,central,max_bytes=8*1024*1024):
 positions={e.filename:i for i,e in enumerate(infos)};groups=[]
 for entry in sorted(selected,key=lambda e:e.header_offset):
  i=positions[entry.filename];stop=(infos[i+1].header_offset if i+1<len(infos) else central)-1
  start=entry.header_offset
  if groups and start-groups[-1][1]<=1024 and stop-groups[-1][0]+1<=max_bytes:
   groups[-1][1]=stop;groups[-1][2].append(entry)
  else:groups.append([start,stop,[entry]])
 return groups

def safe(name):
 p=pathlib.PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('Unsafe source member path')
 return name

def acquire(row,directory,out,retained=(),include_terrain=False):
 assert urllib.parse.urlsplit(row['sourceURL']).scheme=='https' and urllib.parse.urlsplit(row['sourceURL']).hostname=='download.map.gov.hk'
 out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True);record_path=out/'download.json';archive=out/(row['sheet']+'.zip')
 raw=pathlib.Path(directory).read_bytes();assert ac.sha(raw)==row['directorySHA256'];infos,check=ac.parse_directory(raw);by_name={e.filename:e for e in infos}
 names={m['name'] for model in row['models'] for m in model['members']}
 if include_terrain:names.update(e.filename for e in infos if e.filename.startswith('TERRAIN') and e.filename.endswith(('.gltf','.bin')))
 selected=[by_name[safe(name)] for name in sorted(names)]
 for model in row['models']:
  for m in model['members']:
   e=by_name[m['name']];assert (e.CRC,e.header_offset,e.compress_size,e.file_size)==(m['crc32'],m['headerOffset'],m['compressedBytes'],m['decodedBytes'])
 if record_path.exists() and archive.exists():
  record=ac.read(record_path)
  if record.get('dependencyScanVersion')==1 and record.get('terrainGeometryIncluded',False)==include_terrain and record['sourceETag']==row['etag'] and record['directorySHA256']==row['directorySHA256'] and ac.sha(archive.read_bytes())==record['sha256']:
   with zipfile.ZipFile(archive) as z:
    # A valid compact ZIP may cover an earlier, smaller selection on this sheet.
    # Reuse its verified members below and fetch only the newly requested ones.
    if names.issubset(z.namelist()):
     for e in selected:
      value=z.read(e.filename);assert len(value)==e.file_size and zlib.crc32(value)&0xffffffff==e.CRC
     return record
 if record_path.exists() and archive.exists():retained=list(retained)+[(record_path,ac.read(record_path))]
 values={};origin={}
 for path,record in retained:
  if record.get('source')!=row['sourceURL'] or record.get('sourceETag')!=row['etag']:continue
  old=path.parent/(row['sheet']+'.zip')
  if not old.is_file() or ac.sha(old.read_bytes())!=record.get('sha256'):continue
  with zipfile.ZipFile(old) as z:
   for name in names.intersection(z.namelist())-values.keys():
    e=by_name[name];value=z.read(name)
    if len(value)==e.file_size and zlib.crc32(value)&0xffffffff==e.CRC:values[name]=value;origin[name]='retained-verified-cache'
 planned=spans(infos,selected,check['centralDirectoryOffset']);budget=sum(end-start+1 for start,end,_ in planned)
 net=ac.Network(out/'transfer.json',cap=max(1_000_000,budget*3+1_000_000))
 def fetch(entries):
  for start,end,members in spans(infos,entries,check['centralDirectoryOffset']):
   path=out/f'range-{start}-{end}.bin';proof=path.with_suffix('.json')
   valid=path.exists() and proof.exists() and ac.read(proof).get('etag')==row['etag'] and ac.sha(path.read_bytes())==ac.read(proof).get('sha256')
   if valid:blob=path.read_bytes()
   else:
    blob,_=net.get(row['sourceURL'],end-start+1,f'{start}-{end}',row['etag']);path.write_bytes(blob);ac.write(proof,{'etag':row['etag'],'sha256':ac.sha(blob)})
   for e in members:values[e.filename]=ac.unpack_member(blob[e.header_offset-start:],e);origin[e.filename]='verified-range'
 fetch([e for e in selected if e.filename not in values])
 # Discover archive-local dependencies before conversion; no arbitrary URL requests.
 dependencies=set()
 for name in sorted(names):
  if not name.endswith('.gltf'):continue
  try:data=json.loads(values[name])
  except (ValueError,UnicodeError):continue  # converter records this model's explicit parse failure
  for entry in data.get('buffers',[])+(data.get('images',[]) if name.startswith('BUILDING/') else []):
   uri=entry.get('uri','')
   if not uri or uri.startswith('data:'):continue
   if urllib.parse.urlsplit(uri).scheme:continue  # converter records external dependencies as held
   dep=safe(str(pathlib.PurePosixPath(name).parent/urllib.parse.unquote(uri)))
   if dep in by_name:dependencies.add(dep)
 missing=[by_name[n] for n in dependencies-values.keys()]
 if missing:
  extra=sum(end-start+1 for start,end,_ in spans(infos,missing,check['centralDirectoryOffset']))
  net.cap+=extra*3;fetch(missing)
 selected=[by_name[n] for n in sorted(values)]
 temp=archive.with_suffix('.zip.part')
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for e in selected:
   info=zipfile.ZipInfo(e.filename,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,values[e.filename])
 temp.replace(archive)
 record={'sheet':row['sheet'],'source':row['sourceURL'],'revisionDate':ac.datetime.datetime.fromtimestamp(row['revision']/1000,ac.datetime.timezone.utc).isoformat(),'sourceETag':row['etag'],'directorySHA256':row['directorySHA256'],'sha256':ac.sha(archive.read_bytes()),'archiveSha256':None,'bytes':archive.stat().st_size,'cacheKind':'Derived compact ZIP of unmodified original government building members; not the full source archive','entries':[{'name':e.filename,'bytes':len(values[e.filename]),'sha256':ac.sha(values[e.filename]),'sourceCRC32':e.CRC,'sourceCompressedBytes':e.compress_size,'origin':origin[e.filename]} for e in selected],'expectedModels':len(row['models']),'receivedBytes':net.data['receivedBytes'],'newThisInvocationBytes':net.data['receivedBytes']-net.initial,'sourceArchiveBytes':row['archiveBytes'],'dependencyScanVersion':1,'terrainGeometryIncluded':include_terrain,'terrainPhotographsOmitted':include_terrain}
 ac.write(record_path,record);return record
