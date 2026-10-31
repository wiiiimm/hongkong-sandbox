"""Measure exact original projection coverage for a proposed dependency closure."""
import argparse
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from candidate_availability_graph_v1_20261026 import validate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime','graph']:p.add_argument('--'+name,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    _,pins=authenticate(base/a.runtime);selection=base/a.runtime/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
    selected=read(selection);by={r['uid']:r for r in selected['rows']};graphpath=(ROOT/a.graph).resolve();assert graphpath.is_relative_to(ROOT)
    proposal=read(graphpath);assert proposal['diagnosticOnly']is True and proposal['installationApproved']is False
    assert set(proposal['dependencies'])==set(by)
    graph,order=validate(list(by),[u+','+v for u,values in proposal['dependencies'].items()for v in values])
    refs=[Path(__file__),HERE/'candidate_availability_graph_v1_20261026.py',HERE/'exact_packed_world_geometry_20261009.py',base/a.runtime/'result.json',selection,graphpath]
    projections={};forms={};closures={};hashes={}
    for uid in order:
        row=by[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);hashes[uid]=row['sourceSHA256']
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
        tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles']
        projections[uid]=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));f=row['source']['building'];forms[uid]=shapely.Polygon(f['rings'][0],f['rings'][1:])
        closure={uid}
        for peer in graph[uid]:closure.update(closures[peer])
        closures[uid]=closure
    rows=[]
    for uid in by:
        combined=shapely.union_all([projections[v]for v in closures[uid]]);target=forms[uid]
        rows.append(dict(uid=uid,directDependencies=graph[uid],completeDependencyClosure=sorted(closures[uid]),ownCoverageFraction=float(projections[uid].intersection(target).area/target.area),closureCoverageFraction=float(combined.intersection(target).area/target.area),diagnosticOnlyNonImport=uid in proposal['nonImportDiagnosticUids']))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=list(by),sourceSHA256ByUid=hashes,dependencyFirstOrder=order,proposedDependencies=graph,rows=rows,currentManifestSHA256=selected['manifestSHA256'],acyclic=True,sourceGeometryChanges=0,physicalAcceptance=False,identityAccepted=False,installationApproved=False,publication=False,qualification='Complete original Float64 source projections within exact proposed dependency closures only. Projection at any height is not roof-height, source ownership, structural support, BASIC/native collision, device, browser, dependency fallback or installation approval. A&E is explicitly non-import diagnostic.')
    save(out/'summary.json',result)
    module('candidate_dependency_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'proposed-acyclic-original-dependency-closure-projection-diagnostic',list(dict.fromkeys(refs)),result)
    print([(r['uid'],r['closureCoverageFraction'])for r in rows],flush=True)


if __name__=='__main__':main()
