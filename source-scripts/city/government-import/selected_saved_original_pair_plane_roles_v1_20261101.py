"""Describe saved finite original contacts using exact represented source planes.

This is geometric context, not a coplanarity exemption or acceptance predicate.
"""
import argparse,sys,uuid
from collections import Counter
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,sub,cross,dot
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','selection','attributes','contacts']:p.add_argument('--'+name,required=True)
    p.add_argument('--lease');a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.selection,a.attributes,a.contacts])and not out.exists()
    if not a.lease:
        uids=read(base/a.contacts/'summary.json')['uids'];lp=HERE/'local'/a.batch/'reservation.json';assert not lp.parent.exists()
        c=reservations.claim('original-plane-context-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--lease',str(lp)])
    lease=read(Path(a.lease));assert reservations.owns(lease);pins={};refs=[Path(__file__)];worlds={}
    def take(batch,name):
        if batch not in pins:_,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        path=ROOT/name if name.startswith('docs/')else base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.selection,'selection.json.gz');attrs={r['uid']:r for r in take(a.attributes,'attributes.json.gz')['rows']};contacts=take(a.contacts,'summary.json')
    sources={r['uid']:r for r in selection['rows']};assert set(contacts['uids'])<=sources.keys()and {'building:'+u for u in contacts['uids']}<=set(lease['resources'])
    for uid in contacts['uids']:
        r=sources[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==contacts['sourceSHA256ByUid'][uid]==attrs[uid]['sourceSHA256'];refs.append(asset);worlds[uid]=represented(attrs[uid],decode_original_world_triangles(asset.read_bytes()))
    rows=[]
    for r in contacts['rows']:
        if r['strictBoundsSeparated']:continue
        u,v,mode=r['uid'],r['peerUid'],r['mode'];left,right=worlds[u][mode],worlds[v][mode];assert r['sourceWorldSHA256ByUid']=={u:digest(left.tobytes()),v:digest(right.tobytes())}
        raw=take(a.contacts,r['rawPath']);assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0;planes={};facets={};classified=[]
        def face(uid,idx):
            key=uid,idx
            if key not in facets:facets[key]=rational_face(worlds[uid][mode][idx])
            return facets[key]
        for contact in raw['contacts']:
            if contact['sourcePrimitiveDimensionA']!=2 or contact['sourcePrimitiveDimensionB']!=2:kind='degenerate-source-primitive'
            else:
                fa=face(u,contact['sourceFaceA']);fb=face(v,contact['sourceFaceB']);key=v,contact['sourceFaceB']
                if key not in planes:planes[key]=cross(sub(fb[1],fb[0]),sub(fb[2],fb[0]))
                kind='coplanar'if all(dot(planes[key],sub(pt,fb[0]))==0 for pt in fa)else'noncoplanar'
            classified.append(dict(sourceFaceA=contact['sourceFaceA'],sourceFaceB=contact['sourceFaceB'],dimension=contact['dimension'],planeRelationship=kind))
        assert len(classified)==sum(r['contactDimensions'].values());name=u.split('/')[1]+'--'+v.split('/')[1]+'--'+mode+'.json.gz';save(out/name,dict(rows=classified,sourceWorldSHA256ByUid=r['sourceWorldSHA256ByUid'],exactRepresentedPlanes=True,acceptance=False))
        rows.append(dict(uid=u,peerUid=v,mode=mode,counts=dict(Counter(x['planeRelationship']+'-dimension-'+str(x['dimension'])for x in classified)),allContactsAccounted=True))
        assert reservations.owns(lease)
    result=dict(uids=contacts['uids'],sourceSHA256ByUid=contacts['sourceSHA256ByUid'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Exact rational planes in every saved source coordinate mode; no epsilon, no omitted saved contacts, no contact recomputation, source edits, root/terrain interpretation or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'original_assembly_four_world_pair_context_v3_20261101.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']);assert reservations.owns(lease)
    module('saved_original_pair_planes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-saved-original-pair-plane-context',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
