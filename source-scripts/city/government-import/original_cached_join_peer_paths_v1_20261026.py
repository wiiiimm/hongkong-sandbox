"""Reuse exact source self-joins while testing explicitly nominated companion roots."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','contacts','cached-joins','uid']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--peer',action='append',required=True);a=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.runtime,a.attributes,a.contacts,a.cached_joins]) and not out.exists()
    assert len(a.peer)==len(set(a.peer))and a.uid not in a.peer
    refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/file;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,'selection.json.gz');by={r['uid']:r for r in selection['rows']}
    attributes=take(a.attributes,'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']}
    previous=take(a.cached_joins,'summary.json');assert previous['uids']==[a.uid]and previous['sourceSHA256']==by[a.uid]['sourceSHA256']
    contacts=take(a.contacts,'summary.json');assert contacts['sourceSHA256ByUid']=={u:r['sourceSHA256']for u,r in by.items()}
    worlds={}
    for uid in [a.uid,*a.peer]:
        r=by[uid];attr=attrs[uid];path=ROOT/r['candidate']['path'];raw=path.read_bytes()
        assert digest(raw)==r['sourceSHA256']==attr['sourceSHA256'];refs.append(path)
        ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(raw),**{m:np.asarray(attr[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
    summaries=[]
    for mode,tri in worlds[a.uid].items():
        old=take(a.cached_joins,mode+'-paths.json.gz')
        selfproof=take(a.cached_joins,mode+'-self-contacts.json.gz')
        assert selfproof['allPairsExamined']and selfproof['sourceFacesOmitted']==0
        # The historical exact self-contact producer pins its complete packed
        # source and attributes. Reconstruct those exact rows independently.
        oldattrs=[ROOT/p for p in pins[a.cached_joins]if p.endswith('/attributes.json.gz')]
        oldmatches=[]
        field={'original':None,'literal':'completeLiteralWorldPosition','leftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','balancedF32':'completeExplicitBalancedFloat32WorldPosition'}[mode]
        for path in oldattrs:
            assert digest(path.read_bytes())==pins[a.cached_joins][str(path.relative_to(ROOT))];refs.append(path)
            matches=[r for r in read(path)['rows']if r['uid']==a.uid]
            for r in matches:
                assert r['sourceSHA256']==by[a.uid]['sourceSHA256']
                prior=worlds[a.uid]['original']if mode=='original'else np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]
                assert np.array_equal(prior,tri);oldmatches.append(r)
        assert oldmatches,'No exact historical world-array binding for cached joins'
        terminals=[]
        for pair in contacts['rows']:
            if a.uid not in [pair['left'],pair['right']]:continue
            peer=pair['right']if pair['left']==a.uid else pair['left']
            if peer not in a.peer:continue
            measured=next(r for r in pair['modes']if r['mode']==mode)
            for uid in [a.uid,peer]:assert measured['sourceWorldSHA256ByUid'][uid]==digest(worlds[uid][mode].tobytes())
            if measured['method']=='strict-complete-bounds-separation':continue
            raw=take(a.contacts,pair['left'].split('/')[1]+'--'+pair['right'].split('/')[1]+'--'+mode+'.json.gz')
            assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
            for c in raw['contacts']:
                if c['dimension']<=0 or c['sourcePrimitiveDimensionA']!=2 or c['sourcePrimitiveDimensionB']!=2:continue
                terminal=dict(c,peerUid=peer)
                if pair['right']==a.uid:terminal['sourceFaceA'],terminal['sourceFaceB']=c['sourceFaceB'],c['sourceFaceA']
                terminals.append(terminal)
        assert terminals
        targets=[dict(witness=r['witness'],incidentFaces=r['incidentFaces'])for r in old['rows']]
        paths=attachment_paths(tri,dict(targets=targets,proof=dict(contacts=terminals)),old['joins'])
        assert len(paths)==len(old['rows']) and all(r['witness']==s['witness']for r,s in zip(paths,old['rows']))
        save(out/(mode+'.json.gz'),dict(rows=paths,allowedPeerUids=a.peer,reusedSelfJoins=old['joins'],terminals=terminals,sourceWorldSHA256=digest(tri.tobytes())))
        summaries.append(dict(mode=mode,witnesses=len(paths),finiteAttachmentPaths=sum(r['hasUnrestrictedFiniteAttachment']for r in paths),pathsWithinEndpointHeight=sum(r.get('passesExistingEndpointHeight',False)for r in paths),allowedPeerUids=a.peer,actualPeerUids=sorted({r['terminal']['contact']['peerUid']for r in paths if r.get('terminal')})))
        print(summaries[-1],flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==contacts['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=[a.uid,*a.peer],targetUid=a.uid,sourceSHA256ByUid={u:by[u]['sourceSHA256']for u in [a.uid,*a.peer]},rows=summaries,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact existing self-contact geometry and unchanged witness inventory rebound to complete current source arrays; only explicitly nominated companion terminals considered. Different exact contact endpoints are measured without raising the endpoint-height or incidence limits. This is source attachment evidence, not support-root, ground, architectural, runtime or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'original_face_attachment_minimax_v2_20261024.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('cached_join_peer_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'cached-exact-source-joins-with-explicit-companion-terminals',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
