"""Complete exact original component/contact census; no support roots or approval."""
import argparse
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();_,pins=authenticate(base/a.capture);sp=base/a.capture/'selection.json.gz';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))];selection=read(sp);rows=selection['rows'];assert 1<len(rows)<=8 and len({r['uid']for r in rows})==len(rows);refs=[Path(__file__),base/a.capture/'result.json',sp];parts=[];geometry=[];actors=[];empty=[]
    for row in rows:
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];offset=sum(len(t)for t in geometry);geometry.append(tri);topology=census(tri,list(range(len(tri))));save(out/(row['uid'].split('/')[1]+'-topology.json.gz'),topology)
        actors.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],globalFaceRange=[offset,offset+len(tri)],originalWorldSHA256=digest(tri.tobytes())))
        empty.extend(offset+i for i in topology['exactNonrenderingOriginalFaces'])
        for n,ids in enumerate(topology['sharedEdgeConnectedComponents']):
            group=tri[ids];parts.append(dict(actorUID=row['uid'],originalComponent=n,globalOriginalFaces=[offset+i for i in ids],bounds=[group.min((0,1)).tolist(),group.max((0,1)).tolist()]))
    tri=np.concatenate(geometry);allids=[i for p in parts for i in p['globalOriginalFaces']];assert len(set(allids))==len(allids)and set(allids)|set(empty)==set(range(len(tri)))and not set(allids)&set(empty)
    bounds=np.asarray([p['bounds']for p in parts]);pairs=[(i,j)for i in range(len(parts))for j in range(i+1,len(parts))if np.all(bounds[i,1]>=bounds[j,0])and np.all(bounds[j,1]>=bounds[i,0])];save(out/'input.json.gz',dict(actors=actors,components=parts,exactNonrenderingOriginalFaces=empty,completeOriginalFaces=len(tri),completeOriginalWorldSHA256=digest(tri.tobytes()),inclusiveBoundsCandidatePairs=pairs));contacts=[];reports=[]
    for n,(i,j)in enumerate(pairs,1):
        proof=exact_finite_contacts(tri,parts[i]['globalOriginalFaces'],tri,parts[j]['globalOriginalFaces']);assert proof['allPairsExamined'];positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2];file=out/'pairs'/(str(i)+'-'+str(j)+'.json.gz');save(file,proof)
        if positive:contacts.append(dict(components=[i,j],actorUIDs=[parts[i]['actorUID'],parts[j]['actorUID']],globalOriginalFaces=[positive[0]['sourceFaceA'],positive[0]['sourceFaceB']],exactPositiveWitness=positive[0]))
        reports.append(dict(components=[i,j],positiveInterfaces=len(positive),pointOnlyOrNonSurfaceContacts=len(proof['contacts'])-len(positive),proofPath=str(file.relative_to(ROOT)),proofSHA256=digest(file.read_bytes())))
        if n%25==0 or n==len(pairs):save(out/'progress.json',dict(completed=n,total=len(pairs),positiveEdges=len(contacts),sourceGeometryChanges=0,installationApproved=False));print(dict(completed=n,total=len(pairs),positiveEdges=len(contacts)),flush=True)
    adjacency={i:set()for i in range(len(parts))}
    for c in contacts:i,j=c['components'];adjacency[i].add(j);adjacency[j].add(i)
    remaining=set(adjacency);groups=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);group={seed};todo=[seed]
        while todo:
            i=todo.pop()
            for j in sorted(adjacency[i]&remaining):remaining.remove(j);group.add(j);todo.append(j)
        groups.append(sorted(group))
    save(out/'contacts.json.gz',dict(positiveOriginalComponentContacts=contacts,pairReports=reports,connectedOriginalComponentGroups=groups))
    result=dict(uids=[r['uid']for r in rows],completeOriginalFaces=len(tri),renderableOriginalComponents=len(parts),exactNonrenderingOriginalFaces=empty,candidateComponentPairs=len(pairs),verifiedPositiveOriginalComponentEdges=len(contacts),connectedComponentGroups=groups,actorComponentCounts=dict(Counter(p['actorUID']for p in parts)),actorGroupMembership={r['uid']:sorted({n for n,group in enumerate(groups)if any(parts[i]['actorUID']==r['uid']for i in group)})for r in rows},sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,physicalAcceptance=False,groundRootCredit=False,publication=False,qualification='Every exact original face belongs to a complete nonzero-shared-edge component or is separately retained as exactly nonrendering. Every inclusive closed-bound candidate component pair checked with exact finite original surface contacts. Point-only and collapsed primitives cannot bridge. This is connectivity, not load-bearing intent, ground-root, identity, collision, physical or publication acceptance.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']);module('original_component_census_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-assembly-component-finite-contact-census',refs,result);print({k:result[k]for k in ['completeOriginalFaces','renderableOriginalComponents','verifiedPositiveOriginalComponentEdges','actorComponentCounts','actorGroupMembership']},flush=True)


if __name__=='__main__':main()
