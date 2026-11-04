"""Measure exact source/footprint boundary differences; no acceptance buffers or approval."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture','uid']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists()
    _,pins=authenticate(base/a.capture)
    sourcepath=base/a.capture/'selection.json.gz';assert digest(sourcepath.read_bytes())==pins[str(sourcepath.relative_to(ROOT))]
    row=next(r for r in read(sourcepath)['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
    form=next(b for b in read(tile)['buildings']if b['uid']==a.uid);assert form==row['source']['building']
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles']
    source=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));target=shapely.Polygon(form['rings'][0],form['rings'][1:])
    distances=[.1,.25,.5,.75,1.,1.5]
    probes=[dict(distanceMetres=d,entireTargetCovered=bool(source.buffer(d,quad_segs=64).covers(target)))for d in distances]
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],modelId=row['modelId'],completeSourceFaces=len(tri),originalWorldSHA256=digest(tri.astype('<f8').tobytes()),targetAreaM2=target.area,sourceProjectionAreaM2=source.area,uncoveredTargetAreaM2=target.difference(source).area,targetCoveredBySourceProjection=target.intersection(source).area/target.area,distanceDiagnostics=probes,sourceSpecific2DPrecisionCodeKnown=False,installationApproved=False,identityApproved=False,sourceGeometryChanges=0,qualification='Diagnostic distances only: original identity/footprint tests remain unbuffered and unchanged. These probes do not establish a record-specific accuracy allowance or excuse neighbour/placement failures. Exact-source interpretation remains separate.',referenceSources=[dict(url='https://www.hkmapmeta.gov.hk/mcs/home/web/data/lands/b1000.faq.html',context='B1000 uses a label-point geographic identifier and heterogeneous capture methods; general published accuracy is not a precision guarantee for this record.'),dict(url='https://static.csdi.gov.hk/csdi-webpage/download/common/5fae157cd31d217e580ea22cd65cc3e12f4bd55a26bf26339693b2865204ae1e',context='The original non-textured LOD3 is a feature-based building polyhedron with a unique model identifier. No geometry or placement is modified here.')])
    save(doc/'summary.json',result)
    refs=[Path(__file__),base/a.capture/'result.json',sourcepath,asset,tile,HERE/'exact_packed_world_geometry_20261009.py']
    module('boundary_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-source-boundary-context',refs,result)
    print(dict(uid=a.uid,uncoveredTargetAreaM2=result['uncoveredTargetAreaM2'],distanceDiagnostics=probes),flush=True)


if __name__=='__main__':main()
