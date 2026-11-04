"""CPU-only complete surface/prism context for three private BASIC continuations."""
import argparse,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_footing_prism_contacts_v1_20261028 import surface_contacts
BASE=ROOT/'docs/astra-city/government-import'
PREFIX='government-xl-sha-tin-'
SCOPE=PREFIX+'seven-upward-floor-scope-v1-20261029'
RUNTIME=PREFIX+'seven-upward-floor-runtime-v1-20261029'
ATTRS=PREFIX+'seven-final-ground-attributes-v1-20261029'
PROPOSAL=PREFIX+'three-basic-ground-proposals-v2-20261029'
BATCH=PREFIX+'three-basic-continuation-foreign-volume-v1-20261029'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned',action='store_true')
    a=parser.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH
    assert not out.exists()
    forms=read(BASE/SCOPE/'form-obligations.json.gz')
    resources=sorted({'building:'+b['uid'] for b in forms}|{'terrain:city/data/terrain.json'})
    lp=local/'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim=reservations.claim('basic-continuation-volume-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)<=set(lease['resources'])
    pins={};refs=[Path(__file__),HERE/'exact_footing_prism_contacts_v1_20261028.py',HERE/'exact_packed_world_geometry_20261009.py']
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    assert take(SCOPE,'form-obligations.json.gz')==forms
    scope=take(SCOPE,'scope.json');natives=take(SCOPE,'native-obligations.json.gz')
    selection=take(RUNTIME,'selection.json.gz');attrs=take(ATTRS,'attributes.json.gz');proposal=take(PROPOSAL,'summary.json')
    assert attrs['startEndAllInputsVerified']and len(forms)==70 and scope['touchingNativeUids']==[] and not natives
    attrs={r['uid']:r for r in attrs['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    out.mkdir()
    basic_rows=[];tile_hashes={}
    for form in forms:
        tile=ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json')
        assert digest(tile.read_bytes())==pins[SCOPE][str(tile.relative_to(ROOT))]
        assert [b for b in read(tile)['buildings']if b['uid']==form['uid']]==[form]
        tile_hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());refs.append(tile)
        basic_rows.append(dict(building=form,tile=str(tile.relative_to(ROOT))))
    save(out/'basic-inputs.json',dict(manifestSHA256=selection['manifestSHA256'],currentInputHashes=tile_hashes,rows=basic_rows))
    basic_tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    addition_tool=HERE/'source_bound_basic_additions_capture_v1_20261029.mjs'
    subprocess.run(['node',str(basic_tool),str((out/'basic-inputs.json').relative_to(ROOT)),str((out/'basic.json').relative_to(ROOT))],cwd=ROOT,check=True)
    subprocess.run(['node',str(addition_tool),str((BASE/PROPOSAL/'summary.json').relative_to(ROOT)),str((out/'additions.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
    refs.extend([basic_tool,addition_tool]);basics=read(out/'basic.json');additions=read(out/'additions.json.gz')
    for report in [basics,additions]:
        for path,sha in report['inputHashes'].items():
            assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    assert basics['startAndEndInputHashesVerified']and len(basics['rows'])==70
    sources=[]
    for row in selection['rows']:
        attr=attrs[row['uid']];path=ROOT/row['candidate']['path']
        assert digest(path.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(path)
        sources.append((row['uid'],'original',decode_original_world_triangles(path.read_bytes())))
        index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
            sources.append((row['uid'],mode,np.asarray(attr[field]).reshape(-1,3)[index]))
    rows=[]
    for addition in additions['rows']:
        target=addition['uid'];tri=np.asarray(addition['position']).reshape(-1,3)[np.asarray(addition['index']).reshape(-1,3)]
        bottom,top=float(tri[:,:,1].min()),float(tri[:,:,1].max())
        assert np.all((tri[:,:,1]==bottom)|(tri[:,:,1]==top))
        caps=tri[(tri[:,:,1]==top).all(1)]
        assert len(caps)and np.all(np.cross(caps[:,1]-caps[:,0],caps[:,2]-caps[:,0])[:,1]!=0)
        def check(uid,role,mode,foreign):
            proof=surface_contacts(foreign,caps,bottom,top)
            name=target.split('/')[1]+'--'+uid.split('/')[1]+'--'+role+'--'+mode+'.json.gz'
            save(out/name,proof)
            rows.append(dict(targetUid=target,uid=uid,role=role,mode=mode,completeFaces=len(foreign),contactPairs=len(proof['contacts']),proof=name,worldSHA256=digest(np.asarray(foreign,dtype='<f8').tobytes()),reverseSolidContainmentProved=False))
            if proof['contacts']:print(dict(target=target,other=uid,role=role,mode=mode,contacts=len(proof['contacts'])),flush=True)
            assert reservations.owns(lease)
        for uid,mode,foreign in sources:check(uid,'candidate-original',mode,foreign)
        for basic in basics['rows']:
            if basic['uid']==target:continue
            foreign=np.asarray(basic['position']).reshape(-1,3)[np.asarray(basic['index']).reshape(-1,3)]
            check(basic['uid'],'current-basic','productionFloat32',foreign)
    result=dict(uids=scope['uids'],targets=proposal['uids'],rows=rows,regionalBasicForms=70,candidateOriginals=7,coordinateStreams=4,touchingInstalledNatives=0,surfaceVolumeContactRows=sum(r['contactPairs']>0 for r in rows),privateProposalOnly=True,sourceGeometryChanges=0,reverseSolidContainmentProved=False,collisionReviewApproved=False,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Every seven-source surface in four exact captured streams and every other regional BASIC production surface is tested against closed prisms of each actual new Float32 BASIC continuation top cap. Raw contacts retained, including source counterparts. No physical, identity, reverse-solid-containment, runtime, visual or publication acceptance.')
    save(out/'summary.json',result)
    module('basic_continuation_foreign_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-basic-continuation-complete-current-foreign-surface-volume-context',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
