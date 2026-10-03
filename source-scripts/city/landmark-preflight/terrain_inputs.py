"""Inventory retained source terrain prerequisites; do not download or build terrain."""
import collections,hashlib,importlib.util,json,pathlib,time,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/landmark-preflight'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 started=time.perf_counter();report=read(DOC/'report.json');flagged=[p for p in report['parts']if p['candidate']and any(t in p['classification']for t in ['foundation-burial-context','sampled-roof-occlusion','elevated-component-support-context'])];sheets={p['candidate']['sourceTile']for p in flagged};native=[];invalid=[]
 for path in sorted((ROOT/'source-scripts/city').rglob('manifest.json')):
  try:d=read(path)
  except (ValueError,OSError)as e:invalid.append({'path':str(path.relative_to(ROOT)),'error':str(e)});continue
  t=d.get('terrain')
  if not isinstance(t,dict)or d.get('tile')not in sheets:continue
  original=t.get('sourceHashes',{});hashes={n:h for n,h in original.items()if n.endswith('.bin')};hashes[t['url']]=t.get('derivedSha256');good=bool(hashes)and all(h and (path.parent/n).is_file()and sha(path.parent/n)==h for n,h in hashes.items())
  native.append({'sheet':d['tile'],'revision':d.get('tileRevision'),'manifest':str(path.relative_to(ROOT)),'manifestSha256':sha(path),'worldBounds':t.get('worldBounds'),'files':[{'path':str((path.parent/n).relative_to(ROOT)),'sha256':h,'bytes':(path.parent/n).stat().st_size if(path.parent/n).exists()else None}for n,h in hashes.items()],'sourceFilesVerified':good})
 # Reuse complete-directory decoder; merely importing does not start network work.
 helper=ROOT/'source-scripts/city/landmark-acquisition/acquire.py';spec=importlib.util.spec_from_file_location('landmark_source_acquire',helper);acquire=importlib.util.module_from_spec(spec);spec.loader.exec_module(acquire)
 directories={}
 for path in sorted((ROOT/'source-scripts/city').rglob('zip-directory.bin')):
  sheet=path.parent.name
  if sheet not in sheets:continue
  try:entries,proof=acquire.parse_directory(path.read_bytes())
  except (AssertionError,ValueError)as e:invalid.append({'path':str(path.relative_to(ROOT)),'error':str(e)});continue
  wanted=[e for e in entries if e.filename.startswith('TERRAIN')and e.filename.endswith(('.gltf','.bin'))]
  directories.setdefault(sheet,[]).append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'directoryProof':proof,'members':[{'name':e.filename,'compressedBytes':e.compress_size,'decodedBytes':e.file_size,'crc32':e.CRC,'headerOffset':e.header_offset}for e in wanted],'compressedGeometryBytes':sum(e.compress_size for e in wanted)})
 dtm=ROOT/'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip';dtm_info={'path':str(dtm.relative_to(ROOT)),'available':dtm.is_file()}
 if dtm.is_file():
  with zipfile.ZipFile(dtm)as z:
   with z.open('Whole_HK_DTM_5m.asc')as f:header=[f.readline().decode().strip()for _ in range(6)]
  dtm_info.update(sha256=sha(dtm),bytes=dtm.stat().st_size,asciiHeader=header,limitation='Archival 5 m DTM may omit retaining edges or differ in date; its presence does not solve model placement.')
 archives={}
 for path in sorted((ROOT/'source-scripts/city').rglob('*.zip')):
  sheet=path.stem
  if sheet not in sheets:continue
  try:
   with zipfile.ZipFile(path)as z:entries=[e for e in z.infolist()if e.filename.startswith('TERRAIN')and e.filename.endswith(('.gltf','.bin'))]
  except zipfile.BadZipFile:continue
  if any(e.filename.endswith('.gltf')for e in entries)and any(e.filename.endswith('.bin')for e in entries):archives.setdefault(sheet,[]).append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'members':[{'name':e.filename,'compressedBytes':e.compress_size,'decodedBytes':e.file_size,'crc32':e.CRC}for e in entries],'status':'retained-unextracted-source-members; CRC/read validation required at extraction'})
 rows=[]
 for p in flagged:
  m=p['candidate'];a,b=m['worldBounds'];cover=[]
  for n in native:
   if not n['sourceFilesVerified']or not n['worldBounds']:continue
   c,d=n['worldBounds']
   if c[0]<=a[0]and c[2]<=a[2]and d[0]>=b[0]and d[2]>=b[2]:cover.append(n['manifest'])
  rows.append({'uid':p['uid'],'name':p['name'],'landmarks':p['landmarkIds'],'sheet':m['sourceTile'],'classification':p['classification'],'nativeTerrainSourcesCoveringBounds':cover,'nativeTerrainLocallyAvailable':bool(cover or archives.get(m['sourceTile'])),'retainedSourceArchives':archives.get(m['sourceTile'],[]),'archivalDTMLocallyAvailable':dtm_info['available'],'nextAction':'Use retained native terrain/source-support inputs in later modelling review.'if cover or archives.get(m['sourceTile']) else'Inspect/download the exact native terrain geometry members if needed for the flagged foundation; do not fetch imagery or redesign terrain now.'})
 requests=[]
 for sheet in sorted({r['sheet']for r in rows if not r['nativeTerrainLocallyAvailable']}):
  options=directories.get(sheet,[]);best=next((o for o in reversed(options)if o['members']),None)
  requests.append({'sheet':sheet,'uids':[r['uid']for r in rows if r['sheet']==sheet and not r['nativeTerrainLocallyAvailable']],'directory':best,'status':'bounded-native-geometry-members-listed'if best else'no-complete-terrain-directory-retained','publicationOrTerrainCorrectionApproved':False})
 output={'issue':'HKS-214','snapshotId':report['snapshotId'],'reportSha256':sha(DOC/'report.json'),'flaggedModels':len(rows),'nativeTerrainAvailableModels':sum(r['nativeTerrainLocallyAvailable']for r in rows),'nativeTerrainMissingModels':sum(not r['nativeTerrainLocallyAvailable']for r in rows),'missingNativeSheets':len(requests),'potentialCompressedGeometryBytes':sum(r['directory']['compressedGeometryBytes']for r in requests if r['directory']),'dtm':dtm_info,'rows':rows,'nativeSources':native,'downloadPrerequisites':requests,'invalidInputs':invalid,'seconds':time.perf_counter()-started,'networkRequests':0,'terrainChanges':0,'limits':['Native terrain availability is assessed from verified local payloads and source bounding boxes, not exhaustive triangle coverage.','Listed directory members are bounded acquisition candidates, not proof of corrected placement.','All geometry remains at 1x HKPD.']};(DOC/'terrain-inputs.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:output[k]for k in ['flaggedModels','nativeTerrainAvailableModels','nativeTerrainMissingModels','missingNativeSheets','potentialCompressedGeometryBytes','seconds']}))
if __name__=='__main__':main()
