"""Audit every Pui O fallback against current official source ZIP catalogues.
No relaxed identity matching and no live mutation. Reuses the source pipeline.
"""
import collections,datetime,gzip,hashlib,json,pathlib,struct,urllib.request
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent/'pui-o-completion';DOC=ROOT/'docs/astra-city/pui-o-detail-completion'
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def request(url,span):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes='+span}),timeout=60) as r:
  assert r.status==206;assert int(r.headers['Content-Length'])<=4*1024*1024,'Reject oversized directory responses before reading';raw=r.read();headers=dict(r.headers);assert len(raw)==int(headers['Content-Length']);return raw,headers

def directory_entries(raw):
 entries=[];offset=0
 while raw[offset:offset+4]==b'PK\x01\x02':
  header=struct.unpack('<4s6H3L5H2L',raw[offset:offset+46]);name_len,extra_len,comment_len=header[10:13];name=raw[offset+46:offset+46+name_len].decode('utf-8' if header[3]&2048 else 'cp437');size=header[9]
  if size==0xffffffff:
   extra=raw[offset+46+name_len:offset+46+name_len+extra_len];i=0
   while i<len(extra):
    tag,length=struct.unpack('<HH',extra[i:i+4])
    if tag==1:size=struct.unpack('<Q',extra[i+4:i+12])[0];break
    i+=4+length
  entries.append({'filename':name,'file_size':size,'CRC':header[7]});offset+=46+name_len+extra_len+comment_len
 assert raw[offset:offset+4] in [b'PK\x05\x06',b'PK\x06\x06'],'Directory ended unexpectedly'
 return entries

def audit(individual=False):
 index_name='individual-index.json' if individual else 'index.json'; directory_name='individual-directories' if individual else 'directories'; output_name='individual-audit.json' if individual else 'audit.json'
 index=json.loads((HERE/index_name).read_text());assert not index.get('exceededTransferLimit')
 buildings=json.loads(gzip.decompress((BASE/'building-selection.json.gz').read_bytes()))['buildings'];existing=json.loads((BASE/'compact/catalogue.json').read_text());known={m['uid'] for m in existing['models']};remaining=[b for b in buildings if b['uid'] not in known]
 sheets=[];entries=[]
 for f in index['features']:
  a=f['attributes'];tile=a['SHEETNO'];record=HERE/directory_name/f'{tile}.json'
  if record.exists():
   s=json.loads(record.read_text());expected_revision=datetime.datetime.fromtimestamp(a['REVISIONDATE']/1000,datetime.timezone.utc).isoformat();assert s['revision']==expected_revision and s['url']==a['Format_glTF'],'Source index changed: review/invalidate retained directory cache before refresh'
  else:
   url=a['Format_glTF'];raw,h=request(url,'-65536');start=int(h['Content-Range'].split()[1].split('-')[0]);size=int(h['Content-Range'].split('/')[-1]);pos=raw.rfind(b'PK\x05\x06');assert pos>=0
   sig,disk,cd_disk,n_disk,n_total,cd_size,cd_offset,comment=struct.unpack('<4s4H2LH',raw[pos:pos+22]);assert disk==cd_disk==0 and n_disk==n_total
   if cd_offset==0xffffffff or cd_size==0xffffffff or n_total==65535:
    zip64pos=raw.rfind(b'PK\x06\x06');assert zip64pos>=0,'ZIP64 end record must be retained in tail'
    _,record_size,version_made,version_needed,disk64,cd_disk64,n_disk,n_total,cd_size,cd_offset=struct.unpack('<4sQ2H2L4Q',raw[zip64pos:zip64pos+56]);assert disk64==cd_disk64==0 and n_disk==n_total
   assert 0<=cd_offset<size and 0<=cd_size<=4*1024*1024,'Bound directory acquisition before any range fetch'
   requests=[{'span':'-65536','bytes':len(raw),'sha256':sha(raw),'contentRange':h['Content-Range']}]
   if cd_offset<start:
    assert start-cd_offset<=4*1024*1024,'Reject oversized directory request before network access'
    prefix,ph=request(url,f'{cd_offset}-{start-1}');assert ph.get('ETag')==h.get('ETag');requests.append({'span':f'{cd_offset}-{start-1}','bytes':len(prefix),'sha256':sha(prefix),'contentRange':ph['Content-Range']});directory=prefix+raw
   else:directory=raw[cd_offset-start:]
   # Read original central records directly; ZIP64 locators retain archive offsets.
   infos=directory_entries(directory)
   assert len(infos)==n_total
   (HERE/directory_name).mkdir(exist_ok=True);(HERE/directory_name/f'{tile}.bin').write_bytes(directory)
   s={'tile':tile,'revision':datetime.datetime.fromtimestamp(a['REVISIONDATE']/1000,datetime.timezone.utc).isoformat(),'url':url,'sourceETag':h.get('ETag'),'sourceLastModified':h.get('Last-Modified'),'sourceArchiveBytes':size,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directorySha256':sha(directory),'entries':len(infos),'transferredBytes':sum(x['bytes'] for x in requests),'requests':requests,'models':[{'path':i['filename'],'modelId':pathlib.PurePosixPath(i['filename']).stem,'geoRefNo':pathlib.PurePosixPath(i['filename']).stem[1:11],'bytes':i['file_size'],'crc32':i['CRC']} for i in infos if i['filename'].endswith('.gltf')]}
   save(record,s)
  sheets.append(s)
  for e in s['models']:entries.append({**e,'tile':tile})
  print(tile,len(s['models']),flush=True)
 byref=collections.defaultdict(list)
 for e in entries:byref[e['geoRefNo']].append(e)
 manifest_models=[{**m,'tile':p.parent.name} for p in (BASE/'staged').glob('*/manifest.json') for m in json.loads(p.read_text())['models']]
 ledger=[]
 for b in remaining:
  ref=b['sourceAttributes']['GeoRefNo'];candidates=byref.get(ref,[]);staged=[m for m in manifest_models if m['geoRefNo']==ref]
  status='candidate-requires-exact-geometry-check' if candidates else 'no-exact-reference-model-in-current-local-source-sheets'
  if candidates and staged and all(not m['officialBuildingCSUIDs'] for m in staged):status='existing-source-model-fails-unchanged-geometric-match'
  ledger.append({'uid':b['uid'],'buildingCSUID':b['buildingCSUID'],'geoRefNo':ref,'structureType':b['structureType'],'centre':b['centre'],'candidates':candidates,'status':status,'existingGeometricScreens':[{'modelId':m['id'],'tile':m['tile'],'worldBounds':m['worldBounds'],'matches':m['officialMatches']} for m in staged]})
 report={'scope':'Existing 919-form Pui O selection, four sheets plus 35 m matching buffer; 15 current intersecting source sheets inspected. No claim about whole Lantau.','dataset':'landsd_rcd_1671676915450_88604' if individual else 'landsd_rcd_1742809441342_98380','selectionSha256':sha((BASE/'building-selection.json.gz').read_bytes()),'existingCatalogueSha256':sha((BASE/'compact/catalogue.json').read_bytes()),'indexSha256':sha((HERE/index_name).read_bytes()),'counts':{'selectedForms':len(buildings),'existingDetailed':len(known),'fallback':len(remaining),'sheets':len(sheets),'catalogueEntries':len(entries),'sourceArchiveBytes':sum(s['sourceArchiveBytes'] for s in sheets),'directoryTransferredBytes':sum(s['transferredBytes'] for s in sheets),'statuses':dict(collections.Counter(r['status'] for r in ledger)),'fallbackStructureTypes':dict(collections.Counter(r['structureType'] for r in ledger))},'ledger':ledger}
 save(DOC/output_name,report);print(json.dumps(report['counts'],indent=2))
if __name__=='__main__':
 import sys
 audit('--individual' in sys.argv)
