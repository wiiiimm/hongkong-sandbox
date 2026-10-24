"""Test complete original facets of detached groups against finite same-source facades."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify as finite_facade


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','census','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch;out=ROOT/'docs/astra-city/government-import'/a.batch;assert not out.exists();base=out.parent;refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    census=take(a.census,base/a.census/'input.json.gz');summary=take(a.census,base/a.census/'summary.json');parts=census['components'];groups=summary['connectedComponentGroups'];actor=next(r for r in census['actors']if r['uid']==a.uid);offset,end=actor['globalFaceRange'];hostids=sorted(i-offset for k in groups[0]for i in parts[k]['globalOriginalFaces']if parts[k]['actorUID']==a.uid);assert hostids
    candidates=[dict(group=n,faces=sorted(i-offset for k in group for i in parts[k]['globalOriginalFaces']))for n,group in enumerate(groups)if n and all(parts[k]['actorUID']==a.uid for k in group)];assert len(candidates)==len(groups)-1
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==attr['sourceSHA256']==actor['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(raw),**{n:np.asarray(attr[k]).reshape(-1,3)[ix]for n,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]});assert digest(modes['original'].tobytes())==actor['originalWorldSHA256'];cached={};bindings=[]
    for mode,tri in modes.items():
        assert len(tri)==row['triangles']==end-offset;sha=digest(tri.tobytes());bindings.append(dict(mode=mode,completeSourceWorldSHA256=sha))
        if sha in cached:continue
        hosts=tri[hostids];lo,hi=hosts.min(1),hosts.max(1);records=[]
        for candidate in candidates:
            ids=candidate['faces'];assert ids and set(ids).isdisjoint(hostids);part=tri[ids];lower=np.nextafter(part.min((0,1))-.1,-np.inf);upper=np.nextafter(part.max((0,1))+.1,np.inf);selected=np.flatnonzero(np.all(hi>=lower,axis=1)&np.all(lo<=upper,axis=1));faceids=[hostids[int(i)]for i in selected];selectedhosts=hosts[selected];passing=[]
            for i in ids:
                if not len(selectedhosts):continue
                proof=finite_facade(tri[i],selectedhosts)
                if proof['verifiedWholeOriginalFacetFiniteFacadeBand']:passing.append(dict(originalSourceFace=i,proof=proof))
            record=dict(group=candidate['group'],completeOriginalFaceIds=ids,sourceGroupBounds=[part.min((0,1)).tolist(),part.max((0,1)).tolist()],sameSourceMainGroupHostFaceIds=faceids,allPotentialHostsWithinFixedBandIncluded=True,wholeFacetFacadeBandWitnesses=passing,hasWholeFacetFacadeWitness=bool(passing));save(out/(mode+'-group-'+str(candidate['group'])+'.json.gz'),record);records.append(dict(group=candidate['group'],originalFaces=len(ids),passingWholeFacets=len(passing),candidateHostFacets=len(faceids)));print(dict(mode=mode,**records[-1]),flush=True)
        cached[sha]=dict(proofMode=mode,groups=records,groupsWithWholeFacetWitness=sum(r['passingWholeFacets']>0 for r in records))
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],coordinateBindings=bindings,distinctWorlds=cached,separateOriginalGroups=len(candidates),sourceGeometryChanges=0,sourcePoseChanges=0,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every face of each separate original group probed against the exact finite same-source main-group facade union in the unchanged0.1m Euclidean band. Host broadphase includes every facet whose bounds meet the full group expanded by that existing band. Complete facets only, no new backing plane, snapping, welding or convex hull. A nearby/backing facet is association evidence, not an architectural mount, load, root or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'exact_original_projection_coverage_20261009.py']);module('source_facade_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-separate-group-finite-facade-association-context',refs,result)


if __name__=='__main__':main()
