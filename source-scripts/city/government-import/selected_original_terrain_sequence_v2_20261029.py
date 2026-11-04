"""Run existing terrain, renderer, foundation and scope guards for explicit originals.

Complete cached terrain is an input, never approval. Per-source construction
failures remain recorded and do not stop the other explicitly selected sources.
"""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

def main():
    p=argparse.ArgumentParser()
    for key in ['batch','capture','terrain-check','inventory']:p.add_argument('--'+key,required=True)
    p.add_argument('--uid',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and 0<len(a.uid)==len(set(a.uid))<=20
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/a.batch/'reservation.json';assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();claim=reservations.claim('selected-original-terrain-'+str(uuid.uuid4()),['building:'+u for u in a.uid]+['terrain:city/data/terrain.json'],batch=a.batch,ttl=3600);assert claim['ok']
        execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
        # The neighbour checker owns its own full lease; never nest its claim
        # inside this constructor's terrain/building lease.
        receipt,_=authenticate(out)
        for uid in a.uid:
            part=uid.split('/')[1].replace(':','-');prefix=a.batch+'-'+part
            if not any(r['phase']=='scope' and r['uid']==uid and r['exitCode']==0 for r in receipt['completed']):continue
            scope,_=authenticate(base/(prefix+'-scope'))
            if scope.get('terrainContacts'):continue
            log=out/(part+'-deferred-neighbours.log')
            with log.open('w')as stream:
                check=subprocess.run([sys.executable,str(HERE/'selected_bounded_native_neighbours_v1.py'),'--batch',prefix+'-neighbours','--scope',prefix+'-scope','--inventory',a.inventory,'--patch',prefix+'-inset'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
            print(dict(uid=uid,phase='neighbours-after-parent-release',exitCode=check.returncode),flush=True)
        return
    lease=read(lp);assert reservations.owns(lease);out.mkdir();refs=[Path(__file__)];completed=[];obligations=[]
    authenticate(base/a.terrain_check);terrain=read(base/a.terrain_check/'summary.json');refs.extend([base/a.terrain_check/'result.json',base/a.terrain_check/'summary.json'])
    def run(part,phase,script,tail):
        assert reservations.owns(lease);batch=a.batch+'-'+part+'-'+phase;log=out/(part+'-'+phase+'.log')
        with log.open('w')as stream:r=subprocess.run([sys.executable,str(HERE/script),'--batch',batch,*tail],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        item=dict(uid='landsd/'+part.replace('-',':'),phase=phase,batch=batch,exitCode=r.returncode);refs.extend([HERE/script,log])
        receipt=None
        if r.returncode==0:
            receipt,_=authenticate(base/batch);item['jobId']=receipt['jobId'];refs.append(base/batch/'result.json')
        completed.append(item);print(item,flush=True);return receipt
    for uid in a.uid:
        part=uid.split('/')[1].replace(':','-');source=next(r for r in terrain['rows']if r['uid']==uid)
        if not source.get('sourceTerrainPaths')or source.get('missingOriginalTerrain'):
            obligations.append(dict(uid=uid,reason='complete-original-terrain-unavailable'));continue
        inset=run(part,'inset','selected_original_local_inset_v14_20261029.py',['--capture',a.capture,'--terrain-check',a.terrain_check,'--uid',uid])
        if not inset or not inset.get('candidate'):
            obligations.append(dict(uid=uid,reason='inset-construction-held',details=inset.get('reason')if inset else None));continue
        prefix=a.batch+'-'+part
        if not run(part,'runtime','selected_original_patch_runtime_v2.py',['--patch',prefix+'-inset','--capture',a.capture]):continue
        if not run(part,'attributes','selected_original_render_attributes_v1.py',['--capture',prefix+'-runtime']):continue
        foundation=run(part,'foundations','original_four_world_foundation_context_v1_20261025.py',['--runtime',prefix+'-runtime','--attributes',prefix+'-attributes','--uid',uid])
        scope=run(part,'scope','selected_original_patch_scope_v1.py',['--inventory',a.inventory,'--patch',prefix+'-inset'])
        # Neighbour checks run in the parent after execute_reserved releases
        # this constructor's lease. Every neighbour assertion stays unchanged.
        obligations.append(dict(uid=uid,foundationPolicyPassed=foundation.get('establishedFoundationPolicyPassed')if foundation else None,reason='physical-source-interface-and-publication-gates-remain'))
    result=dict(uids=a.uid,completed=completed,remainingObligations=obligations,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,publication=False,qualification='Existing unmodified V14 constructor, actual current renderer, four-world foundations and scoped neighbour checks run against complete pinned cached source terrain. Construction failure is retained individually. No model edits, optimisation, identity waiver, suppression or installation.')
    save(out/'summary.json',result);assert reservations.owns(lease)
    module('selected_original_terrain_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'selected-complete-original-terrain-current-physical-sequence',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
