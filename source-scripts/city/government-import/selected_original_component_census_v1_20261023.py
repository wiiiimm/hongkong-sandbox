"""Account for every unchanged original face with exact nonzero shared-edge topology."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    _,pins=authenticate(base/a.capture);selected=base/a.capture/'selection.json.gz';assert digest(selected.read_bytes())==pins[str(selected.relative_to(ROOT))]
    rows=read(selected)['rows'];assert 0<len(rows)<=8;refs=[Path(__file__),base/a.capture/'result.json',selected];summary=[]
    for row in rows:
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset)
        tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']
        report=census(tri,list(range(len(tri))))
        components=[]
        for ids in report['sharedEdgeConnectedComponents']:
            part=tri[ids];components.append(dict(faces=len(ids),firstFace=ids[0],worldBounds=dict(min=part.min((0,1)).tolist(),max=part.max((0,1)).tolist())))
        report.update(uid=row['uid'],sourceSHA256=row['sourceSHA256'],components=components,installationApproved=False)
        name=row['uid'].replace('/','-').replace(':','-')+'.json.gz';save(out/name,report)
        summary.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],sourceFaces=len(tri),renderableComponents=len(components),componentFaceCounts=sorted([c['faces']for c in components],reverse=True),exactNonrenderingFaces=len(report['exactNonrenderingOriginalFaces']),boundaryEdges=report['boundaryEdges'],nonmanifoldEdges=report['nonmanifoldEdges'],twoFaceOrientationConflicts=report['twoFaceOrientationConflicts'],census=name))
    result=dict(uids=[r['uid']for r in rows],rows=summary,sourceGeometryChanges=0,installationApproved=False,qualification='Complete exact original face/edge/component inventory. Nonrendering primitives preserved without support/bridge credit. Components are not architectural roles or closed solids; every runtime coordinate mode/contact/support/current scene still needs separate checks.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py'])
    module('selected_component_census_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-unchanged-original-component-census',refs,result)
    print([{k:v for k,v in r.items()if k not in ['componentFaceCounts','sourceSHA256','census']}for r in summary],flush=True)


if __name__=='__main__':main()
