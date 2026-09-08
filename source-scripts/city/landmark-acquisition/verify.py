"""Read-only acquisition payload verification; writes evidence only in its docs folder."""
import argparse,gzip,hashlib,importlib.util,json,math,pathlib,sys,zipfile
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('landmark_acquisition',HERE/'acquire.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch');args=parser.parse_args();config=a.configure_batch(args.batch);work=a.HERE
 checks=[];errors=[];plan=a.read(work/'plan.json');ledger=a.read(work/'transfer-ledger.json')
 assert ledger['receivedBytes']<=ledger['chargedBytes']<=ledger['capBytes']==(config['capBytes']if config else a.CAP)
 for sheet in plan['tiles']:
  folder=work/'sources'/sheet;state_path=folder/'state.json'
  if not state_path.exists():continue
  state=a.read(state_path)
  if state.get('status')not in ('staged','complete-directory-no-exact-model'):continue
  try:
   infos,directory=a.parse_directory((folder/'zip-directory.bin').read_bytes());assert directory==state['directoryCheck']
   download=a.read(folder/'download.json');archive=folder/(sheet+'.zip');assert a.sha(archive.read_bytes())==download['sha256']and archive.stat().st_size==download['bytes']
   assert download['archiveSha256']is None and download['sourceETag']==state['sourceETag']
   head=a.read(folder/'head.json');assert head['headers']['ETag']==state['sourceETag']and int(head['headers']['Content-Length'])==download['sourceArchiveBytes']
   native={entry.filename:entry for entry in infos}
   with zipfile.ZipFile(archive)as compact:
    assert compact.testzip()is None
    assert set(compact.namelist())=={entry['name']for entry in download['entries']}
    for entry in download['entries']:
     raw=compact.read(entry['name']);source=native[entry['name']]
     assert len(raw)==source.file_size and a.zlib.crc32(raw)&0xffffffff==source.CRC
     assert a.sha(raw)==entry['sha256']==a.sha((folder/'members'/entry['name']).read_bytes())
   manifest=a.read(a.ROOT/state['manifest']);assert manifest['sourceCacheSha256']==download['sha256']
   assert manifest['rootTranslation']==[-834500,0,816500]and manifest['verticalDatum']=='Hong Kong Principal Datum'
   staged=(a.ROOT/state['manifest']).parent
   for model in manifest['models']:
    assert model['rootTranslation']==[-834500,0,816500]and all(math.isfinite(value)for row in model['worldBounds']for value in row)
    for name,digest in model['sourceHashes'].items():assert a.sha((staged/name).read_bytes())==digest
   checks.append({'sheet':sheet,'directoryEntries':len(infos),'directorySHA256':directory['directorySHA256'],'nativeMembers':len(download['entries']),'sourceCacheSHA256':download['sha256'],'stagedModels':len(manifest['models']),'native1xHKPD':True})
  except Exception as error:errors.append({'sheet':sheet,'error':str(error)})
 result={'issue':'HKS-213','batchId':plan.get('batchId','original-115'),'checkedAt':a.now(),'result':'passed'if not errors else'failed','completedTilesVerified':len(checks),'nativeMembers':sum(check['nativeMembers']for check in checks),'uniqueStagedModels':sum(check['stagedModels']for check in checks),'receivedBytes':ledger['receivedBytes'],'chargedBytes':ledger['chargedBytes'],'capBytes':ledger['capBytes'],'checks':checks,'errors':errors}
 a.write(a.DOCS/'verification.json',result);print(json.dumps({key:result[key]for key in ('result','completedTilesVerified','nativeMembers','uniqueStagedModels','receivedBytes','errors')},indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
