"""Host an existing unapproved-original browser preview on owned loopback4177.

The existing preview keeps its own model/terrain leases and assertions. This
wrapper owns only the private server, closes it on every exit and never uses4176.
"""
import argparse,functools,http.server,json,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();base=ROOT/'docs/astra-city/government-import';path=(ROOT/a.config).resolve();assert path.is_relative_to(base)
    config=read(path);assert config['viewerURL']=='http://127.0.0.1:4177/city.html'and config['batch'].startswith('government-xl-')and '/'not in config['batch']
    batch=config['batch']+'-loopback';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists()
    claim=reservations.claim('private-original-loopback-'+str(uuid.uuid4()),['server:127.0.0.1:4177'],batch=batch,ttl=3600);assert claim['ok'];lease=claim['reservation'];server=None;thread=None;log=None
    try:
        save(local/'reservation.json',json.loads(json.dumps(lease,default=str)));out.mkdir();log=(out/'server.log').open('w')
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,format,*args):log.write((format%args)+'\n');log.flush()
        server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        tool=HERE/'selected_original_unapproved_terrain_browser_v2_20261025.py'
        with(out/'preview.log').open('w')as stream:
            result=subprocess.run([sys.executable,str(tool)],cwd=ROOT,env={**os.environ,'ORIGINAL_PREVIEW_CONFIG':str(path.relative_to(ROOT))},stdout=stream,stderr=subprocess.STDOUT,timeout=3500)
        refs=[Path(__file__),path,tool];receipt=None
        if result.returncode==0:receipt,_=authenticate(base/config['batch']);refs.append(base/config['batch']/'result.json')
        summary=dict(uids=list(config['sources']),previewBatch=config['batch'],previewJobId=receipt['jobId']if receipt else None,exitCode=result.returncode,privateLoopbackPort=4177,shared4176Untouched=True,serverClosedOnExit=True,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Existing unapproved-original desktop/mobile preview assertions run unchanged on owned private loopback server. The child owns its independent model/terrain lease. No production writes or acceptance.')
        server.shutdown();server.server_close();thread.join(timeout=5);server=None;save(out/'summary.json',summary)
        module('loopback_original_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'owned-private-loopback-original-preview-lifecycle',refs,summary)
        assert result.returncode==0,'Preview failed; exact diagnostic retained'
    finally:
        if server is not None:server.shutdown();server.server_close()
        if thread is not None:thread.join(timeout=5)
        if log is not None:log.close()
        assert reservations.release(lease)['ok']

if __name__=='__main__':main()
