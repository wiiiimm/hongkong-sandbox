"""Reuse only the exact complete desktop; rerun the entire mobile viewport."""
import argparse,copy,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from completed_viewport_contract_v1_20261023 import validate_completed,unchanged_render_config


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owned',action='store_true');args=parser.parse_args();base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-four-original-private-browser-v3-20261023';out=base/batch;local=HERE/'local'/batch;leasepath=local/'reservation.json';refs=[Path(__file__)];pins={}
    terminal='government-xl-island-cheong-shing-browser-v2-terminal-evidence-v1-20261023';receipt,bound=authenticate(base/terminal);pins.update(bound);refs.append(base/terminal/'result.json');assert receipt['completedViewportWidths']==[1280]and receipt['incompleteViewportWidths']==[390]and receipt['oldLeaseReleased']
    runtime='government-xl-island-cheong-shing-four-original-runtime-v4-20261023';_,bound=authenticate(base/runtime)
    for name,sha in bound.items():assert name not in pins or pins[name]==sha;pins[name]=sha
    refs.append(base/runtime/'result.json')
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    old='government-xl-island-cheong-shing-four-original-private-browser-v2-20261023';oldlocal=HERE/'local'/old;cat=take(oldlocal/'catalogue.json');sources={m['uid']:m for m in cat['models']};assert {u:m['sha256']for u,m in sources.items()}==receipt['sourceSHA256ByUid'];oldcfg=take(oldlocal/'browser-config-390.json');assert len(oldcfg['additionalRetainedUids'])==32 and not oldcfg.get('retainedOnly')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==receipt['currentManifestSHA256'];refs.append(manifest);retained={}
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for m in read(path)['models']:
            if m['uid']in oldcfg['additionalRetainedUids']:
                assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);asset=path.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256']==receipt['retainedSourceSHA256ByUid'][m['uid']];refs.append(asset);retained[m['uid']]=m
    assert len(retained)==32;desktop=take(base/old/'1280/staged-browser.json');validate_completed(desktop,1280,sources,retained)
    metrics=take(base/runtime/'metrics.json')
    for name,sha in metrics['inputHashes'].items():
        if name.endswith(('.js','.mjs','.html')):assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    tool=HERE/'ronsdale_three_live_browser_v9_20261023.mjs';previous='government-xl-fu-tor-loy-five-source-retained-original-installed-v9-20261023';_,proven=authenticate(base/previous);assert digest(tool.read_bytes())==proven[str(tool.relative_to(ROOT))];refs.extend([tool,base/previous/'result.json'])
    if not args.owned:
        assert not out.exists()and not local.exists();keys={'building:'+u for u in set(sources)|set(retained)}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['replaces']['url']for r in oldcfg['terrain']};claim=reservations.claim('complete-mobile-resume-'+str(uuid.uuid4()),sorted(keys),batch=batch,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(leasepath,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(leasepath),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(leasepath);assert reservations.owns(lease)and not out.exists();out.mkdir();aliases=[]
    # Actual source/stage data stays at the same tested URI. These local copies
    # support the later qualified publisher and must be byte-identical.
    for source in oldlocal.rglob('*'):
        if not source.is_file()or source.name=='reservation.json':continue
        assert digest(source.read_bytes())==pins[str(source.relative_to(ROOT))];refs.append(source);target=local/source.relative_to(oldlocal);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert digest(target.read_bytes())==digest(source.read_bytes())
    for source in(base/old/'1280').rglob('*'):
        if not source.is_file():continue
        assert digest(source.read_bytes())==pins[str(source.relative_to(ROOT))];refs.append(source);target=out/'1280'/source.relative_to(base/old/'1280');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);sha=digest(target.read_bytes());assert sha==digest(source.read_bytes());aliases.append(dict(path=str(target.relative_to(ROOT)),sha256=sha,viewedOriginalPath=str(source.relative_to(ROOT)),copiedByteIdentically=True))
    cfg=copy.deepcopy(oldcfg);cfg['doc']=str((out/'390').relative_to(ROOT))+'/';unchanged_render_config(oldcfg,cfg);save(local/'browser-config-390.json',cfg);save(out/'completed-desktop-aliases.json',aliases);save(out/'resume-input-binding.json',dict(completedDesktopReport=dict(path=str((base/old/'1280/staged-browser.json').relative_to(ROOT)),sha256=digest((base/old/'1280/staged-browser.json').read_bytes())),sourceAndTerrainConfigUnchanged=True,rendererImplementationUnchanged=True,all32RetainedMobileCasesRequired=True,retainedOnly=False,actorObservationTimeoutMs=300000,desktopIsReusedOnlyAsExactCompletedEvidence=True,visualAcceptance=False,installationApproved=False))
    env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome','PATH':'/home/williamli/.nvm/versions/node/v24.18.0/bin:'+os.environ.get('PATH','')}
    with(out/'browser-390.log').open('w')as log:proc=subprocess.run(['node',str(tool),'staged',str((local/'browser-config-390.json').relative_to(ROOT))],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=3600)
    save(out/'command-390.json',dict(exitCode=proc.returncode));assert proc.returncode==0;mobile=read(out/'390/staged-browser.json');validate_completed(mobile,390,sources,retained);validate_completed(read(out/'1280/staged-browser.json'),1280,sources,retained)
    for path in set(refs):
        name=str(path.relative_to(ROOT))
        if name in pins:assert digest(path.read_bytes())==pins[name]
    assert digest(manifest.read_bytes())==receipt['currentManifestSHA256']and reservations.owns(lease);refs.extend(HERE/n for n in ['completed_viewport_contract_v1_20261023.py','test_completed_viewport_contract_v1_20261023.py']);refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json');result=dict(uids=sorted(sources),sourceGeometryChanges=0,completedViewportWidths=[1280,390],completedDesktopByteIdenticalToTerminalAttempt=True,all32RetainedCasesCompletedInEachViewport=True,visualAcceptance=False,installationApproved=False,scriptExternalAICalls=0,qualification='Whole successful desktop evidence is copied byte-identically, with explicit original-path aliases and unchanged source/terrain/renderer bindings. Entire mobile source/failure/joint/all32retained sequence rerun using the existing proven300s actor observer. No partial mobile cases, retained-only shortcut, source geometry changes, previous visual approval or publication credit reused. ROOT image inspection and guarded publication remain required.')
    save(out/'summary.json',result);module('mobile_resume_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-completed-desktop-and-full-mobile-device-evidence',refs,result)

if __name__=='__main__':main()
