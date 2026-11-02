"""Own a local4177server while the unchanged guarded original installer runs."""
import argparse,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    config=(ROOT/a.config).resolve();assert config.is_relative_to(ROOT/'docs/astra-city/government-import');data=read(config);batch=data['prefix']+'-retained-owned-loopback-'+data['date'];assert batch.startswith('government-xl-')and'/'not in batch
    lp=HERE/'local'/batch/'server-reservation.json';resources=['server:127.0.0.1:4177']
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('original-install-loopback-'+str(uuid.uuid4()),resources,batch=batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--config',a.config,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
    try:
        threading.Thread(target=server.serve_forever,daemon=True).start()
        subprocess.run([sys.executable,str(HERE/'yoho_original_pair_live_install_v1_20261102.py'),'--install'],cwd=ROOT,env={**os.environ,'ORIGINAL_INSTALL_CONFIG':str(config),'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'},check=True)
        assert reservations.owns(lease)
    finally:server.shutdown();server.server_close()

if __name__=='__main__':main()
