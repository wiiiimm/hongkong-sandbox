"""Bind saved original support paths and current terrain facts for all20sources.

No historical compound foundation, physical, visual or publication approval transfers.
"""
import argparse,sys,uuid,subprocess
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from rebind_original_foreign_basic_contacts_v1_20261101 import identical_array
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';OLD='government-xl-palazzo76610-';BATCH=P+'current-twenty-assembly-context-v1-20261101'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--lease');a=ap.parse_args()
    if not a.lease:
        from north_pair_nonwall_topology_v1_20261027 import execute_reserved
        selection=read(BASE/(P+'twenty-authentic-tin-runtime-v1-20261101')/'selection.json.gz')
        resources=sorted('building:'+r['uid'] for r in selection['rows'])
        claim=reservations.claim('palazzo-context-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        lp=HERE/'local'/BATCH/'reservation.json'
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--lease',str(lp)])
    lease=read(Path(a.lease));assert reservations.owns(lease)
    out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__),HERE/'local'/BATCH/'FAILED-FIRST-LAUNCH.json',HERE/'local'/BATCH/'FAILED-SECOND-LAUNCH.json'];hashed={}
    def take(n,filename,external=None):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        p=external if external is not None else BASE/n/filename
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def code_unchanged(n):
        for name,sha in pins[n].items():
            if name.endswith(('.py','.mjs','.js')):
                assert name not in hashed or hashed[name]==sha,'Conflicting historical code revisions need separate revalidation'
                if name not in hashed:assert digest((ROOT/name).read_bytes())==sha;hashed[name]=sha;refs.append(ROOT/name)
    runtime=P+'twenty-authentic-tin-runtime-v1-20261101';attrbatch=P+'twenty-original-attributes-v1-20261101';selection=take(runtime,'selection.json.gz');sources={r['uid']:r for r in selection['rows']};assert len(sources)==20
    assert {'building:'+u for u in sources}<=set(lease['resources'])
    attrs={r['uid']:r for r in take(attrbatch,'attributes.json.gz')['rows']};geometry={r['uid']:r for r in take(runtime,'',HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']};worlds={};sha_by_uid={}
    for uid,r in sources.items():
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attrs[uid]['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(asset)
        attr=attrs[uid];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);w={'original':decode_original_world_triangles(asset.read_bytes())}
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:w[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]
        assert all(len(t)==r['triangles']for t in w.values());worlds[uid]=w;sha_by_uid[uid]={m:digest(t.astype('<f8').tobytes())for m,t in w.items()}
    supported=[]
    kinds={u:'finite-self-attachments'for u in ['252774','71042','71045','71703','72626','89150']}
    kinds.update({u:'finite-endpoint-choices'for u in ['71886','88303']});kinds.update({u:'strict-root-paths'for u in ['71688','71709']});kinds['88899']='endpoint-aware';kinds['10198']='current-strict-root-paths';kinds.update({k:'current-finite-attachments'for k in ['68540','88780','252555']})
    for key,kind in kinds.items():
        uid='landsd/'+key+':0';parent='landsd/304541:0'if key=='10198'else'landsd/76610:0'
        strictbatch=(P+'jubilee10198-four-world-support-v1-20261101'if key=='10198'else P+key+'-original-owner-support-v1-20261101'if kind=='current-finite-attachments'else OLD+key+'-0-four-world-support-v1-20261031')
        strict=take(strictbatch,'summary.json');expected={u:sources[u]['sourceSHA256']for u in [uid,parent]};assert strict['sourceSHA256ByUid']==expected and strict['supportedUid']==uid and strict['supportUid']==parent
        if kind=='current-finite-attachments':proofbatch=P+key+'-finite-original-attachments-v1-20261101'
        elif kind=='current-strict-root-paths':proofbatch=P+'jubilee10198-strict-root-paths-v1-20261101'
        elif kind=='endpoint-aware':proofbatch=OLD+'endpoint-aware-strict-roots-v1-20261031'
        else:proofbatch=OLD+key+'-0-'+kind+'-v1-20261031'
        take(proofbatch,'summary.json');records=[]
        for mode in ['original','literal','leftF32','balancedF32']:
            old=next(r for r in strict['rows']if r['mode']==mode)
            assert old['sourceWorldSHA256ByUid']=={u:sha_by_uid[u][mode]for u in [uid,parent]}
            data=take(strictbatch,mode+'/input.json.gz')
            identical_array(np.asarray(data['rows'][0]['position']).reshape(-1,3,3),worlds[uid][mode],'<f8');identical_array(data['podium'],worlds[parent][mode],'<f8')
            name=(key+':0/'if kind=='endpoint-aware'else'')+mode+'.json.gz';proof=take(proofbatch,name)
            rows=proof['selected']if kind=='endpoint-aware'else proof['rows']
            assert [r['witness']for r in rows]==old['support']['unresolved']
            assert all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 for r in rows)
            if kind=='endpoint-aware':assert not proof['remainingIndices']and not proof['newAnchorsCreated']and not proof['endpointToleranceChanged']
            if 'sourceWorldSHA256'in proof:assert proof['sourceWorldSHA256']==sha_by_uid[uid][mode]and proof['supportWorldSHA256']==sha_by_uid[parent][mode]
            records.append(dict(mode=mode,canonicalStrictContacts=old['support']['strictContacts'],unresolvedDirectInterfaceWarnings=len(rows),allSavedOriginalAttachmentPathsWithinExistingBounds=True,rawCompoundFoundationTransferred=False,positiveProofBatch=proofbatch,positiveProofPath=name))
        code_unchanged(strictbatch);code_unchanged(proofbatch)
        supported.append(dict(uid=uid,supportUid=parent,sourceSHA256ByUid=expected,rows=records))
    terrain=[];lower=take(P+'two-lower-source-role-review-v1-20261101','summary.json');assert lower['sourceRoleAccepted']and lower['lowerSourceRoleOnly']
    newlower=take(P+'two-new-lower-role-review-v1-20261101','summary.json');assert newlower['sourceRoleAccepted']and newlower['lowerSourceRoleOnly']
    third=take(P+'88780-lower-wall-role-review-v1-20261101','summary.json');assert third['sourceRoleAccepted']and third['lowerSourceRoleOnly']
    lower=dict(uids=lower['uids']+newlower['uids']+third['uids'],rows=lower['rows']+newlower['rows']+third['rows'])
    actual_ground_support=[]
    for key in ['252556','252558']:
        uid='landsd/'+key+':0';strict=take(P+key+'-original-owner-support-v1-20261101','summary.json');by_mode=[]
        for mode in ['original','literal','leftF32','balancedF32']:
            proof=take(P+key+'-saved-ground-attachments-v1-20261101',mode+'.json.gz');bound=next(r for r in strict['rows']if r['mode']==mode)
            ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
            assert proof['sourceWorldSHA256']==sha_by_uid[uid][mode]and proof['completeGroundSHA256']==digest(ground.tobytes())
            assert [r['witness']for r in proof['rows']]==bound['support']['unresolved']and all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 and r['terminal']['contact']['peerUid']=='current-drawn-ground'for r in proof['rows'])
            by_mode.append(dict(mode=mode,allSavedGroundAttachmentPathsWithinExistingBounds=True,sourceWorldSHA256=sha_by_uid[uid][mode],groundSHA256=proof['completeGroundSHA256'],rawWarningsPreserved=len(proof['rows'])))
        actual_ground_support.append(dict(uid=uid,sourceSHA256=sources[uid]['sourceSHA256'],rows=by_mode))
    full={'landsd/10198:0':P+'10198-fifteen-ground-v1-20261101','landsd/252774:0':P+'252774-fifteen-ground-v1-20261101','landsd/304541:0':P+'304541-0-authentic-tin-ground-v1-20261101'}
    for key in ['68540','252555']:
        uid='landsd/'+key+':0';batch=P+key+'-twenty-complete-ground-v1-20261101';full[uid]=batch
        if not (BASE/batch/'result.json').exists():
            assert reservations.owns(lease)
            tool=HERE/'selected_original_four_world_low_face_context_v3_20261031.py';sha=digest(tool.read_bytes());log=HERE/'local'/BATCH/(key+'-ground.log');log.parent.mkdir(exist_ok=True)
            with log.open('w')as stream:subprocess.run([sys.executable,str(tool),'--batch',batch,'--runtime',runtime,'--attributes',attrbatch,'--uid',uid],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
            assert digest(tool.read_bytes())==sha and reservations.owns(lease)
        take(batch,'summary.json');code_unchanged(batch)
    for uid,w in worlds.items():
        ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gsha=digest(ground.tobytes());rows=[]
        for mode,tri in w.items():
            if uid in full:
                proof=take(full[uid],{'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)+'.json.gz')
                assert proof['sourceWorldSHA256']==sha_by_uid[uid][mode]and proof['groundSHA256']==gsha and proof['rows']==[]
                rows.append(dict(mode=mode,completeTerrainClearance='authenticated-all-face-all-ground-zero-negative-partition',rawNegativeFaces=0))
            elif uid in lower['uids']:
                role=next(r for r in lower['rows']if r['uid']==uid);record=next(r for r in role['rows']if r['mode']==mode)
                assert role['lowerSourceRoleAccepted']and role['sourceSHA256']==sources[uid]['sourceSHA256']and record['sourceWorldSHA256']==sha_by_uid[uid][mode]and record['completeGroundSHA256']==gsha
                rows.append(dict(mode=mode,completeTerrainClearance='bounded-exact-lower-source-role-interpretation',rawNegativeFaces=len(record['rawNegativeFaces']),rawStrictFailuresPreserved=True))
            else:
                smin=Fraction(float(tri[:,:,1].min()));gmax=Fraction(float(ground[:,:,1].max()));gap=smin-gmax
                assert gap>=Fraction(-1,2)
                rows.append(dict(mode=mode,completeTerrainClearance='all-original-source-and-all-drawn-ground-vertex-height-bound',completeSourceFaces=len(tri),completeDrawnGroundFaces=len(ground),exactSourceMinimumY=str(smin),exactGroundMaximumY=str(gmax),exactConservativeGapLowerBoundM=str(gap)))
        terrain.append(dict(uid=uid,sourceSHA256=sources[uid]['sourceSHA256'],sourceWorldSHA256ByMode=sha_by_uid[uid],completeGroundSHA256=gsha,rows=rows))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']and reservations.owns(lease);refs.extend([manifest,HERE/'exact_packed_world_geometry_20261009.py',HERE/'rebind_original_foreign_basic_contacts_v1_20261101.py'])
    result=dict(uids=sorted(sources),sourceSHA256ByUid={u:r['sourceSHA256']for u,r in sources.items()},sourceAttachments=supported,currentGroundContexts=terrain,allFifteenOriginalPeerSupportRoutesBound=True,actualGroundAttachments=actual_ground_support,allTwentyCurrentTerrainContextsAccounted=True,rawStrictWarningsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,historicalCompoundFoundationsTransferred=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Every old canonical support/input/source-parent array and exact positive path is bound to current complete four-world source arrays, with unchanged producer code and every direct warning retained. Terrain is independently current: ten whole-source bounds, five current complete zero-negative partitions, five exact lower-source role reviews; two complete current-ground attachment routes. No old terrain foundation result, extra root, tolerance change, neighbour/browser or publisher approval transfers.')
    save(out/'summary.json',result);module('palazzo_current_twenty_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-twenty-original-source-attachment-and-ground-context-reconciliation',list(dict.fromkeys(refs)),result)
    print(dict(sourceAttachments=len(supported),currentGroundContexts=len(terrain),installationApproved=False),flush=True)

if __name__=='__main__':main()
