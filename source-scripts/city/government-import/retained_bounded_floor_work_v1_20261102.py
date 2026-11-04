"""Run the unchanged floor kernel only on its bounded installed-terrain work set.

Existing faces outside the exact outer domain stay literal. The established
retained_inset_work_budget contract checks the complete result separately.
"""
import numpy as np,shapely
from source_floor_return_with_existing_seabed_v1_20261102 import inset as single
from retained_inset_work_budget_v1_20261026 import verify as verify_work

def budget(baseline,output,lineage):
    records=[dict(parentFace=r['parentFace'],kind=r['kind']if r['kind']in ['unchanged','parent-fragment']else'original-inset-or-return')for r in lineage]
    return verify_work(baseline,output,records)

def inset(terrain,source):
    terrain=np.asarray(terrain,dtype='<f8');source=np.asarray(source,dtype='<f8')
    assert np.isfinite(terrain).all()and np.isfinite(source).all()
    outer=shapely.union_all(shapely.polygons(source[:,:,[0,2]])).buffer(1.,join_style='mitre').buffer(3.,join_style='mitre')
    selected=np.flatnonzero(shapely.intersects(shapely.polygons(terrain[:,:,[0,2]]),outer));assert len(selected)>0
    outside=np.flatnonzero(~np.isin(np.arange(len(terrain)),selected))
    # The existing kernel retains its complete25000work-face, area, clearance,
    # height and parent-fragment assertions. No threshold is changed here.
    work,proof=single(terrain[selected],source)
    assert len(work)<=25000
    rows=[dict(parentFace=int(i),kind='unchanged')for i in outside]
    rows.extend({**r,'parentFace':int(selected[r['parentFace']])}for r in proof['outputLineage'])
    output=np.concatenate([terrain[outside],work]);assert np.array_equal(output[:len(outside)],terrain[outside])
    changed=[int(selected[i])for i in proof['changedTerrainFaceIndices']]
    return output,{**proof,'outputLineage':rows,'changedTerrainFaceIndices':changed,'boundedWorkInputFaces':len(selected),'retainedWorkBudget':budget(terrain,output,rows),'outsideWorkFacesLiteral':True,'genericThresholdChanges':0}
