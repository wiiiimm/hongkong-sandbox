"""Save a completed native run ledger to verified R2 and the existing Neon checkpoint registry."""
import argparse,gzip,hashlib,json,os,pathlib,subprocess,tarfile,tempfile
import store
from download import ac
from dotenv import dotenv_values
from source_cache import HERE
import sys
sys.path.insert(0,str(HERE.parent/'landmark-resume'))
from r2_snapshot import R2Store,digest,key_for,verify_object
from psycopg.types.json import Jsonb

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-id',required=True);p.add_argument('--audit-dir',required=True,type=pathlib.Path);p.add_argument('--env-file',required=True,type=pathlib.Path);p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args()
 audit=ac.read(a.audit_dir/'summary.json')
 if (audit['runId']!=a.run_id or audit['status']!='complete-mechanical-audit' or audit['acceptedSheets']!=audit['expectedSheets'] or audit['modelOutcomeRows']!=audit['indexedModels'] or audit['indexedModelsWithoutAcceptedOutcomes']!=0 or not audit['allAcceptedIndexedModelsAccounted'] or audit['countMismatches']!=0 or not audit['rawFootprintAudit']['matchesExpectedSourceSHA256'] or audit['unknownMechanicalFailures']!=0):raise ValueError('Audit is incomplete or still has unexplained mechanical failures')
 state=store.report(a.run_id)
 if state['pending'] or state['cached']!=state['expected']:raise ValueError('Cannot checkpoint an incomplete native run')
 root=HERE.parents[2];run=HERE/'local/runs'/a.run_id
 # All source/prepared bundles already have independent readback evidence and immutable Neon results.
 from runner import write_report
 summary=write_report(a.run_id,run)
 for k,v in dotenv_values(a.env_file).items():
  if k.startswith('R2_') and v:os.environ[k]=v
 remote=R2Store('hk-sandbox-assets');commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
 files=[(run/name,'run/'+name) for name in ('summary.json','shared-results.json.gz','registration.json','inputs.json')]
 files.append((HERE/'local/plan.json','plan.json'))
 files.extend((f,'audit/'+f.relative_to(a.audit_dir).as_posix()) for f in sorted(a.audit_dir.rglob('*')) if f.is_file())
 if not any(name.startswith('audit/') for _,name in files):raise ValueError('A completed audit is required')
 with tempfile.TemporaryDirectory(prefix='native-checkpoint-') as directory:
  temp=pathlib.Path(directory);archive=temp/'ledger.tar.gz'
  with archive.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as gz,tarfile.open(fileobj=gz,mode='w|') as tar:
   for f,name in files:
    info=tarfile.TarInfo(name);info.size=f.stat().st_size;info.mode=0o644
    with f.open('rb') as stream:tar.addfile(info,stream)
  sha=digest(archive);key=key_for(sha);remote.put(key,archive);verify_object(remote,key,sha,archive.stat().st_size,temp/'readback.tar.gz')
  # Inspect the fresh remote readback rather than trusting a local manifest alone.
  manifest_files=[{'path':name,'sha256':digest(f),'bytes':f.stat().st_size} for f,name in files]
  with tarfile.open(temp/'readback.tar.gz','r:gz') as tar:
   members={m.name:m for m in tar.getmembers()}
   if set(members)!={r['path'] for r in manifest_files}:raise ValueError('Remote ledger members differ')
   for row in manifest_files:
    member=members[row['path']]
    if not member.isfile() or member.size!=row['bytes']:raise ValueError('Remote ledger member type/size differs')
    with tar.extractfile(member) as stream:
     h=hashlib.file_digest(stream,'sha256').hexdigest()
    if h!=row['sha256']:raise ValueError('Remote ledger member hash differs')
  manifest={'schemaVersion':1,'issue':'HKS-222','runId':a.run_id,'gitCommit':commit,'summary':summary,'artifact':{'key':key,'sha256':sha,'bytes':archive.stat().st_size},'files':manifest_files,'verifiedRemoteReadback':True,'qualification':store.QUALIFICATION,'published':False}
  payload=(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode();manifest_sha=hashlib.sha256(payload).hexdigest();mf=temp/'manifest.json';mf.write_bytes(payload);mk=key_for(manifest_sha);remote.put(mk,mf);verify_object(remote,mk,manifest_sha,len(payload),temp/'manifest-readback.json')
  proof={'manifestSHA256':manifest_sha,'manifestKey':mk,**manifest}
  with store.connect() as con:
   con.execute('INSERT INTO astra_modelling.city_working_checkpoints(manifest_sha,issue,git_commit,proof) VALUES(%s,%s,%s,%s) ON CONFLICT(manifest_sha) DO NOTHING',(manifest_sha,'HKS-222',commit,Jsonb(proof)))
   if con.execute('SELECT proof FROM astra_modelling.city_working_checkpoints WHERE manifest_sha=%s',(manifest_sha,)).fetchone()[0]!=proof:raise ValueError('Checkpoint conflict')
  ac.write(a.out,proof);print(json.dumps({'checkpoint':manifest_sha,'runId':a.run_id,'remoteVerified':True,'neonRegistered':True,'bytes':archive.stat().st_size}))
if __name__=='__main__':main()
