"""ROOT-only authenticated auxiliary original acquisition and full finite context."""
import argparse,gzip,hashlib,importlib.util,json,subprocess,sys,time,zipfile
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[3];HERE=ROOT/'source-scripts/city/government-import'
C=D/'input-contract.json';OUT=D/'original-source-contact-output-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def save(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def fence(c,h):
 assert sha(C)==h and sha(Path(__file__))==c['callerSHA256']
 for p,v in c['filePins'].items():assert sha(ROOT/p)==v,p
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==c['currentManifestSHA256']

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--preflight-only',action='store_true');g.add_argument('--acquire-original-and-compare-only',action='store_true');p.add_argument('--lease-file',type=Path)
 a=p.parse_args();c=read(C);ch=sha(C);fence(c,ch);assert not OUT.exists()
 lookup=read(ROOT/c['lookupPath']);assert lookup['uid']=='landsd/57455:0'and len(lookup['rows'])==1
 star=lookup['rows'][0];native=star['model'];assert native['modelId']=='B370872650701063C0'and native['triangles']==91 and native['state']=='source-match-held'
 assert native['asset']['sha256']==c['starSourceSHA256']and native['asset']['bytes']==2262
 assert native['matching']['officialMatches']==native['matching']['viewerMatches']==[]and len(native['matching']['officialCandidates'])==1
 assert(native['matching']['officialCandidates'][0]['objectId'],native['matching']['officialCandidates'][0]['buildingCSUID'])==(57455,'3708726507T20050430')
 directory=read(ROOT/c['directoryRecordPath']);members=[m for m in directory['models']if m['modelId']==native['modelId']];assert len(members)==1
 assert directory['directorySHA256']==c['directorySHA256']and members[0]==c['selectedOriginalMembers']
 forms=read(ROOT/c['currentFormsPath']);forms={r['form']['uid']:r for r in forms}
 for r in forms.values():assert [b for b in read(ROOT/r['sourceTile'])['buildings']if b['uid']==r['form']['uid']]==[r['form']]
 assert(forms['landsd/57455:0']['form']['objectId'],forms['landsd/57455:0']['form']['buildingCSUID'],forms['landsd/57455:0']['form']['structureType'])==(57455,'3708726507T20050430','Tower')
 original=read(ROOT/c['completeMuseumArrayPath']);assert original['completeOriginalFaceCount']==15140 and len(original['completeOrderedOriginalTriangles'])==15140
 capture=read(ROOT/c['reusedMuseumAndBASICCapturePath']);assert capture['completeOriginalFaceCount']==15140 and capture['starMart']['completeFaces']==24
 if a.preflight_only:
  assert a.lease_file is None;fence(c,ch);print(json.dumps({'passed':True,'selectedMembers':2,'compressedMemberBytes':2367,'sourceFaces':91,'MuseumFaces':15140,'fullBASICFaces':24,'sourceMatchHoldPreserved':True,'noDBOrLease':True,'noDownloadDecodeOrCalculation':True,'resources':c['canonicalResources']}));return
 sys.path[:0]=[str(HERE),str(HERE.parent/'citywide-native')]
 from run import reservations,connect,NATIVE_RUN
 lease=read(a.lease_file);assert lease['resources']==c['canonicalResources']and reservations.owns(lease)
 def beat():assert reservations.heartbeat(lease,ttl=3600)['ok']
 def db_fence():
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,star['cacheKey'])).fetchall()==[(star['resultSHA256'],)]
   for p in c['priorCompleteReceipts']:
    q=read(ROOT/p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 db_fence();beat();OUT.mkdir()
 try:
  download=module('star_existing_acquisition',ROOT/'source-scripts/city/citywide-native/download.py')
  # Retain validated range as a separate proof field; stored HTTP headers use the six-header allowlist.
  OriginalNetwork=download.ac.Network
  class SixHeaderNetwork(OriginalNetwork):
   def get(self,*args,**kwargs):
    try:return super().get(*args,**kwargs)
    finally:
     for r in self.data['requests']:
      if 'headers'in r:
       h=r['headers'];r['validatedContentRange']=h['Content-Range']if 'Content-Range'in h else None
       r['headers']={k:v for k,v in h.items()if k.lower()in {'date','etag','last-modified','content-type','content-length','content-disposition'}}
     download.ac.write(self.path,self.data)
  download.ac.Network=SixHeaderNetwork
  selected=dict(directory);selected['models']=members
  acquisition=download.acquire(selected,ROOT/c['directoryBytesPath'],OUT/'original',include_terrain=False);beat()
  converter=module('star_existing_source_packer',ROOT/'source-scripts/city/citywide-native/convert.py')
  archive=OUT/'original'/('7-SW-15D.zip')
  with zipfile.ZipFile(archive)as z:
   assert set(z.namelist())=={m['name']for m in members[0]['members']}
   converted=converter._convert_one(z,z.getinfo(native['sourceEntry']),OUT/'decoded',OUT/'packed',{}, {'modelId':native['modelId']})
  asset=OUT/'packed'/native['asset']['asset'];assert sha(asset)==c['starSourceSHA256']and asset.stat().st_size==2262
  assert converted['asset']==native['asset']and converted['triangles']==91 and converted['vertices']==273
  assert converted['worldBounds']==native['worldBounds']
  save(OUT/'authenticated-original-conversion.json',{'lookupNativeVerbatim':star,'derivedSourceConversion':converted,'acquisition':acquisition,'sourceMatchHoldUnchanged':True,'derivedEmptyMatchingIsNotNativeMetadataReplacement':True,'identityAccepted':False})
  import numpy as np
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  from xl_source_stream_binding_20261009 import source_stream_binding
  from original_source_ownership import graph_reasons,document
  from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
  from exact_finite_contact_crossing_classification_20261011 import classify
  raw=asset.read_bytes();doc=document(raw);assert not graph_reasons(doc,native['modelId'],91)
  source_binding=source_stream_binding(raw);source=decode_original_world_triangles(raw);assert source.shape==(91,3,3)and np.isfinite(source).all()
  save(OUT/'complete-star-provider-original.json.gz',{'uid':'landsd/57455:0','sourceSHA256':c['starSourceSHA256'],'completeOriginalFaceCount':91,'completeOrderedOriginalTriangles':source.tolist(),'worldTrianglesSHA256':hashlib.sha256(source.astype('<f8').tobytes()).hexdigest(),'sourceStreamBinding':source_binding,'nativeMatchingVerbatim':native['matching'],'identityAccepted':False})
  beat();node=subprocess.run(['node',str(D/'heritage-starmart-original91-geometry-draft-v1.mjs'),'--capture-authenticated-original-only'],cwd=ROOT,text=True,capture_output=True)
  save(OUT/'actual-original-capture-log.json',{'exitCode':node.returncode,'stdout':node.stdout,'stderr':node.stderr});assert node.returncode==0
  actual=read(OUT/'complete-star-original-current-geometry.json.gz');assert actual['startAndEndInputsVerified']and actual['sourceSHA256']==c['starSourceSHA256']
  for name,key in [('position','position'),('normal','normal'),('color','colour')]:assert actual['mesh']['completeAttributes'][name]['indexedTypedFloat32BytesSHA256BeforeJSON']==source_binding[key+'TriangleStreamSHA256']
  si=np.asarray(actual['mesh']['completeIndex'],dtype=np.int64).reshape(-1,3);mi=np.asarray(capture['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);bi=np.asarray(capture['starMart']['completeIndex'],dtype=np.int64).reshape(-1,3)
  assert len(si)==91 and len(mi)==15140 and len(bi)==24
  museum=np.asarray(original['completeOrderedOriginalTriangles'],dtype='<f8');assert hashlib.sha256(museum.tobytes()).hexdigest()==c['museumOriginalWorldSHA256']
  views=[];cache={}
  for mode in ['providerOriginal','literal','leftFloat32','balancedFloat32']:
   beat()
   if mode=='providerOriginal':mw=museum;sw=source;bw=np.asarray(capture['starMart']['completePosition'],dtype='<f8').reshape(-1,3)[bi]
   else:
    key={'literal':'completeLiteralWorldPosition','leftFloat32':'completeLeftFloat32WorldPosition','balancedFloat32':'completeBalancedFloat32WorldPosition'}[mode]
    mw=np.asarray(capture[key],dtype='<f8').reshape(-1,3)[mi];sw=np.asarray(actual[key],dtype='<f8').reshape(-1,3)[si]
    bk={'literal':'completePosition','leftFloat32':'leftAssociatedPerMultiplyAddFloat32WorldPosition','balancedFloat32':'balancedPerMultiplyAddFloat32WorldPosition'}[mode]
    bw=np.asarray(capture['starMart'][bk],dtype='<f8').reshape(-1,3)[bi]
   row={'arithmetic':mode,'completeMuseumFaces':15140,'completeOriginalStarFaces':91,'completeStarBASICFaces':24,'pairs':{}}
   for label,left,right in [('Museum-vs-originalStar',mw,sw),('originalStar-vs-currentBASIC',sw,bw)]:
    pin=(hashlib.sha256(left.astype('<f8').tobytes()).hexdigest(),hashlib.sha256(right.astype('<f8').tobytes()).hexdigest())
    if pin not in cache:
     r=exact_finite_contacts(left,list(range(len(left))),right,list(range(len(right))),maximum_pairs=len(left)*len(right))
     for q in r['contacts']:q['crossingDiagnostic']=classify(left[q['sourceFaceA']],right[q['sourceFaceB']],q)
     cache[pin]=r
    row['pairs'][label]={'wholeWorldSHA256':list(pin),'contacts':cache[pin],'noSurfaceContacts':not cache[pin]['contacts'],'volumetricOrContainmentClearanceCertified':False}
   views.append(row);save(OUT/(mode+'-two-original-context.json.gz'),row)
  beat();fence(c,ch);db_fence();assert reservations.owns(lease)
  for p,h in actual['inputHashes'].items():assert sha(ROOT/p)==h,p
  result={'uids':['landsd/165054:0','landsd/57455:0'],'complete':True,'sourceSHA256':c['starSourceSHA256'],'MuseumSourceSHA256':c['museumSourceSHA256'],'completeOriginalFaces':{'Museum':15140,'Star':91},'sourceMatchHeldMetadataRetained':star,'allFourViews':views,'old14BASICCrossingsEachViewRetained':True,'noBASICSuppressionOrActorRemoval':True,'freshFullGroundSupportPending':True,'freshWholeGeoRefIdentityPending':True,'noSourceCentroidDistanceWaiver':True,'sourceGeometryChanges':0,'sourcePoseChanges':0,'physicalAccepted':False,'currentAcceptance':False,'installationApproved':False,'allInputHashes':c['filePins']}
  save(OUT/'diagnostic.json.gz',result);summary={'uids':result['uids'],'complete':True,'diagnosticSHA256':sha(OUT/'diagnostic.json.gz'),'sourceOriginalFaces':91,'MuseumFaces':15140,'contactsByFourViews':{r['arithmetic']:{k:len(v['contacts']['contacts'])for k,v in r['pairs'].items()}for r in views},'identityAccepted':False,'physicalAccepted':False,'newlyInstalled':0}
  save(OUT/'result.json',summary);print(json.dumps(summary),flush=True)
 except BaseException as e:
  save(OUT/'failure.json',{'complete':False,'errorType':type(e).__name__,'error':str(e),'sourceCorruptionInferred':False,'physicalAccepted':False});raise
 # ROOT external maintained supervisor releases only after child/group exit.
if __name__=='__main__':main()
