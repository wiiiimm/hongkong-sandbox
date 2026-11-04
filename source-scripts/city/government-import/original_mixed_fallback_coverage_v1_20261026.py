"""Conservative footprint coverage for every mixed BASIC/original companion state.

An activated source and its mandatory closure use complete original projections.
Every other companion contributes only BASIC intersection original: a lower bound
for either representation, requiring no enumeration or assumed detail download.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from candidate_availability_graph_v1_20261026 import validate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','graph']:ap.add_argument('--'+key,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.runtime,a.attributes])and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(a.runtime,'selection.json.gz');attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    by={r['uid']:r for r in selection['rows']};attributes={r['uid']:r for r in attrs['rows']}
    graphpath=(ROOT/a.graph).resolve();assert graphpath.is_relative_to(ROOT);proposal=read(graphpath)
    assert proposal['diagnosticOnly']and not proposal['installationApproved']and set(proposal['dependencies'])==set(by)
    graph,order=validate(list(by),[u+','+v for u,peers in proposal['dependencies'].items()for v in peers]);refs.append(graphpath)
    closures={}
    for u in order:
        closures[u]={u}
        for v in graph[u]:closures[u].update(closures[v])
    forms={};worlds={};hashes={}
    for u,r in by.items():
        asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']==attributes[u]['sourceSHA256'];refs.append(asset);hashes[u]=r['sourceSHA256']
        assert not r['candidate']['entry'].get('suppressesBuildingUids'),'Mixed-fallback proof forbids cross-UID source suppression'
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(f for f in read(tile)['buildings']if f['uid']==u)==r['source']['building'];refs.append(tile)
        f=r['source']['building'];forms[u]=shapely.Polygon(f['rings'][0],f['rings'][1:]);assert forms[u].is_valid and forms[u].area>0
        attr=attributes[u];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds[u]=dict(original=decode_original_world_triangles(raw),**{m:np.asarray(attr[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
        assert all(len(t)==r['triangles']for t in worlds[u].values())
    rows=[]
    for mode in ['original','literal','leftF32','balancedF32']:
        detailed={u:shapely.union_all(shapely.polygons(worlds[u][mode][:,:,[0,2]]))for u in by}
        common={u:detailed[u].intersection(forms[u])for u in by}
        for u in by:
            guaranteed=shapely.union_all([detailed[v]if v in closures[u]else common[v]for v in by])
            fraction=float(guaranteed.intersection(forms[u]).area/forms[u].area)
            rows.append(dict(uid=u,mode=mode,guaranteedMixedCoverageFraction=fraction,passedExistingCoverageGate=fraction>=.95,
                             completeDependencyClosure=sorted(closures[u]),basicOrOriginalCompanions=sorted(set(by)-closures[u]),
                             completeOriginalFaces=by[u]['triangles']))
        print(dict(mode=mode,minimumGuaranteedCoverage=min(r['guaranteedMixedCoverageFraction']for r in rows if r['mode']==mode)),flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=list(by),sourceSHA256ByUid=hashes,currentManifestSHA256=selection['manifestSHA256'],proposedDependencies=graph,
                dependencyFirstOrder=order,acyclic=True,rows=rows,allFourWorldMixedCoveragePassed=all(r['passedExistingCoverageGate']for r in rows),
                requiredCoInstallationUids=sorted(by),sourceGeometryChanges=0,physicalAcceptance=False,identityAccepted=False,
                installationApproved=False,publication=False,qualification='Conservative planar coverage lower bound for every mixed companion fallback state, with the nominated active source closure detailed and all remaining exact BASIC/original intersections. All twelve actors must be co-installed. This proves only existing95percent footprint coverage; it does not prove source identity, physical support, visibility, BASIC suppression behaviour, runtime budgeting or publication.')
    save(out/'summary.json',result);refs.extend([HERE/'candidate_availability_graph_v1_20261026.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('mixed_original_fallback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-conservative-mixed-basic-original-footprint-coverage',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
