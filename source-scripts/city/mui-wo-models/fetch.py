"""Retain original glTF/bin ZIP entries using public HTTP byte ranges.
No imagery is extracted or requested except possible ZIP-directory tail bytes.
The compact cache is derived: its hash is never called a complete archive hash.
"""
import datetime,hashlib,io,json,pathlib,struct,time,urllib.request,zipfile
HERE=pathlib.Path(__file__).resolve().parent
TILES=['10-SW-12D','10-SW-17A','10-SW-17B','10-SW-17C','10-SW-17D','10-SW-18A']
def fetch_tiles(here=HERE, tiles=TILES, member_prefixes=None):
 # Case-sensitive ZIP member prefixes (e.g. TERRAIN for TERRAIN(TB)/, or INFRASTRUCTURE/).
 # None retains the original all-glTF/bin behaviour. Source member paths stay intact.
 prefixes=tuple(member_prefixes) if member_prefixes else None
 features={f['attributes']['SHEETNO']:f['attributes'] for f in json.loads((here/'index.json').read_text())['features']}
 for tile in tiles:
  folder=here/'sources'/tile;folder.mkdir(parents=True,exist_ok=True);dest=folder/(tile+'.zip');attrs=features[tile]
  if dest.exists() and (folder/'download.json').exists():
   cached=json.loads((folder/'download.json').read_text()).get('memberPrefixes')
   if cached and (not prefixes or not all(any(p.startswith(c) for c in cached) for p in prefixes)):
    raise ValueError('Existing filtered cache cannot satisfy requested members: '+str(folder))
   print('Retained',tile,dest.stat().st_size,flush=True);continue
  url=attrs['Format_glTF'];requests=[];etag=None
  def request(span):
   headers={'Range':'bytes='+span}
   if etag:headers['If-Range']=etag
   for attempt in range(3):
    try:response=urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60);break
    except Exception:
     if attempt==2:raise
     time.sleep(2*(attempt+1))
   with response:
    assert response.status==206,'Source must honour bounded range request'
    data=response.read();received=dict(response.headers);size=int(received['Content-Range'].split('/')[-1]);offset=int(received['Content-Range'].split()[1].split('-')[0])
    assert len(data)==int(received['Content-Length'])
    requests.append({'requestedRange':span,'contentRange':received['Content-Range'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    return data,offset,size,received
  tail,offset,size,headers=request('-65536');etag=headers.get('ETag')
  end=tail.rfind(b'PK\x05\x06');assert end>=0
  signature,disk,cd_disk,n_disk,n_total,cd_size,cd_offset,comment=struct.unpack('<4s4H2LH',tail[end:end+22]);assert disk==cd_disk==0 and n_disk==n_total
  # Source archives here are ~50 MB. Hold only one at a time; unused bytes stay zero.
  buffer=bytearray(size);buffer[offset:offset+len(tail)]=tail
  if cd_offset<offset:
   directory,start,_,_=request(f'{cd_offset}-{offset-1}');buffer[start:start+len(directory)]=directory
  (folder/'zip-directory.bin').write_bytes(buffer[cd_offset:])
  with zipfile.ZipFile(io.BytesIO(buffer)) as z:infos=sorted(z.infolist(),key=lambda i:i.header_offset)
  selected=[];spans=[]
  for i,entry in enumerate(infos):
   if not entry.filename.endswith(('.gltf','.bin')):continue
   if prefixes and not entry.filename.startswith(prefixes):continue
   assert '..' not in pathlib.PurePosixPath(entry.filename).parts and not entry.filename.startswith('/')
   selected.append(entry);stop=(infos[i+1].header_offset if i+1<len(infos) else cd_offset)-1
   if spans and entry.header_offset-spans[-1][1]<=65536:spans[-1][1]=stop
   else:spans.append([entry.header_offset,stop])
  for start,stop in spans:
   data,actual,_,received=request(f'{start}-{stop}');assert actual==start and len(data)==stop-start+1;assert received.get('ETag')==etag
   buffer[start:stop+1]=data
  entries=[];temporary=dest.with_suffix('.geometry.part')
  with zipfile.ZipFile(io.BytesIO(buffer)) as source,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as output:
   for entry in selected:
    raw=source.read(entry.filename);output.writestr(entry.filename,raw)
    entries.append({'name':entry.filename,'bytes':len(raw),'sourceCompressedBytes':entry.compress_size,'sourceCRC32':entry.CRC,'sha256':hashlib.sha256(raw).hexdigest()})
  temporary.replace(dest);raw=dest.read_bytes()
  record={'source':url,'sheet':tile,'revisionDate':datetime.datetime.fromtimestamp(attrs['REVISIONDATE']/1000,datetime.timezone.utc).isoformat(),'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'archiveSha256':None,'cacheKind':'Derived compact ZIP containing original unmodified glTF/bin entries only','sourceArchiveBytes':size,'sourceETag':etag,'sourceLastModified':headers.get('Last-Modified'),'transferredBytes':sum(r['bytes'] for r in requests),'rangeRequests':requests,'entries':entries,'indexAttributes':attrs}
  if prefixes:record['memberPrefixes']=list(prefixes);record['cacheKind']='Derived compact ZIP containing only selected original unmodified glTF/bin entries'
  (folder/'download.json').write_text(json.dumps(record,indent=2)+'\n');print('Geometry retained',tile,len(entries),'entries',len(raw),'cache bytes',record['transferredBytes'],'transferred',flush=True)
def main():fetch_tiles()
if __name__=='__main__':main()
