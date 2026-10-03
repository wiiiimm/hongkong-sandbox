"""Audit the frozen Tai O selection against complete official archive directories.
Read-only with respect to live city assets. Never equate archive availability with a verified import.
"""
import collections,datetime,gzip,hashlib,io,json,pathlib,struct,sys,urllib.parse,urllib.request,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=HERE.parent/'tai-o-models';DOC=ROOT/'docs/astra-city/tai-o-detail-completion'
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def index():
 params=dict(f='json',geometry='802940,812545,804560,813255',geometryType='esriGeometryEnvelope',inSR=2326,outSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',returnCountOnly='false',resultRecordCount=2000)
 url='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query?'+urllib.parse.urlencode(params)
 raw=urllib.request.urlopen(url,timeout=60).read();data=json.loads(raw);assert 'error' not in data and not data.get('exceededTransferLimit');(HERE/'index.json').write_bytes(raw);dump(HERE/'index-provenance.json',{'url':url,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':sha(raw),'features':len(data['features']),'exceededTransferLimit':False});return data

def directory(attrs):
 tile=attrs['SHEETNO'];dest=HERE/'directories'/f'{tile}.json'
 if dest.exists():return json.loads(dest.read_text())
 folder=OLD/'sources'/tile;cached=folder/'zip-directory.bin'
 if cached.exists():
  raw=cached.read_bytes();end=raw.rfind(b'PK\x05\x06');eocd=struct.unpack('<4s4H2LH',raw[end:end+22]);start=eocd[6];size=start+len(raw);retained={'kind':'previous retained complete ZIP directory','path':str(cached.relative_to(ROOT)),'sha256':sha(raw),'additionalTransferredBytes':0,'download':str((folder/'download.json').relative_to(ROOT))}
 else:
  spans=[]
  def request(span):
   with urllib.request.urlopen(urllib.request.Request(attrs['Format_glTF'],headers={'Range':'bytes='+span}),timeout=60) as r:
    data=r.read();assert r.status==206;offset=int(r.headers['Content-Range'].split()[1].split('-')[0]);size=int(r.headers['Content-Range'].split('/')[-1]);spans.append({'range':span,'contentRange':r.headers['Content-Range'],'bytes':len(data),'sha256':sha(data)});return data,offset,size,dict(r.headers)
  raw,start,size,headers=request('-65536');end=raw.rfind(b'PK\x05\x06');eocd=struct.unpack('<4s4H2LH',raw[end:end+22]);assert eocd[1]==eocd[2]==0 and eocd[3]==eocd[4]
  if eocd[6]<start:head,offset,_,_=request(f'{eocd[6]}-{start-1}');raw=head+raw;start=offset
  raw=raw[eocd[6]-start:];start=eocd[6];(HERE/'directories').mkdir(exist_ok=True);(HERE/'directories'/f'{tile}.bin').write_bytes(raw)
  retained={'kind':'new official complete ZIP directory only','url':attrs['Format_glTF'],'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':sha(raw),'additionalTransferredBytes':sum(r['bytes'] for r in spans),'ranges':spans,'etag':headers.get('ETag'),'lastModified':headers.get('Last-Modified'),'sourceArchiveBytes':size}
 # ZIP parser requires native directory offset; zero-filled compressed members are never read.
 buf=bytearray(size);buf[start:]=raw
 with zipfile.ZipFile(io.BytesIO(buf)) as z:entries=[{'name':i.filename,'bytes':i.file_size,'compressedBytes':i.compress_size,'crc32':i.CRC,'headerOffset':i.header_offset} for i in z.infolist()]
 assert len(entries)==eocd[4]
 result={'sheet':tile,'revision':attrs['REVISIONDATE'],'source':retained,'entries':entries};dump(dest,result);print('Directory',tile,len(entries),flush=True);return result

def main():
 idx=json.loads((HERE/'index.json').read_text()) if (HERE/'index.json').exists() else index()
 directories=[directory(f['attributes']) for f in idx['features']]
 byref=collections.defaultdict(list)
 for d in directories:
  for e in d['entries']:
   if e['name'].startswith('BUILDING/') and e['name'].endswith('.gltf'):
    model=pathlib.PurePosixPath(e['name']).stem;byref[model[1:11]].append({'sheet':d['sheet'],'modelId':model,'entry':e['name']})
 buildings=json.loads(gzip.decompress((OLD/'building-selection.json.gz').read_bytes()))['buildings'];existing=json.loads(gzip.decompress((OLD/'model-geometries.json.gz').read_bytes()))['byBuildingUid'];rows=[]
 for b in buildings:
  ref=b['sourceAttributes']['GeoRefNo'];candidates=byref[ref]
  rows.append({'uid':b['uid'],'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'geoRefNo':ref,'structureType':b['structureType'],'centre':b['centre'],'existingDetailed':b['uid'] in existing,'candidateModels':candidates,'reason':'already-imported' if b['uid'] in existing else 'candidate-requires-source-match' if candidates else 'no-exact-georef-model-in-inspected-building-directories'})
 counts={'selectedForms':len(rows),'existingDetailed':len(existing),'fallback':sum(not r['existingDetailed'] for r in rows),'fallbackWithCandidates':sum(not r['existingDetailed'] and bool(r['candidateModels']) for r in rows),'fallbackWithoutCandidates':sum(not r['existingDetailed'] and not r['candidateModels'] for r in rows),'sheets':len(directories),'additionalDirectoryBytes':sum(d['source']['additionalTransferredBytes'] for d in directories)}
 dump(DOC/'audit.json',{'counts':counts,'selectionSource':str((OLD/'building-selection.json.gz').relative_to(ROOT)),'selectionSha256':sha((OLD/'building-selection.json.gz').read_bytes()),'footprintRevision':'2026-08-19','scope':'Unchanged existing 1,030-form Tai O slice; whole intersecting footprints with 35 m buffer. Neighbouring archive directories checked to cover boundary models.','limits':['Exact GeoRef directory absence establishes no matching BUILDING entry in this inspected product and these sheets; not absence from every government product.','Candidate entries are not accepted upgrades until geometry/identity checks pass.','No existing source fields or live geometry changed.'],'rows':rows});print(json.dumps(counts,indent=2))
if __name__=='__main__':main()
