"""HKS-209: deterministic cache-only classification of all16 architecture exceptions.
No network, live writes, source translations or shared inventory mutations.
"""
import collections,gzip,hashlib,importlib.util,json,pathlib,sqlite3,sys,time
import numpy as np
from shapely.geometry import MultiPoint,Polygon,box
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];B=H.parent/'architecture-batch';DOC=R/'docs/astra-city/architecture-followup'
sys.path.insert(0,str(H.parent/'building-batch'))
from cached_models import Processor,check_source
sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
sys.path.insert(0,str(H.parent/'landmark-pass'))
from audit_existing import triangle_evidence

def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def footprint(b):
 rings=json.loads(b['rings_json']);return Polygon(rings[0],rings[1:])
def thin_triangle_evidence(e):return {k:v for k,v in e.items() if k!='rays'}

def main():
 started=time.monotonic();accept=read(B/'acceptance.json');prior=read(B/'report.json');priorByUid={r['uid']:r for r in prior['results']};ids=sorted(set(accept['held'])|{r['uid']for r in prior['results']if r['outcome']=='no-standard-match-in-cache'},key=lambda u:int(u.split('/')[1].split(':')[0]));assert len(ids)==16
 con=sqlite3.connect('file:'+str(H.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);con.row_factory=sqlite3.Row;targets={u:dict(con.execute('select * from buildings where uid=? and active=1',(u,)).fetchone())for u in ids};nearby={}
 for b in targets.values():
  for row in con.execute('select * from buildings where active=1 and x between ? and ? and z between ? and ?',(b['x']-120,b['x']+120,b['z']-120,b['z']+120)):nearby[row['uid']]=dict(row)
 settings={r['key']:r['value']for r in con.execute('select * from settings')};con.close();save(H/'input-records.json',{'targetUids':ids,'targets':targets,'nearbyRecords':nearby,'inventorySettings':settings})
 inputs={str(p.relative_to(R)):sha(p)for p in [pathlib.Path(__file__),H.parent/'building-batch/cached_models.py',R/'docs/astra-city/mui-wo-buildings/review/prepare_model_sample.py',H.parent/'landmark-pass/audit_existing.py',B/'acceptance.json',B/'report.json',B/'compact/catalogue.json',R/'3d-viewer/city/data/manifest.json',R/'3d-viewer/city/data/terrain.json']};bygeo=collections.defaultdict(list);allSpecs=[];manifests=sorted(R.glob('source-scripts/city/*/staged/*/manifest.json'))
 for path in manifests:
  manifest=read(path)
  for spec in manifest.get('models',[]):
   if not spec.get('sourceEntry'):continue
   candidate={'manifest':str(path.relative_to(R)),'spec':spec,'tile':manifest['tile'],'revision':manifest['tileRevision'],'sourceArchiveSHA256':manifest.get('sourceArchiveSha256',manifest.get('sourceCacheSha256'))};allSpecs.append(candidate);bygeo[spec.get('geoRefNo',spec['id'][1:11])].append(candidate)
 output=H/'compact';processor=Processor(R,output,max_output_bytes=20_000_000);rows=[];packed=[];cache={};sourcebytes=0;seenfiles=set();direct=[]
 def native(candidate):
  nonlocal sourcebytes
  folder=(R/candidate['manifest']).parent;spec=candidate['spec'];path=folder/spec['sourceEntry']
  if str(path)not in cache:
   check_source(R,candidate);inputs[candidate['manifest']]=sha(R/candidate['manifest'])
   for rel,expected in spec['sourceHashes'].items():
    p=folder/rel;inputs[str(p.relative_to(R))]=expected
    if str(p)not in seenfiles:sourcebytes+=p.stat().st_size;seenfiles.add(str(p))
   vertices,triangles=model_geometry(read(path),lambda u:(path.parent/u).read_bytes());cache[str(path)]=(path,vertices,triangles)
  return cache[str(path)]
 for uid in ids:
  b=targets[uid];poly=footprint(b);options=sorted(bygeo[b['csuid'][:10]],key=lambda c:(c['revision'],c['manifest']),reverse=True);dedup={}
  for option in options:dedup.setdefault((option['spec']['id'],option['revision'],json.dumps(option['spec']['sourceHashes'],sort_keys=True)),option)
  options=list(dedup.values());row={'uid':uid,'name':b['name'],'objectId':b['object_id'],'buildingCSUID':b['csuid'],'sourceBaseTop':[b['source_base'],b['source_top']],'estimatedBaseHeight':[b['base'],b['height']],'structureType':b['structure_type'],'originalClassification':'prepared-placement-hold'if uid in accept['held']else'source-or-match-case','originalReason':accept['held'].get(uid,priorByUid[uid]['outcome']),'outcome':'held','classification':None,'nextAction':None,'exactReferenceCandidates':[],'supportCandidates':[]}
  try:
   for candidate in options:
    path,vertices,triangles=native(candidate);hull=MultiPoint(vertices[:,[0,2]]).convex_hull;intersection=hull.intersection(poly).area;overlap=intersection/max(.001,min(hull.area,poly.area));distance=hull.centroid.distance(poly.centroid);ev=triangle_evidence(path,vertices,poly,b['source_base'],b['base'],b['height']);e={'modelId':candidate['spec']['id'],'sourceManifest':candidate['manifest'],'sourceRevision':candidate['revision'],'sourceHashes':candidate['spec']['sourceHashes'],'nativeBounds':np.stack([vertices.min(0),vertices.max(0)]).tolist(),'triangles':triangles,'existingOfficialMatches':candidate['spec'].get('officialBuildingCSUIDs',[]),'currentFootprintMatch':{'overlapOfSmallerFootprint':overlap,'centroidDistanceMetres':distance,'matchesExistingThresholds':bool(overlap>=.5 and distance<=10)},'actualTriangles':thin_triangle_evidence(ev)};row['exactReferenceCandidates'].append(e)
    # Re-evaluate only the existing >=50% overlap / <=10m centroid policy against
    # current surveyed footprint IDs; never alter its thresholds or source bytes.
    if uid not in accept['held'] and len({o['spec']['id']for o in options})==1 and overlap>=.5 and distance<=10 and ev['projectedTriangleCoverageFraction']>=.5 and not packedUid(packed,uid):
     currentMatch={'buildingCSUID':b['csuid'],'objectId':b['object_id'],'geoRefNo':b['csuid'][:10],'blockType':b['structure_type'],'overlapOfSmallerFootprint':overlap,'footprintCentroidDistanceMetres':distance,'sourceBaseHeight':b['source_base'],'sourceTopHeight':b['source_top']};fresh={**candidate,'spec':{**candidate['spec'],'officialBuildingCSUIDs':[b['csuid']],'officialMatches':[currentMatch]}};result=processor({'building':b,'candidate':fresh,'priorCompact':[],'disposition':'match-and-pack'})
     if result.get('record'):
      record=result['record'];record['sourceMatchReview']='Current-footprint recheck using unchanged standard overlap/centroid thresholds; source original snapshot had no official match.';record['placementReviewed']=False;packed.append(record);e['freshStandardMatchPacked']=True;row['outcome']='ready';row['classification']='fresh-standard-match-candidate';row['nextAction']='Run shared loader and actual browser placement/identity review before publication.'
   # Locate related native components by actual footprint proximity, then ray-test
   # their original indexed triangles; names and convex hulls cannot suppress IDs.
   if not options or uid in ('landsd/223348:0','landsd/223783:0'):
    related=[]
    for candidate in allSpecs:
     spec=candidate['spec'];bounds=spec.get('worldBounds')
     if not bounds or not box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2]).intersects(poly):continue
     if spec.get('geoRefNo')==b['csuid'][:10]:continue
     related.append(candidate)
    unique={}
    for cand in sorted(related,key=lambda c:(c['revision'],c['manifest']),reverse=True):unique.setdefault(cand['spec']['id'],cand)
    for candidate in unique.values():
     path,vertices,triangles=native(candidate);ev=triangle_evidence(path,vertices,poly,b['source_base'],b['base'],b['height'])
     if ev['projectedTriangleCoverageFraction']<.05:continue
     row['supportCandidates'].append({'modelId':candidate['spec']['id'],'sourceManifest':candidate['manifest'],'sourceRevision':candidate['revision'],'officialBuildingCSUIDs':candidate['spec'].get('officialBuildingCSUIDs',[]),'nativeBounds':candidate['spec']['worldBounds'],'actualTriangles':thin_triangle_evidence(ev)})
   if row['outcome']!='ready':
    if uid in accept['held']:
     row['classification']='rendered-terrain-contact'if uid in ('landsd/114964:0','landsd/330467:0','landsd/322573:0','landsd/248218:0')else'component-support-review';row['nextAction']='Evaluate bounded source terrain/support correction without moving source model elevations.'
    elif options:row['classification']='exact-reference-fails-current-standard-match';row['nextAction']='Review explicit model/footprint correspondence; retain fallback. Do not relax global thresholds.'
    elif row['supportCandidates']:row['classification']='possible-shared-source-component';row['nextAction']='Review actual triangle coverage and vertical levels before any duplicate suppression; retain fallback.'
    else:row['outcome']='missing';row['classification']='not-in-retained-model-cache';row['nextAction']='Check recorded complete source directories; bounded acquisition only if separately authorised. Cache absence is not dataset-wide absence.'
  except Exception as error:
   row.update(outcome='retry',classification='cached-source-audit-error',nextAction='Repair or refresh the identified local source evidence and rerun this UID.',error={'type':type(error).__name__,'message':str(error)})
  rows.append(row);print(uid,row['outcome'],row['classification'],flush=True)
 # Reuse earlier complete-directory evidence, verifying retained bytes again.
 tai=read(B/'taikwun-audit.json');td=tai['sourceDirectory'];tdpath=R/td['path'];assert sha(tdpath)==td['sha256'];inputs[td['path']]=td['sha256'];inputs[str((B/'taikwun-audit.json').relative_to(R))]=sha(B/'taikwun-audit.json')
 missing=read(B/'missing-source-report.json');checked=[]
 for d in missing.get('completeDirectoryChecks',[]):
  path=B/'sources/acquisition/sources'/d['sheet']/'zip-directory.bin'
  if path.exists():
   assert sha(path)==d['directorySHA256'];inputs[str(path.relative_to(R))]=d['directorySHA256'];checked.append(d)
 for row in rows:
  if row['uid']=='landsd/242698:0':
   previous=next(p for p in tai['parts']if p['uid']==row['uid']);assert previous['status']=='source-not-present-in-checked-sheet-directory';row['priorCompleteDirectoryEvidence']={'source':str((B/'taikwun-audit.json').relative_to(R)),'directory':td,'matchingMembers':previous['sourceDirectoryEntries']};row['classification']='source-not-in-reviewed-cached-directory';row['nextAction']='Retain surveyed fallback; no standalone exact-reference member in checked complete11-SW-8Ddirectory. Review future/newer source revision or commission explicit geometry.'
  if row['uid']=='landsd/324948:0':
   previous=next(p for p in missing['rows']if p['uid']==row['uid']);row['priorCompleteDirectoryEvidence']={'source':str((B/'missing-source-report.json').relative_to(R)),'checkedDirectories':checked,'matchingMembers':previous['completeDirectoryExactReferences'],'outcome':previous['outcome']};row['classification']='source-not-in-reviewed-cached-directories';row['nextAction']='Retain surveyed fallback; previous bounded complete-directory review found no exact-reference source model. No dataset-wide absence claimed.'
 packed=[m for m in packed if any(r['uid']==m['uid'] and r['outcome']=='ready' for r in rows)]
 for name in ['placement-context.json','missing-source-report.json','taikwun-terrain-review.json']:
  if (B/name).exists():inputs[str((B/name).relative_to(R))]=sha(B/name)
 result={'issue':'HKS-209','kind':'architecture-exception-bulk-pass','verticalScale':1,'nativeDatum':'HKPD','networkRequests':0,'networkBytes':0,'aiCalls':0,'scriptSeconds':round(time.monotonic()-started,3),'cachedManifestsInspected':len(manifests),'sourceFilesRead':len(seenfiles),'sourceBytesRead':sourcebytes,'scope':{'expectedFlaggedParts':16,'accountedParts':len(rows),'landmarkRegistryNotDuplicated':True},'counts':dict(collections.Counter(r['outcome']for r in rows)),'inputHashes':dict(sorted(inputs.items())),'inputRecordSnapshotSha256':sha(H/'input-records.json'),'rows':rows,'limits':['Ready means staged candidate ready for loader/browser review, not live publication or architectural sign-off.','No source heights or coordinates changed. No live/catalogue/SQLite writes.','No network acquisition in this pass. Missing outcomes are qualified to retained sources.']};save(H/'bulk-report.json',result);save(H/'queue.json',{'issue':'HKS-209','inputRecordSnapshotSha256':sha(H/'input-records.json'),'items':[{'uid':r['uid'],'name':r['name'],'outcome':r['outcome'],'classification':r['classification'],'nextAction':r['nextAction']}for r in rows]});save(output/'catalogue.json',{'schemaVersion':1,'kind':'staged-official-model-catalogue','datasetId':'landsd_rcd_1742809441342_98380','area':'HKS-209 cached exact reference follow-up','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'models':packed,'counts':{'packedModels':len(packed)}});save(output/'catalogue-index.json',{'models':len(packed),'catalogues':['catalogue.json']});save(DOC/'bulk-report.json',result)
 print(json.dumps({k:result[k]for k in ['scope','counts','scriptSeconds','sourceBytesRead','networkBytes','aiCalls']},indent=2))
def packedUid(records,uid):return any(r['uid']==uid for r in records)
if __name__=='__main__':main()
