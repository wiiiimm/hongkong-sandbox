"""DRAFT bounded official terrain directory discovery, no member acquisition/acceptance."""
from pathlib import Path
import json,struct,sys,concurrent.futures
from fractions import Fraction as F
from shapely.geometry import Polygon,box
import shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-mongkok-stadium240332-adjacent-authentic-tin-directory-search-v2-20261011';DOC=B/NAME;PRIOR=B/'government-xl-mongkok-stadium240332-actual-native-union-authentic-core-inventory-v2-20261011';AUTH=B/'government-xl-mongkok-stadium240332-complete-original-authentic-tin-finite-v1-20261011'
INDEX='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query';MAX_SHEETS=4
METHOD=B/'government-xl-mongkok-stadium240332-adjacent-authentic-tin-method-v2-20261011/METHOD.md'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def query(params,label):
 raw,rec=request(INDEX,params,method='POST');DOC.mkdir(parents=True,exist_ok=True);(DOC/(label+'.json')).write_bytes(raw);save(DOC/(label+'.request.json'),rec);return json.loads(raw)
def covering(data,foot):
 assert isinstance(data.get('features'),list)and not data.get('exceededTransferLimit');assert data.get('spatialReference',{}).get('latestWkid',data.get('spatialReference',{}).get('wkid'))in(2326,102140)
 accepted=[];touch=[]
 for f in data['features']:
  rings=f['geometry']['rings'];assert rings and all(r[0]==r[-1]for r in rings);p=Polygon(rings[0],rings[1:]);assert p.is_valid and not p.is_empty
  if p.intersection(foot).area>0:accepted.append(f)
  else:touch.append(f['attributes']['SHEETNO'])
 assert 1<=len(accepted)<=MAX_SHEETS and len({r['attributes']['SHEETNO']for r in accepted})==len(accepted);assert shapely.union_all([Polygon(f['geometry']['rings'][0],f['geometry']['rings'][1:])for f in accepted]).covers(foot)
 return sorted(accepted,key=lambda r:r['attributes']['SHEETNO']),sorted(touch)
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 d=decoded(read(PRIOR/'diagnostic.json.gz'));assert len(d['allUncoveredNativeFacets'])==50 and not d['actualFiniteNativeUnionCoreProvenanceAndProjectionQualified'];pts=[q for row in d['allUncoveredNativeFacets']for p in row['allUncoveredPositivePolygons']for q in p];bounds=[min(p[k]for p in pts)for k in[0,1]]+[max(p[k]for p in pts)for k in[0,1]];assert bounds==[F(1500),F('-8615/2'),F('3025/2'),F('-8335/2')]
 # Exact bounds come from every saved uncovered polygon. The envelope selects
 # source sheets only; it is not a new terrain/candidate recovery domain.
 hk_bounds=[float(bounds[0]+834500),float(816500-bounds[3]),float(bounds[2]+834500),float(816500-bounds[1])];foot=box(*hk_bounds);ring=[[hk_bounds[0],hk_bounds[1]],[hk_bounds[0],hk_bounds[3]],[hk_bounds[2],hk_bounds[3]],[hk_bounds[2],hk_bounds[1]],[hk_bounds[0],hk_bounds[1]]];params=dict(f='json',where='1=1',geometry=json.dumps(dict(rings=[ring],spatialReference=dict(wkid=2326)),separators=(',',':')),geometryType='esriGeometryPolygon',inSR='2326',outSR='2326',spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',resultRecordCount='100');data=query(params,'official-covering-index-before');rows,touches=covering(data,foot);errors=[];results=[]
 def work(f):
  a=f['attributes'];url=a['Format_glTF'];assert url.startswith('https://download.map.gov.hk/')and 'REVISIONDATE'in a;folder=DOC/'directories'/a['SHEETNO'];folder.mkdir(parents=True,exist_ok=True);net=ac.Network(folder/'directory-transfer.json',cap=8_000_000);_,head=net.get(url,0,method='HEAD');etag=head.get('ETag');assert etag;size=int(head['Content-Length']);tail,h=net.get(url,65536,'-65536',etag);i=tail.rfind(b'PK\x05\x06');assert i>=0;fields=struct.unpack('<4s4H2LH',tail[i:i+22]);offset=fields[6];start=int(h['Content-Range'].split()[1].split('-')[0]);assert int(h['Content-Range'].split('/')[-1])==size
  if offset<start:prefix,_=net.get(url,start-offset,f'{offset}-{start-1}',etag);directory=prefix+tail
  else:directory=tail[offset-start:]
  infos,check=ac.parse_directory(directory);assert check['directorySHA256']==digest(directory);(folder/'zip-directory.bin').write_bytes(directory);members=[dict(name=e.filename,crc32=e.CRC,headerOffset=e.header_offset,compressedBytes=e.compress_size,decodedBytes=e.file_size)for e in infos];terrain=[m for m in members if Path(m['name']).parts[0].startswith('TERRAIN')and m['name'].lower().endswith(('.gltf','.bin'))];_,after=net.get(url,0,method='HEAD');assert after.get('ETag')==etag and int(after['Content-Length'])==size;out=dict(sheet=a['SHEETNO'],sourceURL=url,revision=a['REVISIONDATE'],etag=etag,archiveBytes=size,completeArchiveMembers=members,allOriginalTerrainGLTFAndBinMembers=terrain,sourceMemberRequests=0,**check);save(folder/'directory.json.gz',out);return out
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures={pool.submit(work,f):f for f in rows}
  for future in concurrent.futures.as_completed(futures):
   try:results.append(future.result())
   except Exception as e:errors.append(dict(sheet=futures[future]['attributes']['SHEETNO'],error=type(e).__name__+': '+str(e)[:300]))
 after=query(params,'official-covering-index-after');assert covering(after,foot)==(rows,touches),'Official sheet index changed';original=read(HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz');results.sort(key=lambda x:x['sheet']);refs=[ref(p)for p in[Path(__file__),METHOD,HERE/'mongkok_stadium240332_adjacent_authentic_tin_directory_search_v1_20261011.py',HERE/'local/government-xl-mongkok-stadium240332-adjacent-authentic-tin-directory-search-v1-20261011/failed-official-index-get-attempt.json',PRIOR/'result.json',PRIOR/'diagnostic.json.gz',HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz',HERE.parent/'landsd-territory/source.py',HERE.parent/'citywide-source/discover.py',HERE.parent/'landmark-acquisition/acquire.py']];refs.extend(ref(p)for p in DOC.rglob('*')if p.is_file());save(DOC/'diagnostic.json.gz',dict(uids=['landsd/240332:0','landsd/240527:0'],sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,originalSourceGeometryChanges=0,liveTerrainChanges=0,sourceMemberRequests=0,exactUncoveredFringeWorldBounds=[str(x)for x in bounds],officialQueryHKGridBounds=hk_bounds,queryBoundsSelectSheetsOnly=True,officialIndexURL=INDEX,completeOfficialCoveringFeatures=rows,excludedBoundaryOnlySheetTouches=touches,freshDirectoryResults=results,originalCachedSheet='11-NW-14D',originalCachedRevision=original['sourceRevision'],allFreshSheetsMatchOriginalCachedRevision=not errors and all(q['revision']==original['sourceRevision']for q in results),completeBoundedFreshDirectorySearch=not errors and len(results)==len(rows),errors=errors,raw50CoverageAnd494SourceOverlapFailuresPreserved=True,evidenceRefs=refs,qualification='Bounded official source-sheet directory availability only. Every source member, index revision, ETag and CRC remains explicit. No glTF/bin member acquired, no adjacent source identity/terrain elevation/projection/seam qualification, no current/native/candidate approval. Fresh revision mismatch prevents silently mixing historical source revisions. All494 exact originalsource overlaps and protected240527 obligations remain independent. Next member plan must uniquely select actual terrain dependencies with exact version/ETag and complete original pose/source provenance before finite union recompute.'))
 print(json.dumps(dict(sheets=[q['sheet']for q in results],errors=errors,sourceMemberRequests=0)),flush=True)
if __name__=='__main__':main()
