"""Compose the existing fixed-clearance kernel across disconnected source floors.

Keep pre-existing low terrain exactly, outside every edit domain; apply the1.2m
floor to every new fragment. This does not modify either existing constructor.
"""
import numpy as np
import shapely
from source_floor_return_with_existing_seabed_v1_20261102 import inset as single
from retained_native_template_v3_20261023 import verify_existing_low_faces

def inset(terrain,source):
    terrain=np.asarray(terrain,dtype='<f8');source=np.asarray(source,dtype='<f8')
    assert np.isfinite(terrain).all()and np.isfinite(source).all()
    polygons=shapely.polygons(source[:,:,[0,2]]);assert len(polygons)and np.all(shapely.area(polygons)>1e-10)
    outer=shapely.union_all(polygons).buffer(1.,join_style='mitre').buffer(3.,join_style='mitre')
    components=sorted(shapely.get_parts(outer),key=lambda p:p.bounds);assert all(p.geom_type=='Polygon'for p in components)
    out=terrain.copy();origins=list(range(len(terrain)));kinds=['unchanged']*len(terrain);changed=set();assigned=[];proofs=[]
    for component in components:
        ids=[i for i,p in enumerate(polygons)if component.intersection(p).area>1e-10];assert ids;assigned+=ids
        out,proof=single(out,source[ids]);assert shapely.from_wkt(proof['outerWKT']).symmetric_difference(component).area<1e-6
        changed.update(origins[i]for i in proof['changedTerrainFaceIndices'])
        rows=proof['outputLineage'];kinds=[kinds[r['parentFace']]if r['kind']=='unchanged'else r['kind']for r in rows];origins=[origins[r['parentFace']]for r in rows]
        proofs.append(dict(sourceFloorIndices=ids,**proof))
    assert sorted(assigned)==list(range(len(source)))and len(out)<=25000
    lineage=[dict(parentFace=i,kind=k)for i,k in zip(origins,kinds)]
    untouched={r['parentFace']:i for i,r in enumerate(lineage)if r['kind']=='unchanged'}
    assert set(untouched)==set(range(len(terrain)))-changed
    assert all(np.array_equal(out[i],terrain[parent])for parent,i in untouched.items())
    assert all(out[i,:,1].min()>=1.2 for i,r in enumerate(lineage)if r['kind']!='unchanged')
    low=verify_existing_low_faces(terrain,out,lineage,outer)
    return out,dict(outputLineage=lineage,changedTerrainFaceIndices=sorted(changed),componentProofs=proofs,existingLowTerrainProof=low,sourceClearanceM=.05,coreMarginM=1.,returnWidthM=3.,sourceDerivedMinimumTerrainY=min(p['sourceDerivedMinimumTerrainY']for p in proofs),outerWKT=outer.wkt,sourceGeometryChanges=0,genericThresholdChanges=0,policy='Existing source-floor return independently per connected domain; exact old low-terrain preservation outside domains, unchanged1.2m floor for all new fragments, fixed1m core/3m return/0.05m clearance/25k cap. No source-model edit or acceptance.')
