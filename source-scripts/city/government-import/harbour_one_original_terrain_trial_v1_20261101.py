"""Existing original-TIN diagnostics for the exact Harbour One tower/podium.

Private diagnostic only; no public terrain/source edits, acceptance or install.
"""
import sys, uuid, subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-harbour-one-after-hkdi-a-terrain-trial-v1-20261101'
CAPTURE='government-xl-harbour-one-after-hkdi-a-current-v1-20261101-runtime'
UIDS=['landsd/269828:0','landsd/319571:0']
def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';resources=['building:'+u for u in UIDS]+['terrain:city/data/terrain.json']
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists()
        c=reservations.claim('harbour-one-original-terrain-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    receipt,pins=authenticate(BASE/CAPTURE);selected=BASE/CAPTURE/'selection.json.gz'
    assert digest(selected.read_bytes())==pins[str(selected.relative_to(ROOT))]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());selection=read(selected)
    assert selection['manifestSHA256']==sha and {r['uid']for r in selection['rows']}==set(UIDS)
    refs=[Path(__file__),BASE/CAPTURE/'result.json',selected,manifest];out.mkdir();completed=[]
    terrain=BATCH+'-cached-terrain';inset=BATCH+'-inset'
    phases=[('selected_complete_cached_source_terrain_v1_20261029.py',terrain,['--capture',CAPTURE,*[a for u in UIDS for a in ['--uid',u]]]),
        ('selected_original_local_inset_v14_20261029.py',inset,['--capture',CAPTURE,'--terrain-check',terrain,'--uid',UIDS[0],'--companion',UIDS[1]])]
    for script,batch,args in phases:
        assert reservations.owns(lease)and digest(manifest.read_bytes())==sha and not(BASE/batch).exists()
        tool=HERE/script;start=digest(tool.read_bytes());log=out/(script+'.log')
        save(out/(script+'.command.json'),dict(command=[sys.executable,str(tool),'--batch',batch,*args],producerSHA256=start))
        with log.open('w')as stream:cp=subprocess.run([sys.executable,str(tool),'--batch',batch,*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        assert reservations.owns(lease)and digest(tool.read_bytes())==start and digest(manifest.read_bytes())==sha
        refs.extend([tool,log,out/(script+'.command.json')]);row=dict(batch=batch,script=script,exitCode=cp.returncode)
        if cp.returncode==0:
            result,_=authenticate(BASE/batch);row['jobId']=result['jobId'];refs.append(BASE/batch/'result.json')
        completed.append(row);save(out/'state.json',dict(running=True,completed=completed))
        if cp.returncode:break
    save(out/'state.json',dict(running=False,completed=completed))
    result=dict(uids=UIDS,completed=completed,currentManifestSHA256=sha,sourceGeometryChanges=0,sourcePoseChanges=0,publicTerrainEdits=False,privateOriginalTerrainTrial=True,installationApproved=False,publication=False,newlyInstalled=0)
    save(out/'summary.json',result)
    module('harbour_one_original_terrain_trial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'explicit-original-harbour-one-pair-cached-terrain-and-private-v14-trial',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
