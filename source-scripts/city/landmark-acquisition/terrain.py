"""Acquire pinned native terrain prerequisite members without applying terrain."""
import argparse,concurrent.futures,gzip,json,pathlib,sys,zipfile
sys.dont_write_bytecode=True
import acquire as a

def verify_sheet(sheet):
 folder=a.HERE/'sources'/sheet;state=a.read(folder/'state.json');download=a.read(folder/'download.json')
 infos,proof=a.parse_directory((folder/'zip-directory.bin').read_bytes());assert proof==state['directoryCheck'];native={entry.filename:entry for entry in infos}
 archive=folder/(sheet+'.zip');assert a.sha(archive.read_bytes())==download['sha256']
 with zipfile.ZipFile(archive)as compact:
  assert compact.testzip()is None
  for member in download['entries']:
   raw=compact.read(member['name']);entry=native[member['name']]
   assert a.sha(raw)==member['sha256']and len(raw)==entry.file_size and a.zlib.crc32(raw)&0xffffffff==entry.CRC
 manifest=a.read(a.ROOT/state['manifest']);terrain=manifest['terrain'];assert terrain and manifest['rootTranslation']==[-834500,0,816500]and manifest['verticalDatum']=='Hong Kong Principal Datum'
 staged=(a.ROOT/state['manifest']).parent
 for name,digest in terrain['sourceHashes'].items():
  assert a.sha((folder/'members'/name).read_bytes())==digest
  if name.endswith('.bin'):assert a.sha((staged/name).read_bytes())==digest
 assert a.sha((staged/terrain['url']).read_bytes())==terrain['derivedSha256']
 return {'sheet':sheet,'outcome':'native-terrain-acquired-verified','manifest':state['manifest'],'sourceCacheSHA256':download['sha256'],'sourceETag':download['sourceETag'],'directorySHA256':proof['directorySHA256'],'nativeMembers':len(download['entries']),'worldBounds':terrain['worldBounds'],'native1xHKPD':True,'photoOmitted':True}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',default='terrain-prerequisites');parser.add_argument('--targets-source');parser.add_argument('--workers',type=int,default=4);parser.add_argument('--budget-mb',type=int);parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
 assert 1<=args.workers<=8
 config=a.configure_batch(args.batch,args.targets_source,args.budget_mb);snapshot=a.read(a.HERE/'target-input.json');inputs=snapshot['downloadPrerequisites'];assert inputs
 network=a.Network(a.HERE/'transfer-ledger.json',config['capBytes']);network.data['maxConcurrentSheetWorkers']=args.workers;a.write(network.path,network.data)
 official=a.HERE/'official-selection.json.gz'
 if not official.exists():official.write_bytes(gzip.compress(json.dumps({'datasetVersion':'No building match requested; native terrain prerequisite only','features':[]}).encode(),mtime=0))
 caches=a.retained_caches();rows=[]
 def work(item):
  sheet=item['sheet']
  try:
   if item['status']!='bounded-native-geometry-members-listed':raise ValueError('No complete pinned source directory')
   directory=a.ROOT/item['directory']['path'];raw=directory.read_bytes();assert a.sha(raw)==item['directory']['sha256'];a.parse_directory(raw)
   source=a.read(directory.parent/'download.json');tile={'attributes':source['indexAttributes'],'uids':[]}
   state=a.HERE/'sources'/sheet/'state.json'
   completed=state.exists()and a.read(state).get('status')=='native-terrain-verified'
   if not completed and not args.verify_only:
    result=a.acquire_tile(network,sheet,tile,{},caches,exact_members={entry['name']:entry for entry in item['directory']['members']})
   result=verify_sheet(sheet)
   state_data=a.read(state);state_data['status']='native-terrain-verified';a.write(state,state_data)
   result['uids']=item['uids'];return result
  except Exception as error:
   state_path=a.HERE/'sources'/sheet/'state.json'
   if state_path.exists():
    failed=a.read(state_path);failed.update(status='terrain-verification-retryable',error=f'{type(error).__name__}: {error}');a.write(state_path,failed)
   return {'sheet':sheet,'uids':item['uids'],'outcome':'deferred','error':f'{type(error).__name__}: {error}'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)as pool:
  for result in pool.map(work,inputs):rows.append(result);print(result['sheet'],result['outcome'],result.get('error',''),flush=True)
 report={'issue':'HKS-213','relatedIssue':'HKS-214','batchId':args.batch,'snapshotSHA256':config['targetSnapshotSHA256'],'generatedAt':a.now(),'summary':{'sheets':len(rows),'verified':sum(row['outcome']=='native-terrain-acquired-verified'for row in rows),'deferred':sum(row['outcome']=='deferred'for row in rows)},'rows':rows,'transfer':{'receivedBytes':network.data['receivedBytes'],'newThisInvocationBytes':network.data['receivedBytes']-network.initial,'requests':len(network.data['requests']),'chargedBytes':network.data['chargedBytes'],'capBytes':network.cap},'qualification':'Native source geometry unchanged,1x HKPD. Geometry-only staged glTF omits photograph/material references; no terrain application, reconstruction, placement approval or publication. Existing whole-HK5mDTM not downloaded.'}
 a.write(a.DOCS/('terrain-verification.json'if args.verify_only else'terrain-report.json'),report);print(json.dumps(report['summary']));print(json.dumps(report['transfer']));return bool(report['summary']['deferred'])
if __name__=='__main__':raise SystemExit(main())
