"""Reduce exact component contacts without treating connectivity as support."""
import argparse
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import numpy as np

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','interfaces','capture']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[HERE/'selected_original_contact_connectivity_v1_20261023.py']
    def take(batch,name):
        folder=base/batch;_,pins=authenticate(folder);path=folder/name
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([folder/'result.json',path]);return read(path)
    sources=take(a.capture,'selection.json.gz')['rows'];inventory=take(a.interfaces,'summary.json');rows=[]
    assert {s['uid']for s in sources}==set(inventory['uids'])
    for row in inventory['rows']:
        d=take(a.interfaces,row['summary']);groups=d['groups'];valid={i for i,g in enumerate(groups)if g['kind']=='renderable-shared-edge-component'};parent={i:i for i in valid}
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        edges=0
        for pair in d['pairs']:
            i,j=pair['componentA'],pair['componentB']
            if i in valid and j in valid and any(pair['dimensions'].get(str(k),0)>0 for k in (1,2)):
                parent[find(i)]=find(j);edges+=1
        clusters={}
        for i in sorted(valid):clusters.setdefault(find(i),[]).extend(groups[i]['faceIds'])
        source=next(s for s in sources if s['uid']==row['uid']);asset=ROOT/source['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==source['sourceSHA256']==d['sourceSHA256'];refs.append(asset)
        tri=decode_original_world_triangles(raw);assert len(tri)==d['sourceFaces']
        cluster_rows=[]
        for ids in sorted(clusters.values(),key=lambda ids:(-len(ids),min(ids))):
            t=tri[ids];cluster_rows.append(dict(faceIds=sorted(ids),faceCount=len(ids),bounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],supportApproved=False))
        excluded=sorted(i for k,g in enumerate(groups)if k not in valid for i in g['faceIds'])
        assert sorted(excluded+[i for c in cluster_rows for i in c['faceIds']])==list(range(len(tri)))
        result=dict(uid=row['uid'],sourceSHA256=source['sourceSHA256'],renderableGroups=len(valid),positiveDimensionEdges=edges,clusters=cluster_rows,excludedNonrenderingFaces=excluded,supportApproved=False)
        path=out/(row['uid'].replace('/','-').replace(':','-')+'.json');save(path,result)
        rows.append(dict(uid=row['uid'],renderableGroups=len(valid),positiveDimensionEdges=edges,connectedGroups=len(clusters),faceCounts=[c['faceCount']for c in cluster_rows],excludedNonrenderingFaces=len(excluded),details=str(path.relative_to(ROOT))))
    result=dict(uids=inventory['uids'],rows=rows,installationApproved=False,sourceGeometryChanges=0,qualification='Exact positive-length/area contact connectivity only. Nonrendering primitives and point-only contacts excluded. All original faces accounted for. Connectedness establishes neither architecture nor a gravity load path; separate support review required.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('connectivity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-positive-dimensional-contact-connectivity',refs,result)
    print(rows,flush=True)

if __name__=='__main__':main()
