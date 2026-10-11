"""DRAFT exact four original individualised GLTF/bin/texture members; no conversion or acceptance."""
import json,re,sys
from pathlib import Path,PurePosixPath
from run import ROOT,HERE,read,save,digest,connect
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request,BASE as OUTLINE_BASE
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-museum-open-sided-original-gltf-members-acquisition-v1-20261011';DOC=B/BATCH
PLAN=B/'government-xl-science-museum-open-sided-original-source-acquisition-method-v1-20261011/plan.json';FRESH=B/'government-xl-science-museum-open-sided-fresh-official-allclass-directory-search-v1-20261011';CSUID='3631518015T20071227';MODEL='B363151801501063A0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def query(url,params,name):
 raw,receipt=request(url,params);DOC.mkdir(parents=True,exist_ok=True);(DOC/(name+'.json')).write_bytes(raw);save(DOC/(name+'.request.json'),receipt);return json.loads(raw)
def main():
 assert not DOC.exists();plan=read(PLAN);assert plan['modelId']==MODEL and plan['stableCSUID']==CSUID and plan['sourceModelMemberRequests']==4
 for e in plan['evidenceRefs']:assert ref(ROOT/e['path'])==e
 receipt=read(FRESH/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 fresh=read(FRESH/'diagnostic.json.gz');assert fresh['completeBoundedFreshOfficialSearch']and not fresh['errors'];found={part.split('.')[0].upper()for r in fresh['freshDirectoryResults']for member in r['exactGeoRefPrefixMembers']for part in PurePosixPath(member['name']).parts if re.fullmatch(r'[A-Za-z]+3631518015(01|02)06[0-9A-Z]{3}',part.split('.')[0],re.I)};assert found=={MODEL},'Ambiguous all-class source nomination'
 source=[r for r in fresh['freshDirectoryResults']if r['indexFamily']=='individualised'and r['format']=='Format_glTF'];assert len(source)==1;source=source[0];assert source['sheet']==plan['sheet']and source['etag']==plan['etag']and source['revision']==plan['revision']and source['sourceURL']==plan['sourceURL'];nom=[m for m in source['nativeGLTFModels']if m['geoRefNo']=='3631518015'];assert len(nom)==1 and nom[0]['modelId']==MODEL
 rawdir=FRESH/'directories/individualised'/source['sheet']/'Format_glTF/zip-directory.bin';infos,check=ac.parse_directory(rawdir.read_bytes());assert check['directorySHA256']==source['directorySHA256'];selected=[e for e in infos if e.filename.startswith('BUILDING/'+MODEL+'/')and not e.is_dir()];assert len(selected)==4 and {e.filename for e in selected}=={e['name']for e in plan['members']};positions={e.filename:i for i,e in enumerate(infos)}
 index_url=fresh['officialIndexFamilies']['individualised'];params=dict(f='json',where="SHEETNO='"+source['sheet']+"'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100');outline_params=dict(f='json',where="BuildingCSUID='"+CSUID+"'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100')
 expected=read(FRESH/'individualised-official-covering-index-before.json')['features'];assert len(expected)==1
 def fences(label):
  idx=query(index_url,params,'official-index-'+label);assert not idx.get('exceededTransferLimit')and idx['features']==expected
  outline=query(OUTLINE_BASE+'/0/query',outline_params,'official-csuid-'+label);assert outline==fresh['currentOutlineQueries']['exact-csuid']
 fences('before');net=ac.Network(DOC/'member-transfer.json',cap=2_000_000);_,head=net.get(source['sourceURL'],0,etag=source['etag'],method='HEAD');assert head.get('ETag')==source['etag']and int(head['Content-Length'])==source['archiveBytes'];members=[]
 for entry in selected:
  assert not PurePosixPath(entry.filename).is_absolute()and'..'not in PurePosixPath(entry.filename).parts and'\\'not in entry.filename
  pinned=next(e for e in plan['members']if e['name']==entry.filename);assert (entry.CRC,entry.header_offset,entry.compress_size,entry.file_size)==(pinned['crc32'],pinned['headerOffset'],pinned['compressedBytes'],pinned['decodedBytes'])
  i=positions[entry.filename];stop=(infos[i+1].header_offset if i+1<len(infos)else check['centralDirectoryOffset'])-1;assert 0<stop-entry.header_offset+1<=1_300_000
  raw,_=net.get(source['sourceURL'],stop-entry.header_offset+1,f'{entry.header_offset}-{stop}',source['etag']);value=ac.unpack_member(raw,entry);dest=DOC/'original-members'/entry.filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value);members.append(dict(name=entry.filename,sourceCRC32=entry.CRC,sourceHeaderOffset=entry.header_offset,sourceCompressedBytes=entry.compress_size,bytes=len(value),sourceRange=[entry.header_offset,stop],file=ref(dest)))
 gltf_path=DOC/'original-members/BUILDING'/MODEL/(MODEL+'.gltf');gltf=json.loads(gltf_path.read_bytes());uris=[]
 for section in ['buffers','images']:
  for item in gltf.get(section,[]):
   assert 'uri'in item, 'Embedded/source extension requires separate review';uri=PurePosixPath(item['uri']);assert not uri.is_absolute()and'..'not in uri.parts and':'not in item['uri']and'\\'not in item['uri'];full=str(PurePosixPath('BUILDING')/MODEL/uri);assert full in {e.filename for e in selected};uris.append(dict(section=section,originalURI=item['uri'],member=full))
 assert {x['member']for x in uris}=={e.filename for e in selected if not e.filename.endswith('.gltf')};_,after=net.get(source['sourceURL'],0,etag=source['etag'],method='HEAD');assert after.get('ETag')==source['etag']and int(after['Content-Length'])==source['archiveBytes'];fences('after')
 for e in plan['evidenceRefs']:assert ref(ROOT/e['path'])==e
 refs=[ref(Path(__file__)),ref(PLAN),ref(rawdir),ref(FRESH/'result.json'),ref(FRESH/'diagnostic.json.gz'),ref(HERE.parent/'landmark-acquisition/acquire.py'),ref(HERE.parent/'citywide-source/discover.py'),ref(HERE.parent/'landsd-territory/source.py')];refs.extend(ref(p)for p in sorted(DOC.rglob('*'))if p.is_file())
 save(DOC/'acquisition.json',dict(uid='landsd/83471:0',stableCSUID=CSUID,modelId=MODEL,sourceFamily='individualised',sheet=source['sheet'],revision=source['revision'],etag=source['etag'],sourceURL=source['sourceURL'],sourceDirectorySHA256=source['directorySHA256'],sourceArchiveBytes=source['archiveBytes'],completeOriginalMembers=members,completeOriginalGLTFBufferAndImageDependencies=uris,allOriginalTexturesPreserved=True,sourceOnly=True,currentAcceptance=False,identityAccepted=False,sourceModelMemberRequests=4,governmentGeometryChanges=0,conversionPerformed=False,sourcePoseChanged=False,worldHeightInferred=False,neonNativeRegistryWrites=0,qualification='Exact untouched original GLTF/bin and both textures from one version/ETag/CRC-bound individualised source model. Product family nomination and GeoRef uniqueness are not fullCSUID geometry identity or placement approval. Original material/pose/hierarchy remains unedited. Existing63 Museum overlapfaces/raw1.855m2 guard and full source/current obligations preserved.',evidenceRefs=refs));print(json.dumps(dict(modelId=MODEL,sourceMembers=len(members),receivedBytes=net.data['receivedBytes'],geometryChanges=0,identityAccepted=False)),flush=True)
if __name__=='__main__':main()
