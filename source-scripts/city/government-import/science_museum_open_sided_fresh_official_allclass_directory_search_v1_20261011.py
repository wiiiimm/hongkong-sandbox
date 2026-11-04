"""DRAFT fresh bounded Science Museum open-sided source availability lookup; root review before run.
Official2D exact CSUID+object queries and two reviewed3D index families/only genuinely covering sheets,
GLTF+FBX complete ETag-bound central directories only. No mesh acquisition or edit,
source-substitution, current geometry/capture, held-state change or acceptance.
"""
from pathlib import Path
import concurrent.futures,json,re,struct,sys
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request,BASE as OUTLINE_BASE
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac,models
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-museum-open-sided-fresh-official-allclass-directory-search-v1-20261011';DOC=B/BATCH
PRIOR=B/'government-xl-science-museum-open-structure-primary-20261009'
UID='landsd/83471:0';CSUID='3631518015T20071227';GEOREF='3631518015';OLD_OBJECT=83471;MAX_SHEETS=4
INDEXES={'package':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query','individualised':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1671676915450_88604/FeatureServer/0/query'};FORMATS=['Format_glTF','Format_FBX']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def query(url,parameters,name):
 raw,rec=request(url,parameters);p=DOC/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);save(DOC/(name+'.request.json'),rec);return json.loads(raw)
def index_rows(data,footprint):
 assert isinstance(data.get('features'),list)and not data.get('exceededTransferLimit')
 assert data.get('spatialReference',{}).get('latestWkid',data.get('spatialReference',{}).get('wkid'))in (2326,102140)
 accepted=[];excluded=[]
 for f in data['features']:
  rings=f['geometry']['rings'];assert rings and all(r[0]==r[-1]for r in rings)
  polygon=Polygon(rings[0],rings[1:]);assert polygon.is_valid and not polygon.is_empty
  area=polygon.intersection(footprint).area
  if area>0:accepted.append(f)
  else:excluded.append(dict(sheet=f['attributes']['SHEETNO'],intersectionAreaM2=area,qualification='Boundary-only touch, not a genuine covering sheet.'))
 assert 1<=len(accepted)<=MAX_SHEETS and len({f['attributes']['SHEETNO']for f in accepted})==len(accepted)
 assert shapely.union_all([Polygon(f['geometry']['rings'][0],f['geometry']['rings'][1:])for f in accepted]).covers(footprint)
 return sorted(accepted,key=lambda f:f['attributes']['SHEETNO']),excluded
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];errors=[];rows=[]
 receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 refs.extend(ref(PRIOR/n)for n in ['result.json','83471-0-building.json','80343-0-building.json','fresh-source-and-primary-context.json.gz']);refs.append(ref(B/'xl-terrain-recovery-20261009-science-open-structure-context/diagnostic.json.gz'));refs.append(ref(B/'xl-terrain-recovery-20261009-80343-wall-context/diagnostic.json.gz'))
 outline={}
 for label,where in [('exact-csuid',"BuildingCSUID='"+CSUID+"'"),('exact-object','OBJECTID='+str(OLD_OBJECT))]:
  q=query(OUTLINE_BASE+'/0/query',dict(f='json',where=where,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100'), 'outline-'+label);assert isinstance(q.get('features'),list)and not q.get('exceededTransferLimit');outline[label]=q
 exact=[f for f in outline['exact-csuid']['features']if f['attributes'].get('BuildingCSUID')==CSUID];assert len(exact)==1 and exact[0]['attributes']['GeoRefNo']==GEOREF
 actor=exact[0];rings=actor['geometry']['rings'];assert rings and all(r[0]==r[-1]for r in rings);footprint=Polygon(rings[0],rings[1:]);assert footprint.is_valid and not footprint.is_empty
 spatial_parameters=dict(f='json',where='1=1',geometry=json.dumps(actor['geometry'],separators=(',',':')),geometryType='esriGeometryPolygon',inSR='2326',outSR='2326',spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',resultRecordCount='100')
 index_attributes={};covering={};excluded_touches={};tasks=[]
 for family,url in INDEXES.items():
  try:
   q=query(url,spatial_parameters,family+'-official-covering-index-before');features,excluded=index_rows(q,footprint);index_attributes[family]=features;aa=[f['attributes']for f in features];covering[family]=[a['SHEETNO']for a in aa];excluded_touches[family]=excluded
   for a in aa:
    assert 'REVISIONDATE'in a
    for fmt in FORMATS:
     source=a.get(fmt)
     if not isinstance(source,str)or not source.startswith('https://download.map.gov.hk/'):
      errors.append(dict(stage='official-format-not-exposed',family=family,sheet=a['SHEETNO'],format=fmt));continue
     tasks.append((family,a,fmt,source))
  except Exception as e:errors.append(dict(stage='official-index-'+family,error=type(e).__name__+': '+str(e)[:300]))
 assert len(tasks)<=MAX_SHEETS*len(INDEXES)*len(FORMATS)
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
 for family,features in index_attributes.items():
  try:
   q=query(INDEXES[family],spatial_parameters,family+'-official-covering-index-after');after,excluded=index_rows(q,footprint);assert after==features and excluded==excluded_touches[family]
  except Exception as e:errors.append(dict(stage='official-index-final-fence-'+family,error=type(e).__name__+': '+str(e)[:300]))
 for label,where in [('exact-csuid',"BuildingCSUID='"+CSUID+"'"),('exact-object','OBJECTID='+str(OLD_OBJECT))]:
  try:
   q=query(OUTLINE_BASE+'/0/query',dict(f='json',where=where,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100'),'outline-'+label+'-after');assert q==outline[label]
  except Exception as e:errors.append(dict(stage='official-outline-final-fence-'+label,error=type(e).__name__+': '+str(e)[:300]))
 matches=[dict(indexFamily=r['indexFamily'],sheet=r['sheet'],format=r['format'],revision=r['revision'],etag=r['etag'],members=r['exactGeoRefPrefixMembers'],nativeGLTFModels=r['exactGeoRefNativeModels'])for r in rows if r['exactGeoRefPrefixMembers']];expected=sum(len(v)*len(FORMATS)for v in covering.values());complete=not errors and len(index_attributes)==len(INDEXES)and len(rows)==expected
 outline_identity=[f for q in outline.values()for f in q['features']if f['attributes'].get('OBJECTID')==OLD_OBJECT and f['attributes'].get('BuildingCSUID')==CSUID]
 refs.extend(ref(p)for p in [HERE.parent/'landsd-territory/source.py',HERE.parent/'citywide-source/discover.py',HERE.parent/'landmark-acquisition/acquire.py']);refs.extend(ref(p)for p in sorted(DOC.rglob('*'))if p.is_file());save(DOC/'diagnostic.json.gz',dict(uids=['landsd/80343:0',UID],sourceOnly=True,currentAcceptance=False,installationApproved=False,originalSourceGeometryChanges=0,terrainGeometryChanges=0,currentCapturesCreated=False,currentOutlineQueries=outline,stableCSUIDCurrentlyReturned=True,historicalObjectId=OLD_OBJECT,freshStableCSUIDObjectId=actor['attributes']['OBJECTID'],freshRecordedBaseHeight=actor['attributes'].get('BaseHeight'),freshRecordedTopHeight=actor['attributes'].get('TopHeight'),exactObjectAndCSUIDCurrentlyReturned=bool(outline_identity),freshDirectoryResults=rows,exactGeoRefSourceCandidates=matches,completeBoundedFreshOfficialSearch=complete,boundedFreshDirectoryAbsence=(complete and not matches),errors=errors,sourceModelMemberRequests=0,sourceGeometryAcquired=False,originalOpenSidedSourceRecovered=False,coveringSheetsByIndexFamily=covering,excludedBoundaryOnlyTouchesByIndexFamily=excluded_touches,coveringSheetSelection=dict(completeFreshOfficialCSUIDGeometry=actor['geometry'],sourceCoordinateSystem='EPSG2326',positivePolygonIntersectionRequired=True,completePolygonUnionCoverageRequired=True,maximumSheetsPerFamily=MAX_SHEETS,qualification='Source directory search domain selection only; projected sheet coverage is not a building/terrain/support proof.'),expectedDirectoryCount=expected,formatsSearched=FORMATS,officialIndexFamilies=INDEXES,authoritativeAbsenceLimitedToListedRevisionsAndDirectories=True,noGlobalOrPermanentSourceAbsenceClaim=True,preservedOriginalMuseumOverlapFaceCount=63,preservedRawForeignGuardOverlapM2=1.855,primaryPlanRegistrationStillRequired=True,qualification='Fresh exact stableCSUID and independent historicalOBJECTID official queries; only genuinely covering official index sheet polygons at positive area and full footprint union coverage, two reviewed families/GLTF+FBX, all-class letter-prefixed exactGeoRef matching. Record object renumbering and nullable elevation metadata without substitution or invented heights. No source model member acquired, even when a directory match is found; source candidate identity and ambiguity require independent review before geometry acquisition. Complete negative is bounded to exact listed revisions/ETags; any error prevents bounded absence. Existing63 Museum overlap sourcefaces and raw1.855m2 foreign guard remain, along with original source/current support/root/identity/foreign obligations. No architectural ownership/function inference, placement exemption, terrain/building geometry, held-state/pointer/current approval or installation credit.',evidenceRefs=refs));print(json.dumps(dict(uid=UID,complete=complete,coveringSheets=covering,expectedDirectories=expected,exactGeoRefCandidateDirectories=len(matches),errors=errors,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
