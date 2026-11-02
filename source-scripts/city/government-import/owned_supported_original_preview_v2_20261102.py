"""Own private loopback4177 while the existing unapproved supported-original preview runs."""
import argparse,functools,http.server,json,os,subprocess,sys,threading,uuid
from run import ROOT,HERE,read,save,reservations

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True);a=p.parse_args();path=(ROOT/a.config).resolve();base=ROOT/'docs/astra-city/government-import';assert path.is_relative_to(base);config=read(path)
 assert config['batch'].startswith('government-xl-')and'/'not in config['batch']
 args=config['previewArgs'];assert args[args.index('--batch')+1]==config['batch']and not any(v in args for v in ['--owned','--installed-support-update'])
 local=HERE/'local'/(config['batch']+'-server');assert not local.exists();claim=reservations.claim('original-private-server-'+str(uuid.uuid4()),['server:127.0.0.1:4177'],batch=config['batch']+'-server',ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];server=None;thread=None
 try:
  save(local/'reservation.json',json.loads(json.dumps(lease,default=str)))
  class Handler(http.server.SimpleHTTPRequestHandler):
   def log_message(self,*unused):pass
  server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  result=subprocess.run([sys.executable,str(HERE/'unapproved_original_supported_private_preview_v3_20261102.py'),*args],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'},timeout=3500)
  assert reservations.owns(lease);save(local/'result.json',dict(exitCode=result.returncode,privatePort=4177,shared4176Untouched=True));assert result.returncode==0
 finally:
  if server is not None:server.shutdown();server.server_close()
  if thread is not None:thread.join(timeout=5)
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
