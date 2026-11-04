"""Replay exact source-component bridges and finite support paths in four worlds."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from original_contact_paths_with_finite_joins_v1_20261023 import paths


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-joined-source-fourworld-paths-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=ROOT/name if name.startswith('source-scripts/')else base/batch/name
        assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    interfaces='government-xl-island-industrial-three-original-component-interfaces-v1-20261023';inventory=take(interfaces,'landsd-20270-0/summary.json');chosen=[]
    for pair in inventory['pairs']:
        if pair['anyNonrendering']or not any(pair['dimensions'].get(str(d),0)for d in [1,2]):continue
        details=take(interfaces,pair['data']);valid=[c for c in details['contacts']if c['dimension']>0 and c['primitiveDimensions']==[2,2]];assert valid
        c=min(valid,key=lambda c:(c['bounds'][0][1],-c['maximumSpanM'],c['sourceFaceA'],c['sourceFaceB']));chosen.append(dict(componentA=pair['componentA'],componentB=pair['componentB'],originalContact=c))
    save(out/'selected-original-bridges.json.gz',chosen);print(dict(selectedBridges=len(chosen)),flush=True)
    attrs='government-xl-island-industrial-three-original-attributes-v1-20261023';attr=next(r for r in take(attrs,'attributes.json.gz')['rows']if r['uid']=='landsd/20270:0');runtime='government-xl-island-industrial-paired-current-runtime-v2-20261023';source=next(r for r in take(runtime,'selection.json.gz')['rows']if r['uid']=='landsd/20270:0');asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==inventory['sourceSHA256']==source['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
    prior='government-xl-island-industrial-tower-main-podium-fourworld-paths-v1-20261023';rows=[];exactcache={}
    for mode,t in worlds.items():
        before=take(prior,mode+'.json.gz');assert digest(t.tobytes())==before['sourceWorldSHA256'];joins=[]
        for number,c in enumerate(chosen):
            old=c['originalContact'];a,b=old['sourceFaceA'],old['sourceFaceB'];key=digest(t[[a,b]].tobytes())
            if key not in exactcache:exactcache[key]=exact_component_contacts_with_primitives(t,[a],t,[b],maximum_pairs=1)
            proof=exactcache[key];assert proof['allPairsExamined'];valid=[p for p in proof['contacts']if p['dimension']>0 and p['primitiveDimensions']==[2,2]];joins.extend(valid)
            if number%1000==0:print(dict(mode=mode,replayed=number,total=len(chosen)),flush=True)
        report=dict(targets=[dict(witness=r['witness'],incidentFaces=r['incidentFaces'])for r in before['rows']],proof=before['exactContacts']);verified=paths(t,report,joins)
        save(out/(mode+'.json.gz'),dict(sourceWorldSHA256=before['sourceWorldSHA256'],supportWorldSHA256=before['supportWorldSHA256'],finiteSourceJoins=joins,rows=verified));rows.append(dict(mode=mode,targets=len(verified),verifiedPaths=sum(r['verifiedPath']is not None for r in verified),remaining=sum(r['verifiedPath']is None for r in verified),positiveSourceJoins=len(joins)));print(rows[-1],flush=True)
    result=dict(uids=['landsd/20270:0','landsd/159422:0'],rows=rows,installationApproved=False,sourceGeometryChanges=0,qualification='Fresh finite positive-dimensional original component contacts in each exact coordinate representation, convex original-face paths, unchanged 1mm incident residual and own endpoint-height ceilings. No point/nonrendering support credit or architectural/installation approval. Raw strict-interface negatives retained.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['original_contact_paths_with_finite_joins_v1_20261023.py','exact_original_primitive_contacts_v1.py','exact_packed_world_geometry_20261009.py']);module('joined_path_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fourworld-finite-original-component-joined-support-paths',refs,result)

if __name__=='__main__':main()
