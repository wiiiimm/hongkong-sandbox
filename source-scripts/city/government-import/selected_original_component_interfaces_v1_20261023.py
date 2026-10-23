"""Enumerate complete exact interfaces between every original source component.

This is source topology evidence only: contact does not establish architectural
roles, load paths or installation acceptance. All degenerate faces are retained.
"""
import argparse
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture','census']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs=[Path(__file__)]
    def take(batch,name):
        _,pins=authenticate(base/batch);path=base/batch/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([base/batch/'result.json',path]);return read(path)
    selected=take(a.capture,'selection.json.gz')['rows'];inventory=take(a.census,'summary.json');summaries=[]
    assert 0<len(selected)<=8 and {r['uid']for r in selected}==set(inventory['uids'])
    for source in selected:
        record=next(r for r in inventory['rows']if r['uid']==source['uid']);topology=take(a.census,record['census']);assert topology['sourceSHA256']==source['sourceSHA256']
        asset=ROOT/source['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==source['sourceSHA256'];refs.append(asset)
        tri=decode_original_world_triangles(raw);assert len(tri)==source['triangles']and digest(tri.tobytes())==topology['completeWorldTrianglesSHA256']
        groups=[dict(kind='renderable-shared-edge-component',faceIds=g)for g in topology['sharedEdgeConnectedComponents']]
        groups.extend(dict(kind='nonrendering-no-support-credit',faceIds=[i])for i in topology['exactNonrenderingOriginalFaces'])
        assert sorted(i for g in groups for i in g['faceIds'])==list(range(len(tri)))
        bounds=[(tri[g['faceIds']].min((0,1)),tri[g['faceIds']].max((0,1)))for g in groups]
        nominated=[(i,j)for i in range(len(groups))for j in range(i+1,len(groups))if np.all(bounds[i][1]>=bounds[j][0])and np.all(bounds[j][1]>=bounds[i][0])]
        folder=out/source['uid'].replace('/','-').replace(':','-');pairs=[]
        for done,(i,j)in enumerate(nominated,1):
            contacts=exact_component_contacts_with_primitives(tri,groups[i]['faceIds'],tri,groups[j]['faceIds'],maximum_pairs=1000000)
            assert contacts['allPairsExamined']
            path=folder/f'{i}-{j}.json.gz';save(path,contacts)
            pairs.append(dict(componentA=i,componentB=j,contacts=len(contacts['contacts']),trianglePairsTested=contacts['trianglePairsTested'],dimensions=dict(Counter(str(c['dimension'])for c in contacts['contacts'])),data=str(path.relative_to(out)),anyNonrendering=groups[i]['kind']!='renderable-shared-edge-component'or groups[j]['kind']!='renderable-shared-edge-component',supportCredit=False))
            save(out/'progress.json',dict(uid=source['uid'],completePairs=done,nominatedPairs=len(nominated),sourcesCompleted=len(summaries),installationApproved=False))
            if done%20==0:print(dict(uid=source['uid'],pairs=done,total=len(nominated)),flush=True)
        result=dict(uid=source['uid'],sourceSHA256=source['sourceSHA256'],sourceFaces=len(tri),groups=groups,nominatedPairs=len(nominated),allOtherGroupPairsHaveDisjointExactAABBs=True,allNominatedPairsExamined=True,pairs=pairs,sourceGeometryChanges=0,installationApproved=False)
        save(folder/'summary.json',result)
        summaries.append(dict(uid=source['uid'],sourceSHA256=source['sourceSHA256'],sourceFaces=len(tri),groups=len(groups),nominatedPairs=len(nominated),contactingPairs=sum(r['contacts']>0 for r in pairs),trianglePairsTested=sum(r['trianglePairsTested']for r in pairs),summary=str((folder/'summary.json').relative_to(out))))
    result=dict(uids=[r['uid']for r in selected],rows=summaries,sourceGeometryChanges=0,installationApproved=False,qualification='All original faces partitioned once into exact shared-edge components and nonrendering primitives; every overlapping finite component AABB pair checked with exact primitive contacts. Point/line/area contact and degenerate primitives give no automatic support/architectural/installation credit.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py'])
    module('complete_component_interfaces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-component-interface-graph-diagnostic',refs,result)
    print(summaries,flush=True)


if __name__=='__main__':main()
